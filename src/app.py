from fastapi import FastAPI
from src.routers import data, items
import firebase_functions as functions
from infrastructure.database import database

## Db connection
database_connection = database.connect()


app = FastAPI(
    title="FastAPI + Firebase",
    description="FastAPI + Firebase Functions",
    version="1.0.0",
)

# Include routers
app.include_router(data.router)
app.include_router(items.router)

@app.get("/")
def get_index():
    return { "message": "OK" }