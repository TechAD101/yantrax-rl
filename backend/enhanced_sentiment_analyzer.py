#!/usr/bin/env python3
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
        Clean and preprocess text for sentiment analysis
        """
        if not isinstance(text, str):
            return ""
        
        # Remove URLs
        text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
        
        # Remove special characters but keep emoticons
        text = re.sub(r'[^\w\s\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF]', ' ', text)
        
        # Handle repeated characters
        text = re.sub(r'(.)\1{2,}', r'\1\1', text)
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def textblob_sentiment(self, text: str) -> Dict[str, float]:
        """
        Get sentiment using TextBlob
        """
        try:
            blob = TextBlob(text)
            polarity = blob.sentiment.polarity  # -1 to 1
            subjectivity = blob.sentiment.subjectivity  # 0 to 1
            
            # Convert polarity to confidence
            confidence = abs(polarity) * subjectivity
            
            return {
                'polarity': polarity,
                'confidence': confidence,
                'subjectivity': subjectivity
            }
        except Exception as e:
            self.logger.error(f"TextBlob error: {e}")
            return {'polarity': 0.0, 'confidence': 0.0, 'subjectivity': 0.0}
    
    def vader_sentiment(self, text: str) -> Dict[str, float]:
        """
        Get sentiment using VADER
        """
        try:
            scores = self.vader_analyzer.polarity_scores(text)
            return {
                'polarity': scores['compound'],
                'confidence': abs(scores['compound']),
                'positive': scores['pos'],
                'negative': scores['neg'],
                'neutral': scores['neu']
            }
        except Exception as e:
            self.logger.error(f"VADER error: {e}")
            return {'polarity': 0.0, 'confidence': 0.0, 'positive': 0.0, 'negative': 0.0, 'neutral': 1.0}
    
    def custom_sentiment(self, text: str) -> Dict[str, float]:
        """
        Custom rule-based sentiment analysis
        """
        positive_words = ['good', 'great', 'excellent', 'amazing', 'awesome', 'fantastic', 'wonderful', 'love', 'best']
        negative_words = ['bad', 'terrible', 'awful', 'horrible', 'worst', 'hate', 'disgusting', 'disappointing']
        
        text_lower = text.lower()
        words = text_lower.split()
        
        positive_count = sum(1 for word in words if word in positive_words)
        negative_count = sum(1 for word in words if word in negative_words)
        total_words = len(words)
        
        if total_words == 0:
            return {'polarity': 0.0, 'confidence': 0.0}
        
        # Calculate polarity
        polarity = (positive_count - negative_count) / total_words
        polarity = max(-1.0, min(1.0, polarity * 5))  # Scale and bound
        
        # Calculate confidence based on sentiment word density
        sentiment_density = (positive_count + negative_count) / total_words
        confidence = min(1.0, sentiment_density * 2)
        
        return {
            'polarity': polarity,
            'confidence': confidence,
            'positive_words': positive_count,
            'negative_words': negative_count
        }
    
    def ensemble_analysis(self, text: str) -> Dict[str, Any]:
        """
        Perform ensemble sentiment analysis with RL-weighted combination
        """
        if not text or not text.strip():
            return {
                'sentiment': 'neutral',
                'polarity': 0.0,
                'confidence': 0.0,
                'models': {}
            }
        
        # Preprocess text
        clean_text = self.preprocess_text(text)
        
        # Get individual model predictions
        textblob_result = self.textblob_sentiment(clean_text)
        vader_result = self.vader_sentiment(clean_text)
        custom_result = self.custom_sentiment(clean_text)
        
        # Store individual results
        models = {
            'textblob': textblob_result,
            'vader': vader_result,
            'custom': custom_result
        }
        
        # Calculate weighted ensemble
        polarities = [textblob_result['polarity'], vader_result['polarity'], custom_result['polarity']]
        confidences = [textblob_result['confidence'], vader_result['confidence'], custom_result['confidence']]
        
        # Weighted average
        ensemble_polarity = np.average(polarities, weights=self.rl_weights)
        ensemble_confidence = np.average(confidences, weights=self.rl_weights)
        
        # Determine sentiment label
        if ensemble_polarity > 0.1:
            sentiment = 'positive'
        elif ensemble_polarity < -0.1:
            sentiment = 'negative'
        else:
            sentiment = 'neutral'
        
        result = {
            'text': text,
            'sentiment': sentiment,
            'polarity': float(ensemble_polarity),
            'confidence': float(ensemble_confidence),
            'models': models,
            'weights': self.rl_weights.tolist(),
            'timestamp': datetime.now().isoformat()
        }
        
        # Store in history for RL learning
        self.sentiment_history.append(result)
        if len(self.sentiment_history) > 1000:  # Keep only recent history
            self.sentiment_history = self.sentiment_history[-1000:]
        
        return result
    
    def update_weights(self, feedback: Dict[str, float]):
        """
        Update RL weights based on feedback
        """
        learning_rate = 0.01
        
        # Simple gradient update based on performance feedback
        for i, model in enumerate(['textblob', 'vader', 'custom']):
            if model in feedback:
                performance = feedback[model]
                # Update weight based on performance (0-1 scale)
                self.rl_weights[i] += learning_rate * (performance - 0.5)
        
        # Normalize weights
        self.rl_weights = np.abs(self.rl_weights)  # Ensure positive
        self.rl_weights = self.rl_weights / np.sum(self.rl_weights)  # Normalize
        
        self.logger.info(f"Updated weights: {self.rl_weights}")
    
    def get_sentiment_trends(self) -> Dict[str, Any]:
        """
        Analyze sentiment trends from history
        """
        if not self.sentiment_history:
            return {'error': 'No sentiment history available'}
        
        df = pd.DataFrame(self.sentiment_history)
        
        trends = {
            'total_analyses': len(df),
            'sentiment_distribution': df['sentiment'].value_counts().to_dict(),
            'average_polarity': df['polarity'].mean(),
            'polarity_std': df['polarity'].std(),
            'confidence_avg': df['confidence'].mean(),
            'recent_trend': df.tail(10)['sentiment'].tolist()
        }
        
        return trends
    
    def save_model(self, filepath: str):
        """
        Save the trained model
        """
        try:
            model_data = {
                'rl_weights': self.rl_weights,
                'sentiment_history': self.sentiment_history,
                'model_performance': self.model_performance,
                'confidence_threshold': self.confidence_threshold
            }
            
            with open(filepath, 'wb') as f:
                pickle.dump(model_data, f)
            
            self.logger.info(f"Model saved to {filepath}")
        except Exception as e:
            self.logger.error(f"Error saving model: {e}")
    
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
