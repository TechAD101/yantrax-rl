# Content of enhanced_sentiment_analyzer.py
# Assuming this is the content of the file that needs to be moved.

# Your Python code goes here...#!/usr/bin/env python3
"""
YantraX RL Enhanced Sentiment Analyzer
Advanced sentiment analysis with reinforcement learning optimization
"""

import numpy as np
import pandas as pd
from textblob import TextBlob
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import re
from typing import Dict, List, Tuple, Any
from datetime import datetime
import logging
from sklearn.preprocessing import MinMaxScaler
import pickle
import os

class EnhancedSentimentAnalyzer:
    """
    Advanced sentiment analyzer with RL-based optimization and multi-model ensemble
    """
    
    def __init__(self):
        self.vader_analyzer = SentimentIntensityAnalyzer()
        self.scaler = MinMaxScaler()
        self.rl_weights = np.array([0.4, 0.3, 0.3])  # TextBlob, VADER, Custom
        self.confidence_threshold = 0.7
        self.sentiment_history = []
        self.model_performance = {'textblob': 0.8, 'vader': 0.85, 'custom': 0.75}
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
def preprocess_text(self, text: str) -> str:
        """
        Advanced text preprocessing with domain-specific optimization
        """
        if not isinstance(text, str):
            return ""
            
        # Remove URLs, mentions, hashtags for cleaner analysis
        text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
        text = re.sub(r'@[A-Za-z0-9_]+', '', text)
        text = re.sub(r'#[A-Za-z0-9_]+', '', text)
        
        # Handle negations and intensifiers
        text = re.sub(r"n't", " not", text)
        text = re.sub(r"'re", " are", text)
        text = re.sub(r"'ll", " will", text)
        text = re.sub(r"'ve", " have", text)
        
        # Clean whitespace
        text = ' '.join(text.split())
        
        return text.strip()
    
    def textblob_analysis(self, text: str) -> Dict[str, float]:
        """
        TextBlob-based sentiment analysis
        """
        blob = TextBlob(text)
        polarity = blob.sentiment.polarity
        subjectivity = blob.sentiment.subjectivity
        
        return {
            'polarity': polarity,
            'subjectivity': subjectivity,
            'confidence': abs(polarity)
        }
    
    def vader_analysis(self, text: str) -> Dict[str, float]:
        """
        VADER sentiment analysis
        """
        scores = self.vader_analyzer.polarity_scores(text)
        return {
            'compound': scores['compound'],
            'positive': scores['pos'],
            'neutral': scores['neu'],
            'negative': scores['neg'],
            'confidence': abs(scores['compound'])
        }
    
    def custom_sentiment_analysis(self, text: str) -> Dict[str, float]:
        """
        Custom rule-based sentiment analysis with domain-specific keywords
        """
        positive_words = ['excellent', 'amazing', 'outstanding', 'fantastic', 'love', 'perfect', 'wonderful']
        negative_words = ['terrible', 'awful', 'horrible', 'hate', 'worst', 'disgusting', 'pathetic']
        
        text_lower = text.lower()
        words = text_lower.split()
        
        positive_count = sum(1 for word in words if word in positive_words)
        negative_count = sum(1 for word in words if word in negative_words)
        
        total_words = len(words)
        if total_words == 0:
            return {'polarity': 0.0, 'confidence': 0.0}
        
        polarity = (positive_count - negative_count) / total_words
        confidence = (positive_count + negative_count) / total_words
        
        return {
            'polarity': np.clip(polarity, -1, 1),
            'confidence': min(confidence, 1.0)
        }
    
    def ensemble_analysis(self, text: str) -> Dict[str, Any]:
        """
        Ensemble sentiment analysis combining multiple models with RL optimization
        """
        preprocessed_text = self.preprocess_text(text)
        
        # Get predictions from all models
        textblob_result = self.textblob_analysis(preprocessed_text)
        vader_result = self.vader_analysis(preprocessed_text)
        custom_result = self.custom_sentiment_analysis(preprocessed_text)
        
        # Extract polarities and confidences
        polarities = np.array([
            textblob_result['polarity'],
            vader_result['compound'],
            custom_result['polarity']
        ])
        
        confidences = np.array([
            textblob_result['confidence'],
            vader_result['confidence'],
            custom_result['confidence']
        ])
        
        # RL-optimized weighted ensemble
        weighted_polarity = np.sum(self.rl_weights * polarities)
        weighted_confidence = np.sum(self.rl_weights * confidences)
        
        # Classify sentiment
        if weighted_polarity > 0.1:
            sentiment = 'positive'
        elif weighted_polarity < -0.1:
            sentiment = 'negative'
        else:
            sentiment = 'neutral'
        
        result = {
            'sentiment': sentiment,
            'polarity': float(weighted_polarity),
            'confidence': float(weighted_confidence),
            'individual_results': {
                'textblob': textblob_result,
                'vader': vader_result,
                'custom': custom_result
            },
            'timestamp': datetime.now().isoformat(),
            'processed_text': preprocessed_text
        }
        
        self.sentiment_history.append(result)
        return result
    
    def update_rl_weights(self, feedback_score: float, prediction_accuracy: float):
        """
        Update RL weights based on feedback and prediction accuracy
        """
        learning_rate = 0.01
        
        # Simple reward-based weight adjustment
        reward = feedback_score * prediction_accuracy
        
        if reward > 0.8:
            # Successful prediction, slightly increase current weights
            self.rl_weights += learning_rate * reward
        else:
            # Poor prediction, adjust weights
            self.rl_weights -= learning_rate * (1 - reward)
        
        # Normalize weights
        self.rl_weights = np.clip(self.rl_weights, 0.1, 0.8)
        self.rl_weights = self.rl_weights / np.sum(self.rl_weights)
        
        self.logger.info(f"Updated RL weights: {self.rl_weights}")
    
    def batch_analyze(self, texts: List[str]) -> List[Dict[str, Any]]:
        """
        Analyze multiple texts efficiently
        """
        return [self.ensemble_analysis(text) for text in texts]
    
    def get_sentiment_trends(self, window_size: int = 10) -> Dict[str, Any]:
        """
        Analyze sentiment trends from recent history
        """
        if len(self.sentiment_history) < window_size:
            return {'error': 'Insufficient data for trend analysis'}
        
        recent_sentiments = self.sentiment_history[-window_size:]
        polarities = [s['polarity'] for s in recent_sentiments]
        
        trend = {
            'average_polarity': np.mean(polarities),
            'polarity_std': np.std(polarities),
            'trend_direction': 'increasing' if polarities[-1] > polarities[0] else 'decreasing',
            'sentiment_distribution': {
                'positive': sum(1 for s in recent_sentiments if s['sentiment'] == 'positive'),
                'neutral': sum(1 for s in recent_sentiments if s['sentiment'] == 'neutral'),
                'negative': sum(1 for s in recent_sentiments if s['sentiment'] == 'negative')
            }
        }
        
        return trend
    
    def save_model(self, filepath: str):
        """
        Save the trained model and weights
        """
        model_data = {
            'rl_weights': self.rl_weights,
            'sentiment_history': self.sentiment_history[-1000:],  # Keep last 1000 records
            'model_performance': self.model_performance,
            'confidence_threshold': self.confidence_threshold
        }
        
        with open(filepath, 'wb') as f:
            pickle.dump(model_data, f)
        
        self.logger.info(f"Model saved to {filepath}")
    
    def load_model(self, filepath: str):
        """
        Load a pre-trained model
        """
        if not os.path.exists(filepath):
            self.logger.warning(f"Model file {filepath} not found, using default weights")
            return
        
        try:
            with open(filepath, 'rb') as f:
                model_data = pickle.load(f)
            
            self.rl_weights = model_data.get('rl_weights', self.rl_weights)
            self.sentiment_history = model_data.get('sentiment_history', [])
            self.model_performance = model_data.get('model_performance', self.model_performance)
            self.confidence_threshold = model_data.get('confidence_threshold', self.confidence_threshold)
            
            self.logger.info(f"Model loaded from {filepath}")
        except Exception as e:
            self.logger.error(f"Error loading model: {e}")

# Example usage and testing
if __name__ == "__main__":
    analyzer = EnhancedSentimentAnalyzer()
    
    # Test cases
    test_texts = [
        "I absolutely love this product! It's amazing and works perfectly.",
        "This is the worst experience I've ever had. Completely disappointed.",
        "The product is okay, nothing special but does the job.",
        "Fantastic service! Will definitely recommend to others.",
        "Not sure how I feel about this. It's complicated."
    ]
    
    print("YantraX RL Enhanced Sentiment Analysis Results:")
    print("=" * 60)
    
    for i, text in enumerate(test_texts, 1):
        result = analyzer.ensemble_analysis(text)
        print(f"\nTest {i}: {text[:50]}...")
        print(f"Sentiment: {result['sentiment'].upper()}")
        print(f"Polarity: {result['polarity']:.3f}")
        print(f"Confidence: {result['confidence']:.3f}")
    
    # Show trend analysis
    trends = analyzer.get_sentiment_trends()
    if 'error' not in trends:
        print("\nSentiment Trends:")
        print(f"Average Polarity: {trends['average_polarity']:.3f}")
        print(f"Distribution: {trends['sentiment_distribution']}")
    
    # Save model
    analyzer.save_model('yantrax_sentiment_model.pkl')
    print("\nModel saved successfully!")

# Add this at the VERY END of enhanced_sentiment_analyzer.py

_analyzer_instance = EnhancedSentimentAnalyzer()

def analyze(text):
    return _analyzer_instance.ensemble_analysis(text)