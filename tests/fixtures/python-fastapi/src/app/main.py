"""FastAPI application entrypoint."""

from fastapi import FastAPI

app = FastAPI(title="My App")


@app.get("/health")
async def health():
    return {"status": "ok"}
