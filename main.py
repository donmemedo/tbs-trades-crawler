import datetime
import json
import secrets
from datetime import datetime
from logging.config import dictConfig
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from typing import Annotated
from  statics import statics
import requests
import uvicorn
from fastapi import Depends, FastAPI, status, HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pymongo import MongoClient
from pymongo.errors import BulkWriteError, DuplicateKeyError
import messages
from config import *
from database import get_database
from logger import log_config, logger
from schemas import *
from khayyam import JalaliDatetime

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


class Cookie:
    def __init__(self, cookie_value=None):
        self.cookie = cookie_value


cookie = Cookie()


@app.post("/cookie", tags=["Cookie"])
async def set_cookie(args: CookieIn = Depends(CookieIn)):
    cookie.cookie = args.cookie_value

    return cookie.cookie


@app.get("/cookie", tags=["Cookie"])
async def get_cookie():
    return cookie.cookie


@app.get("/BAK/trades", tags=["BAK"])
async def get_trades(
    args: TradesIn = Depends(TradesIn),
    db: MongoClient = Depends(get_database),
    user: str = Depends(get_current_username),
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


@app.get("/BAK/get-private-portfolios", tags=["BAK"], response_model=None)
async def get_private_portfolios(
    args: PortfolioIn = Depends(PortfolioIn),
    db: MongoClient = Depends(get_database),
    user: str = Depends(get_current_username),
):
    try:
        response = requests.get(
            setting.TBS_PORTFOLIOS_URL,
            params=tbs_portfolio_params(),
            headers=tbs_portfolio_header(args.cookie),
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
    logger.info(f"Number of records are: {response.get('total')}")

    if response.get("total", 0) != 0:
        records = response.get("data")
        results = []
        for record in records:
            try:
                db.portfolio.insert_one(record)
                logger.info(
                    f"Successfully get Private Portfolios in {datetime.now().isoformat()} "
                )
            except DuplicateKeyError as e:
                if e.details.get("code") == 11000:
                    logger.error(f"Duplicate Key Error for {record.get('Title')}")
                    db.portfolio.delete_one({"TradeCodes": record.get("TradeCodes")})
                    db.portfolio.insert_one(record)
                    record.pop("_id")
                    results.append(record)

                    logger.info(f"Record {record.get('Title')} was Updated")
                else:
                    logger.error("Bulk Write Error")
                    logger.exception("Bulk Write Error")
                    return JSONResponse(
                        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                        content=jsonable_encoder(
                            ResponseOut(
                                error=messages.BULK_WRITE_ERROR,
                                result=[],
                                timeGenerated=datetime.now(),
                            )
                        ),
                    )
        result = {}
        if results:
            result["pagedData"] = results
            result["errorCode"] = None
            result["errorMessage"] = None
            result["AllEditedPrivatePortfolioCount"] = len(results)
            result["AllNewPrivatePortfolioCount"] = len(records) - len(results)
            result["Date"] = JalaliDatetime.now().date()
            resp = {
                "result": result,
                "GeneratedDateTime": datetime.now(),
                "error": {
                    "message": "Null",
                    "code": "Null",
                },
            }

            return JSONResponse(
                status_code=status.HTTP_202_ACCEPTED, content=jsonable_encoder(resp)
            )
        else:
            result["errorCode"] = None
            result["errorMessage"] = messages.SUCCESSFULLY_WRITE_DATA
            result["AllPrivatePortfolioCount"] = len(records)
            result["Date"] = JalaliDatetime.now().date()
            resp = {
                "result": result,
                "GeneratedDateTime": datetime.now(),
                "error": {
                    "message": messages.SUCCESSFULLY_WRITE_DATA,
                    "code": "Null",
                },
            }

            return JSONResponse(
                status_code=status.HTTP_201_CREATED, content=jsonable_encoder(resp)
            )
    else:
        logger.info("No records found. List is empty.")
        return ResponseOut(
            error=messages.NO_RECORDS_ERROR, result=[], timeGenerated=datetime.now()
        )


@app.delete("/trades", tags=["Trades"])
def delete_trades(
    args: DeleteTradesIn = Depends(DeleteTradesIn),
    db: MongoClient = Depends(get_database),
    user: str = Depends(get_current_username),
):
    try:
        db.trades.delete_many(
            {"TradeDate": {"$regex": args.trade_date.strftime(setting.DATE_STRING)}}
        )
        logger.info(f"All trades has been deleted for {args.trade_date}")
        return ResponseOut(
            error="داده‌ها با موفقیت از سیستم حذف شد",
            result=[],
            timeGenerated=datetime.now(),
        )
    except Exception:
        logger.error("Error while delete data in database")
        logger.exception("Error while delete data in database")
        return jsonable_encoder(
            JSONResponse(
                status_code=500,
                content=ResponseOut(
                    error=messages.HTTP_500_ERROR,
                    result=[],
                    timeGenerated=datetime.now(),
                ),
            )
        )


@app.get("/trades", tags=["Trades"])
async def get_trades(
    args: TradesIn = Depends(TradesIn),
    db: MongoClient = Depends(get_database),
    user: str = Depends(get_current_username),
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
        duplicates = 0
        buys = 0
        sells = 0
        inserted = []
        try:
            for trade in trade_records:
                # total commission
                trade["TotalCommission"] = trade["TradeItemTotalCommission"]

                # set trade type
                if trade["TradeSideTitle"] == "فروش":
                    trade["TradeType"] = 2
                    sells += 1
                else:
                    trade["TradeType"] = 1
                    buys += 1

                # set ISIN
                trade["MarketInstrumentISIN"] = trade["ISIN"]

                # set symbol
                trade["TradeSymbol"] = trade["Symbol"]
                try:
                    db.tradesbackup.insert_one(trade)
                    inserted.append(trade)
                except DuplicateKeyError as dup_error:
                    logger.info("Duplicate record", {"error": dup_error})
                    duplicates += 1
                    if trade["TradeType"] == 2:
                        sells -= 1
                    else:
                        buys -= 1
                logger.info(f"Successfully get trade records of  {args.trade_date}")

            result = {}
            # if results:
            result["InsertedTradeCount"] = len(trade_records) - duplicates
            result["errorCode"] = None
            result["errorMessage"] = None
            result["InsertedBuyTradeCount"] = buys
            result["InsertedSellTradeCount"] = sells
            result["InsertedTradeCodeCount"] = len(
                {v["TradeCode"]: v for v in inserted}
            )
            result["TradeDate"] = JalaliDatetime.now().date().isoformat()
            resp = {
                "result": result,
                "GeneratedDateTime": datetime.now(),
                "error": {
                    "message": "Null",
                    "code": "Null",
                },
            }

            return JSONResponse(
                status_code=status.HTTP_202_ACCEPTED, content=jsonable_encoder(resp)
            )
        except BulkWriteError as e:
            for error in e.details.get("writeErrors"):
                if error.get("code") != 11000:
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


@app.get("/customers", tags=["Customers"], response_model=None)
async def get_customers(
    args: CustomersIn = Depends(CustomersIn),
    db: MongoClient = Depends(get_database),
    user: str = Depends(get_current_username),
):
    if args.register_date:
        register_date = args.register_date.strftime(statics.DATE_FORMAT)
    else:
        register_date = None

    if args.modified_date:
        modified_date = args.modified_date.strftime(statics.DATE_FORMAT)
    else:
        modified_date = None

    try:
        response = requests.get(
            setting.TBS_CUSTOMERS_URL,
            params=tbs_customer_filter_params(register_date, modified_date),
            headers=tbs_customer_header(cookie.cookie),
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
    logger.info(f"Number of records are: {response.get('total')}")

    if response.get("total", 0) != 0:
        records = response.get("data")
        results = []
        privates = legals = newp = newl = updp = updl = 0
        for record in records:

            if record["PartyTypeTitle"] == statics.PRIVATE_USER:
                record["CustomerType"] = 1
                privates += 1
            else:
                record["CustomerType"] = 2
                legals += 1
            record["BrokerBranch"] = record["BrokerBranchTitle"]
            record["DetailLedgerCode"] = record["AccountCodes"]
            record["Email"] = record["UserEmail"]
            record["IDNumber"] = record["BirthCertificateNumber"]
            record["NationalCode"] = record["NationalIdentification"]
            record["PAMCode"] = record["TradeCodes"]
            record["BourseCode"] = record["BourseCodes"]
            record["Referer"] = record["RefererTitle"]
            record["Username"] = record["UserName"]
            if not record["Mobile"]:
                record["Mobile"] = record["Phones"]
            try:
                db.customerzs.insert_one(record)
                if record["CustomerType"] == 1:
                    newp += 1
                else:
                    newl += 1
                logger.info(
                    f"Successfully get Customers in {datetime.now().isoformat()} "
                )
            except DuplicateKeyError as e:
                if e.details.get("code") == 11000:
                    logger.error(
                        f"Duplicate Key Error for {record.get('FirstName')} {record.get('LastName')}"
                    )
                    record.pop("_id")
                    if (
                        db.customerzs.find_one(
                            {"PAMCode": record.get("PAMCode")}, {"_id": False}
                        )
                        != record
                    ):
                        db.customerzs.delete_one({"PAMCode": record.get("PAMCode")})
                        db.customerzs.insert_one(record)
                        if record["CustomerType"] == 1:
                            updp += 1
                        else:
                            updl += 1
                        record.pop("_id")
                        results.append(record)
                        logger.info(
                            f"Record {record.get('FirstName')} {record.get('LastName')} was Updated"
                        )
                else:
                    logger.error("Bulk Write Error")
                    logger.exception("Bulk Write Error")
                    return JSONResponse(
                        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                        content=jsonable_encoder(
                            ResponseOut(
                                error=messages.BULK_WRITE_ERROR,
                                result=[],
                                timeGenerated=datetime.now(),
                            )
                        ),
                    )
        result = {}
        if results:
            result["pagedData"] = results
            result["errorCode"] = None
            result["errorMessage"] = None
            result["AllCustomerCount"] = len(records)
            result["AllPrivateCustomerCount"] = privates
            result["AllLegalCustomerCount"] = legals
            result["AllNewPrivateCustomerCount"] = newp
            result["AllNewLegalCustomerCount"] = newl
            result["AllUpdatedPrivateCustomerCount"] = updp
            result["AllUpdatedLegalCustomerCount"] = updl
            result["Date"] = JalaliDatetime.now().date().isoformat()
            resp = {
                "result": result,
                "GeneratedDateTime": datetime.now(),
                "error": {
                    "message": "Null",
                    "code": "Null",
                },
            }

            return JSONResponse(
                status_code=status.HTTP_202_ACCEPTED, content=jsonable_encoder(resp)
            )
        else:
            result["errorCode"] = None
            result["errorMessage"] = messages.SUCCESSFULLY_WRITE_DATA
            result["AllCustomersCount"] = len(records)
            result["AllPrivateCustomerCount"] = privates
            result["AllLegalCustomerCount"] = legals
            result["AllNewPrivateCustomerCount"] = newp
            result["AllNewLegalCustomerCount"] = newl
            result["Date"] = JalaliDatetime.now().date().isoformat()
            resp = {
                "result": result,
                "GeneratedDateTime": datetime.now(),
                "error": {
                    "message": messages.SUCCESSFULLY_WRITE_DATA,
                    "code": "Null",
                },
            }

            return JSONResponse(
                status_code=status.HTTP_201_CREATED, content=jsonable_encoder(resp)
            )
    else:
        logger.info("No records found. List is empty.")
        return ResponseOut(
            error=messages.NO_RECORDS_ERROR, result=[], timeGenerated=datetime.now()
        )


if __name__ == "__main__":
    uvicorn.run(
        app="main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_config=dictConfig(log_config),
    )
