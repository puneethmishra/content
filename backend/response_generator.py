import asyncio
import logging
import json
import re
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import random
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

class ResponseGenerator:
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
        
        # Default response templates for each category
        self.response_templates = {
            "support": [
                "Hi! I understand you're having an issue. Let me help you with that. Can you provide more details about the problem you're experiencing?",
                "Thank you for reaching out! I'm here to assist you. Could you please describe the issue in more detail so I can better help you?",
                "I see you need support. I'll be happy to help! Can you tell me more about what's not working correctly?"
            ],
            "sales": [
                "Hello! Thank you for your interest in our products/services. I'd be happy to provide you with pricing information and help you with your purchase.",
                "Hi there! I can help you with your purchase inquiry. Let me get you the information you need right away.",
                "Thank you for considering us! I'll provide you with detailed pricing and product information. What specific product are you interested in?"
            ],
            "inquiry": [
                "Hi! I'd be happy to answer your questions. What would you like to know?",
                "Hello! Thanks for your inquiry. I'm here to provide you with the information you need.",
                "Thank you for reaching out! I'll help you get the answers you're looking for."
            ],
            "complaint": [
                "I sincerely apologize for any inconvenience you've experienced. Your feedback is very important to us, and I want to make this right.",
                "I'm sorry to hear about your negative experience. I take your concerns seriously and would like to resolve this issue for you.",
                "Thank you for bringing this to my attention. I apologize for the trouble and will work to address your concerns immediately."
            ],
            "compliment": [
                "Thank you so much for your kind words! We really appreciate your positive feedback.",
                "That's wonderful to hear! Thank you for taking the time to share your positive experience with us.",
                "We're thrilled that you're happy with our service! Your feedback means a lot to us."
            ],
            "appointment": [
                "I'd be happy to help you schedule an appointment. What date and time work best for you?",
                "Thank you for wanting to book an appointment. Let me check our availability and find a suitable time for you.",
                "I can assist you with scheduling. What type of appointment are you looking to book?"
            ],
            "general": [
                "Hello! Thank you for your message. How can I assist you today?",
                "Hi there! I'm here to help. What can I do for you?",
                "Thank you for reaching out! I'm ready to assist you with whatever you need."
            ]
        }
        
        # Context variables that can be used in templates
        self.context_variables = {
            "current_time": datetime.now().strftime("%H:%M"),
            "current_date": datetime.now().strftime("%Y-%m-%d"),
            "current_day": datetime.now().strftime("%A"),
            "business_hours": "9:00 AM - 6:00 PM",
            "support_email": "support@company.com",
            "website": "www.company.com"
        }
    
    async def generate_response(
        self, 
        message_text: str, 
        template: str, 
        classification: Dict[str, Any],
        use_ai: bool = True
    ) -> str:
        """Generate a response based on the message and classification"""
        try:
            # First try AI-generated response if enabled
            if use_ai:
                if self.anthropic_client:
                    ai_response = await self._generate_with_claude(message_text, classification)
                    if ai_response:
                        return ai_response
                        
                if self.openai_client:
                    ai_response = await self._generate_with_openai(message_text, classification)
                    if ai_response:
                        return ai_response
            
            # Fallback to template-based response
            return self._generate_with_template(template, classification)
            
        except Exception as e:
            logger.error(f"Response generation error: {e}")
            return self._get_fallback_response(classification.get("category", "general"))
    
    async def _generate_with_claude(self, message_text: str, classification: Dict[str, Any]) -> Optional[str]:
        """Generate response using Anthropic Claude"""
        try:
            category = classification.get("category", "general")
            sentiment = classification.get("sentiment", "neutral")
            tags = classification.get("tags", [])
            
            prompt = f"""
            You are a helpful customer service assistant responding to WhatsApp messages. 
            
            Original message: "{message_text}"
            Message category: {category}
            Message sentiment: {sentiment}
            Key topics: {', '.join(tags) if tags else 'none'}
            
            Generate a professional, friendly, and helpful response that:
            1. Acknowledges the customer's message appropriately
            2. Addresses their specific needs based on the category
            3. Maintains a tone appropriate to their sentiment
            4. Keeps the response concise but complete
            5. Offers next steps or additional help when appropriate
            
            Guidelines:
            - Keep responses under 200 words
            - Use a conversational but professional tone
            - For complaints: apologize and offer to resolve
            - For sales: show enthusiasm and offer assistance
            - For support: be helpful and ask clarifying questions
            - For general messages: be welcoming and ask how to help
            
            Response:
            """
            
            response = self.anthropic_client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=300,
                messages=[{"role": "user", "content": prompt}]
            )
            
            return response.content[0].text.strip()
            
        except Exception as e:
            logger.error(f"Claude response generation error: {e}")
            return None
    
    async def _generate_with_openai(self, message_text: str, classification: Dict[str, Any]) -> Optional[str]:
        """Generate response using OpenAI GPT"""
        try:
            category = classification.get("category", "general")
            sentiment = classification.get("sentiment", "neutral")
            
            response = self.openai_client.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": f"""You are a professional customer service assistant. Generate appropriate responses to WhatsApp messages.
                        Keep responses under 200 words, friendly but professional. Consider the message category ({category}) and sentiment ({sentiment})."""
                    },
                    {
                        "role": "user",
                        "content": f"Customer message: '{message_text}'\nGenerate an appropriate response."
                    }
                ],
                max_tokens=300,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"OpenAI response generation error: {e}")
            return None
    
    def _generate_with_template(self, template: str, classification: Dict[str, Any]) -> str:
        """Generate response using template system"""
        try:
            category = classification.get("category", "general")
            
            # Use provided template or get default for category
            if template and template.strip():
                response_template = template
            else:
                # Get random template for the category
                templates = self.response_templates.get(category, self.response_templates["general"])
                response_template = random.choice(templates)
            
            # Replace context variables in template
            response = response_template
            for var, value in self.context_variables.items():
                response = response.replace(f"{{{var}}}", str(value))
            
            # Replace classification-specific variables
            response = response.replace("{category}", category)
            response = response.replace("{sentiment}", classification.get("sentiment", "neutral"))
            response = response.replace("{confidence}", str(classification.get("confidence", 0.0)))
            
            # Replace tag-specific variables
            tags = classification.get("tags", [])
            if tags:
                response = response.replace("{tags}", ", ".join(tags))
                response = response.replace("{first_tag}", tags[0])
            else:
                response = response.replace("{tags}", "")
                response = response.replace("{first_tag}", "")
            
            return response
            
        except Exception as e:
            logger.error(f"Template generation error: {e}")
            return self._get_fallback_response(classification.get("category", "general"))
    
    def _get_fallback_response(self, category: str) -> str:
        """Get a simple fallback response"""
        fallback_responses = {
            "support": "Thank you for contacting support. We'll help you resolve this issue.",
            "sales": "Thank you for your interest! We'll get back to you with the information you need.",
            "inquiry": "Thank you for your question. We'll provide you with the information you need.",
            "complaint": "We apologize for any inconvenience. We take your feedback seriously.",
            "compliment": "Thank you for your positive feedback! We appreciate it.",
            "appointment": "Thank you for wanting to schedule an appointment. We'll help you find a suitable time.",
            "general": "Thank you for your message. How can we assist you today?"
        }
        
        return fallback_responses.get(category, "Thank you for your message. We'll get back to you soon.")
    
    def add_response_template(self, category: str, templates: List[str]):
        """Add custom response templates for a category"""
        if category not in self.response_templates:
            self.response_templates[category] = []
        
        self.response_templates[category].extend(templates)
        logger.info(f"Added {len(templates)} templates for category: {category}")
    
    def update_context_variable(self, key: str, value: str):
        """Update a context variable that can be used in templates"""
        self.context_variables[key] = value
        logger.info(f"Updated context variable: {key} = {value}")
    
    def get_response_templates(self, category: str = None) -> Dict[str, List[str]]:
        """Get response templates for a category or all categories"""
        if category:
            return {category: self.response_templates.get(category, [])}
        return self.response_templates.copy()
    
    async def generate_bulk_responses(
        self, 
        messages: List[Dict[str, Any]], 
        use_ai: bool = False
    ) -> List[str]:
        """Generate responses for multiple messages"""
        responses = []
        
        for msg_data in messages:
            try:
                response = await self.generate_response(
                    msg_data.get("message_text", ""),
                    msg_data.get("template", ""),
                    msg_data.get("classification", {}),
                    use_ai=use_ai
                )
                responses.append(response)
            except Exception as e:
                logger.error(f"Error generating response for message: {e}")
                responses.append(self._get_fallback_response("general"))
        
        return responses
    
    def validate_template(self, template: str) -> Dict[str, Any]:
        """Validate a response template"""
        issues = []
        warnings = []
        
        # Check for valid variables
        variables = re.findall(r'\{([^}]+)\}', template)
        valid_variables = list(self.context_variables.keys()) + [
            "category", "sentiment", "confidence", "tags", "first_tag"
        ]
        
        for var in variables:
            if var not in valid_variables:
                issues.append(f"Unknown variable: {{{var}}}")
        
        # Check template length
        if len(template) > 500:
            warnings.append("Template is quite long (>500 chars). Consider shortening for better user experience.")
        
        if len(template) < 10:
            issues.append("Template is too short. Should be at least 10 characters.")
        
        # Check for basic politeness
        polite_words = ["thank", "please", "sorry", "appreciate", "help", "assist"]
        if not any(word in template.lower() for word in polite_words):
            warnings.append("Template might benefit from more polite language.")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "warnings": warnings,
            "variables_found": variables,
            "length": len(template)
        }
    
    def get_sample_response(self, category: str, use_template: bool = True) -> str:
        """Get a sample response for testing"""
        if use_template:
            templates = self.response_templates.get(category, ["Hello! How can I help you?"])
            return random.choice(templates)
        else:
            # Return a more dynamic sample
            sample_classification = {
                "category": category,
                "confidence": 0.8,
                "sentiment": "neutral",
                "tags": ["sample", "test"]
            }
            return self._generate_with_template("", sample_classification)