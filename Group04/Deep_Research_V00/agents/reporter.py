from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from modules.llm_factory import LLMFactory

class ReportAgent:
    """
    Compiles the final research report.
    """
    
    def __init__(self, model_provider="openai"):
        self.llm = LLMFactory.create_llm(model_provider, temperature=0.3)

    def generate_report(self, plan: dict, findings: list, insights: list, sources: list, scope: dict,
                       hypotheses: list = None, implications: list = None, research_questions: list = None,
                       reasoning_chains: list = None, connections: list = None, trends: list = None) -> str:
        """
        Writes the final structured report in Markdown.
        """
        if not self.llm:
            return "## Error: LLM not available for report generation."

        # Format inputs
        findings_str = "\n".join([f"- {f.get('summary', '')}" for f in findings])
        insights_str = "\n".join([f"- {i}" for i in insights])
        hypotheses_str = "\n".join([f"- {h}" for h in (hypotheses or [])])
        reasoning_chains_str = "\n".join([f"- {rc}" for rc in (reasoning_chains or [])])
        connections_str = "\n".join([f"- {c}" for c in (connections or [])])
        implications_str = "\n".join([f"- {i}" for i in (implications or [])])
        trends_str = "\n".join([f"- {t}" for t in (trends or [])])
        research_questions_str = "\n".join([f"- {q}" for q in (research_questions or [])])
        sources_str = "\n".join([f"- {s.get('source', '')} (Score: {s.get('score', 'N/A')})" for s in sources])
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a Professional Research Writer and Report Builder Agent.
            Write a comprehensive, structured research report based on the provided data.
            
            Structure:
            # Executive Summary
            # Research Scope & Assumptions
            (Include: Scope, Assumptions, Limitations, Time Horizon)
            # Top Insights (Key takeaways)
            # Key Findings
            # In-Depth Analysis
            # Hypotheses Generated
            # Multi-Hop Reasoning Chains
            # Connections Between Findings
            # Insights & Implications
            # Trends Identified
            # Contradictions & Validations
            # Research Questions for Future Investigation
            # Uncertainties & Gaps
            # Recommendations / Next Steps (Actionable recommendations based on findings)
            # References & Citations (with credibility scores)
            
            Use professional tone suitable for the discipline.
            Ensure the report is well-structured and comprehensive.
            Include actionable recommendations in the Next Steps section.
            """),
            ("human", """
            Plan: {plan}
            Scope: {scope}
            Findings: {findings}
            Insights: {insights}
            Hypotheses: {hypotheses}
            Reasoning Chains: {reasoning_chains}
            Connections: {connections}
            Implications: {implications}
            Trends: {trends}
            Research Questions: {research_questions}
            Sources: {sources}
            """)
        ])

        chain = prompt | self.llm | StrOutputParser()
        
        try:
            report_markdown = chain.invoke({
                "plan": str(plan),
                "scope": str(scope),
                "findings": findings_str,
                "insights": insights_str,
                "hypotheses": hypotheses_str,
                "reasoning_chains": reasoning_chains_str,
                "connections": connections_str,
                "implications": implications_str,
                "trends": trends_str,
                "research_questions": research_questions_str,
                "sources": sources_str
            })
            return report_markdown
        except Exception as e:
            return f"## Error Generating Report\n{e}"
