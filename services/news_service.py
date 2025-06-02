# services/news_service.py
import requests
from datetime import datetime, timedelta
import logging

class NewsService:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://newsapi.org/v2"
    
    def get_stock_news(self, symbol, days_back=7):
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)
        
        params = {
            'q': f"{symbol} stock OR {symbol} earnings OR {symbol} financial",
            'from': start_date.strftime('%Y-%m-%d'),
            'to': end_date.strftime('%Y-%m-%d'),
            'sortBy': 'publishedAt',
            'language': 'en',
            'pageSize': 20,
            'apiKey': self.api_key
        }
        
        try:
            response = requests.get(f"{self.base_url}/everything", params=params)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logging.error(f"News API error: {e}")
            return {'articles': []}