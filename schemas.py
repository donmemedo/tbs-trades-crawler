from datetime import date, datetime
from typing import List, Any, Optional

from fastapi import Query
from pydantic import BaseModel


class TradesIn(BaseModel):
    trade_date: date = Query(alias="TradeDate")


class CustomersIn(BaseModel):
    register_date: Optional[date] = Query(alias="RegisterDate", default=None)
    modified_date: Optional[date] = Query(alias="ModifiedDate", default=None)


class PortfolioIn(BaseModel):
    cookie: str = Query(alias="Cookie")


class DeleteTradesIn(BaseModel):
    trade_date: date = Query(alias="TradeDate")


class ResponseOut(BaseModel):
    timeGenerated: datetime
    result: List[TradesIn] = List[Any]
    error: str


class CookieIn(BaseModel):
    cookie_value: str
