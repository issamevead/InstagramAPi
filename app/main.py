import uvicorn
from fastapi import FastAPI
from routers import instagram

app = FastAPI(title="Instagram API", version="1.0.0")
app.include_router(instagram.router)


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8015)
