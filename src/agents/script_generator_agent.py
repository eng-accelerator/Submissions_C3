import os
import re
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from src.automation.script_templates.base_script import generate_base_playwright_script


class ScriptGeneratorAgent:
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
        self.prompt_template = PromptTemplate.from_template(
            """Convert this flow description into Playwright Python code steps:

{flow_description}

You MUST output ONLY Python Playwright code statements, one per line. Each line should be a valid Playwright command like:
- await page.goto("url")
- await page.fill("selector", "value")
- await page.click("selector")
- await page.wait_for_selector("selector")

Do not include any explanations, comments, or markdown formatting. Output only the code statements."""
        )

    def generate_script(self, flow_description):
        chain = self.prompt_template | self.llm
        response = chain.invoke({"flow_description": flow_description})
        content = response.content

        # Extract code from markdown code blocks if present
        code_match = re.search(
            r'```(?:python)?\s*(.*?)\s*```', content, re.DOTALL)
        if code_match:
            content = code_match.group(1)

        # Split into lines and filter out empty lines and comments
        steps = [line.strip() for line in content.split("\n")
                 if line.strip() and not line.strip().startswith("#")]

        return generate_base_playwright_script(steps)
