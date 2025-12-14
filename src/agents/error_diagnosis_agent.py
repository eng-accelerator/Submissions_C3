import os
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate


class ErrorDiagnosisAgent:
    def __init__(self):
        api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            raise ValueError(
                "OPENROUTER_API_KEY environment variable is not set. "
                "Please set it in your environment or .env file."
            )
        self.llm = ChatOpenAI(
            model="meta-llama/llama-3.1-70b-instruct",
            openai_api_key=api_key,
            openai_api_base="https://openrouter.ai/api/v1"
        )
        self.prompt_template = PromptTemplate.from_template(
            """
        Analyze this Playwright error:
        {stderr}


        Explain what went wrong and suggest a fix.
        """
        )

    def diagnose(self, stderr):
        chain = self.prompt_template | self.llm
        response = chain.invoke({"stderr": stderr})
        return response.content
