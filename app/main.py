from fastapi import FastAPI
from database import engine, Base
from routes import users, chat

app = FastAPI(title="TUM-GPT")

Base.metadata.create_all(bind=engine)

app.include_router(users.router)
app.include_router(chat.router)

@app.get("/")
def root():
    return {"message": "Welcome to TUM-GPT"}
