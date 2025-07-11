from fastapi import FastAPI
from pydantic import BaseModel
from dispathcer import AgentDispatcher

app = FastAPI(title="智能法律助手 API")

dispatcher = AgentDispatcher()

class QuestionRequest(BaseModel):
    prompt: str
    historyId: int
    model: str = "deepseek-chat"

@app.post("/ai/chat")
def chat(q: QuestionRequest):
    result = dispatcher.route_question(q.prompt, q.historyId, q.model)
    return result

@app.get("/")
def root():
    return {"message": "欢迎使用智能法律助手 API。访问 /docs 查看接口文档。"}


# uvicorn main:app --reload
# http://127.0.0.1:8000/docs