from flask import Flask, jsonify, render_template
from datetime import datetime
import logging
from config import Config

# Create Flask app
app = Flask(__name__)
app.config.from_object(Config)

# Import after app creation to avoid circular imports
from models.sentiment import SentimentAnalyzer
from services.news_service import NewsService

# Initialize services
sentiment_analyzer = SentimentAnalyzer()
news_service = NewsService(app.config['NEWS_API_KEY'])

def analyze_stock_sentiment_enhanced(symbol, news_data, sentiment_analyzer):
    """
    Enhanced sentiment analysis that considers financial context and patterns
    """
    analyzed_articles = []
    sentiment_scores = []
    
    # Financial keywords that indicate positive/negative sentiment
    positive_indicators = [
        'rises', 'gains', 'up', 'surge', 'rally', 'outperform', 'beats', 
        'strong', 'growth', 'profit', 'revenue increase', 'bullish',
        'buys', 'buying', 'investment', 'upgrade', 'target price raised',
        'earnings beat', 'exceeds expectations', 'record high', 'breakout'
    ]
    
    negative_indicators = [
        'falls', 'drops', 'down', 'decline', 'crash', 'plunge', 'underperform',
        'misses', 'weak', 'loss', 'revenue decline', 'bearish',
        'sells', 'selling', 'trimmed', 'reduced', 'downgrade', 'target price cut',
        'earnings miss', 'below expectations', 'concerns', 'challenges'
    ]
    
    for article in news_data['articles'][:30]:  # Increased to 30 articles
        title = article.get('title', '').lower()
        description = article.get('description', '').lower()
        
        # Combine title and description
        full_text = f"{article.get('title', '')}. {article.get('description', '')}"
        text_to_analyze = full_text[:500]
        
        # Get AI sentiment
        ai_sentiment = sentiment_analyzer.analyze_text(text_to_analyze)
        
        # Check for financial context indicators
        combined_text = f"{title} {description}"
        
        positive_count = sum(1 for word in positive_indicators if word in combined_text)
        negative_count = sum(1 for word in negative_indicators if word in combined_text)
        
        # Adjust sentiment based on financial context
        final_sentiment = ai_sentiment.copy()
        
        # If we detect clear financial signals, adjust the sentiment
        if positive_count > negative_count and positive_count >= 2:
            if ai_sentiment['label'] == 'NEUTRAL':
                final_sentiment = {'label': 'POSITIVE', 'confidence': 0.75}
            elif ai_sentiment['label'] == 'POSITIVE':
                # Boost confidence if AI agrees with financial indicators
                final_sentiment['confidence'] = min(0.95, ai_sentiment['confidence'] + 0.2)
                
        elif negative_count > positive_count and negative_count >= 2:
            if ai_sentiment['label'] == 'NEUTRAL':
                final_sentiment = {'label': 'NEGATIVE', 'confidence': 0.75}
            elif ai_sentiment['label'] == 'NEGATIVE':
                # Boost confidence if AI agrees with financial indicators
                final_sentiment['confidence'] = min(0.95, ai_sentiment['confidence'] + 0.2)
        
        # Special case: selling/trimming positions is generally negative for that stock
        selling_terms = ['trimmed', 'sells', 'selling', 'reduced', 'dumped', 'unloaded']
        if any(word in combined_text for word in selling_terms) and symbol.lower() in combined_text:
            if ai_sentiment['label'] in ['NEUTRAL', 'POSITIVE']:
                final_sentiment = {'label': 'NEGATIVE', 'confidence': 0.70}
        
        analyzed_articles.append({
            'title': article.get('title'),
            'url': article.get('url'),
            'published_at': article.get('publishedAt'),
            'source': article.get('source', {}).get('name'),
            'sentiment': final_sentiment,
            'debug_info': {
                'ai_original': ai_sentiment,
                'positive_signals': positive_count,
                'negative_signals': negative_count
            }
        })
        
        # Convert to numeric score for overall calculation
        if final_sentiment['label'] == 'POSITIVE':
            sentiment_scores.append(final_sentiment['confidence'])
        elif final_sentiment['label'] == 'NEGATIVE':
            sentiment_scores.append(-final_sentiment['confidence'])
        else:
            sentiment_scores.append(0)
    
    # Calculate overall sentiment with better thresholds
    if sentiment_scores:
        overall_score = sum(sentiment_scores) / len(sentiment_scores)
        if overall_score > 0.15:  # Slightly higher threshold for positive
            overall_sentiment = 'POSITIVE'
        elif overall_score < -0.15:  # Slightly higher threshold for negative
            overall_sentiment = 'NEGATIVE'
        else:
            overall_sentiment = 'NEUTRAL'
    else:
        overall_sentiment = 'NEUTRAL'
        overall_score = 0
    
    return {
        'symbol': symbol.upper(),
        'overall_sentiment': overall_sentiment,
        'overall_score': round(overall_score, 3),
        'total_articles': len(analyzed_articles),
        'articles': analyzed_articles,
        'methodology': 'Enhanced financial sentiment analysis with 30 articles'
    }

@app.route('/')
def dashboard():
    return render_template('dashboard.html')

@app.route('/api/sentiment/<symbol>')
def analyze_stock_sentiment(symbol):
    try:
        # Get news articles
        news_data = news_service.get_stock_news(symbol.upper())
        
        if not news_data.get('articles'):
            return jsonify({
                'error': 'No news found for this symbol',
                'symbol': symbol.upper()
            }), 404
        
        # Use enhanced sentiment analysis
        result = analyze_stock_sentiment_enhanced(symbol, news_data, sentiment_analyzer)
        result['timestamp'] = datetime.now().isoformat()
        
        return jsonify(result)
        
    except Exception as e:
        logging.error(f"Error analyzing sentiment for {symbol}: {e}")
        return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    # Production configuration
    app.run(
        host='0.0.0.0',      # Bind to all network interfaces
        port=5001,           # Internal port for Apache proxy
        debug=False,         # Disable debug mode in production
        threaded=True        # Enable threading for better performance
    )