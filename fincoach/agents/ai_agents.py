"""
AI Financial Coach Agents System
Multi-agent orchestration for financial advisory
Compatible with existing fincoach project structure
"""

import os
from typing import Dict, List, Any, Optional
from datetime import datetime
import json
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from database.db_manager import DBManager

class BaseFinancialAgent:
    """Base class for all financial agents"""
    
    def __init__(self, agent_name: str, model_name: str = "gpt-4", openrouter_api_key: str = None):
        self.agent_name = agent_name
        self.db = DBManager()
        
        # Initialize OpenRouter LLM
        self.llm = ChatOpenAI(
            model=model_name,
            openai_api_key=openrouter_api_key,
            openai_api_base="https://openrouter.ai/api/v1",
            default_headers={
                "HTTP-Referer": "https://fincoach.app",
                "X-Title": "AI Financial Coach"
            },
            temperature=0.7,
            max_tokens=2000
        )
    
    def get_user_context(self, user_id: int) -> Dict[str, Any]:
        """Get comprehensive user financial context"""
        user = self.db.get_user_by_id(user_id)
        
        # Get financial data
        expenses = self.db.get_financial_data(user_id, data_type='expense')
        income = self.db.get_financial_data(user_id, data_type='income')
        debts = self.db.get_financial_data(user_id, data_type='debt')
        investments = self.db.get_financial_data(user_id, data_type='investment')
        
        # Get documents
        documents = self.db.get_user_documents(user_id)
        
        return {
            'user': {
                'id': user.id,
                'name': user.full_name or user.username,
                'monthly_income': user.monthly_income or 0,
                'age': user.age or 30,
                'dependents': user.dependents or 0,
                'city': user.city or 'India',
                'occupation': user.occupation or 'Professional'
            },
            'financial_summary': {
                'total_expenses': sum(e.amount for e in expenses),
                'total_income': sum(i.amount for i in income),
                'total_debt': sum(d.amount for d in debts),
                'total_investments': sum(inv.amount for inv in investments),
                'expense_categories': self._categorize_transactions(expenses),
                'debt_items': [{'category': d.category, 'amount': d.amount, 'description': d.description} for d in debts]
            },
            'documents': {
                'has_salary_slip': user.has_salary_slip,
                'has_bank_statement': user.has_bank_statement,
                'has_loan_data': user.has_loan_data,
                'has_credit_card_statement': user.has_credit_card_statement,
                'has_collateral_details': user.has_collateral_details,
                'uploaded_count': len(documents)
            }
        }
    
    def _categorize_transactions(self, transactions: List) -> Dict[str, float]:
        """Categorize transactions by category"""
        categories = {}
        for txn in transactions:
            cat = txn.category or 'Other'
            categories[cat] = categories.get(cat, 0) + txn.amount
        return categories
    
    def process_query(self, user_id: int, query: str, context: str = "") -> str:
        """Process query with agent - to be overridden by subclasses"""
        raise NotImplementedError("Subclasses must implement process_query")


class DebtAnalyzerAgent(BaseFinancialAgent):
    """Agent specialized in debt analysis and payoff strategies"""
    
    def __init__(self, openrouter_api_key: str = None):
        super().__init__("DebtAnalyzer", "anthropic/claude-3.5-sonnet", openrouter_api_key)
    
    def process_query(self, user_id: int, query: str, context: str = "") -> str:
        """Analyze user's debt and provide payoff strategies"""
        user_context = self.get_user_context(user_id)
        
        system_prompt = f"""You are an expert Debt Analysis Agent for AI Financial Coach.

USER PROFILE:
- Name: {user_context['user']['name']}
- Monthly Income: ₹{user_context['user']['monthly_income']:,.2f}
- Age: {user_context['user']['age']}
- Dependents: {user_context['user']['dependents']}
- Location: {user_context['user']['city']}

FINANCIAL SUMMARY:
- Total Debt: ₹{user_context['financial_summary']['total_debt']:,.2f}
- Monthly Expenses: ₹{user_context['financial_summary']['total_expenses']:,.2f}
- Monthly Income: ₹{user_context['financial_summary']['total_income']:,.2f}

DEBT BREAKDOWN:
{json.dumps(user_context['financial_summary']['debt_items'], indent=2)}

ADDITIONAL CONTEXT FROM DOCUMENTS:
{context}

Your task is to:
1. Analyze the user's debt situation comprehensively
2. Identify high-interest debts and prioritize them
3. Suggest debt payoff strategies (Snowball vs Avalanche method)
4. Create a realistic timeline for debt freedom
5. Recommend budget adjustments to accelerate debt payoff
6. Provide psychological support and motivation

Be empathetic, practical, and specific. Use Indian financial context (₹ INR).
"""
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=query)
        ]
        
        response = self.llm.invoke(messages)
        return response.content


class SavingsStrategyAgent(BaseFinancialAgent):
    """Agent specialized in savings strategies and wealth building"""
    
    def __init__(self, openrouter_api_key: str = None):
        super().__init__("SavingsStrategy", "anthropic/claude-3.5-sonnet", openrouter_api_key)
    
    def process_query(self, user_id: int, query: str, context: str = "") -> str:
        """Create personalized savings strategies"""
        user_context = self.get_user_context(user_id)
        
        # Calculate savings potential
        monthly_income = user_context['user']['monthly_income'] or 0
        monthly_expenses = user_context['financial_summary']['total_expenses']
        savings_potential = monthly_income - monthly_expenses
        savings_rate = (savings_potential / monthly_income * 100) if monthly_income > 0 else 0
        
        system_prompt = f"""You are an expert Savings Strategy Agent for AI Financial Coach.

USER PROFILE:
- Name: {user_context['user']['name']}
- Monthly Income: ₹{monthly_income:,.2f}
- Current Savings Potential: ₹{savings_potential:,.2f}/month ({savings_rate:.1f}%)
- Age: {user_context['user']['age']}
- Occupation: {user_context['user']['occupation']}

EXPENSE BREAKDOWN:
{json.dumps(user_context['financial_summary']['expense_categories'], indent=2)}

ADDITIONAL CONTEXT:
{context}

Your task is to:
1. Analyze current savings rate and potential
2. Suggest realistic savings goals (Emergency fund, retirement, specific goals)
3. Recommend expense optimization strategies
4. Propose automated savings mechanisms
5. Suggest appropriate savings instruments (FD, RD, PPF, Mutual Funds)
6. Create a phased savings plan (3-month, 6-month, 1-year targets)

Use the 50-30-20 rule and Indian financial products. Be specific and actionable.
"""
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=query)
        ]
        
        response = self.llm.invoke(messages)
        return response.content


class InvestmentAdvisorAgent(BaseFinancialAgent):
    """Agent specialized in investment portfolio building"""
    
    def __init__(self, openrouter_api_key: str = None):
        super().__init__("InvestmentAdvisor", "anthropic/claude-3.5-sonnet", openrouter_api_key)
    
    def process_query(self, user_id: int, query: str, context: str = "") -> str:
        """Build personalized investment portfolio"""
        user_context = self.get_user_context(user_id)
        
        system_prompt = f"""You are an expert Investment Advisory Agent for AI Financial Coach.

USER PROFILE:
- Name: {user_context['user']['name']}
- Age: {user_context['user']['age']}
- Monthly Income: ₹{user_context['user']['monthly_income']:,.2f}
- Current Investments: ₹{user_context['financial_summary']['total_investments']:,.2f}
- Risk Profile: {'Conservative' if user_context['user']['age'] > 45 else 'Moderate' if user_context['user']['age'] > 30 else 'Aggressive'}

FINANCIAL POSITION:
- Available for Investment: Calculate based on income - expenses - debt payments
- Existing Debt: ₹{user_context['financial_summary']['total_debt']:,.2f}

ADDITIONAL CONTEXT:
{context}

Your task is to:
1. Assess risk tolerance based on age, income, and goals
2. Recommend asset allocation (Equity, Debt, Gold, Real Estate)
3. Suggest specific investment products (Mutual Funds, Stocks, ETFs, Bonds)
4. Create diversified portfolio recommendation
5. Explain investment strategy and expected returns
6. Suggest SIP amounts and frequency
7. Address tax optimization (80C, ELSS, etc.)

Use Indian investment products and tax laws. Be specific with fund names and allocation percentages.
"""
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=query)
        ]
        
        response = self.llm.invoke(messages)
        return response.content


class BudgetPlannerAgent(BaseFinancialAgent):
    """Agent specialized in budget planning and optimization"""
    
    def __init__(self, openrouter_api_key: str = None):
        super().__init__("BudgetPlanner", "anthropic/claude-3.5-sonnet", openrouter_api_key)
    
    def process_query(self, user_id: int, query: str, context: str = "") -> str:
        """Create optimized budget plans"""
        user_context = self.get_user_context(user_id)
        
        system_prompt = f"""You are an expert Budget Planning Agent for AI Financial Coach.

USER PROFILE:
- Monthly Income: ₹{user_context['user']['monthly_income']:,.2f}
- Dependents: {user_context['user']['dependents']}
- Location: {user_context['user']['city']}

CURRENT SPENDING:
{json.dumps(user_context['financial_summary']['expense_categories'], indent=2)}

ADDITIONAL CONTEXT:
{context}

Your task is to:
1. Analyze current spending patterns
2. Identify areas of overspending
3. Create a 50-30-20 budget framework (Needs-Wants-Savings)
4. Suggest specific cost-cutting measures
5. Provide category-wise budget recommendations
6. Create actionable monthly budget template
7. Set up spending alerts and checkpoints

Be practical and considerate of Indian lifestyle and costs.
"""
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=query)
        ]
        
        response = self.llm.invoke(messages)
        return response.content


class RetirementPlannerAgent(BaseFinancialAgent):
    """Agent specialized in retirement planning"""
    
    def __init__(self, openrouter_api_key: str = None):
        super().__init__("RetirementPlanner", "anthropic/claude-3.5-sonnet", openrouter_api_key)
    
    def process_query(self, user_id: int, query: str, context: str = "") -> str:
        """Create retirement plans"""
        user_context = self.get_user_context(user_id)
        
        age = user_context['user']['age'] or 30
        retirement_age = 60
        years_to_retirement = max(retirement_age - age, 0)
        
        system_prompt = f"""You are an expert Retirement Planning Agent for AI Financial Coach.

USER PROFILE:
- Current Age: {age}
- Years to Retirement: {years_to_retirement}
- Monthly Income: ₹{user_context['user']['monthly_income']:,.2f}
- Current Investments: ₹{user_context['financial_summary']['total_investments']:,.2f}

ADDITIONAL CONTEXT:
{context}

Your task is to:
1. Calculate retirement corpus needed (considering inflation at 6%)
2. Assess current retirement readiness
3. Recommend retirement savings instruments (PPF, NPS, EPF, Mutual Funds)
4. Create monthly investment plan to meet retirement goals
5. Suggest early retirement options if applicable
6. Plan for healthcare costs in retirement
7. Provide milestone-based targets

Consider Indian retirement products and inflation rates.
"""
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=query)
        ]
        
        response = self.llm.invoke(messages)
        return response.content


class AgentOrchestrator:
    """Orchestrate multiple agents based on user query"""
    
    def __init__(self, openrouter_api_key: str):
        self.openrouter_api_key = openrouter_api_key
        
        # Initialize all agents
        self.agents = {
            'debt_analyzer': DebtAnalyzerAgent(openrouter_api_key),
            'savings_strategy': SavingsStrategyAgent(openrouter_api_key),
            'investment_advisor': InvestmentAdvisorAgent(openrouter_api_key),
            'budget_planner': BudgetPlannerAgent(openrouter_api_key),
            'retirement_planner': RetirementPlannerAgent(openrouter_api_key)
        }
        
        # Router LLM to determine which agent to use
        self.router_llm = ChatOpenAI(
            model="anthropic/claude-3.5-sonnet",
            openai_api_key=openrouter_api_key,
            openai_api_base="https://openrouter.ai/api/v1",
            default_headers={
                "HTTP-Referer": "https://fincoach.app",
                "X-Title": "AI Financial Coach"
            },
            temperature=0.3
        )
    
    def route_query(self, query: str) -> str:
        """Determine which agent should handle the query"""
        routing_prompt = f"""Analyze this financial query and determine which specialized agent should handle it.

Query: "{query}"

Available Agents:
- debt_analyzer: For debt analysis, payoff strategies, debt consolidation
- savings_strategy: For savings plans, emergency funds, expense optimization
- investment_advisor: For investment portfolios, asset allocation, mutual funds, stocks
- budget_planner: For budget creation, expense tracking, spending optimization
- retirement_planner: For retirement planning, early retirement, pension planning

Respond with ONLY the agent name (e.g., "debt_analyzer"). If multiple agents are needed, list them separated by commas.
"""
        
        response = self.router_llm.invoke([HumanMessage(content=routing_prompt)])
        agent_names = response.content.strip().lower()
        
        # Return first agent if multiple
        if ',' in agent_names:
            return agent_names.split(',')[0].strip()
        
        return agent_names if agent_names in self.agents else 'budget_planner'
    
    def process_query(self, user_id: int, query: str, context: str = "", 
                     specific_agent: str = None) -> Dict[str, Any]:
        """Process query through appropriate agent(s)"""
        try:
            # Route to specific agent or auto-route
            agent_name = specific_agent if specific_agent else self.route_query(query)
            
            # Get the agent
            agent = self.agents.get(agent_name, self.agents['budget_planner'])
            
            # Process query
            response = agent.process_query(user_id, query, context)
            
            return {
                'success': True,
                'agent': agent_name,
                'response': response,
                'timestamp': datetime.utcnow().isoformat()
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'agent': agent_name if 'agent_name' in locals() else 'unknown',
                'response': f"I apologize, but I encountered an error processing your request: {str(e)}. Please try again or rephrase your question."
            }
