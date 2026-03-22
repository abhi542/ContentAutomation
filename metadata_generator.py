import os
import json
import logging
from typing import Dict, List
import openai
import config

logger = logging.getLogger(__name__)

class MetadataGenerator:
    def __init__(self):
        self.api_key = config.OPENAI_API_KEY or config.GROQ_API_KEY
        if not self.api_key:
            logger.warning("No AI API Key found. Metadata generation will fail.")
        
        if config.GROQ_API_KEY:
            self.client = openai.OpenAI(
                api_key=config.GROQ_API_KEY,
                base_url="https://api.groq.com/openai/v1"
            )
        else:
            self.client = openai.OpenAI(api_key=config.OPENAI_API_KEY)

    def generate(self, keyword: str) -> Dict:
        """Generate high-CTR metadata based on a keyword."""
        prompt = f"""
        You are a YouTube Shorts growth expert. Generate viral metadata for a video about: "{keyword}"
        
        CRITICAL RULES FOR TITLES:
        Choose the BEST format from these options:
        1. Question: "Why can’t you stay consistent?"
        2. Bold statement: "Discipline is the real cheat code"
        3. Curiosity gap: "This is why you keep failing"
        4. Emotional trigger: "You’re wasting your potential"
        5. Contrarian: "Motivation is a lie"

        REQUIREMENTS:
        - Max 100 characters for titles.
        - Must include "#shorts".
        - Generate 3-5 variations and select the one with the HIGHEST CTR potential.
        - Description: 1-2 lines reinforcing curiosity/emotion + 2-4 hashtags.
        - Tags: 5-10 relevant keywords.

        OUTPUT FORMAT (JSON ONLY):
        {{
            "best_title": "...",
            "description": "...",
            "tags": ["tag1", "tag2", ...],
            "reasoning": "Why this title was chosen for high CTR"
        }}
        """

        try:
            response = self.client.chat.completions.create(
                model=config.AI_MODEL,
                messages=[
                    {"role": "system", "content": "You are a professional YouTube strategist."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"}
            )
            
            content = response.choices[0].message.content
            metadata = json.loads(content)
            logger.info(f"Generated metadata for '{keyword}': {metadata['best_title']}")
            return metadata
        except Exception as e:
            logger.error(f"Metadata generation failed for {keyword}: {e}")
            return {
                "best_title": f"{keyword.title()} #shorts",
                "description": f"Amazing video about {keyword}. #shorts #trending",
                "tags": [keyword, "shorts", "viral"],
                "reasoning": "Fallback due to API error"
            }

if __name__ == "__main__":
    # Test
    gen = MetadataGenerator()
    print(gen.generate("why you cant focus"))
