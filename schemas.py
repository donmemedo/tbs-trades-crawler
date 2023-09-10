from pydantic import BaseModel
from datetime import date, datetime
from typing import List, Any, Optional
from fastapi import Query


class TradesIn(BaseModel):
    trade_date: date = Query(alias="TradeDate")
    cookie: str = Query(alias="Cookie")


class PortfolioIn(BaseModel):
    cookie: str = Query(alias="Cookie")


class DeleteTradesIn(BaseModel):
    trade_date: date = Query(alias="TradeDate")


class ResponseOut(BaseModel):
    timeGenerated: datetime
    result: List[TradesIn] = List[Any]
    error: str


class CustomersIn(BaseModel):
    register_date: Optional[date] = Query(alias="RegisterDate", default=None)
    modified_date: Optional[date] = Query(alias="ModifiedDate", default=None)


class ReconciliationIn(BaseModel):
    MarketerID: Optional[str] = Query(alias="MarketerID", default=None)
    start_date: Optional[date] = Query(alias="StartDate", default=None)
    end_date: Optional[date] = Query(alias="EndDate", default=None)


class CookieIn(BaseModel):
    cookie_value: str
