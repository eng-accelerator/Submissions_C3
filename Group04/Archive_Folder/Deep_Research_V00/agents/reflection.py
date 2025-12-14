from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from modules.llm_factory import LLMFactory

class ReflectionValidation(BaseModel):
    is_sufficient: bool = Field(description="True if the research answers the main objective completely.")
    missing_information: list[str] = Field(description="List of specific gaps if incomplete.")
    follow_up_queries: list[str] = Field(description="New queries to run if incomplete.")

class ReflectionAgent:
    """
    Evaluates if the research is complete or needs iteration.
    """
    
    def __init__(self, model_provider="openai"):
        self.llm = LLMFactory.create_llm(model_provider, temperature=0.1)
        self.parser = PydanticOutputParser(pydantic_object=ReflectionValidation)

    def reflect(self, current_findings: list, original_plan: dict) -> ReflectionValidation:
        """
        Check if we have answered the main objective.
        """
        if not self.llm:
            return ReflectionValidation(is_sufficient=True, missing_information=[], follow_up_queries=[])

        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a Research Manager.
            Review the findings against the original plan.
            Determine if the main objective is fully satisfied.
            If not, generate follow-up queries.
            
            Result must be valid JSON matching the schema.
            """),
            ("human", """
            Original Objective: {objective}
            Scope: {scope}
            Current Findings: {findings}
            """)
        ])

        chain = prompt | self.llm | self.parser
        
        try:
            result = chain.invoke({
                "objective": original_plan.get("main_objective", ""),
                "scope": original_plan.get("scope_and_assumptions", ""),
                "findings": str(current_findings)
            })
            return result
        except Exception:
            # On error, assume sufficient to avoid infinite loops in demo
            return ReflectionValidation(is_sufficient=True, missing_information=[], follow_up_queries=[])
