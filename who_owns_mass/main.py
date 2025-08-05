from fastapi import FastAPI
from who_owns_mass_fastapi.views import router


app = FastAPI(title="Who Owns Massachusetts API")

app.include_router(router)

@app.get("/")
def root():
    return {"Who Owns Massachusetts API is running"}
