from fastapi import FastAPI
from api.routes.chat import router

app = FastAPI()


@app.get("/")
async def test():
    return "hello"


app.include_router(router=router)
