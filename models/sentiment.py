# models/sentiment.py
from transformers import pipeline
import logging

class SentimentAnalyzer:
    def __init__(self):
        try:
            # This will download the model on first run
            self.analyzer = pipeline(
                "sentiment-analysis",
                model="cardiffnlp/twitter-roberta-base-sentiment-latest"
            )
        except Exception as e:
            logging.error(f"Error loading sentiment model: {e}")
            # Fallback to basic model
            self.analyzer = pipeline("sentiment-analysis")
    
    def analyze_text(self, text):
        try:
            result = self.analyzer(text[:512])  # Limit text length
            return {
                'label': result[0]['label'],
                'confidence': round(result[0]['score'], 3)
            }
        except Exception as e:
            logging.error(f"Sentiment analysis error: {e}")
            return {'label': 'NEUTRAL', 'confidence': 0.5}