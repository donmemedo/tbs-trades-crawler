from pydantic import BaseModel, validator
from datetime import date, datetime
from config import setting
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
