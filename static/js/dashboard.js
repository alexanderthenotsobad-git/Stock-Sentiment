// static/js/dashboard.js
async function analyzeSentiment() {
    const symbol = document.getElementById('stockSymbol').value.trim();
    if (!symbol) {
        alert('Please enter a stock symbol');
        return;
    }

    try {
        // Show loading state
        document.getElementById('results').style.display = 'block';
        document.getElementById('symbolTitle').textContent = `Loading ${symbol.toUpperCase()}...`;

        const response = await fetch(`/api/sentiment/${symbol}`);
        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || 'Failed to fetch data');
        }

        displayResults(data);

    } catch (error) {
        console.error('Error:', error);
        alert(`Error: ${error.message}`);
    }
}

function displayResults(data) {
    // Update title and overall sentiment
    document.getElementById('symbolTitle').textContent = `${data.symbol} Sentiment Analysis`;

    const sentimentColor = getSentimentColor(data.overall_sentiment);
    document.getElementById('overallSentiment').innerHTML = `
        <div class="alert alert-${sentimentColor}">
            <strong>Overall Sentiment:</strong> ${data.overall_sentiment} 
            (Score: ${data.overall_score})
            <br><small>Based on ${data.total_articles} recent articles</small>
        </div>
    `;

    // Create sentiment chart
    createSentimentChart(data.articles);

    // Display articles
    displayArticles(data.articles);

    document.getElementById('articlesContainer').style.display = 'block';
}

function getSentimentColor(sentiment) {
    switch (sentiment) {
        case 'POSITIVE': return 'success';
        case 'NEGATIVE': return 'danger';
        default: return 'warning';
    }
}

function createSentimentChart(articles) {
    const ctx = document.getElementById('sentimentChart').getContext('2d');

    const sentimentCounts = {
        'POSITIVE': 0,
        'NEGATIVE': 0,
        'NEUTRAL': 0
    };

    articles.forEach(article => {
        sentimentCounts[article.sentiment.label]++;
    });

    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Positive', 'Negative', 'Neutral'],
            datasets: [{
                data: [sentimentCounts.POSITIVE, sentimentCounts.NEGATIVE, sentimentCounts.NEUTRAL],
                backgroundColor: ['#28a745', '#dc3545', '#ffc107']
            }]
        },
        options: {
            responsive: true,
            plugins: {
                title: {
                    display: true,
                    text: 'Sentiment Distribution'
                }
            }
        }
    });
}

function displayArticles(articles) {
    const container = document.getElementById('articlesList');
    container.innerHTML = articles.map(article => `
        <div class="card mb-3">
            <div class="card-body">
                <h6 class="card-title">
                    <a href="${article.url}" target="_blank">${article.title}</a>
                </h6>
                <div class="d-flex justify-content-between">
                    <small class="text-muted">${article.source} - ${new Date(article.published_at).toLocaleDateString()}</small>
                    <span class="badge bg-${getSentimentColor(article.sentiment.label)}">
                        ${article.sentiment.label} (${article.sentiment.confidence})
                    </span>
                </div>
            </div>
        </div>
    `).join('');
}

// Allow Enter key to trigger search
document.getElementById('stockSymbol').addEventListener('keypress', function (e) {
    if (e.key === 'Enter') {
        analyzeSentiment();
    }
});