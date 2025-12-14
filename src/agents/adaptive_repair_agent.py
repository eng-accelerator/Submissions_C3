import os
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from src.automation.script_templates.base_script import generate_base_playwright_script


class AdaptiveRepairAgent:
    def __init__(self):
        api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            raise ValueError(
                "OPENROUTER_API_KEY environment variable is not set. "
                "Please set it in your environment or .env file."
            )
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",
            openai_api_key=api_key,
            openai_api_base="https://openrouter.ai/api/v1"
        )
        self.prompt_template = PromptTemplate.from_template(
            """
        Original Playwright code:
        {original_script}


        Diagnosis:
        {diagnosis}


        Regenerate a corrected Playwright script.
        """
        )

    def repair(self, original_script, diagnosis):
        chain = self.prompt_template | self.llm
        response = chain.invoke({"original_script": original_script, "diagnosis": diagnosis})
        lines = response.content.split("\n")
        return generate_base_playwright_script(lines)
