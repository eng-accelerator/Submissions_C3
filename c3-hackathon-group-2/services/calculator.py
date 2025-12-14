"""
Financial calculator service for metrics and analysis.

Implements deterministic financial calculations:
- Net worth (assets - liabilities)
- Savings rate ((income - expenses) / income)
- Debt-to-income ratio
- Emergency fund coverage (months)
- Debt health scoring

All calculations are versioned and deterministic for auditability.
"""
from typing import Dict, Any, List
from decimal import Decimal


class FinancialCalculator:
    """Deterministic financial calculations service."""
    
    VERSION = "1.0.0"  # Version for audit trail
    
    @staticmethod
    def calculate_net_worth(assets: List[Dict], liabilities: List[Dict], current_savings: float = 0) -> float:
        """
        Calculate net worth.
        
        Net Worth = Total Assets - Total Liabilities
        
        Args:
            assets: List of asset dictionaries with 'value' key
            liabilities: List of liability dictionaries with 'outstanding' key
            current_savings: Additional savings amount
            
        Returns:
            Net worth value
        """
        total_assets = sum(a.get('value', 0) for a in assets) + current_savings
        total_liabilities = sum(l.get('outstanding', 0) for l in liabilities)
        
        return total_assets - total_liabilities
    
    @staticmethod
    def calculate_savings_rate(monthly_income: float, monthly_expenses: float) -> float:
        """
        Calculate savings rate as percentage.
        
        Savings Rate = ((Income - Expenses) / Income) * 100
        
        Args:
            monthly_income: Monthly income
            monthly_expenses: Monthly expenses
            
        Returns:
            Savings rate percentage (0-100)
        """
        if monthly_income <= 0:
            return 0.0
        
        surplus = monthly_income - monthly_expenses
        savings_rate = (surplus / monthly_income) * 100
        
        return max(0, min(100, savings_rate))  # Clamp between 0-100
    
    @staticmethod
    def calculate_emergency_fund_months(current_savings: float, monthly_expenses: float) -> float:
        """
        Calculate emergency fund coverage in months.
        
        Args:
            current_savings: Current savings amount
            monthly_expenses: Monthly expenses
            
        Returns:
            Number of months covered
        """
        if monthly_expenses <= 0:
            return 0.0
        
        return current_savings / monthly_expenses
    
    @staticmethod
    def calculate_debt_to_income_ratio(total_debt: float, monthly_income: float) -> float:
        """
        Calculate debt-to-income ratio.
        
        DTI = (Total Debt / (Monthly Income * 12)) * 100
        
        Args:
            total_debt: Total outstanding debt
            monthly_income: Monthly income
            
        Returns:
            DTI ratio as percentage
        """
        if monthly_income <= 0:
            return 0.0
        
        annual_income = monthly_income * 12
        dti = (total_debt / annual_income) * 100
        
        return dti
    
    @staticmethod
    def analyze_financial_health(snapshot: Dict, assets: List[Dict], liabilities: List[Dict]) -> Dict[str, Any]:
        """
        Comprehensive financial health analysis.
        
        Args:
            snapshot: Financial snapshot with income/expenses/savings
            assets: List of assets
            liabilities: List of liabilities
            
        Returns:
            Dictionary with all calculated metrics and health scores
        """
        monthly_income = snapshot.get('monthly_income', 0)
        monthly_expenses = snapshot.get('monthly_expenses', 0)
        current_savings = snapshot.get('current_savings', 0)
        
        total_assets = sum(a.get('value', 0) for a in assets) + current_savings
        total_liabilities = sum(l.get('outstanding', 0) for l in liabilities)
        
        # Calculate metrics
        net_worth = FinancialCalculator.calculate_net_worth(assets, liabilities, current_savings)
        savings_rate = FinancialCalculator.calculate_savings_rate(monthly_income, monthly_expenses)
        emergency_months = FinancialCalculator.calculate_emergency_fund_months(current_savings, monthly_expenses)
        dti_ratio = FinancialCalculator.calculate_debt_to_income_ratio(total_liabilities, monthly_income)
        monthly_surplus = monthly_income - monthly_expenses
        
        # Health scores (0-100)
        emergency_score = min(100, (emergency_months / 6) * 100)  # Target: 6 months
        savings_score = min(100, savings_rate)  # Target: >20%
        debt_score = max(0, 100 - dti_ratio)  # Lower DTI is better
        
        overall_health = (emergency_score + savings_score + debt_score) / 3
        
        return {
            'metrics': {
                'net_worth': round(net_worth, 2),
                'total_assets': round(total_assets, 2),
                'total_liabilities': round(total_liabilities, 2),
                'savings_rate': round(savings_rate, 2),
                'emergency_months': round(emergency_months, 2),
                'dti_ratio': round(dti_ratio, 2),
                'monthly_surplus': round(monthly_surplus, 2)
            },
            'scores': {
                'emergency_fund': round(emergency_score, 1),
                'savings': round(savings_score, 1),
                'debt': round(debt_score, 1),
                'overall_health': round(overall_health, 1)
            },
            'version': FinancialCalculator.VERSION
        }
