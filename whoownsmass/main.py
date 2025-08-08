from fastapi import FastAPI
from whoownsmass.api.v1.api import router


app = FastAPI(title="Who Owns Massachusetts API")

app.include_router(router)

@app.get("/")
def root():
    return {"Who Owns Massachusetts API is running"}
