from pydantic import BaseConfig, dataclasses


class Setting(BaseConfig):
    MONGO_CONNECTION_STRING= "mongodb://root:1qaz1qaz@localhost:27017/"
    MONGO_DATABASE = "brokerage"
    TBS_TRADES_URL = "https://tbs.onlinetavana.ir/ClearingSettlement/ClrsReport/StockTradeSummaryAjaxLoadGrid?_dc=1687751713895&action=read"
    SPLUNK_HOST = "172.24.65.206"
    SPLUNK_PORT = 5142
    DATE_STRING = "%Y-%m-%d"
    TITLE = "Get Daily Trades"
    ORIGINS = "*"


headers = {
    'Accept': '*/*',
    'Accept-Language': 'en-US,en;q=0.9',
    'Connection': 'keep-alive',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'Cookie': 'f5avraaaaaaaaaaaaaaaa_session_=ELKNOHCHBKHKIOBDPDPCFDDLFLIKAPEODCCEIIEPLDIPJKCJPPJABOPPEAOCPDKDJDGDBAGCJGPCHLIEIPFALEPPNMENIGMBFJAFFLHNLJDEOAMDCBDGNGAFEAKGGMIO; LocalizerCulture=fa-ir; ASP.NET_SessionId=pv0avry30hlxzemy5slclztp; TBSToken=816BA0565FED9AE389E23702718F6E3CA83556975865FFEA66CEB30302DDEACAC0AACDD43467BDE0BC12EFC03FFC982F9AB5450CE5576B99D9BC2A107D1463C81848C4973585A75921ED969C16484AD25E35FB817B64CDA8B1F77FFAD63CA42F4AE5C6FFAAB5FE75E109DECD486697C74928C3F2AA43EDEF8AB935228ACBC4C49DFBAE76BD67C369A9AE851A2F79B31DF92ECFF5C40C0C00D6BDA8027651D4930DA0C3C56078E6D8B330CF79B4860B53; TS0197c0e4=0180bb6f22eb95d257fd96176bbc7a3af764c6dbba5952cc9af95ae1602e91af770855690b9288fa7e09a6c5f00bdcf332e20d827e85df231d531cd1369d528a076f1ecf977cf88064f2142649bd664faaf73f7ca281c02410424a765af66291897fb90982a1674e5b69edb0e6d4ca2e0f278780ea',
    'Origin': 'https://tbs.onlinetavana.ir',
    'Referer': 'https://tbs.onlinetavana.ir/ClearingSettlement/ClrsReport/StockTradeSummary?FY=24&_dc=1687751379968',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36',
    'X-Requested-With': 'XMLHttpRequest'
    }


setting = Setting()