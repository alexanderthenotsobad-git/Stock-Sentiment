// Enhanced Stock Sentiment Dashboard JavaScript
// /var/www/stock-sent/stock_sentiment_dashboard/static/js/dashboard.js

let sentimentChart = null; // Global variable to track the chart instance

async function analyzeSentiment() {
    const symbol = document.getElementById('stockSymbol').value.toUpperCase().trim();
    if (!symbol) {
        showError('Please enter a stock symbol');
        return;
    }

    console.log('Starting enhanced analysis for:', symbol);

    // Show loading state
    showLoading(true);
    hideError();
    hideResults();

    try {
        const response = await fetch(`/api/sentiment/${symbol}`);
        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || 'Failed to analyze sentiment');
        }

        console.log('Enhanced dashboard - Success:', data);
        displayResults(data);
    } catch (error) {
        console.error('Enhanced dashboard - Error:', error);
        showError(error.message);
    } finally {
        showLoading(false);
    }
}

function displayResults(data) {
    // Update overall sentiment information
    document.getElementById('stockSymbolResult').textContent = data.symbol;
    document.getElementById('overallSentiment').textContent = data.overall_sentiment;
    document.getElementById('overallScore').textContent = data.overall_score;
    document.getElementById('totalArticles').textContent = data.total_articles;

    // Set sentiment color class
    const sentimentElement = document.getElementById('overallSentiment');
    sentimentElement.className = `sentiment-${data.overall_sentiment.toLowerCase()}`;

    // Destroy existing chart if it exists
    if (sentimentChart) {
        sentimentChart.destroy();
        sentimentChart = null;
    }

    // Create new sentiment scatter chart
    createSentimentChart(data.articles);

    // Display articles
    displayArticles(data.articles);

    // Show results
    showResults(true);
}

// Convert sentiment and confidence to Y-axis position
function sentimentToYValue(sentiment, confidence) {
    switch (sentiment) {
        case 'POSITIVE': return confidence;
        case 'NEGATIVE': return -confidence;
        case 'NEUTRAL': return (Math.random() - 0.5) * 0.2; // Small random around 0
        default: return 0;
    }
}

function createSentimentChart(articles) {
    const ctx = document.getElementById('sentimentChart').getContext('2d');

    // Convert articles to scatter plot data points
    const chartData = articles.map((article, index) => ({
        x: index + 1,
        y: sentimentToYValue(article.sentiment.label, article.sentiment.confidence),
        sentiment: article.sentiment.label,
        confidence: article.sentiment.confidence,
        title: article.title
    }));

    // Separate data by sentiment for different colors
    const positiveData = chartData.filter(d => d.sentiment === 'POSITIVE');
    const negativeData = chartData.filter(d => d.sentiment === 'NEGATIVE');
    const neutralData = chartData.filter(d => d.sentiment === 'NEUTRAL');

    // Create new chart instance
    sentimentChart = new Chart(ctx, {
        type: 'scatter',
        data: {
            datasets: [
                {
                    label: 'Positive Articles',
                    data: positiveData,
                    backgroundColor: '#28a745',
                    borderColor: '#28a745',
                    pointRadius: 6,
                    pointHoverRadius: 8
                },
                {
                    label: 'Negative Articles',
                    data: negativeData,
                    backgroundColor: '#dc3545',
                    borderColor: '#dc3545',
                    pointRadius: 6,
                    pointHoverRadius: 8
                },
                {
                    label: 'Neutral Articles',
                    data: neutralData,
                    backgroundColor: '#ffc107',
                    borderColor: '#ffc107',
                    pointRadius: 6,
                    pointHoverRadius: 8
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: {
                    title: {
                        display: true,
                        text: 'Article Number',
                        font: { size: 12, weight: 'bold' }
                    },
                    min: 0,
                    max: articles.length + 1,
                    ticks: {
                        stepSize: 1
                    }
                },
                y: {
                    title: {
                        display: true,
                        text: 'Sentiment Score (Confidence × Direction)',
                        font: { size: 12, weight: 'bold' }
                    },
                    min: -1,
                    max: 1,
                    ticks: {
                        callback: function (value) {
                            if (value > 0.7) return 'Strong Positive';
                            if (value > 0.3) return 'Positive';
                            if (value > -0.3) return 'Neutral';
                            if (value > -0.7) return 'Negative';
                            return 'Strong Negative';
                        }
                    },
                    grid: {
                        color: function (context) {
                            if (context.tick.value === 0) {
                                return '#000000'; // Black line at 0
                            }
                            return '#e0e0e0'; // Regular grid lines
                        },
                        lineWidth: function (context) {
                            if (context.tick.value === 0) {
                                return 2; // Thicker line at 0
                            }
                            return 1;
                        }
                    }
                }
            },
            plugins: {
                tooltip: {
                    callbacks: {
                        title: function (context) {
                            const point = context[0];
                            return `Article ${point.parsed.x}`;
                        },
                        label: function (context) {
                            const point = context.raw;
                            return [
                                `${point.sentiment}: ${Math.round(point.confidence * 100)}% confidence`,
                                `Title: ${point.title.substring(0, 50)}...`
                            ];
                        }
                    }
                },
                legend: {
                    position: 'top',
                    labels: {
                        usePointStyle: true,
                        padding: 15
                    }
                },
                title: {
                    display: true,
                    text: 'Individual Article Sentiment Analysis'
                }
            }
        }
    });
}

function displayArticles(articles) {
    const container = document.getElementById('articlesList');
    container.innerHTML = '';

    if (!articles || articles.length === 0) {
        container.innerHTML = '<p class="text-muted">No articles found.</p>';
        return;
    }

    articles.forEach((article, index) => {
        const articleDiv = document.createElement('div');
        articleDiv.className = 'article-item';

        const sentimentClass = `sentiment-${article.sentiment.label.toLowerCase()}`;
        const confidencePercent = Math.round(article.sentiment.confidence * 100);
        const yValue = sentimentToYValue(article.sentiment.label, article.sentiment.confidence);

        articleDiv.innerHTML = `
            <div class="article-header">
                <h5><a href="${article.url}" target="_blank" rel="noopener noreferrer">${escapeHtml(article.title)}</a></h5>
                <span class="sentiment-badge ${sentimentClass}">
                    ${article.sentiment.label} (${confidencePercent}%)
                </span>
            </div>
            <p class="article-source"><strong>Source:</strong> ${escapeHtml(article.source || 'Unknown')}</p>
            <p class="article-date"><strong>Published:</strong> ${formatDate(article.published_at)}</p>
            <p class="article-plot"><strong>Chart Position:</strong> Article #${index + 1}, Y-value: ${yValue.toFixed(3)}</p>
        `;

        container.appendChild(articleDiv);
    });
}

function formatDate(dateString) {
    if (!dateString) return 'Unknown';
    try {
        const date = new Date(dateString);
        return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    } catch (error) {
        return 'Unknown';
    }
}

function escapeHtml(text) {
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return text ? text.replace(/[&<>"']/g, m => map[m]) : '';
}

// UI Helper Functions
function showLoading(show) {
    document.getElementById('loading').style.display = show ? 'block' : 'none';
    document.getElementById('analyzeButton').disabled = show;
    if (show) {
        document.getElementById('analyzeButton').innerHTML = 'Analyzing...';
    } else {
        document.getElementById('analyzeButton').innerHTML = '📊 Analyze Sentiment';
    }
}

function showResults(show) {
    document.getElementById('results').style.display = show ? 'block' : 'none';
    document.getElementById('articlesContainer').style.display = show ? 'block' : 'none';
}

function hideResults() {
    showResults(false);
}

function showError(message) {
    const errorDiv = document.getElementById('error');
    const errorMessageSpan = document.getElementById('errorMessage');
    if (errorMessageSpan) {
        errorMessageSpan.textContent = message;
    } else {
        errorDiv.innerHTML = `<strong>Error:</strong> ${escapeHtml(message)}`;
    }
    errorDiv.style.display = 'block';
}

function hideError() {
    document.getElementById('error').style.display = 'none';
}

// Event Listeners
document.addEventListener('DOMContentLoaded', function () {
    console.log('Enhanced Dashboard JavaScript loaded with scatter plot visualization');

    // Allow Enter key to trigger analysis
    const stockInput = document.getElementById('stockSymbol');
    if (stockInput) {
        stockInput.addEventListener('keypress', function (e) {
            if (e.key === 'Enter') {
                analyzeSentiment();
            }
        });

        // Focus on input when page loads
        stockInput.focus();
    }
});