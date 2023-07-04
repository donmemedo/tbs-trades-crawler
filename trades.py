import requests
from pymongo import MongoClient
from config import setting
import json
import datetime
from config import headers
from datetime import date, timedelta, datetime
from logger import logger
from fastapi import FastAPI, Depends, status
from schemas import TradesIn, ResponseOut
import messages
import uvicorn
from fastapi.middleware.cors import CORSMiddleware


def get_database():
    connection_string = setting.MONGO_CONNECTION_STRING
    client = MongoClient(connection_string)
    database = client[setting.MONGO_DATABASE]
    return database

app = FastAPI(
    version=setting.VERSION,
    title=setting.SWAGGER_TITLE,
    docs_url=setting.FASTAPI_DOCS,
    redoc_url=setting.FASTAPI_REDOC
)

origins = [setting.ORIGINS]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



@app.get("/get-trades")
def trades(
    args: TradesIn = Depends(TradesIn),
    db: MongoClient = Depends(get_database)
    ):

    dates = [ args.start_date + timedelta(n) for n in range(int ((args.end_date - args.start_date).days))]

    for trade_date in dates:
        payload = f"BranchId=&DateFilter.StartDate={trade_date.month}%2F{trade_date.day}%2F{trade_date.year}&DateFilter.EndDate={trade_date.month}%2F{trade_date.day}%2F{trade_date.year}&TradeState=All&TradeSide=Both&CustomerType=All&Bourse=All&MaxWage=%D9%87%D8%B1%D8%AF%D9%88&MinWage=%D9%87%D8%B1%D8%AF%D9%88&MarketInstrumentType=All&StockTradeSummaryReportType=Simple&CounterPartyType=NoneOfThem&page=1&start=0&limit=2147483647&FY=24"

        try:
            response = requests.post(
                setting.TBS_TRADES_URL, 
                headers=headers, 
                data=payload
                )

            response.raise_for_status()
        except:
            return ResponseOut(response=messages.CONNECTION_FAILED,
                               result=[],
                               timeGenerated=datetime.now())

        response = json.loads(response.content)
        logger.info(f"On {trade_date}, number of records are: {response.get('total')}")

        if response.get("total", 0) != 0:
            trades = response.get("data")
            for trade in trades:
                # total commission
                trade["TotalCommission"] = trade.pop("TradeItemTotalCommission")

                # set trade type 
                if trade["TradeSideTitle"] == "فروش":
                    trade["TradeType"] = 2
                else:
                    trade["TradeType"] = 1

                # set ISIN
                trade["MarketInstrumentISIN"] = trade.pop("ISIN")

                # set symbol
                trade["TradeSymbol"] = trade.pop("Symbol")

            try:
                db.trades.insert_many(trades)
                logger.info(f"Successfully get trade records of  {trade_date}")
            except:
                return ResponseOut(response='',
                                   result=[],
                                   timeGenerated=datetime.now())


        else:
            logger.info("No trade record found. List is empty.")

            return ResponseOut(response=messages.NO_TRADES_ERROR, 
                               result=[], 
                               timeGenerated=datetime.now())


if __name__ == "__main__":
    uvicorn.run(host="0.0.0.0", port=8000, reload=True)