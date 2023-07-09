from pydantic import BaseSettings, dataclasses


class Setting(BaseSettings):
    MONGO_CONNECTION_STRING = "mongodb://root:1qaz1qaz@localhost:27017/"
    MONGO_DATABASE = "brokerage"
    TBS_TRADES_URL = "https://tbs.onlinetavana.ir/ClearingSettlement/ClrsReport/StockTradeSummaryAjaxLoadGrid?_dc=1687751713895&action=read"
    SPLUNK_HOST = "172.24.65.206"
    SPLUNK_PORT = 5142
    DATE_STRING = "%Y-%m-%d"
    SWAGGER_TITLE = "Get Daily Trades"
    ORIGINS = "*"
    VERSION = "0.0.1"
    FASTAPI_DOCS = "/docs"
    FASTAPI_REDOC = "/redoc"
    APP_NAME = "tbs-trade-crawler"


def tbs_trades_header(cookie):
    return {
        "Accept": "*/*",
        "Accept-Language": "en-US,en;q=0.9",
        "Connection": "keep-alive",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Cookie": cookie,
        "Origin": "https://tbs.onlinetavana.ir",
        "Referer": "https://tbs.onlinetavana.ir/ClearingSettlement/ClrsReport/StockTradeSummary?FY=24&_dc=1687751379968",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36",
        "X-Requested-With": "XMLHttpRequest",
    }


def tbs_trades_payload(year, month, day):
    return  f"BranchId=&DateFilter.StartDate={month}%2F{day}" \
              f"%2F{year}&DateFilter.EndDate={month}" \
              f"%2F{day}%2F{year}" \
              f"&TradeState=All&TradeSide=Both&CustomerType=All&Bourse=All" \
              f"&MaxWage=%D9%87%D8%B1%D8%AF%D9%88&MinWage=%D9%87%D8%B1%D8%AF%D9%88" \
              f"&MarketInstrumentType=All&StockTradeSummaryReportType=Simple&" \
              f"CounterPartyType=NoneOfThem&page=1&start=0&limit=2147483647&FY=24"


setting = Setting()
