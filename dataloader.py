import yfinance as yf
import requests
import apimoex
import collections
import yfinance.shared as shared

import datetime


def from_stocks_dt() -> dict:
    """
    Формирует словарь акций,
    анализируя данные с ISS MOEX API.
    """
    api_endpoints = [
        "https://iss.moex.com/iss/statistics/engines/stock/markets/index/analytics/IMOEX/tickers.json",
        "https://iss.moex.com/iss/statistics/engines/stock/markets/index/analytics/IMOEX2/tickers.json",
        "https://iss.moex.com/iss/statistics/engines/stock/markets/index/analytics/RTSI/tickers.json",
    ]

    stock_dict = collections.OrderedDict()
    with requests.Session() as session:
        for endpoint in api_endpoints:
            iss_client = apimoex.ISSClient(session, endpoint)
            data = iss_client.get()

            for ticker_data in data['tickers']:
                ticker = ticker_data['ticker']
                if ticker not in stock_dict:
                    stock_dict[ticker] = [ticker_data['from'], ticker_data['till']]

    return stock_dict


def dwn_stock(name: str, from_date: datetime.date, to_date: datetime.date) -> list:
    """
    Загружает данные об акциях с Yahoo Finance.
    """
    ticker = name + ".ME"
    data = yf.download(ticker, from_date, to_date)

    # Проверяем наличие ошибок Yahoo Finance
    is_success = len(list(shared._ERRORS.keys())) == 0

    # Формируем список данных
    stock_data = [data.columns.tolist()] + data.reset_index().values.tolist()

    # Преобразуем дату в строковый формат ISO
    for row in stock_data[1:]:
        row[0] = row[0].to_pydatetime().date().isoformat()

    # Добавляем флаг успешности загрузки
    stock_data.append(is_success)

    return stock_data