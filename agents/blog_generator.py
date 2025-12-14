import os
import openai
import config
import logging

logger = logging.getLogger(__name__)

class BlogGeneratorAgent:
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
        else:
            logger.warning("API Key not found. Blog generation will be simulated or fail.")

    def generate_blog(self, article_data: dict) -> str:
        """
        Uses LLM to summarize and rewrite the article as a blog post.
        """
        if not self.client:
            logger.error("OpenAI client not initialized.")
            return "Error: OpenAI API Key missing. Please set OPENAI_API_KEY in .env file."

        headline = article_data.get('headline', 'No Title')
        body = article_data.get('body', '')

        if not body:
            return "Error: No content to process."

        logger.info(f"Generating blog post for: {headline}...")

        system_prompt = (
            "You are an expert tech blogger for a popular tech news site. "
            "Your goal is to transform raw news articles into engaging, well-structured blog posts."
        )

        user_prompt = f"""
        Please write a comprehensive blog post based on the following news article.

        SOURCE ARTICLE TITLE: {headline}
        
        SOURCE ARTICLE CONTENT:
        {body[:8000]}  # Truncate to avoid token limits if article is huge
        
        INSTRUCTIONS:
        1. create a catchy, new title for the blog post.
        2. Start with a 'Key Takeaways' section (bullet points).
        3. Write an engaging Introduction that hooks the reader.
        4. Rewrite the main body of the news in your own words, organizing with properties headers.
        5. Add a Conclusion that speculates on the future impact of this news.
        6. logic: If the article mentions code or technical details, simplify them for a general tech audience.
        7. Format: Use Markdown (H1, H2, bullet points, bold text).
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
                # OpenRouter specific headers (optional but good practice)
                extra_headers={
                   "HTTP-Referer": "https://localhost:3000", # Required by OpenRouter for ranking
                   "X-Title": "Browser Automation Agent"
                } if config.OPENROUTER_API_KEY else None
            )
            
            blog_content = response.choices[0].message.content
            logger.info("Blog post generated successfully.")
            return blog_content

        except Exception as e:
            logger.error(f"LLM Generation failed: {e}")
            return f"Error generation blog post: {str(e)}"
