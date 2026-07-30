from textblob import TextBlob
from typing import Dict, Any

class SentimentService:
    @staticmethod
    def analyze(text: str) -> Dict[str, Any]:
        """
        Analyzes the sentiment of a text.
        Returns polarity, subjectivity and category.
        """
        blob = TextBlob(text)
        polarity = blob.sentiment.polarity
        subjectivity = blob.sentiment.subjectivity
        
        if polarity > 0.1:
            category = "positive"
        elif polarity < -0.1:
            category = "negative"
        else:
            category = "neutral"
            
        return {
            "polarity": polarity,
            "subjectivity": subjectivity,
            "category": category
        }
