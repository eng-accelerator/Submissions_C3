from bs4 import BeautifulSoup
import logging

logger = logging.getLogger(__name__)

class ContentExtractionAgent:
    def extract(self, html_content: str) -> dict:
        """
        Parses HTML content to extract headline and body text.
        """
        try:
            logger.info("Extracting content from HTML...")
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Extract Headline
            # TechCrunch uses h1 for titles
            headline_tag = soup.find('h1')
            headline = headline_tag.get_text(strip=True) if headline_tag else "Untitled Article"
            
            # Extract Body Content
            # Attempt to target the main article container to avoid footer/sidebar noise
            # TechCrunch selector structure often involves 'wp-block-post-content' or legacy class names
            # We will try a few likely candidates or fallback to broad p tag collection.
            
            article_body = (
                soup.find('div', class_='wp-block-post-content') or
                soup.find('div', class_='entry-content') or
                soup.find('div', class_='article-content') or 
                soup.find('article')
            )
            
            content_text = ""
            
            if article_body:
                # Extract text from paragraphs within the identified body
                paragraphs = article_body.find_all('p')
                # Filter out empty or navigational paragraphs often found in these blocks
                valid_paragraphs = [p.get_text(strip=True) for p in paragraphs if len(p.get_text(strip=True)) > 20]
                content_text = "\n\n".join(valid_paragraphs)
            else:
                logger.warning("Could not identify specific article body container. using fallback extraction.")
                # Fallback: Find all paragraphs in the document, heuristic filtering
                all_ps = soup.find_all('p')
                valid_paragraphs = [p.get_text(strip=True) for p in all_ps if len(p.get_text(strip=True)) > 50]
                content_text = "\n\n".join(valid_paragraphs)

            if not content_text:
                logger.warning("No content extracted!")

            logger.info(f"Extracted article: {headline} ({len(content_text)} chars)")
            
            return {
                "headline": headline,
                "body": content_text,
                "raw_html": html_content[:500] + "..." # Snippet for debug
            }

        except Exception as e:
            logger.error(f"Extraction failed: {e}")
            raise
