import datetime
import json
import secrets
from datetime import datetime
from logging.config import dictConfig
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from typing import Annotated

import requests
import uvicorn
from fastapi import Depends, FastAPI, status, HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pymongo import MongoClient
from pymongo.errors import BulkWriteError

import messages
from config import setting, tbs_trades_header, tbs_trades_payload
from database import get_database
from logger import log_config, logger
from schemas import ResponseOut, TradesIn, DeleteTradesIn


app = FastAPI(
    version=setting.VERSION,
    title=setting.SWAGGER_TITLE,
    docs_url=setting.FASTAPI_DOCS,
    redoc_url=setting.FASTAPI_REDOC,
)

security = HTTPBasic()

origins = [setting.ORIGINS]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_current_username(
    credentials: Annotated[HTTPBasicCredentials, Depends(security)]
):
    current_username_bytes = credentials.username.encode("utf8")
    correct_username_bytes = b"nastaran"
    is_correct_username = secrets.compare_digest(
        current_username_bytes, correct_username_bytes
    )
    current_password_bytes = credentials.password.encode("utf8")
    correct_password_bytes = b"n@st@r@n"
    is_correct_password = secrets.compare_digest(
        current_password_bytes, correct_password_bytes
    )
    if not (is_correct_username and is_correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username


@app.get("/get-trade_records", tags=["Trades"])
async def trades(
        args: TradesIn = Depends(TradesIn),
        db: MongoClient = Depends(get_database),
        user: str = Depends(get_current_username)
):
    try:
        response = requests.post(
            setting.TBS_TRADES_URL,
            headers=tbs_trades_header(args.cookie),
            data=tbs_trades_payload(
                args.trade_date.year, args.trade_date.month, args.trade_date.day
            ),
        )

        response.raise_for_status()

        if "<html>".encode() in response.content:
            raise Exception()

    except Exception as e:
        return JSONResponse(
            status_code=599,
            content=jsonable_encoder(
                ResponseOut(
                    error=messages.CONNECTION_FAILED,
                    result=[],
                    timeGenerated=datetime.now(),
                )
            ),
        )

    response = json.loads(response.content)
    logger.info(f"On {args.trade_date}, number of records are: {response.get('total')}")

    if response.get("total", 0) != 0:
        trade_records = response.get("data")

        for trade in trade_records:
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
            db.trades.insert_many(trade_records)
            logger.info(f"Successfully get trade records of  {args.trade_date}")

            return JSONResponse(
                status_code=status.HTTP_201_CREATED,
                content=jsonable_encoder(
                    ResponseOut(
                        error=messages.SUCCESSFULLY_WRITE_DATA,
                        result=[],
                        timeGenerated=datetime.now(),
                    )
                ),
            )

        except BulkWriteError as e:
            for error in e.details.get("writeErrors"):
                if error.get("code") == 11000:
                    logger.error("Duplicate Key Error")
                    logger.exception("Duplicate Key Error")
                    return JSONResponse(
                        status_code=status.HTTP_409_CONFLICT,
                        content=jsonable_encoder(
                            ResponseOut(
                                error=messages.DUPLICATE_KEY_ERROR,
                                result=[],
                                timeGenerated=datetime.now(),
                            )
                        ),
                    )
                else:
                    logger.error("Bulk Write Error")
                    logger.exception("Bulk Write Error")
                    return JSONResponse(
                        status_code=status.HTTP_418_IM_A_TEAPOT,
                        content=jsonable_encoder(
                            ResponseOut(
                                error=messages.BULK_WRITE_ERROR,
                                result=[],
                                timeGenerated=datetime.now(),
                            )
                        ),
                    )
    else:
        logger.info("No trade record found. List is empty.")
        return ResponseOut(
            error=messages.NO_TRADES_ERROR, result=[], timeGenerated=datetime.now()
        )


@app.delete("/trades")
def delete_trades(
    args: DeleteTradesIn = Depends(DeleteTradesIn),
    db: MongoClient = Depends(get_database),
    user: str = Depends(get_current_username)
):
    try:
        db.trades.delete_many(
            {
                "TradeDate": {
                    "$regex": args.trade_date.strftime(setting.DATE_STRING)
                }
            }
        )
        logger.info(f"All trades has been deleted for {args.trade_date}")
        return ResponseOut(error="داده‌ها با موفقیت از سیستم حذف شد",
                           result=[],
                           timeGenerated=datetime.now()
                           )
    except Exception:
        logger.error("Error while delete data in database")
        logger.exception("Error while delete data in database")
        return jsonable_encoder(JSONResponse(
            status_code=500,
            content=ResponseOut(
                error=messages.HTTP_500_ERROR,
                result=[],
                timeGenerated=datetime.now()
            )
        )
    )


if __name__ == "__main__":
    uvicorn.run(
        app="main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_config=dictConfig(log_config),
    )
