from pydantic import BaseSettings


class Setting(BaseSettings):
    MONGO_CONNECTION_STRING = "mongodb://root:1qaz1qaz@localhost:27017/"
    MONGO_DATABASE = "brokerage"
    TBS_TRADES_URL = "https://tbs.onlinetavana.ir/ClearingSettlement/ClrsReport/StockTradeSummaryAjaxLoadGrid?_dc=1687751713895&action=read"
    TBS_PORTFOLIOS_URL = "https://tbs.onlinetavana.ir/CustomerManagement/Customer/AjaxReadPortfolio"
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


def tbs_portfolio_header(cookie):
    return {
    'Accept': '*/*',
    # 'Accept-Encoding': 'gzip, deflate, br',
    'X-Requested-With': 'XMLHttpRequest',
    'Connection': 'keep-alive',
    'Referer': 'https://tbs.onlinetavana.ir/CustomerManagement/Customer/PortfolioIndex?FY=24&_dc=1691393987026',
    'Cookie': cookie,#'f5avraaaaaaaaaaaaaaaa_session_=IGNKEKBENOCPMGPGIJDDOCHMBJANGCAFLDOCFPKGLMIOFPOCNCIELOJLNLCGKLKPNJKDADIMHNKGMBCJBHPAPKBFOJLGLEEFACOCHDNGPLJKBFMCFEBDJBKJNDOJIGBC; f5avraaaaaaaaaaaaaaaa_session_=GKCDCDODOBBCECFLMBCMPNGOPOEBIMDDEBCEIBBEEJFACPPNHAPMICNFJOFABFPBPNIDGKGGPOPGKBNDIKOAFIKDJJACKPOHBKFKOFLHJILBOOPJEIKDGCFNOHPFJDOG; TS0197c0e4=0180bb6f22f18d77a1c83d14d43eb533e41e89692f1fc591f57cbfcb8b7fb44c9a9ffd5bdcec493ad290b5739695f1dadf6ef5d797718f75cccde69fdf9bdad9b7e25819a47c9cef1522705e7290dda8e7fa58047fc888201aaaf391ca9cb0d3141aa05ec9d145e8a1b390732b948b7e19c73d8c8f; LocalizerCulture=fa-ir; ASP.NET_SessionId=krfkijeclbrgpbvilzxmb20k; TBSToken=680D9A25AAB6D32FA08AE586EDD30336BCAF273E186C3E08816A05FD76B012AB4B237E8BF98A29C432AE413FC09836ADBD5C4EADD4A01A7A76C8F7BE5693377D70E3E43BC0384991AD181519B946ECFC9C4A07C0AD81161BA2995A9F82ADF7B9D21116A35DDDCBEA3F6969E10B7D8FFBDEC3A28F7461E23B04FD734E1E1D956B309D789FE05382E5B8284FCD27FF9512AAA0AADFDBFC9E8A2C0D336558A11C7A3B9E9EBC55323A680910A660A069DAEA',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
    }

def tbs_portfolio_params():
    return {
    '_dc': '1691399042865',
    'action': 'read',
    'Filter.TradeSystem': 'TSETradingSystem',
    'filterheader': '{}',
    'page': '1',
    'start': '0',
    'limit': '500',
    'FY': '24',
    }


setting = Setting()
