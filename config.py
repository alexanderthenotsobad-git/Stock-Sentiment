# config.py
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    NEWS_API_KEY = os.getenv('NEWS_API_KEY')
    ALPHA_VANTAGE_KEY = os.getenv('ALPHA_VANTAGE_KEY')  # Optional
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-key')

# app.py - Basic structure
from flask import Flask, jsonify, render_template
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

@app.route('/')
def dashboard():
    return render_template('dashboard.html')

if __name__ == '__main__':
    app.run(debug=True)