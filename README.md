# Stock Market Sentiment Analysis Dashboard

A real-time sentiment analysis tool for stock market news using AI-powered natural language processing.

## Features

- 🤖 **AI-Powered Analysis**: Uses Hugging Face RoBERTa model for sentiment classification
- 📰 **Real-Time News**: Fetches latest financial news from News API
- 📊 **Interactive Dashboard**: Clean web interface with sentiment visualizations
- 🔄 **RESTful API**: Clean API endpoints for programmatic access
- 📈 **Multiple Stocks**: Analyze sentiment for any stock symbol

## Tech Stack

### Backend

- **Flask** - Web framework
- **Hugging Face Transformers** - AI sentiment analysis
- **pandas** - Data processing
- **requests** - HTTP API calls

### Frontend

- **HTML5/CSS3/JavaScript** - Core web technologies
- **Bootstrap** - Responsive UI framework
- **Chart.js** - Data visualizations

### APIs

- **News API** - Real-time financial news data
- **Hugging Face Models** - Pre-trained NLP models

## Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/yourusername/stock-sentiment-dashboard.git
   cd stock-sentiment-dashboard
   ```

2. **Create virtual environment**

   ```bash
   python -m venv stock_sentiment_env
   source stock_sentiment_env/bin/activate  # Linux/Mac
   # stock_sentiment_env\Scripts\activate  # Windows
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**

   ```bash
   cp .env.example .env
   # Edit .env with your News API key
   ```

5. **Run the application**
   ```bash
   python app.py
   ```

## Configuration

Create a `.env` file with:

```bash
NEWS_API_KEY=your_news_api_key_here
SECRET_KEY=your_flask_secret_key
FLASK_ENV=development
```

## API Usage

### Analyze Stock Sentiment

```bash
GET /api/sentiment/{symbol}
```

**Example:**

```bash
curl http://localhost:5001/api/sentiment/AAPL
```

**Response:**

```json
{
  "symbol": "AAPL",
  "overall_sentiment": "POSITIVE",
  "overall_score": 0.234,
  "total_articles": 15,
  "articles": [...],
  "timestamp": "2025-06-02T21:01:26.848335"
}
```

## Deployment

This project can be deployed to:

- Cloudflare Pages
- Heroku
- AWS Lambda
- Google Cloud Functions

See `/docs` for deployment guides.

## License

MIT License

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## Author

Alexander Gomez - Software Engineer & Technology Instructor
# Stock-Sentiment
This is a Python and Hugging Face project to assess stock sentiment for any given stock (i.e. TSLA, AAPL)
