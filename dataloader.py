import yfinance as yf
import requests
import apimoex
import collections
import yfinance.shared as shared

import datetime


def form_dict_of_stocks() -> dict:
    """
    This function forms a dictionary of stocks
    by parsing data from the ISS MOEX API.
    """
    request_urls = [
        "https://iss.moex.com/iss/statistics/engines/stock/markets/index/analytics/IMOEX/tickers.json",
        "https://iss.moex.com/iss/statistics/engines/stock/markets/index/analytics/IMOEX2/tickers.json",
        "https://iss.moex.com/iss/statistics/engines/stock/markets/index/analytics/RTSI/tickers.json",
    ]

    dict_stocks = collections.OrderedDict()
    with requests.Session() as session:
        for request_url in request_urls:
            iss = apimoex.ISSClient(session, request_url)
            data = iss.get()

            for ticker in data['tickers']:
                if ticker['ticker'] not in dict_stocks:
                    mas = [ticker['from'], ticker['till']]
                    dict_stocks[ticker['ticker']] = mas

    return dict_stocks


def download_stock(name: str, from_date: datetime.date, to_date: datetime.date) -> list:
    """
    This function downloads stock data from Yahoo Finance.
    """
    flag = True
    data = yf.download(name + '.ME', from_date, to_date)
    if len(list(shared._ERRORS.keys())) != 0:
        flag = False

    mas = [data.columns.tolist()] + data.reset_index().values.tolist()
    for i in range(1, len(mas)):
        mas[i][0] = mas[i][0].to_pydatetime().date()
        mas[i][0] = mas[i][0].isoformat()
    mas.append(flag)

    return mas




