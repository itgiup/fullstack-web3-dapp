from fastapi import FastAPI

app = FastAPI()

@app.get("/health")
def health():
    return {"status": "OK"}

@app.post("/login")
def login():
    return {"token": "fake-jwt-token"}
