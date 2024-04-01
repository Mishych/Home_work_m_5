import platform
import aiohttp
import asyncio
import json
from datetime import datetime, timedelta
import sys


class APIRequester:
    @staticmethod
    
    async def request(session, url):
        async with session.get(url) as response:
            try:
                if response.status == 200:
                    result = await response.json()
                else:
                    raise ValueError(f"Error status: {response.status} for {url}")
                
            except aiohttp.ClientConnectorError as err:
                raise ConnectionError(f'Connection error: {url}')
                
            return result
 
 
class DataTransformer:
    @staticmethod
    
    def transform_json(data, currencys):
        result = {}
        for item in data['exchangeRate']:
            date = data['date']
            
            if item['currency'] in currencys:
                currency = item['currency']
                sale = item.get('saleRate', item['saleRateNB'])
                purchase = item.get('purchaseRate', item['purchaseRateNB'])
                
                entry = {
                    'sale': sale,
                    'purchase': purchase
                    }       
                
                if date not in result:
                    result[date] = {}
                result[date][currency] = entry
        
        return result


class Count_of_dates:
    @staticmethod
        
    def count_dates(days):
        dates = []
        curently_date = datetime.now()
        
        for i in range(int(days)):
            date = curently_date - timedelta(days=i)
            dates.append(date.strftime("%d.%m.%Y"))  
        return dates


class URLGenerator_with_date:
    @staticmethod
        
    def urls_with_date(url, dates):
        urls = []
        for day in dates:
            url_with_date = url + day
            urls.append(url_with_date)
        return urls

async def main():
    days = sys.argv[1]

    if len(sys.argv) != 2:
        print("Потрібно ввести лише один аргумент - кількість днів.")
        sys.exit(1)

    try:
        days = int(sys.argv[1])
        
    except ValueError:
        print("Помилка: введено нечислове значення.")
        sys.exit(1)

    if days < 1 or days > 10:
        print("Кількість днів має бути від 1 до 10.")
        sys.exit(1)
        
    url = 'https://api.privatbank.ua/p24api/exchange_rates?date='
    
    dates = Count_of_dates.count_dates(days)
    
    urls = URLGenerator_with_date.urls_with_date(url, dates)
    
    transform_result = []
        
    async with aiohttp.ClientSession() as session:
        js = await asyncio.gather(*{APIRequester.request(session, url) for url in urls})
        currencys = ['USD', 'EUR']    
        for data in js:
            transform_result.append(DataTransformer.transform_json(data, currencys))
        
        result = sorted(transform_result, key=lambda x: list(x.keys())[0], reverse=True)
   
        with open('storage/data.json', 'w') as f:
            json.dump(result, f, indent=2)

        return result


if __name__ == "__main__":
    if platform.system() == 'Windows':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        
    r = asyncio.run(main())
    print(r)
