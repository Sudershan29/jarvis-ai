import os
if os.getenv("ENV") != "production":
    import dotenv
    dotenv.load_dotenv()

from typing import List
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_openai import ChatOpenAI

class EventWeek(BaseModel):
    class Event(BaseModel):
        name: str = Field(description="name of the event")
        startTime: str = Field(
            description="start time of the event in 2024-03-20T10:30:00-05:00 format"
        )
        endTime: str = Field(
            description="end time of the event in 2024-03-20T10:30:00-05:00 format"
        )
        internal: bool = Field(description="true if its a routine else false")
        color: str = Field(description="color of the event")

    day1: List[Event] = Field(description="Events excluding routines for day 1")
    day2: List[Event] = Field(description="Events excluding routines for day 2")
    day3: List[Event] = Field(description="Events excluding routines for day 3")

TEMPLATE = """
        You are a world class calendar management assistant. \
        You have been given <non_Moveable_Events>, <routines>, <skills/tasks_to_add>, and timezone {timezone} of the user. \
        Your task is to plan the next 3 days for the user given today is {today} Create a timetable using taking <skills/tasks_to_add> \
        and checking if they need to be scheduled, by checking if achieved < allocated and accounting for deadline /
        Assume user follows routines everyday, and has non_moveable_events scheduled already which are not to be moved, \
        and you have flexibility with skills/tasks_to_add\

        <non_Moveable_Events>
        Use startTime and endTime to determine the date, and duration of the event\
        Set `internal` as false in the output
        {non_movable_events}
        </non_moveable_Events>

        <Routines>
        Incorporate them into your schedule everyday but return them as internal : true in the result
        {routines}
        </Routines>

        <Skills/Tasks_To_Add>
        1. Maximize the number of scheduled tasks as possible in the next 3 days. \
        2. The maximum hours you can schedule a task is the difference between duration and allocated in minutes. Do not schedule if the difference is non positive. \
        3. Obey the constraints with routines and non_moveable_events \
        4. Set `internal` as false in the output \
        {to_schedule}
        </Skills/Tasks_To_Add>

        Keep it concise, take your time to think to avoid collision and maximize time effieciency. \ 
        Ensure to return only the timetable in JSON format and ensure startTime and endTime are in 2024-03-20T10:30:00-05:00 format\
        without any explanations. Keep the day1, day2, and day3 params in the result the same. \

        day1: [ /definition/Event ]
        day2: [ /definition/Event ]
        day3: [ /definition/Event ]
        """

TEMPLATE_INPUT_VARIABLES = [
    "timezone",
    "non_movable_events",
    "routines",
    "to_schedule",
    "today",
]

def planThisWeek(events, schedules, routines, timezone, today):
    # gpt-3.5-turbo-1106, gpt-4-turbo
    model = ChatOpenAI(model="gpt-3.5-turbo-1106", temperature=0)
    parser = JsonOutputParser(pydantic_object=EventWeek)
    prompt = PromptTemplate(
        template=TEMPLATE,
        input_variables=TEMPLATE_INPUT_VARIABLES,
        partial_variables={"format_instructions": parser.get_format_instructions()},
    )

    chain = prompt | model | parser
    return chain.invoke(
        {
            "timezone": timezone,
            "non_movable_events": events,
            "routines": routines,
            "to_schedule": schedules,
            "today": today,
        }
    )
