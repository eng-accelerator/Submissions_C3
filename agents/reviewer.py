import openai
import config
import logging

logger = logging.getLogger(__name__)

class ReviewerAgent:
    def __init__(self):
        self.api_key = config.OPENROUTER_API_KEY or config.OPENAI_API_KEY
        self.base_url = "https://openrouter.ai/api/v1" if config.OPENROUTER_API_KEY else None
        self.client = None
        
        if self.api_key:
            try:
                self.client = openai.OpenAI(
                    api_key=self.api_key,
                    base_url=self.base_url
                )
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI client: {e}")

    def review(self, draft: str, topic: str = "") -> str:
        """
        Reviews and polished the blog draft.
        """
        if not self.client:
           logger.warning("No API key for reviewer.")
           return draft + "\n\n[Review skipped due to missing API key]"

        logger.info("Reviewing draft...")
        
        system_prompt = "You are a senior editor. Your job is to critique and polish blog posts to be professional, engaging, and error-free."
        user_prompt = f"""
        Please review and polish the following blog draft about '{topic}'.
        
        DRAFT:
        {draft}
        
        INSTRUCTIONS:
        1. Fix any grammar or spelling errors.
        2. Improve flow and readability.
        3. Ensure the tone is consistent and professional (Pro Level).
        4. Return the Polished Version ONLY (do not output your critique thoughts, just the final text).
        """
        
        try:
            model_name = "openai/gpt-4o-mini" if config.OPENROUTER_API_KEY else "gpt-4"
            
            response = self.client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                extra_headers={
                   "HTTP-Referer": "https://localhost:3000",
                   "X-Title": "Browser Automation Agent"
                } if config.OPENROUTER_API_KEY else None
            )
            
            polished_content = response.choices[0].message.content
            logger.info("Review complete.")
            return polished_content
        except Exception as e:
            logger.error(f"Review failed: {e}")
            return draft # Return original if review fails
