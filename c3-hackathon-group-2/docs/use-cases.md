# 📚 Use Cases & Scenarios with Examples

This document provides detailed, real-world use cases with concrete data examples for the Personal Finance Coach application.

---

## Use Case 1: Profile Analysis & Initial Plan Generation

### Scenario: Young Professional with Credit Card Debt

**User Profile:**
- **Name:** Priya Sharma
- **Age:** 28
- **Location:** Mumbai, India
- **Occupation:** Software Engineer
- **Dependents:** 0
- **Risk Profile:** Medium
- **Financial Knowledge:** Beginner

**Financial Snapshot:**
```json
{
  "monthly_income": 85000,
  "monthly_expenses": 55000,
  "current_savings": 35000
}
```

**Assets:**
```json
[
  {
    "type": "cash",
    "name": "Savings Account",
    "current_value": 35000,
    "liquidity": "high",
    "expected_return": 0.03
  },
  {
    "type": "mf",
    "name": "HDFC Equity Fund",
    "current_value": 45000,
    "liquidity": "medium",
    "expected_return": 0.12
  }
]
```

**Liabilities:**
```json
[
  {
    "type": "credit_card",
    "outstanding_amount": 75000,
    "interest_rate": 0.36,
    "tenure_months": 0
  },
  {
    "type": "personal_loan",
    "outstanding_amount": 120000,
    "interest_rate": 0.14,
    "tenure_months": 24
  }
]
```

**Goals:**
```json
[
  {
    "name": "Emergency Fund",
    "target_amount": 165000,
    "target_date": "2026-06-01",
    "priority": 1
  },
  {
    "name": "House Down Payment",
    "target_amount": 500000,
    "target_date": "2028-12-31",
    "priority": 2
  }
]
```

### System Analysis

#### Step 1: Financial Metrics Calculation

```javascript
// Net Worth
netWorth = sum(assets) - sum(liabilities)
netWorth = (35000 + 45000) - (75000 + 120000)
netWorth = 80000 - 195000 = -115000  // Negative net worth

// Savings Rate
savings = monthly_income - monthly_expenses
savings = 85000 - 55000 = 30000
savingsRate = 30000 / 85000 = 0.353 = 35.3%  // Good!

// Emergency Fund Coverage
emergencyMonths = current_savings / monthly_expenses
emergencyMonths = 35000 / 55000 = 0.64 months  // Critical!

// Debt-to-Income Ratio
monthlyDebtPayment = (120000 / 24) + (75000 * 0.03)  // EMI + min CC payment
monthlyDebtPayment = 5000 + 2250 = 7250
debtToIncome = 7250 / 85000 = 0.085 = 8.5%  // Manageable

// High-Interest Debt
creditCardAPR = 36%  // CRITICAL - highest priority
personalLoanAPR = 14%  // HIGH - second priority
```

#### Step 2: Rule Engine Application

```javascript
// Emergency Fund Rule
if (emergencyMonths < 3) {
  priorityActions.push({
    priority: 1,
    action: "Build emergency fund to 3 months",
    target: 165000,  // 3 * 55000
    current: 35000,
    gap: 130000,
    monthly_allocation: 5000
  });
}

// High-Interest Debt Rule (36% > 12% threshold)
if (creditCard.interest_rate > 0.12) {
  priorityActions.push({
    priority: 1,  // Same as emergency - both critical
    action: "Pay off credit card immediately",
    target: 75000,
    interest_cost_per_month: 2250,
    recommended_payment: 15000  // Aggressive payoff
  });
}

// Medium-Interest Debt Rule
if (personalLoan.interest_rate > 0.10) {
  priorityActions.push({
    priority: 2,
    action: "Accelerate personal loan payoff",
    current_emi: 5000,
    recommended_emi: 7000,
    months_saved: 6
  });
}
```

#### Step 3: Bucketization

```javascript
buckets = {
  emergency: {
    target: 165000,
    current: 35000,
    monthly_allocation: 5000,
    priority: "CRITICAL"
  },
  debt: {
    high_interest: {
      amount: 75000,
      apr: 36,
      monthly_allocation: 15000,
      priority: "CRITICAL"
    },
    medium_interest: {
      amount: 120000,
      apr: 14,
      monthly_allocation: 7000,
      priority: "HIGH"
    }
  },
  short_term: {
    goals: [],
    monthly_allocation: 0,
    status: "DEFERRED until debts cleared"
  },
  long_term: {
    existing_mf: 45000,
    monthly_allocation: 3000,  // Continue existing SIPs
    priority: "MEDIUM"
  }
}
```

#### Step 4: Plan Generation

```javascript
finalPlan = {
  net_worth: -115000,
  savings_rate: 0.353,
  monthly_surplus: 30000,
  allocation: {
    emergency_fund: 5000,
    credit_card_payoff: 15000,
    personal_loan_extra: 2000,  // On top of 5000 EMI
    continue_sip: 3000,
    buffer: 5000  // Rainy day
  },
  top_3_actions: [
    {
      order: 1,
      title: "Pay off Credit Card ASAP",
      description: "Your 36% APR credit card is costing you ₹2,250/month in interest alone. Allocate ₹15,000/month to clear this in 5 months.",
      impact: "Save ₹11,250 in interest",
      timeline: "5 months"
    },
    {
      order: 2,
      title: "Build 3-month Emergency Fund",
      description: "You have only 0.6 months of expenses saved. Build to 3 months (₹1,65,000) while paying debt.",
      current: 35000,
      target: 165000,
      monthly_save: 5000,
      timeline: "26 months"
    },
    {
      order: 3,
      title: "Accelerate Personal Loan",
      description: "After clearing credit card, add ₹10,000/month to personal loan EMI to finish 10 months early.",
      interest_saved: 16800,
      timeline: "14 months (vs 24 months)"
    }
  ],
  projections: {
    month_6: {
      credit_card: 0,  // Paid off
      emergency_fund: 65000,
      net_worth: -45000  // Improved by 70k
    },
    month_12: {
      credit_card: 0,
      personal_loan: 60000,
      emergency_fund: 95000,
      net_worth: 35000  // Positive net worth!
    },
    month_24: {
      all_debt_cleared: true,
      emergency_fund: 165000,
      mf_value: 135000,  // With growth
      net_worth: 300000
    }
  }
}
```

### RAG Explanation Example

**User Question:** "Why should I pay credit card before building emergency fund?"

**RAG Retrieved Context:**
```
Document 1: "High-Interest Debt Priority" (confidence: 0.95)
Source: Financial Planning Handbook 2024
---
Credit card debt at 24-36% APR compounds monthly, effectively doubling your debt every 2-3 years if unpaid. Emergency fund earning 3-4% will never catch up to debt growing at 36%. The mathematical priority is always: eliminate debt above 12% APR first.

Document 2: "Debt Avalanche Method" (confidence: 0.87)
Source: Personal Finance Best Practices
---
The avalanche method prioritizes highest APR debts first. For every month you delay, you lose money to interest that could have been savings. A ₹75,000 credit card at 36% costs ₹2,250/month - more than most emergency expenses.
```

**LLM Generated Explanation:**
```
Your credit card debt at 36% APR is costing you ₹2,250 every month in interest alone. 

Here's why we prioritize this:

• **Math doesn't lie**: If you save ₹1,000 in an emergency fund earning 3%, you get ₹30/year. But that same ₹1,000 on your credit card costs you ₹360/year. You're losing ₹330.

• **Emergency fund backup**: You have ₹35,000 saved, which covers major emergencies. We're not asking you to spend it all - we're asking you to pause adding to it temporarily to kill the high-interest debt.

• **Psychological win**: Clearing the credit card in 5 months will free up ₹15,000/month to turbocharge your emergency fund AND other goals.

**Sources:**
- Financial Planning Handbook 2024 (Debt Management)
- Personal Finance Best Practices (Avalanche Method)

**Confidence:** High ●●●●○
```

---

## Use Case 2: Debt Payoff Strategy Comparison

### Scenario: Choosing Between Avalanche and Snowball

**User Has Multiple Debts:**
```json
[
  {
    "name": "Credit Card A",
    "balance": 45000,
    "apr": 0.32,
    "min_payment": 1350
  },
  {
    "name": "Personal Loan",
    "balance": 180000,
    "apr": 0.14,
    "min_payment": 7500
  },
  {
    "name": "Credit Card B",
    "balance": 18000,
    "apr": 0.28,
    "min_payment": 540
  },
  {
    "name": "Car Loan",
    "balance": 250000,
    "apr": 0.09,
    "min_payment": 8333
  }
]
```

**Total Debt:** ₹4,93,000  
**Monthly Surplus:** ₹25,000 (after minimum payments)

### Strategy 1: Avalanche Method (Highest APR First)

**Order:** Credit Card A (32%) → Credit Card B (28%) → Personal Loan (14%) → Car Loan (9%)

```javascript
avalancheResults = {
  month_3: {
    paid_off: ["Credit Card A"],
    freed_amount: 1350
  },
  month_5: {
    paid_off: ["Credit Card A", "Credit Card B"],
    freed_amount: 1890
  },
  month_14: {
    paid_off: ["Credit Card A", "Credit Card B", "Personal Loan"],
    freed_amount: 9390
  },
  month_22: {
    all_debts_cleared: true,
    total_interest_paid: 67420
  },
  psychological_impact: "Slow start, mathematical optimal"
}
```

### Strategy 2: Snowball Method (Smallest Balance First)

**Order:** Credit Card B (18k) → Credit Card A (45k) → Personal Loan (180k) → Car Loan (250k)

```javascript
snowballResults = {
  month_1: {
    paid_off: ["Credit Card B"],
    freed_amount: 540,
    motivation: "Quick win!"
  },
  month_3: {
    paid_off: ["Credit Card B", "Credit Card A"],
    freed_amount: 1890
  },
  month_12: {
    paid_off: ["Credit Card B", "Credit Card A", "Personal Loan"],
    freed_amount: 9390
  },
  month_23: {
    all_debts_cleared: true,
    total_interest_paid: 71230
  },
  psychological_impact: "Quick wins, slightly more expensive"
}
```

### Comparison

| Metric | Avalanche | Snowball | Difference |
|--------|-----------|----------|------------|
| **Total Interest Paid** | ₹67,420 | ₹71,230 | ₹3,810 more |
| **Time to Clear** | 22 months | 23 months | 1 month longer |
| **First Payoff** | Month 3 | Month 1 | 2 months faster |
| **Motivation Level** | Medium | High | Better compliance |

**System Recommendation:**

For this user with high financial knowledge and discipline → **Avalanche Method**

If user had low discipline or needed motivation → **Snowball Method** (small wins matter)

---

## Use Case 3: Emergency Fund Calculation

### Scenario: Family with Variable Income

**User Profile:**
- **Occupation:** Freelance Consultant
- **Income:** Variable (₹80k - ₹150k per month)
- **Dependents:** 2 (spouse + child)
- **Health:** One chronic condition in family

**Monthly Expenses:**
```json
{
  "rent": 25000,
  "groceries": 12000,
  "utilities": 3000,
  "transport": 5000,
  "health_insurance": 4000,
  "medications": 2500,
  "child_education": 8000,
  "misc": 5000,
  "total": 64500
}
```

### Step 1: Determine Emergency Target

```javascript
baseEmergency = monthlyExpenses * 3  // Standard
baseEmergency = 64500 * 3 = 193500

// Adjustment factors
adjustments = {
  variable_income: 1.5,  // Add 50% for income uncertainty
  health_risk: 1.2,      // Add 20% for medical buffer
  single_earner: 1.0,    // No adjustment (spouse can work)
  dependents: 1.1        // Add 10% for family
}

recommendedEmergency = baseEmergency * 1.5  // Most critical factor
recommendedEmergency = 193500 * 1.5 = 290250
roundedTarget = 300000  // Round up for safety

targetMonths = 6  // Not 3, due to variable income
```

### Step 2: Build Plan

```javascript
emergencyPlan = {
  phase_1: {
    name: "Bare Minimum Buffer",
    target: 64500,  // 1 month
    timeline: "ASAP - 2 months",
    monthly_save: 32000,
    priority: "CRITICAL - Drop everything else"
  },
  phase_2: {
    name: "Comfortable Buffer",
    target: 193500,  // 3 months
    timeline: "6 months",
    monthly_save: 25000,
    priority: "HIGH - Balance with other goals"
  },
  phase_3: {
    name: "Ideal Safety Net",
    target: 300000,  // 6 months for freelancer
    timeline: "12 months",
    monthly_save: 15000,
    priority: "MEDIUM - After basic buffer"
  }
}
```

### Step 3: Where to Keep It

```javascript
emergencyAllocation = {
  instant_access: {
    amount: 64500,  // 1 month
    instruments: ["Savings Account with high interest"],
    why: "Immediate emergencies - medical, urgent repairs"
  },
  quick_access: {
    amount: 129000,  // 2 months
    instruments: ["Liquid Mutual Funds", "Ultra-Short Duration Funds"],
    why: "Access in 1-2 days, better returns than savings",
    expected_return: 0.06
  },
  buffer_access: {
    amount: 106500,  // Remaining
    instruments: ["Short-term FDs with premature withdrawal"],
    why: "Higher returns, still accessible in a week",
    expected_return: 0.07
  }
}
```

---

## Use Case 4: Goal-Based Planning with Timeline

### Scenario: Multiple Life Goals

**User Profile:**
- **Age:** 32
- **Monthly Surplus:** ₹40,000
- **Current Investments:** ₹2,50,000 in mixed assets

**Goals:**
```json
[
  {
    "name": "European Vacation",
    "target_amount": 300000,
    "target_date": "2026-09-01",
    "timeline_months": 21,
    "priority": 3,
    "flexibility": "High - can postpone"
  },
  {
    "name": "Car Purchase",
    "target_amount": 600000,
    "target_date": "2027-12-31",
    "timeline_months": 49,
    "priority": 2,
    "flexibility": "Medium"
  },
  {
    "name": "Child's Education Fund",
    "target_amount": 5000000,
    "target_date": "2040-06-01",
    "timeline_months": 186,
    "priority": 1,
    "flexibility": "None - Time-bound"
  },
  {
    "name": "Retirement",
    "target_amount": 30000000,
    "target_date": "2053-12-31",
    "timeline_months": 348,
    "priority": 1,
    "flexibility": "None"
  }
]
```

### System Analysis

#### Step 1: Categorize by Timeline

```javascript
categoryMapping = {
  vacation: {
    category: "Short-term",
    timeline: "< 3 years",
    risk: "Low",
    instruments: ["FD", "Debt Funds", "Liquid Funds"],
    expected_return: 0.07
  },
  car: {
    category: "Medium-term",
    timeline: "3-5 years",
    risk: "Low-Medium",
    instruments: ["Balanced Funds", "Conservative Hybrid Funds"],
    expected_return: 0.10
  },
  education: {
    category: "Long-term",
    timeline: "15+ years",
    risk: "Medium-High",
    instruments: ["Equity Mutual Funds", "Index Funds", "PPF"],
    expected_return: 0.12
  },
  retirement: {
    category: "Very Long-term",
    timeline: "25+ years",
    risk: "High",
    instruments: ["Aggressive Equity Funds", "NPS", "Stocks/ETFs"],
    expected_return: 0.13
  }
}
```

#### Step 2: Calculate Required SIPs

```javascript
// Formula: SIP = [FV * r] / [(1+r)^n - 1]
// Where r = monthly return, n = months

vacation = {
  fv: 300000,
  months: 21,
  rate: 0.07/12,
  sip_required: calculateSIP(300000, 21, 0.07/12),
  sip_required: 13150,
  recommendation: "Too high for timeline - consider postponing or reducing target"
}

car = {
  fv: 600000,
  months: 49,
  rate: 0.10/12,
  sip_required: 10850,
  recommendation: "Achievable"
}

education = {
  fv: 5000000,
  months: 186,
  rate: 0.12/12,
  sip_required: 9350,
  current_value: 100000,  // Allocated from existing
  sip_adjusted: 8100,
  recommendation: "Start immediately"
}

retirement = {
  fv: 30000000,
  months: 348,
  rate: 0.13/12,
  sip_required: 15600,
  current_value: 150000,  // Allocated from existing
  sip_adjusted: 14200,
  recommendation: "Critical - leverage time"
}
```

#### Step 3: Allocation Strategy

**Total SIP Needed:** ₹46,300  
**Available Surplus:** ₹40,000  
**Gap:** ₹6,300

```javascript
optimizedAllocation = {
  retirement: {
    sip: 16000,  // Increased from 14200 (highest priority)
    instruments: ["Nifty Index Fund: 8000", "Aggressive Equity MF: 8000"]
  },
  education: {
    sip: 9000,
    instruments: ["Balanced Advantage Fund: 5000", "Children's Fund: 4000"]
  },
  car: {
    sip: 10000,
    instruments: ["Conservative Hybrid Fund: 10000"]
  },
  vacation: {
    sip: 5000,  // Reduced from 13150
    instruments: ["Fixed Deposit: 5000"],
    adjustment: "Extend timeline to 30 months OR reduce target to ₹200,000",
    user_choice required: true
  },
  total: 40000
}
```

### What-If Scenario

**User asks:** "What if I get a ₹10,000 raise?"

```javascript
newSurplus = 50000

revisedAllocation = {
  retirement: 18000,  // +2000
  education: 10000,   // +1000
  car: 10000,         // no change
  vacation: 7000,     // +2000 (now full amount at 25 months)
  emergency_top_up: 3000,  // Build emergency to 9 months
  flex_buffer: 2000,  // Personal spending / guilt-free money
  total: 50000
}

impact = {
  vacation: "Achieved on time at full amount",
  retirement_corpus_increase: 1200000,  // Extra ₹12 lakhs at retirement
  emergency_months 7: 9  // Enhanced safety net
}
```

---

## Use Case 5: Monthly Progress Tracking

### Scenario: User Tracking After 3 Months

**Original Plan (Set in Month 1):**
```json
{
  "monthly_saving_target": 8000,
  "monthly_invest_sip": 12000,
  "debt_payment": 15000,
  "total_commitment": 35000
}
```

**Month 1 Self-Report:**
```json
{
  "saved": 8000,
  "invested": 12000,
  "debt_paid": 15000,
  "status": "ON_TRACK",
  "confidence": "High"
}
```

**Month 2 Self-Report:**
```json
{
  "saved": 3000,  // Expected: 8000
  "invested": 12000,
  "debt_paid": 10000,  // Expected: 15000
  "unexpected_expense": {
    "description": "Car repair",
    "amount": 12000
  },
  "status": "BEHIND",
  "confidence": "Medium"
}
```

**Month 3 Self-Report:**
```json
{
  "saved": 5000,  // Expected: 8000
  "invested": 8000,  // Expected: 12000
  "debt_paid": 15000,
  "bonus_received": 25000,
  "status": "PARTIALLY_RECOVERED",
  "confidence": "Medium"
}
```

### System Analysis

```javascript
progressAnalysis = {
  cumulative: {
    expected: {
      saved: 24000,
      invested: 36000,
      debt_paid: 45000
    },
    actual: {
      saved: 16000,  // 67% of target
      invested: 32000,  // 89% of target
      debt_paid: 40000  // 89% of target
    },
    variance: {
      saved: -8000,
      invested: -4000,
      debt_paid: -5000
    }
  },
  trend: "Recovering but below target",
  risk_level: "Medium",
  action_needed: "Gentle correction"
}
```

### System Nudges

**Nudge 1 (After Month 2):**
```
Subject: "Car repairs happen - let's adjust 🚗"

Hey there! 

We noticed your unexpected car expense in Month 2. These things happen - that's exactly why we're building an emergency fund!

📊 Your 3-month snapshot:
• Debt payments: 89% of target ✅
• Investments: 89% of target ✅  
• Savings: 67% of target ⚠️

💡 Small adjustment suggestion:
Since you got a ₹25,000 bonus, let's allocate:
• ₹8,000 → Catch up on emergency fund gap
• ₹12,000 → Extra debt payment (finish credit card faster!)
• ₹5,000 → Treat yourself (you earned it!)

You're still on track for debt freedom in 6 months. Keep going! 💪

[View Adjusted Plan] [Tell Us More] [Skip This Month]
```

**Nudge 2 (After Month 3):**
```
Subject: "You're 75% there - here's how to close the gap"

Progress Check! 📈

You've paid off ₹40,000 in debt over 3 months. That's huge! 

But we noticed you're tracking slightly behind on savings. Here's why it matters:

🎯 Current emergency fund: ₹51,000 (1.6 months of expenses)
🎯 Target: ₹90,000 (3 months)

Two options to get back on track:

Option A: "Steady Recovery" (Recommend)
• No lifestyle change needed
• Add ₹2,000/month to savings for next 4 months
• You'll hit the target in Month 7

Option B: "Aggressive Catch-up"
• Find ₹8,000 in next 2 months
• Cut discretionary spending temporarily
• Hit target by Month 5

Which feels better for you?

[Choose Option A] [Choose Option B] [I'll figure it out]

Remember: Progress > Perfection. You're doing great! 🌟
```

---

## Use Case 6: RAG Q&A Examples

### Example 1: Debt Strategy Question

**User Query:** "Is it better to pay off my home loan early or invest in mutual funds?"

**RAG Process:**
1. **Query Embedding:** Convert to vector
2. **Retrieved Documents:**
   - "Opportunity Cost of Debt Prepayment" (score: 0.92)
   - "Home Loan Tax Benefits vs Returns" (score: 0.88)
   - "Risk-Adjusted Returns Analysis" (score: 0.85)

**Context Passed to LLM:**
```
Document 1: Opportunity Cost Analysis
---
If your home loan APR is 8.5% and you're in the 30% tax bracket, your effective rate is ~6%. If you can earn 12% post-tax from equity mutual funds, investing wins mathematically. However, this assumes you can tolerate market volatility and maintain investment discipline.

Document 2: Psychological Factors
---
Debt-free living provides peace of mind that's hard to quantify. Many people sleep better without a home loan, even if it's not the optimal mathematical choice. Consider your personal risk tolerance and stress levels.

Document 3: Hybrid Approach
---
Best strategy for most people: Do both. Pay minimum EMI + modest prepayment while investing remainder. This balances wealth building with debt reduction and provides flexibility.
```

**LLM Response:**
```
Great question! The answer depends on numbers AND your peace of mind.

📊 **The Math:**
Your home loan: 8.5% APR
After tax benefits: ~6% effective rate
Mutual fund potential: 10-12% long-term

**If you invest instead of prepaying:**
₹10,000/month prepayment saves ~₹3L interest over 15 years
₹10,000/month SIP could grow to ~₹45L (at 12%)

Net benefit: ~₹15L more by investing

🧠 **BUT consider this:**
• Can you handle market ups and downs?
• Does loan stress affect your mental health?
• Do you have stable income for 15+ years?

✅ **Our recommendation:**
Split the difference:
• 60% → Mutual fund SIPs (₹6,000)
• 40% → Loan prepayment (₹4,000)

This way you:
→ Build wealth through compounding
→ Reduce loan burden
→ Sleep better at night

**Sources:**
- "Opportunity Cost of Debt Prepayment" - CFA Institute Study
- "Home Loan Tax Benefits" - India Tax Code 2024

[Run Your Numbers] [Ask Follow-up] [See Examples]
```

### Example 2: Investment Risk Question

**User Query:** "I'm 55 years old. Should I still invest in equity?"

**Retrieved Context + Response:**
```
The "100 minus age" rule suggests 45% equity at age 55. But this rule is outdated.

✅ **Modern Approach:**
Your equity allocation depends on:
1. **Timeline:** When do you need this money?
2. **Other income:** Do you have pension/rental income?
3. **Risk capacity:** Can you handle a market crash?

🎯 **For age 55:**
If retiring at 60 but living till 85:
• First 10 years: Moderate risk (50% equity, 50% debt)
• Next 15 years: Gradual shift to conservative
• Final years: Capital preservation

✅ **Recommended split:**
• 40% equity index funds (for growth)
• 40% debt funds (for stability)  
• 20% cash/FD (for emergencies)

**Why still equity?**
You have 30+ years of retirement ahead! Inflation will erode pure debt returns.

[Retirement Calculator] [Read More] [Talk to Advisor]
```

---

## Use Case 7: Edge Cases

### Edge Case 1: Irregular Income (Gig Worker)

**Challenge:** Income varies from ₹20k to ₹80k per month

**Solution:**
```javascript
strategy = {
  baseline_budget: 35000,  // Absolute minimum expenses
  planning_income: 40000,  // 25th percentile of income (conservative)
  savings_strategy: "Percentage-based, not fixed",
  
  allocation: {
    if_income_below_40k: {
      emergency: "50% of surplus",
      investments: "0% - survival mode",
      debt: "Minimum payments only"
    },
    if_income_40k_to_60k: {
      emergency: "30% of surplus",
      investments: "20% of surplus",
      debt: "50% of surplus"
    },
    if_income_above_60k: {
      emergency: "20% of surplus",
      investments: "40% of surplus",
      debt: "40% of surplus"
    }
  },
  
  buffer_account: {
    target: 120000,  // 3 months baseline
    purpose: "Smoothen income volatility",
    rule: "Draw from this in low months, replenish in high months"
  }
}
```

### Edge Case 2: Medical Emergency During Debt Payoff

**Situation:** User paying ₹20k/month to debt, suddenly needs ₹1L for surgery

**System Recommendation:**
```javascript
emergencyResponse = {
  immediate: {
    action: "PAUSE aggressive debt payment",
    reduce_to: "Minimum payments only",
    freed_amount: 15000
  },
  
  cover_medical: {
    from_emergency_fund: 60000,  // If available
    from_reduced_debt_payment: 15000,
    from_reduced_investment: 10000,
    total_available: 85000,
    gap: 15000,
    gap_solution: "Medical loan at lower APR than credit card"
  },
  
  recovery_plan: {
    month_1_to_3: {
      focus: "Recover health + replenish emergency fund",
      debt: "Minimum only",
      savings: "High priority"
    },
    month_4_onwards: {
      resume: "Normal debt payment plan",
      delay_impact: "2 months on debt-free date (acceptable trade-off)"
    }
  },
  
  lesson: "This is exactly why emergency fund comes before aggressive debt payoff"
}
```

---

## API Request/Response Examples

### Example 1: Generate Plan API

**Request:**
```http
POST /api/v1/plan/generate
Authorization: Bearer eyJhbGc...
Content-Type: application/json

{
  "user_id": "usr_28x9k2",
  "snapshot_id": "snap_91m3n7",
  "include_explanations": true,
  "risk_override": null
}
```

**Response:**
```json
{
  "success": true,
  "plan_id": "plan_45k9x2",
  "generated_at": "2025-12-13T07:30:00Z",
  "summary": {
    "net_worth": -115000,
    "savings_rate": 0.353,
    "emergency_months": 0.64,
    "debt_to_income": 0.085
  },
  "buckets": {
    "emergency": {
      "current": 35000,
      "target": 165000,
      "gap": 130000,
      "monthly_allocation": 5000,
      "priority": 1
    },
    "debt": {
      "total_outstanding": 195000,
      "high_interest_amount": 75000,
      "monthly_allocation": 15000,
      "priority": 1
    }
  },
  "top_actions": [
    {
      "order": 1,
      "title": "Pay off Credit Card ASAP",
      "description": "Your 36% APR credit card is costing you ₹2,250/month...",
      "impact": "Save ₹11,250 in interest",
      "timeline": "5 months",
      "explanation_id": "exp_82k1m9"
    }
  ],
  "monthly_targets": {
    "save": 5000,
    "invest": 3000,
    "debt_payoff": 15000,
    "total_commitment": 23000
  },
  "projections": {
    "month_6": {...},
    "month_12": {...},
    "month_24": {...}
  }
}
```

---

## Testing Scenarios

### Test Case 1: Zero Savings User
```javascript
testInput = {
  income: 50000,
  expenses: 48000,
  savings: 0,
  assets: [],
  liabilities: []
}

expectedOutput = {
  warning: "CRITICAL - No financial buffer",
  top_action: "Create a ₹500/month micro-savings habit",
  next_steps: [
    "Track expenses for 30 days",
    "Find ₹2,000 to cut",
    "Start with ₹500/month emergency fund"],
  rationale: "Small wins build confidence"
}
```

### Test Case 2: Windfall Allocation
```javascript
testInput = {
  existing_plan: {...},
  windfall_amount: 200000,
  windfall_type: "bonus"
}

expectedAllocation = {
  emergency_fund_gap: 50000,
  high_interest_debt: 75000,
  prepay_medium_debt: 50000,
  treat_yourself: 10000,  // 5% guilt-free spending
  invest_remainder: 15000
}
```

---

**Last Updated:** 2025-12-13  
**Version:** 1.0  
**Coverage:** 7 core use cases + 2 edge cases + API examples
