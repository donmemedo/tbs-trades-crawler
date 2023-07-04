from pydantic import BaseModel, validator
from datetime import date, datetime
from config import setting
from typing import List, Any
from fastapi import Query


class TradesIn(BaseModel):
    start_date: date
    end_date: date


    @validator("start_date", pre=True)
    def parse_date(cls, value):
        return datetime.strptime(
            value, 
            setting.DATE_STRING
        ).date()


    @validator("end_date", pre=True)
    def parse_date(cls, value):
        return datetime.strptime(
            value, 
            setting.DATE_STRING
        ).date()
    

class ResponseOut(BaseModel):
    timeGenerated: date
    result: List[TradesIn] = List[Any]
    error: str = Query("nothing")

