# /var/www/stock-sent/stock_sentiment_dashboard/models/sentiment.py

from transformers import pipeline
import logging
import re

class SentimentAnalyzer:
    def __init__(self):
        try:
            # Load FinBERT - specifically trained for financial sentiment
            self.pipeline = pipeline(
                "sentiment-analysis",
                model="ProsusAI/finbert",
                device=-1  # Use CPU
            )
            self.model_type = "finbert"
            print("✅ Loaded FinBERT model for financial sentiment analysis")
        except Exception as e:
            logging.error(f"Error loading FinBERT model: {e}")
            try:
                # Fallback to RoBERTa if FinBERT fails
                self.pipeline = pipeline(
                    "sentiment-analysis",
                    model="cardiffnlp/twitter-roberta-base-sentiment-latest"
                )
                self.model_type = "roberta"
                print("⚠️ Loaded RoBERTa model as fallback")
            except Exception as e2:
                logging.error(f"Error loading fallback model: {e2}")
                # Final fallback
                self.pipeline = pipeline("sentiment-analysis")
                self.model_type = "basic"
                print("⚠️ Loaded basic sentiment model as final fallback")
    
    def analyze_text(self, text):
        """
        Enhanced FinBERT analysis with financial context boosting
        """
        try:
            if not text or len(text.strip()) == 0:
                return {'label': 'NEUTRAL', 'confidence': 0.5}
            
            # Clean and limit text length
            text = text.strip()[:512]
            text_lower = text.lower()
            
            # Get sentiment from FinBERT
            result = self.pipeline(text)[0]
            
            if self.model_type == "finbert":
                # FinBERT returns: positive, negative, neutral
                label_map = {
                    'positive': 'POSITIVE',
                    'negative': 'NEGATIVE', 
                    'neutral': 'NEUTRAL'
                }
                ai_label = label_map.get(result['label'].lower(), 'NEUTRAL')
                ai_confidence = result['score']
                
            elif self.model_type == "roberta":
                # RoBERTa returns: LABEL_0 (negative), LABEL_1 (neutral), LABEL_2 (positive)
                if result['label'] == 'LABEL_0':
                    ai_label = 'NEGATIVE'
                elif result['label'] == 'LABEL_2':
                    ai_label = 'POSITIVE'
                else:
                    ai_label = 'NEUTRAL'
                ai_confidence = result['score']
                
            else:
                # Basic model
                ai_label = result['label'].upper()
                ai_confidence = result['score']
            
            # Financial context enhancement for edge cases
            final_label = ai_label
            final_confidence = ai_confidence
            
            # Strong selling indicators that should override neutral
            selling_patterns = [
                r'trimmed.*position', r'reduced.*stake', r'sold.*shares',
                r'cutting.*position', r'exiting.*position', r'dumping.*stock',
                r'sells.*million', r'unloads.*shares'
            ]
            
            # Check if this is about selling a specific stock
            contains_selling = any(re.search(pattern, text_lower) for pattern in selling_patterns)
            
            # If FinBERT says neutral but we detect selling activity, upgrade to negative
            if ai_label == 'NEUTRAL' and contains_selling and ai_confidence < 0.8:
                # Look for stock symbols or company names being sold
                stock_indicators = ['tesla', 'tsla', 'apple', 'aapl', 'nvidia', 'nvda', 'stock', 'shares']
                if any(indicator in text_lower for indicator in stock_indicators):
                    final_label = 'NEGATIVE'
                    final_confidence = 0.75
                    print(f"DEBUG: Upgraded NEUTRAL to NEGATIVE - detected selling activity: {text[:100]}...")
            
            # Strong positive patterns that might be missed
            strong_positive_patterns = [
                r'surge[sd]?\s+\d+%', r'rally\s+\d+%', r'soar[sd]?\s+\d+%',
                r'beat[s]?\s+estimate', r'exceed[s]?\s+expectation', r'record\s+profit'
            ]
            
            contains_strong_positive = any(re.search(pattern, text_lower) for pattern in strong_positive_patterns)
            if ai_label == 'NEUTRAL' and contains_strong_positive and ai_confidence < 0.8:
                final_label = 'POSITIVE'
                final_confidence = 0.75
                print(f"DEBUG: Upgraded NEUTRAL to POSITIVE - strong positive signals: {text[:100]}...")
            
            return {
                'label': final_label,
                'confidence': round(final_confidence, 3)
            }
            
        except Exception as e:
            logging.error(f"Error in sentiment analysis: {e}")
            return {'label': 'NEUTRAL', 'confidence': 0.5}