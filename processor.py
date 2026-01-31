import vertexai
from vertexai.generative_models import GenerativeModel, Part
import os
import logging

class AIProcessor:
    def __init__(self, project_id, location="asia-southeast1", model_name="gemini-1.5-flash"):
        vertexai.init(project=project_id, location=location)
        self.model = GenerativeModel(model_name)
        self.logger = logging.getLogger(__name__)

    def rewrite_to_myanmar(self, article_text):
        """
        Summarizes and rewrites the English article text into Myanmar language.
        """
        prompt = f"""
        Please summarize the following news article into beautiful, professional, and clear Myanmar language.
        Focus on the most important facts, key people, and the core event.
        The summary should be engaging for a general audience and suitable for a Telegram channel post.
        Use professional Unicode Myanmar font.

        Article Content:
        {article_text}
        
        Myanmar Summary:
        """
        
        try:
            response = self.model.generate_content(prompt)
            if response.text:
                return response.text.strip()
            return None
        except Exception as e:
            self.logger.error(f"Error communicating with Vertex AI: {e}")
            return None
