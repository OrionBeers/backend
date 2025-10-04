from fastapi import FastAPI
from routers import data, items


app = FastAPI(
    title="Vercel + FastAPI",
    description="Vercel + FastAPI",
    version="1.0.0",
)

# Include routers
app.include_router(data.router)
app.include_router(items.router)

@app.get("/")
def get_index():
    return { "message": "OK" }