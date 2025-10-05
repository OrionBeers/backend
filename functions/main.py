from firebase_functions import https_fn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import users, publish, prediction, dashboard
from routers.publish import *


app = FastAPI()

# Configure CORS to allow all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

routes = [users.router, publish.router, prediction.router, dashboard.router]

# Include routers
for route in routes:
    app.include_router(route)

@https_fn.on_request()
def api(req: https_fn.Request) -> https_fn.Response:
    """
    Main entry point for Firebase Functions.
    All HTTP requests are forwarded to the FastAPI application.
    """
    from fastapi.testclient import TestClient

    # Create a test client to make requests to FastAPI
    client = TestClient(app)

    # Convert Firebase request to FastAPI-compatible format
    method = req.method
    path = req.path
    headers = dict(req.headers)

    # Make the request to FastAPI
    if method == "GET":
        response = client.get(path, headers=headers, params=req.args)
    elif method == "POST":
        response = client.post(path, headers=headers, json=req.get_json(silent=True))
    elif method == "PUT":
        response = client.put(path, headers=headers, json=req.get_json(silent=True))
    elif method == "DELETE":
        response = client.delete(path, headers=headers)
    elif method == "PATCH":
        response = client.patch(path, headers=headers, json=req.get_json(silent=True))
    else:
        response = client.request(method, path, headers=headers)

    # Return the response
    return (response.content, response.status_code, dict(response.headers))
