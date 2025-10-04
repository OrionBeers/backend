from fastapi import FastAPI
from routers import users

app = FastAPI(
    title="FastAPI + Firebase",
    description="FastAPI + Firebase Functions",
    version="1.0.0",
)

routes = [users.router]

# Include routers
for route in routes:
    app.include_router(route, prefix='/api')


@app.get("/")
def get_index():
    return { "message": "OK" }