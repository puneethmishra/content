import asyncio
import logging
import json
import re
from typing import Dict, List, Any, Optional
from textblob import TextBlob
import os
from dotenv import load_dotenv

# AI client imports
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

load_dotenv()

logger = logging.getLogger(__name__)

class MessageClassifier:
    def __init__(self):
        self.openai_client = None
        self.anthropic_client = None
        
        # Initialize AI clients
        if OPENAI_AVAILABLE and os.getenv("OPENAI_API_KEY"):
            openai.api_key = os.getenv("OPENAI_API_KEY")
            self.openai_client = openai
            
        if ANTHROPIC_AVAILABLE and os.getenv("ANTHROPIC_API_KEY"):
            self.anthropic_client = anthropic.Anthropic(
                api_key=os.getenv("ANTHROPIC_API_KEY")
            )
        
        # Default categories and their patterns
        self.categories = {
            "support": {
                "keywords": ["help", "problem", "issue", "error", "bug", "fix", "broken", "not working"],
                "patterns": [r"i need help", r"having trouble", r"doesn't work", r"can't.*"]
            },
            "sales": {
                "keywords": ["buy", "purchase", "price", "cost", "order", "payment", "billing"],
                "patterns": [r"how much", r"want to buy", r"pricing", r"quote"]
            },
            "inquiry": {
                "keywords": ["question", "ask", "wonder", "curious", "info", "information"],
                "patterns": [r"can you tell me", r"i want to know", r"what is", r"how do"]
            },
            "complaint": {
                "keywords": ["angry", "disappointed", "terrible", "awful", "worst", "hate", "refund"],
                "patterns": [r"very bad", r"not satisfied", r"want refund", r"poor service"]
            },
            "compliment": {
                "keywords": ["great", "awesome", "excellent", "amazing", "love", "perfect", "wonderful"],
                "patterns": [r"very good", r"well done", r"keep it up", r"impressed"]
            },
            "appointment": {
                "keywords": ["meeting", "appointment", "schedule", "book", "reservation", "calendar"],
                "patterns": [r"book.*appointment", r"schedule.*meeting", r"available.*time"]
            },
            "general": {
                "keywords": ["hello", "hi", "thanks", "thank you", "goodbye", "bye"],
                "patterns": [r"good morning", r"good afternoon", r"good evening"]
            }
        }
        
    async def classify_message(self, message_text: str) -> Dict[str, Any]:
        """Classify a message using AI or rule-based classification"""
        try:
            # First try AI classification
            if self.anthropic_client:
                result = await self._classify_with_claude(message_text)
                if result:
                    return result
                    
            if self.openai_client:
                result = await self._classify_with_openai(message_text)
                if result:
                    return result
            
            # Fallback to rule-based classification
            return self._classify_with_rules(message_text)
            
        except Exception as e:
            logger.error(f"Classification error: {e}")
            return self._classify_with_rules(message_text)
    
    async def _classify_with_claude(self, message_text: str) -> Optional[Dict[str, Any]]:
        """Classify message using Anthropic Claude"""
        try:
            categories_list = list(self.categories.keys())
            
            prompt = f"""
            Classify the following WhatsApp message into one of these categories and analyze its sentiment:

            Categories: {', '.join(categories_list)}

            Message: "{message_text}"

            Please respond with a JSON object containing:
            - category: one of the provided categories that best fits the message
            - confidence: a float between 0.0 and 1.0 indicating your confidence
            - sentiment: "positive", "negative", or "neutral"
            - tags: an array of relevant keywords or topics from the message
            - reasoning: a brief explanation of your classification

            Example response:
            {{
                "category": "support",
                "confidence": 0.85,
                "sentiment": "negative",
                "tags": ["help", "problem", "not working"],
                "reasoning": "Message requests help with a technical issue"
            }}
            """
            
            response = self.anthropic_client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=500,
                messages=[{"role": "user", "content": prompt}]
            )
            
            # Parse the response
            response_text = response.content[0].text
            try:
                result = json.loads(response_text)
                
                # Validate the result
                if all(key in result for key in ["category", "confidence", "sentiment"]):
                    return {
                        "category": result.get("category", "general"),
                        "confidence": float(result.get("confidence", 0.5)),
                        "sentiment": result.get("sentiment", "neutral"),
                        "tags": result.get("tags", []),
                        "reasoning": result.get("reasoning", "")
                    }
            except json.JSONDecodeError:
                logger.warning("Failed to parse Claude response as JSON")
                
        except Exception as e:
            logger.error(f"Claude classification error: {e}")
            
        return None
    
    async def _classify_with_openai(self, message_text: str) -> Optional[Dict[str, Any]]:
        """Classify message using OpenAI GPT"""
        try:
            categories_list = list(self.categories.keys())
            
            response = self.openai_client.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": f"""You are a WhatsApp message classifier. Classify messages into these categories: {', '.join(categories_list)}. 
                        Respond with JSON containing: category, confidence (0.0-1.0), sentiment (positive/negative/neutral), tags (array), and reasoning."""
                    },
                    {
                        "role": "user",
                        "content": f"Classify this message: '{message_text}'"
                    }
                ],
                max_tokens=500,
                temperature=0.3
            )
            
            response_text = response.choices[0].message.content
            
            try:
                result = json.loads(response_text)
                
                if all(key in result for key in ["category", "confidence", "sentiment"]):
                    return {
                        "category": result.get("category", "general"),
                        "confidence": float(result.get("confidence", 0.5)),
                        "sentiment": result.get("sentiment", "neutral"),
                        "tags": result.get("tags", []),
                        "reasoning": result.get("reasoning", "")
                    }
            except json.JSONDecodeError:
                logger.warning("Failed to parse OpenAI response as JSON")
                
        except Exception as e:
            logger.error(f"OpenAI classification error: {e}")
            
        return None
    
    def _classify_with_rules(self, message_text: str) -> Dict[str, Any]:
        """Rule-based classification as fallback"""
        message_lower = message_text.lower()
        
        # Calculate scores for each category
        category_scores = {}
        
        for category, rules in self.categories.items():
            score = 0
            matched_tags = []
            
            # Check keywords
            for keyword in rules["keywords"]:
                if keyword in message_lower:
                    score += 1
                    matched_tags.append(keyword)
            
            # Check patterns
            for pattern in rules["patterns"]:
                if re.search(pattern, message_lower):
                    score += 2  # Patterns have higher weight
                    matched_tags.append(pattern.replace(r".*", ""))
            
            if score > 0:
                category_scores[category] = {
                    "score": score,
                    "tags": matched_tags
                }
        
        # Determine best category
        if category_scores:
            best_category = max(category_scores.items(), key=lambda x: x[1]["score"])
            category = best_category[0]
            tags = best_category[1]["tags"]
            
            # Calculate confidence based on score
            max_possible_score = len(self.categories[category]["keywords"]) + len(self.categories[category]["patterns"]) * 2
            confidence = min(best_category[1]["score"] / max_possible_score, 1.0)
        else:
            category = "general"
            tags = []
            confidence = 0.3
        
        # Determine sentiment using TextBlob
        try:
            blob = TextBlob(message_text)
            polarity = blob.sentiment.polarity
            
            if polarity > 0.1:
                sentiment = "positive"
            elif polarity < -0.1:
                sentiment = "negative"
            else:
                sentiment = "neutral"
        except:
            sentiment = "neutral"
        
        return {
            "category": category,
            "confidence": confidence,
            "sentiment": sentiment,
            "tags": tags,
            "reasoning": f"Rule-based classification based on keywords and patterns"
        }
    
    def add_custom_category(self, category: str, keywords: List[str], patterns: List[str] = None):
        """Add a custom category for classification"""
        self.categories[category] = {
            "keywords": keywords,
            "patterns": patterns or []
        }
        logger.info(f"Added custom category: {category}")
    
    def update_category_rules(self, category: str, keywords: List[str] = None, patterns: List[str] = None):
        """Update rules for an existing category"""
        if category in self.categories:
            if keywords:
                self.categories[category]["keywords"] = keywords
            if patterns:
                self.categories[category]["patterns"] = patterns
            logger.info(f"Updated category rules: {category}")
        else:
            logger.warning(f"Category not found: {category}")
    
    def get_categories(self) -> List[str]:
        """Get list of available categories"""
        return list(self.categories.keys())
    
    def get_category_stats(self, messages: List[str]) -> Dict[str, int]:
        """Get classification statistics for a list of messages"""
        stats = {category: 0 for category in self.categories.keys()}
        
        for message in messages:
            result = self._classify_with_rules(message)
            stats[result["category"]] += 1
        
        return stats