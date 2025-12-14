"""
Specialized Credit Card Transaction Processor
Handles Axis Bank and HDFC Bank credit card statements with table extraction
"""

import re
import pandas as pd
from typing import Dict, List, Any
from datetime import datetime

def extract_axis_bank_transactions(text: str) -> List[Dict[str, Any]]:
    """
    Extract transactions from Axis Bank credit card statement
    Format: DATE | TRANSACTION DETAILS | MERCHANT CATEGORY | AMOUNT | CASHBACK
    """
    transactions = []
    
    # Pattern for Axis Bank transaction lines
    # 18/10/2025 WWW AMAZON IN,GURGAON DEPT STORES 12,047.00 Dr 181.00 Cr
    
    lines = text.split('\n')
    
    for line in lines:
        # Look for date pattern at start of line
        date_match = re.match(r'(\d{2}/\d{2}/\d{4})\s+(.+)', line)
        
        if date_match:
            date_str = date_match.group(1)
            rest = date_match.group(2)
            
            # Extract amount (looks for pattern like "12,047.00 Dr" or "816.00 Cr")
            amount_pattern = r'([\d,]+\.?\d*)\s+(Dr|Cr)'
            amounts = re.findall(amount_pattern, rest)
            
            if amounts:
                # First amount is transaction amount
                amount_str = amounts[0][0].replace(',', '')
                amount_type = amounts[0][1]
                
                try:
                    amount = float(amount_str)
                    
                    # Skip if amount is too large or too small
                    if amount <= 0 or amount > 1000000:
                        continue
                    
                    # Extract description (text before amount)
                    desc_end = rest.find(amounts[0][0])
                    description = rest[:desc_end].strip()
                    
                    # Determine transaction type
                    trans_type = 'expense' if amount_type == 'Dr' else 'income'
                    
                    # Parse date
                    try:
                        trans_date = datetime.strptime(date_str, '%d/%m/%Y')
                    except:
                        trans_date = None
                    
                    # Categorize
                    category = categorize_description(description)
                    
                    transactions.append({
                        'type': trans_type,
                        'category': category,
                        'amount': amount,
                        'description': description[:200],
                        'transaction_date': trans_date,
                        'extracted_from': 'credit_card_statement'
                    })
                
                except:
                    continue
    
    return transactions


def extract_hdfc_transactions(text: str) -> List[Dict[str, Any]]:
    """
    Extract transactions from HDFC credit card statement
    Format: DATE & TIME | TRANSACTION DESCRIPTION | REWARDS | AMOUNT | PI
    """
    transactions = []
    
    lines = text.split('\n')
    
    for line in lines:
        # Look for HDFC date pattern: 02/11/2025| 00:00
        date_match = re.match(r'(\d{2}/\d{2}/\d{4})\|\s*(\d{2}:\d{2})\s+(.+)', line)
        
        if date_match:
            date_str = date_match.group(1)
            time_str = date_match.group(2)
            rest = date_match.group(3)
            
            # Extract amount (looks for C 23.00 or C23.00 or ₹23.00)
            amount_pattern = r'[C₹]\s*([\d,]+\.?\d*)'
            amounts = re.findall(amount_pattern, rest)
            
            if amounts:
                # Last amount is usually the transaction amount
                amount_str = amounts[-1].replace(',', '')
                
                try:
                    amount = float(amount_str)
                    
                    # Skip if amount is too large or invalid
                    if amount <= 0 or amount > 10000000:
                        continue
                    
                    # Extract description (text before amount)
                    desc_end = rest.rfind(amounts[-1])
                    description = rest[:desc_end].strip()
                    
                    # Remove reward points from description
                    description = re.sub(r'\+\s*\d+\s*$', '', description).strip()
                    
                    # Parse date
                    try:
                        trans_date = datetime.strptime(date_str, '%d/%m/%Y')
                    except:
                        trans_date = None
                    
                    # Categorize
                    category = categorize_description(description)
                    
                    # Determine if it's a payment/credit
                    trans_type = 'income' if 'payment' in description.lower() or 'credit' in description.lower() else 'expense'
                    
                    transactions.append({
                        'type': trans_type,
                        'category': category,
                        'amount': amount,
                        'description': description[:200],
                        'transaction_date': trans_date,
                        'extracted_from': 'credit_card_statement'
                    })
                
                except:
                    continue
    
    return transactions


def categorize_description(description: str) -> str:
    """Smart categorization based on merchant/description"""
    desc_lower = description.lower()
    
    categories = {
        'Shopping': ['amazon', 'flipkart', 'myntra', 'shop'],
        'Technology': ['digitalocean', 'google workspace', 'adobe', 'microsoft', 'github', 'aws', 'amazon web'],
        'Entertainment': ['netflix', 'spotify', 'youtube', 'prime', 'hotstar'],
        'Professional': ['linkedin', 'upwork', 'fiverr'],
        'AI Services': ['openai', 'claude', 'chatgpt', 'anthropic'],
        'Utilities': ['electricity', 'water', 'gas', 'gpay utilities'],
        'Food & Dining': ['zomato', 'swiggy', 'restaurant'],
        'Insurance': ['lic', 'insurance'],
        'EMI': ['emi'],
        'Fees & Charges': ['gst', 'fee', 'charge', 'interest'],
    }
    
    for category, keywords in categories.items():
        if any(kw in desc_lower for kw in keywords):
            return category
    
    return 'Credit Card Transaction'


def extract_credit_card_summary(text: str) -> List[Dict[str, Any]]:
    """Extract summary fields (Total Due, Minimum Payment, Credit Limit)"""
    data = []
    
    patterns = {
        'Total Amount Due': [
            r'Total\s+(?:Payment\s+)?Due[:\s]+(?:₹|C|Rs\.?)?\s*([\d,]+\.?\d*)',
            r'TOTAL\s+AMOUNT\s+DUE[:\s]+(?:₹|C)?\s*([\d,]+\.?\d*)',
        ],
        'Minimum Payment': [
            r'Minimum\s+(?:Payment\s+)?Due[:\s]+(?:₹|C|Rs\.?)?\s*([\d,]+\.?\d*)',
            r'MINIMUM\s+DUE[:\s]+(?:₹|C)?\s*([\d,]+\.?\d*)',
        ],
        'Credit Limit': [
            r'Credit\s+Limit[:\s]+(?:₹|C|Rs\.?)?\s*([\d,]+\.?\d*)',
            r'TOTAL\s+CREDIT\s+LIMIT[:\s]+(?:₹|C)?\s*([\d,]+\.?\d*)',
        ],
    }
    
    for category, pattern_list in patterns.items():
        for pattern in pattern_list:
            matches = re.findall(pattern, text, re.IGNORECASE)
            
            if matches:
                try:
                    amount = float(matches[0].replace(',', ''))
                    
                    if 0 < amount < 100000000:
                        data.append({
                            'type': 'debt',
                            'category': category,
                            'amount': amount,
                            'description': f'{category} from credit card statement',
                            'extracted_from': 'credit_card_statement'
                        })
                        break
                except:
                    continue
    
    return data


def process_credit_card_statement(doc: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Main processor for credit card statements
    Detects bank type and extracts accordingly
    """
    text = doc.get('full_text', '')
    data = []
    
    # Detect bank type
    is_axis = 'axis bank' in text.lower()
    is_hdfc = 'hdfc bank' in text.lower()
    
    print(f"Credit card processor: Axis={is_axis}, HDFC={is_hdfc}")
    
    # Extract summary data first
    summary = extract_credit_card_summary(text)
    data.extend(summary)
    
    # Extract transactions
    if is_axis:
        transactions = extract_axis_bank_transactions(text)
        print(f"Extracted {len(transactions)} Axis Bank transactions")
    elif is_hdfc:
        transactions = extract_hdfc_transactions(text)
        print(f"Extracted {len(transactions)} HDFC Bank transactions")
    else:
        # Generic extraction
        transactions = []
    
    data.extend(transactions)
    
    print(f"Total credit card data: {len(data)} entries ({len(summary)} summary + {len(transactions)} transactions)")
    
    return data


# Test function
if __name__ == "__main__":
    import sys
    from processors.document_processor import DocumentProcessor
    
    if len(sys.argv) < 2:
        print("Usage: python credit_card_processor.py <pdf_file>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    
    processor = DocumentProcessor()
    doc = processor.process_pdf(file_path)
    
    if doc.get('success'):
        data = process_credit_card_statement(doc)
        
        print(f"\n{'='*80}")
        print(f"EXTRACTED DATA: {len(data)} records")
        print(f"{'='*80}\n")
        
        for item in data:
            print(f"{item['type'].upper()}: {item['category']} = ₹{item['amount']:,.2f}")
            print(f"  Description: {item.get('description', 'N/A')}")
            print()
