"""
Data Validation and Cleanup Script
Finds and fixes incorrect amounts in the database
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database.db_manager import DBManager
from database.models import SessionLocal, FinancialData
from datetime import datetime

def validate_and_fix_data(user_id: int, dry_run: bool = True):
    """
    Validate financial data and optionally fix issues
    
    Args:
        user_id: User ID to check
        dry_run: If True, only report issues. If False, fix them.
    """
    
    db = DBManager()
    session = SessionLocal()
    
    print(f"\n{'='*80}")
    print(f"DATA VALIDATION REPORT - User ID: {user_id}")
    print(f"Mode: {'DRY RUN (no changes)' if dry_run else 'FIX MODE (will modify data)'}")
    print(f"{'='*80}\n")
    
    # Get all financial data
    all_data = session.query(FinancialData).filter(FinancialData.user_id == user_id).all()
    
    if not all_data:
        print("No financial data found for this user.")
        return
    
    print(f"Total records: {len(all_data)}\n")
    
    # Issue tracking
    issues = {
        'extreme_values': [],  # > 1 trillion or < 0
        'likely_wrong': [],    # Suspicious amounts
        'missing_category': [],
        'missing_date': []
    }
    
    # Check each record
    for data in all_data:
        # Check for extreme values
        if data.amount and (data.amount > 1e12 or data.amount < 0):
            issues['extreme_values'].append(data)
        
        # Check for likely wrong amounts based on type
        elif data.data_type == 'expense' and data.amount and data.amount > 10000000:  # > 1 crore
            issues['likely_wrong'].append(data)
        
        elif data.data_type == 'income' and data.amount and data.amount > 100000000:  # > 10 crore monthly
            issues['likely_wrong'].append(data)
        
        # Check for missing data
        if not data.category or data.category == '':
            issues['missing_category'].append(data)
        
        if not data.transaction_date:
            issues['missing_date'].append(data)
    
    # Report issues
    print("ISSUES FOUND:\n")
    
    if issues['extreme_values']:
        print(f"⚠️  EXTREME VALUES ({len(issues['extreme_values'])} records):")
        print("-" * 80)
        for d in issues['extreme_values']:
            print(f"  ID: {d.id} | Type: {d.data_type} | Amount: ₹{d.amount:,.2f}")
            print(f"  Category: {d.category or 'N/A'} | Description: {(d.description or 'N/A')[:50]}")
            print()
    
    if issues['likely_wrong']:
        print(f"\n⚠️  LIKELY WRONG AMOUNTS ({len(issues['likely_wrong'])} records):")
        print("-" * 80)
        for d in issues['likely_wrong']:
            print(f"  ID: {d.id} | Type: {d.data_type} | Amount: ₹{d.amount:,.2f}")
            print(f"  Category: {d.category or 'N/A'} | Description: {(d.description or 'N/A')[:50]}")
            print()
    
    if issues['missing_category']:
        print(f"\n⚠️  MISSING CATEGORY ({len(issues['missing_category'])} records)")
    
    if issues['missing_date']:
        print(f"⚠️  MISSING DATE ({len(issues['missing_date'])} records)")
    
    # Summary
    total_issues = sum(len(v) for v in issues.values())
    print(f"\n{'='*80}")
    print(f"SUMMARY: {total_issues} issues found")
    print(f"{'='*80}\n")
    
    # Fix if not dry run
    if not dry_run and total_issues > 0:
        print("\n🔧 FIXING ISSUES...\n")
        
        deleted = 0
        updated = 0
        
        # Delete extreme values
        for d in issues['extreme_values']:
            session.delete(d)
            deleted += 1
            print(f"✅ Deleted record ID {d.id} (extreme value: ₹{d.amount:,.2f})")
        
        # Update missing categories
        for d in issues['missing_category']:
            d.category = f"Uncategorized {d.data_type.title()}"
            updated += 1
        
        # Update missing dates
        for d in issues['missing_date']:
            d.transaction_date = d.created_at or datetime.now()
            updated += 1
        
        session.commit()
        
        print(f"\n{'='*80}")
        print(f"FIXED:")
        print(f"  - Deleted {deleted} records")
        print(f"  - Updated {updated} records")
        print(f"{'='*80}\n")
    
    elif dry_run and total_issues > 0:
        print("\n💡 To fix these issues, run:")
        print(f"   python validate_data.py {user_id} --fix\n")
    
    session.close()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Validate and fix financial data')
    parser.add_argument('user_id', type=int, help='User ID to check')
    parser.add_argument('--fix', action='store_true', help='Fix issues (default: dry run only)')
    
    args = parser.parse_args()
    
    validate_and_fix_data(args.user_id, dry_run=not args.fix)
