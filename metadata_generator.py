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
        You are a top 0.1% YouTube Shorts strategist who specializes in creating viral content that maximizes CTR, watch time, shares, and saves.

        Your goal is to generate HIGH-PERFORMANCE metadata for a Short based on this topic:
        "{keyword}"

        ---

        ## 🧠 THINK LIKE A VIRAL CREATOR

        Before generating, internally optimize for:
        - Curiosity gap (viewer MUST feel compelled to click)
        - Emotional trigger (fear, ambition, insecurity, urgency)
        - Relatability (use "you" whenever possible)
        - Pattern interrupt (must stand out in feed)
        - Retention (title should match a strong hook)

        ---

        ## 🎯 TITLE GENERATION

        Generate 5 different title options using DIFFERENT styles:

        1. Question (curiosity-driven)
        2. Bold statement (authoritative)
        3. Curiosity gap (incomplete info)
        4. Emotional/pain trigger
        5. Contrarian/unexpected

        ---

        ## 🔥 TITLE RULES (STRICT)

        - Max 90 characters (shorter = better CTR)
        - MUST include "#shorts"
        - Must feel human, not robotic
        - Avoid generic phrases like "Did you know"
        - Avoid weak words like "tips", "things", "ways"
        - Each title must feel like a HOOK, not a description

        ---

        ## 🧪 SELECTION LOGIC

        From the 5 generated titles:
        - Pick the ONE with highest viral potential based on:
          - curiosity
          - emotional impact
          - relatability
          - scroll-stopping power

        ---

        ## 📝 DESCRIPTION RULES

        - 1–2 lines MAX
        - Reinforce curiosity or emotion
        - DO NOT explain everything (leave open loop)
        - Add 2–4 strong hashtags (not generic spam)

        ---

        ## 🏷️ TAGS RULES

        - 5–10 tags
        - Mix of:
          - niche keywords
          - broad viral tags
        - Keep them short and relevant

        ---

        ## ⚠️ OUTPUT FORMAT (STRICT JSON ONLY)

        Return ONLY valid JSON. No extra text.

        {{
            "title_options": [
                "...",
                "...",
                "...",
                "...",
                "..."
            ],
            "best_title": "...",
            "description": "...",
            "tags": ["...", "..."],
            "reasoning": "Explain why this title will perform best (CTR + retention psychology)"
        }}

        ---

        ## 🚀 EXAMPLE (REFERENCE STYLE)

        Input: "why you cant focus"

        Example Output Style:
        - "Why can’t you focus for 10 minutes? #shorts"
        - "Your focus is being destroyed (here’s why) #shorts"
        - "This is why you’re always distracted #shorts"

        ---

        Now generate the best possible metadata.
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
            
            best_title = metadata.get("best_title", f"{keyword.title()} #shorts")
            options = metadata.get("title_options", [])
            
            logger.info(f"Generated {len(options)} title options for '{keyword}'.")
            for i, opt in enumerate(options, 1):
                logger.info(f"Option {i}: {opt}")
                
            logger.info(f"Selected Best Title: {best_title}")
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
