from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse

app = FastAPI()

@app.get("/")
async def home():
    return {"Hello": "World"}

@app.get("/chats")
async def chat(request=Request):
    return {"chat": "page"}
    # return redirect("http://127.0.0.1:8081/")


