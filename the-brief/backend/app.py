from fastapi import FastAPI

app = FastAPI(title="The Brief", version="0.1.0")


@app.get("/api/health")
async def health():
    return {"status": "ok"}
