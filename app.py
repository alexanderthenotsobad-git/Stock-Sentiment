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
        
        # Analyze sentiment for each article
        analyzed_articles = []
        sentiment_scores = []
        
        for article in news_data['articles'][:15]:  # Limit to 15 articles
            title = article.get('title', '')
            description = article.get('description', '')
            
            # Analyze title and description
            text_to_analyze = f"{title}. {description}"[:500]
            sentiment = sentiment_analyzer.analyze_text(text_to_analyze)
            
            analyzed_articles.append({
                'title': title,
                'url': article.get('url'),
                'published_at': article.get('publishedAt'),
                'source': article.get('source', {}).get('name'),
                'sentiment': sentiment
            })
            
            # Convert sentiment to numeric score for overall calculation
            label = sentiment['label'].upper()  # Convert to uppercase
            if label == 'POSITIVE':
                sentiment_scores.append(sentiment['confidence'])
            elif label == 'NEGATIVE':
                sentiment_scores.append(-sentiment['confidence'])
            else:
                sentiment_scores.append(0)
        
        # Calculate overall sentiment
        if sentiment_scores:
            overall_score = sum(sentiment_scores) / len(sentiment_scores)
            if overall_score > 0.1:
                overall_sentiment = 'POSITIVE'
            elif overall_score < -0.1:
                overall_sentiment = 'NEGATIVE'
            else:
                overall_sentiment = 'NEUTRAL'
        else:
            overall_sentiment = 'NEUTRAL'
            overall_score = 0
        
        return jsonify({
            'symbol': symbol.upper(),
            'overall_sentiment': overall_sentiment,
            'overall_score': round(overall_score, 3),
            'total_articles': len(analyzed_articles),
            'articles': analyzed_articles,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logging.error(f"Error analyzing sentiment for {symbol}: {e}")
        return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5001)