from fastapi import FastAPI, Request

app = FastAPI()


@app.get("/chats")
async def home(request=Request):
    return {"message": "Hello World"}


