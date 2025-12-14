"""
Enhanced Credit Card Transaction Extractor
Extracts individual transactions from credit card statements
"""

import re
import pandas as pd
from typing import Dict, List, Any
from datetime import datetime

def extract_credit_card_transactions_enhanced(doc: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Extract individual credit card transactions
    Works with both table-based and text-based statements
    """
    data = []
    text = doc.get('full_text', '')
    
    # First, extract summary fields (existing logic)
    summary_patterns = {
        'Total Amount Due': [
            r'Total\s+Amount\s+Due[:\s]+₹?\s*([\d,]+\.?\d*)',
            r'Amount\s+Due[:\s]+₹?\s*([\d,]+\.?\d*)',
        ],
        'Minimum Payment': [
            r'Minimum\s+(?:Payment|Due)[:\s]+₹?\s*([\d,]+\.?\d*)',
            r'Min\.?\s+Payment[:\s]+₹?\s*([\d,]+\.?\d*)',
        ],
        'Credit Limit': [
            r'Credit\s+Limit[:\s]+₹?\s*([\d,]+\.?\d*)',
            r'Limit[:\s]+₹?\s*([\d,]+\.?\d*)',
        ],
    }
    
    # Extract summary data
    for category, pattern_list in summary_patterns.items():
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
    
    # Now try to extract individual transactions
    transactions = []
    
    # Check if there are tables (PDF with structured data)
    tables = doc.get('metadata', {}).get('tables', [])
    
    if tables:
        # Process tables
        for table_info in tables:
            table_data = table_info.get('data', [])
            
            if len(table_data) < 2:
                continue
            
            try:
                # Convert to DataFrame
                df = pd.DataFrame(table_data[1:], columns=table_data[0])
                
                # Find relevant columns
                date_col = None
                desc_col = None
                amount_col = None
                
                for col in df.columns:
                    col_lower = str(col).lower()
                    
                    if any(x in col_lower for x in ['date', 'txn', 'trans']):
                        date_col = col
                    elif any(x in col_lower for x in ['description', 'merchant', 'particulars', 'details']):
                        desc_col = col
                    elif any(x in col_lower for x in ['amount', 'debit', 'transaction']):
                        amount_col = col
                
                # Extract transactions
                for idx, row in df.iterrows():
                    try:
                        if amount_col and pd.notna(row[amount_col]):
                            amount_str = str(row[amount_col]).replace(',', '').replace('₹', '').strip()
                            amount = float(amount_str)
                            
                            if 0 < amount < 1000000:  # Reasonable CC transaction
                                description = "Credit Card Transaction"
                                if desc_col and pd.notna(row[desc_col]):
                                    description = str(row[desc_col])[:200]
                                
                                trans_date = None
                                if date_col and pd.notna(row[date_col]):
                                    try:
                                        trans_date = pd.to_datetime(row[date_col])
                                    except:
                                        pass
                                
                                transactions.append({
                                    'type': 'expense',
                                    'category': 'Credit Card Transaction',
                                    'amount': amount,
                                    'description': description,
                                    'transaction_date': trans_date,
                                    'extracted_from': 'credit_card_statement'
                                })
                    except:
                        continue
            
            except:
                continue
    
    # If no table data, try text extraction
    if not transactions:
        lines = text.split('\n')
        
        # Pattern for transaction lines
        # Date | Description | Amount
        date_pattern = r'(\d{2}[/-]\d{2}[/-]\d{4})'
        amount_pattern = r'₹?\s*([\d,]+\.?\d*)'
        
        for line in lines:
            # Skip headers
            if any(h in line.lower() for h in ['date', 'transaction', 'description', 'amount', 'merchant']):
                continue
            
            # Look for date
            date_match = re.search(date_pattern, line)
            
            if date_match:
                # Extract amounts
                amounts = re.findall(amount_pattern, line)
                
                if amounts:
                    for amt_str in amounts:
                        try:
                            amt = float(amt_str.replace(',', ''))
                            
                            if 0 < amt < 1000000:  # Reasonable CC transaction
                                # Get description
                                desc_start = date_match.end()
                                desc_end = line.find(amt_str, desc_start)
                                description = line[desc_start:desc_end].strip()[:200] or "Transaction"
                                
                                transactions.append({
                                    'type': 'expense',
                                    'category': 'Credit Card Transaction',
                                    'amount': amt,
                                    'description': description,
                                    'extracted_from': 'credit_card_statement'
                                })
                                break  # Only take first valid amount per line
                        except:
                            continue
    
    # Add transactions to data
    data.extend(transactions)
    
    print(f"Credit card extraction: {len(data)} total entries ({len(transactions)} transactions)")
    
    return data


# Add this method to your DocumentProcessor class:
def _extract_credit_card_data_v2(self, doc: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Enhanced credit card extraction with individual transactions"""
    return extract_credit_card_transactions_enhanced(doc)
