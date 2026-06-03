import uvicorn
from .api import app
import os

if __name__ == "__main__":
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", "8000"))
    debug = os.getenv("DEBUG", "False").lower() == "true"
    uvicorn.run("api:app", host=host, port=port, reload=debug)
