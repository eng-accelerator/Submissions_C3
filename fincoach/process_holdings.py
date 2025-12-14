"""
Process Investment Holdings Excel File
Extracts equity and mutual fund data from Zerodha-style holdings file
"""

import pandas as pd
import os
from database.db_manager import DBManager
from datetime import datetime

def process_holdings_excel(file_path: str, user_id: int, db: DBManager):
    """
    Process investment holdings Excel file
    Returns dict with success status and extracted data
    """
    result = {
        'success': False,
        'message': '',
        'investments_added': 0,
        'total_value': 0
    }
    
    try:
        # Read Excel file
        xls = pd.ExcelFile(file_path)
        print(f"Found sheets: {xls.sheet_names}")
        
        investments_added = 0
        total_value = 0
        
        # Process each sheet
        for sheet_name in xls.sheet_names:
            if sheet_name.lower() in ['equity', 'mutual funds', 'mf', 'stocks']:
                df = pd.read_excel(file_path, sheet_name=sheet_name, header=None)
                
                # Find header row (look for common column names)
                header_row = None
                for idx, row in df.iterrows():
                    row_str = ' '.join([str(x).lower() for x in row if pd.notna(x)])
                    if any(keyword in row_str for keyword in ['symbol', 'scrip', 'instrument', 'quantity', 'value', 'isin']):
                        header_row = idx
                        break
                
                if header_row is not None:
                    # Re-read with proper header
                    df = pd.read_excel(file_path, sheet_name=sheet_name, header=header_row)
                    
                    # Clean column names
                    df.columns = [str(col).strip() for col in df.columns]
                    
                    # Find relevant columns (case-insensitive)
                    col_map = {}
                    for col in df.columns:
                        col_lower = col.lower()
                        if 'symbol' in col_lower or 'scrip' in col_lower or 'instrument' in col_lower:
                            col_map['name'] = col
                        elif 'quantity' in col_lower or 'qty' in col_lower:
                            col_map['quantity'] = col
                        elif 'current value' in col_lower or 'market value' in col_lower:
                            col_map['value'] = col
                        elif 'current price' in col_lower or 'ltp' in col_lower:
                            col_map['price'] = col
                    
                    print(f"Processing {sheet_name} sheet...")
                    print(f"Column mapping: {col_map}")
                    
                    # Extract investment data
                    for idx, row in df.iterrows():
                        try:
                            # Skip rows with all NaN
                            if row.isna().all():
                                continue
                            
                            # Get investment name
                            name = None
                            if 'name' in col_map:
                                name = str(row[col_map['name']]).strip() if pd.notna(row[col_map['name']]) else None
                            
                            if not name or name == 'nan' or len(name) < 2:
                                continue
                            
                            # Get value
                            value = 0
                            if 'value' in col_map and pd.notna(row[col_map['value']]):
                                try:
                                    value = float(str(row[col_map['value']]).replace(',', ''))
                                except:
                                    pass
                            
                            # Calculate value from quantity and price if value not available
                            if value == 0 and 'quantity' in col_map and 'price' in col_map:
                                try:
                                    qty = float(str(row[col_map['quantity']]).replace(',', ''))
                                    price = float(str(row[col_map['price']]).replace(',', ''))
                                    value = qty * price
                                except:
                                    pass
                            
                            # Skip if no valid value
                            if value <= 0 or value > 1e10:  # Skip invalid amounts
                                continue
                            
                            # Add to database
                            category = 'Equity' if sheet_name.lower() == 'equity' else 'Mutual Funds'
                            
                            db.add_financial_data(
                                user_id=user_id,
                                data_type='investment',
                                category=category,
                                amount=value,
                                description=f"{name} - Current Value"
                            )
                            
                            investments_added += 1
                            total_value += value
                            print(f"Added: {name} = ₹{value:,.2f}")
                        
                        except Exception as e:
                            print(f"Error processing row {idx}: {e}")
                            continue
        
        if investments_added > 0:
            result['success'] = True
            result['message'] = f"Successfully extracted {investments_added} investments worth ₹{total_value:,.2f}"
            result['investments_added'] = investments_added
            result['total_value'] = total_value
        else:
            result['message'] = "No valid investment data found in Excel file. Please check file format."
    
    except Exception as e:
        result['message'] = f"Error processing Excel file: {str(e)}"
        import traceback
        print(traceback.format_exc())
    
    return result


if __name__ == "__main__":
    # Test the processor
    import sys
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
        user_id = int(sys.argv[2]) if len(sys.argv) > 2 else 1
        
        db = DBManager()
        result = process_holdings_excel(file_path, user_id, db)
        print(result)
