from fastapi import FastAPI, Request
from langchain.document_loaders import DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
import chromadb
from chromadb.config import Settings
import requests
import json
import uuid
from langchain.schema import Document
from langchain import OpenAI
from langchain.chains.question_answering import load_qa_chain
from fastapi.responses import JSONResponse
import os
from fastapi.middleware.cors import CORSMiddleware



app = FastAPI()


origins = [
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)




EMBEDDING_URL = "http://localhost:9000/embeddings"
COLLECTION_NAME = "custom_knowledge"

# initialize chroma client 
client = chromadb.Client(Settings(
    chroma_db_impl="duckdb+parquet",
    persist_directory="./chroma_index"
))

@app.get("/")
async def home():
    return {"Hello": "World"}


@app.post("/query")
async def fetch_response(request: Request):
    try:
        req_payload = await request.json()

        # get embedding of query using embedding service
        query = req_payload['query']
        payload = json.dumps({
            "text": query
        })
        headers = {
            'Content-Type': 'application/json'
        }
        response = requests.request("POST", EMBEDDING_URL, headers=headers, data=payload)
        resp_json = response.json()

        # query chromadb with the query embedding and fetch the required documents
        print(f"collections are: {client.list_collections()}")
        collection = client.get_collection(COLLECTION_NAME)
        docs = collection.query(query_embeddings=[resp_json['embeddings']],
            n_results=3, include=["documents"])
        print(f"number of documents fetched are {len(docs['documents'][0])}")
        # convert the returned responses to langchain docuemnts
        documents = []
        for doc in docs['documents'][0]:
            document = Document(page_content=doc)
            documents.append(document)
        
        
        # initialize the openai model and pass the required docs and query to question answering chain 
        llm = OpenAI(temperature=0, openai_api_key=os.environ['API_KEY'])
        print("created the llm model")
        qa_chain = load_qa_chain(llm=llm, chain_type="stuff")
        print("created the qa chain")
        result = qa_chain.run(input_documents=documents, question=query)
        print("get the result")

        return JSONResponse({"answer": result})
    except Exception as exp:
        return JSONResponse({"message": f"Exception raised: {exp}"}, status_code=500)



@app.get("/load_document")
async def load_document(request: Request):
    
    try:
        # create chroma collection
        collection = client.get_or_create_collection(COLLECTION_NAME)
        print(f"collections are: {client.list_collections()}")


        # create document chunks
        loader = DirectoryLoader('pdf')
        documents = loader.load()
        print(f"documents to process are: {len(documents)}")
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=400, chunk_overlap=5)
        texts = text_splitter.split_documents(documents)
        print(f"no of chunks are: {len(texts)}")


        # create embeddings of chunks
        for idx, text in enumerate(texts):
            page_content = text.page_content
            page_content = page_content.replace("\n", " ")
            payload = json.dumps({
                "text": page_content
            })
            headers = {
                'Content-Type': 'application/json'
            }
            response = requests.request("POST", EMBEDDING_URL, headers=headers, data=payload)
            resp_json = response.json()
            id = uuid.uuid4()
            
            # add embedding and document in collection
            print("adding document in db")
            collection.add(documents=[page_content], embeddings=[resp_json['embeddings']], ids=[str(id)])


        print("all documents are added in db")
        return JSONResponse({"message": "process completed"}, status_code=200)
    except Exception as exp:
        return JSONResponse({"message": f"Exception raised: {exp}"}, status_code=500)



