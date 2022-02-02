import requests
import json
import os
from datetime import datetime
import time


class Request:
    # This is the class to connect this code to CoinMarketCap APIs
    def __init__(self):
        self.url = ''
        self.params = {}
        self.headers = {}

    def fetch_currencies_data(self):
        r = requests.get(url=self.url, headers=self.headers, params=self.params).json()
        return r['data']


class Reports(Request):
    # This is the class in which I set the parameters to fetch the data I need from CoinMarketCap
    def __init__(self):
        super(Reports, self).__init__()
        self.url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest'
        self.headers = {
            'Accepts': 'application/json',
            'X-CMC_PRO_API_KEY': '546fa23d-37b7-4976-8156-ab3a28ffc2c7',
        }
        self.reports = self.get_reports()

    def highest_trading_volume_currency(self):
        # This method fetches the cryptocurrency with the higher volume trading of the last 24 hours and returns it
        self.params = {
            'start': 1,
            'limit': 1,
            'sort': 'volume_24h',
            'sort_dir': 'desc',
            'convert': 'USD'
        }

        currencies = self.fetch_currencies_data()
        return currencies[0]

    def ten_best_percentage_increase_currencies(self):
        # This method fetches the best 10 cryptocurrencies based on percentage increase over the last 24 hours
        # and returns them as a list
        self.params = {
            'start': 1,
            'limit': 10,
            'sort': 'percent_change_24h',
            'sort_dir': 'desc',
            'convert': 'USD'
        }

        currencies = self.fetch_currencies_data()
        return currencies

    def ten_worst_percentage_increase_currencies(self):
        # This method fetches the worst 10 cryptocurrencies based on percentage increase over the last 24 hours
        # and returns them as a list
        self.params = {
            'start': 1,
            'limit': 10,
            'sort': 'percent_change_24h',
            'sort_dir': 'asc',
            'convert': 'USD'
        }

        currencies = self.fetch_currencies_data()
        return currencies

    def total_price_20_best_currencies(self):
        # This method fetches the price of 20 best cryptocurrencies based on CoinMarketCap ranking and returns the sum
        total_price = 0
        self.params = {
            'start': 1,
            'limit': 20,
            'sort': 'market_cap',
            'sort_dir': 'desc',
            'convert': 'USD'
        }

        currencies = self.fetch_currencies_data()
        for currency in currencies:
            total_price += currency['quote']['USD']['price']
        return round(total_price, 2)

    def total_price_of_higher_volume_currencies(self):
        # This method fetches the price of cryptocurrencies that have a volume of the last 24 hours of more than 76M$
        # and returns the sum
        total_price = 0
        self.params = {
            'start': 1,
            'volume_24h_min': 76000000,
            'convert': 'USD'
        }

        currencies = self.fetch_currencies_data()
        for currency in currencies:
            total_price += currency['quote']['USD']['price']
        return round(total_price, 2)

    def twenty_best_currencies_percent_change_24h(self):
        # This method fetches the price and the percentage change of the last 24 hours of 20 best cryptocurrencies based
        # on CoinMarketCap ranking and returns the percentage change of the sum of the prices in the last 24 hours
        yesterday_total_price = 0
        today_total_price = 0
        self.params = {
            'start': 1,
            'limit': 20,
            'sort': 'market_cap',
            'sort_dir': 'desc',
            'convert': 'USD'
        }

        currencies = self.fetch_currencies_data()
        for currency in currencies:
            yesterday_price = currency['quote']['USD']['price'] / (1 + (currency['quote']['USD']['percent_change_24h'] / 100))
            yesterday_total_price += yesterday_price
            today_total_price += currency['quote']['USD']['price']
        twenty_best_currencies_percent_change_24h = round((((today_total_price / yesterday_total_price) - 1) * 100), 2)
        return twenty_best_currencies_percent_change_24h

    def get_reports(self):
        # This method returns a dictionary that contains the responses of the calls with the parameters set above
        reports = {
            'highest_traded': self.highest_trading_volume_currency(),
            'top_10_by_increment': self.ten_best_percentage_increase_currencies(),
            'top_10_by_decrement': self.ten_worst_percentage_increase_currencies(),
            'total_price_top_20': self.total_price_20_best_currencies(),
            'total_price_of_higher_volume_currencies': self.total_price_of_higher_volume_currencies(),
            'percent_change_of_twenty_best': self.twenty_best_currencies_percent_change_24h()
        }
        return reports


def make_json_report(report):
    # This function makes a json file (named with the date and hour) that contains the reports
    # and puts it in a new directory named 'report'
    now = str(datetime.now()).replace(' ', '_')[:-7]
    json_name = now + '.json'
    script_dir = os.path.dirname(os.path.abspath(__file__))
    destination_dir = os.path.join(script_dir, 'report')
    path = os.path.join(destination_dir, json_name)

    try:
        os.mkdir(destination_dir)
    except OSError:
        pass
    with open(path, 'w') as f:
        json.dump(report, f, indent=4)


while True:
    # This is an infinite loop that sleeps for 24 hours each cycle, so it returns 1 report per day
    # and print the fundamental information
    report = Reports()

    print(f"Daily report of crypto according to CoinMarketCap of: {datetime.now()}")
    print("")
    print(f"The highest trading volume currency of last 24h is "
          f"{report.reports['highest_traded']['symbol']} "
          f"with a volume of {round(report.reports['highest_traded']['quote']['USD']['volume_24h'], 0)}$")
    print("Top 10 by increment: ")
    for currency in report.reports['top_10_by_increment']:
        print(currency['symbol'], f"{round(currency['quote']['USD']['percent_change_24h'], 2)}%")
    print("")
    print("Top ten by decrement: ")
    for currency in report.reports['top_10_by_decrement']:
        print(currency['symbol'], f"{round(currency['quote']['USD']['percent_change_24h'], 2)}%")
    print("")
    print(f"Total price of 20 best currencies of CoinMarketCap ranking: {report.reports['total_price_top_20']}$")
    print(f"Total price of currencies that have a daily volume higher than 76M$: "
          f"{report.reports['total_price_of_higher_volume_currencies']}$")
    print(f"Percentage change of 20 best currencies of CoinMarketCap ranking: "
          f"{report.reports['percent_change_of_twenty_best']}%")
    print("------------------------------------------------------------")

    make_json_report(report.reports)
    time.sleep(86400)
