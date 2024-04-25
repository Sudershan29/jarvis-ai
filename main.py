from fastapi import FastAPI, Header
from typing_extensions import Annotated
from typing import Union
import datetime
from fastapi.middleware.cors import CORSMiddleware

from lib.api import getContextForAIAssistant
from lib.chat import planThisWeek

app = FastAPI(
    title="LangChain Server",
    version="1.0",
    description="A simple api server using Langchain's Runnable interfaces",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


API_VERSION = "v1"

@app.get(f"/api/{API_VERSION}/status")
async def root():
    return {"message": "Hello World", "status": 200}


# TODO: Rate limit this API
@app.get(f"/api/{API_VERSION}/plan")
async def plan(authorization: Annotated[Union[str, None], Header()] = None, startTime: str = None, endTime: str = None):
    user_token = authorization.split(" ")[1] if authorization else None
    if not user_token:
        return {"message": "Authorization header is missing", "status": 401}

    events, routines, schedules = getContextForAIAssistant(
        user_token, startTime, endTime
    )

    today = datetime.date.today().strftime("%Y-%m-%d")
    response = planThisWeek(events, schedules, routines, "America/Chicago", today)
    return response


@app.get(f"/api/{API_VERSION}/chat")
async def chat():
    response = planThisWeek([], [], [], "America/Chicago")
    return {"message": response, "status": 200}
