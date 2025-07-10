from fastapi import FastAPI
from pydantic import BaseModel
from RAG.agent.dispathcer import AgentDispatcher

app = FastAPI(title="智能法律助手 API")

dispatcher = AgentDispatcher()

class QuestionRequest(BaseModel):
    question: str
    model_name: str = "deepseek-chat"

@app.post("/ask")
def ask(q: QuestionRequest):
    result = dispatcher.route_question(q.question,q.max_results, q.model_name)
    return result

@app.get("/")
def root():
    return {"message": "欢迎使用智能法律助手 API。访问 /docs 查看接口文档。"}
