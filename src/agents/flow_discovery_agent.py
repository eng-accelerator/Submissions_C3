import os
import json
import re
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate


class FlowDiscoveryAgent:
    def __init__(self):
        api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            raise ValueError(
                "OPENROUTER_API_KEY environment variable is not set. "
                "Please set it in your environment or .env file."
            )
        self.llm = ChatOpenAI(
            model="anthropic/claude-3.5-sonnet",
            openai_api_key=api_key,
            openai_api_base="https://openrouter.ai/api/v1",
            temperature=0.3
        )

    def _extract_json(self, text):
        """Extract JSON from text, handling markdown code blocks and nested structures."""
        # Try to find JSON in markdown code blocks first
        json_match = re.search(
            r'```(?:json)?\s*(\[.*?\]|\{.*?\})\s*```', text, re.DOTALL)
        if json_match:
            return json_match.group(1).strip()

        # Try to find JSON array (balanced brackets)
        bracket_count = 0
        start_idx = text.find('[')
        if start_idx != -1:
            for i in range(start_idx, len(text)):
                if text[i] == '[':
                    bracket_count += 1
                elif text[i] == ']':
                    bracket_count -= 1
                    if bracket_count == 0:
                        return text[start_idx:i+1].strip()

        # Try to find JSON object (balanced braces)
        brace_count = 0
        start_idx = text.find('{')
        if start_idx != -1:
            for i in range(start_idx, len(text)):
                if text[i] == '{':
                    brace_count += 1
                elif text[i] == '}':
                    brace_count -= 1
                    if brace_count == 0:
                        return text[start_idx:i+1].strip()

        # Fallback: return original text
        return text.strip()

    def _fetch_webpage_content(self, url):
        """Fetch and extract relevant content from a webpage using Playwright."""
        print(f"[DEBUG] _fetch_webpage_content called with URL: {url}")
        try:
            print(f"[DEBUG] Starting Playwright browser...")
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                print(f"[DEBUG] Browser launched, navigating to {url}...")

                # Navigate to the page and wait for it to load
                page.goto(url, wait_until="networkidle", timeout=30000)
                print(f"[DEBUG] Page loaded successfully")

                # Wait a bit for any dynamic content
                page.wait_for_timeout(2000)

                # Get the HTML content
                html_content = page.content()

                # Get visible text content
                visible_text = page.evaluate("""
                    () => {
                        // Get all visible text
                        const walker = document.createTreeWalker(
                            document.body,
                            NodeFilter.SHOW_TEXT,
                            null,
                            false
                        );
                        let text = [];
                        let node;
                        while (node = walker.nextNode()) {
                            const parent = node.parentElement;
                            if (parent && 
                                parent.offsetParent !== null && 
                                !parent.closest('script, style, noscript')) {
                                const trimmed = node.textContent.trim();
                                if (trimmed) text.push(trimmed);
                            }
                        }
                        return text.join('\\n');
                    }
                """)

                # Extract interactive elements
                interactive_elements = page.evaluate("""
                    () => {
                        const elements = [];
                        
                        // Forms
                        document.querySelectorAll('form').forEach(form => {
                            const inputs = Array.from(form.querySelectorAll('input, select, textarea'))
                                .map(el => ({
                                    type: el.type || el.tagName.toLowerCase(),
                                    name: el.name || '',
                                    placeholder: el.placeholder || '',
                                    label: el.labels?.[0]?.textContent || ''
                                }));
                            elements.push({
                                type: 'form',
                                action: form.action || '',
                                method: form.method || 'get',
                                inputs: inputs
                            });
                        });
                        
                        // Buttons and links
                        document.querySelectorAll('button, a[href], input[type="submit"], input[type="button"]').forEach(el => {
                            const text = el.textContent?.trim() || el.value || el.getAttribute('aria-label') || '';
                            if (text) {
                                elements.push({
                                    type: el.tagName.toLowerCase(),
                                    text: text,
                                    href: el.href || '',
                                    onclick: el.onclick ? 'has onclick' : ''
                                });
                            }
                        });
                        
                        return elements;
                    }
                """)

                browser.close()

                # Parse HTML with BeautifulSoup to extract structure
                soup = BeautifulSoup(html_content, 'html.parser')

                # Remove script and style elements
                for script in soup(["script", "style", "noscript", "meta"]):
                    script.decompose()

                # Get clean HTML structure (limited to body)
                body_content = soup.find('body')
                clean_html = str(body_content) if body_content else str(soup)

                # Limit content size to avoid token limits (keep first 50000 chars)
                if len(clean_html) > 50000:
                    clean_html = clean_html[:50000] + "... [truncated]"

                result = {
                    # Limit HTML to 20k chars
                    "html_structure": clean_html[:20000],
                    # Limit text to 10k chars
                    "visible_text": visible_text[:10000],
                    "interactive_elements": interactive_elements,
                    "title": soup.find('title').get_text() if soup.find('title') else ""
                }
                print(
                    f"[DEBUG] Successfully extracted content: title='{result['title']}', {len(interactive_elements)} interactive elements")
                return result
        except Exception as e:
            # If scraping fails, return None and fall back to URL-only analysis
            print(
                f"[DEBUG] ERROR in _fetch_webpage_content: {type(e).__name__}: {str(e)}")
            import traceback
            print(f"[DEBUG] Traceback:\n{traceback.format_exc()}")
            return None

    def discover(self, url):
        # Fetch webpage content
        page_content = self._fetch_webpage_content(url)

        # Debug: Check if page_content was fetched
        print(f"[DEBUG] page_content is None: {page_content is None}")
        if page_content:
            print(f"[DEBUG] page_content keys: {list(page_content.keys())}")
            print(
                f"[DEBUG] interactive_elements count: {len(page_content.get('interactive_elements', []))}")
            print(
                f"[DEBUG] interactive_elements (first 3): {page_content.get('interactive_elements', [])[:3]}")

        # Build prompt template with actual page content if available
        if page_content:
            interactive_elements = page_content.get('interactive_elements', [])
            print(
                f"[DEBUG] Processing {len(interactive_elements)} interactive elements")

            interactive_summary = "\n".join([
                f"- {elem.get('type', 'element')}: {elem.get('text', elem.get('action', ''))}"
                # Limit to 50 elements
                for elem in interactive_elements[:50]
            ])

            print(
                f"[DEBUG] interactive_summary length: {len(interactive_summary)}")
            print(
                f"[DEBUG] interactive_summary preview (first 500 chars): {interactive_summary[:500]}")

            prompt_template = PromptTemplate.from_template(
                """I have extracted the following content from the webpage at {url}. Based on this actual page content, identify the most important user flows (login, signup, checkout, search, etc.).

Page Title: {title}

Interactive Elements Found:
{interactive_summary}

Visible Text Content (sample):
{visible_text}

HTML Structure (key elements):
{html_structure}

Using the above extracted content, identify the user flows that exist on this page.

You MUST respond with ONLY a valid JSON array. Each item should be a flow object with:
- "name": string (e.g., "Login", "Signup", "Checkout")
- "description": string (brief description of the flow)
- "steps": array of strings (list of steps in the flow)

Example format:
[
  {{
    "name": "Login",
    "description": "User authentication flow",
    "steps": ["Navigate to login page", "Enter credentials", "Click login button"]
  }},
  {{
    "name": "Search",
    "description": "Product search functionality",
    "steps": ["Enter search query", "Click search button", "View results"]
  }}
]

Respond with ONLY the JSON array, no additional text or explanation."""
            )

            print(
                f"[DEBUG] Using page_content-based prompt")

            chain = prompt_template | self.llm
            response = chain.invoke({
                "url": url,
                "title": page_content.get('title', 'N/A'),
                "interactive_summary": interactive_summary,
                "visible_text": page_content.get('visible_text', '')[:3000],
                "html_structure": page_content.get('html_structure', '')[:5000]
            })
        else:
            # Fallback to URL-only analysis if scraping fails
            print(
                f"[DEBUG] page_content is None or empty, using fallback URL-only prompt")

            prompt_template = PromptTemplate.from_template(
                """Analyze the webpage at {url} and identify the most important user flows (login, signup, checkout, search, etc.).

Note: Unable to fetch actual page content. Base your analysis on the URL structure and common patterns.

You MUST respond with ONLY a valid JSON array. Each item should be a flow object with:
- "name": string (e.g., "Login", "Signup", "Checkout")
- "description": string (brief description of the flow)
- "steps": array of strings (list of steps in the flow)

Example format:
[
  {{
    "name": "Login",
    "description": "User authentication flow",
    "steps": ["Navigate to login page", "Enter credentials", "Click login button"]
  }},
  {{
    "name": "Search",
    "description": "Product search functionality",
    "steps": ["Enter search query", "Click search button", "View results"]
  }}
]

Respond with ONLY the JSON array, no additional text or explanation."""
            )

            chain = prompt_template | self.llm
            response = chain.invoke({"url": url})

        content = response.content

        # Extract and parse JSON
        try:
            json_text = self._extract_json(content)
            flows = json.loads(json_text)
            return {"flows": flows, "url": url}
        except json.JSONDecodeError:
            # If JSON parsing fails, return error structure
            return {
                "error": "Failed to parse JSON response",
                "raw_response": content,
                "url": url
            }
