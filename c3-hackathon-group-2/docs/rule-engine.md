# 🧠 Rule Engine Pseudocode

function generatePlan(profile, snapshot, assets, liabilities, goals):

  calculate:
    netWorth = sum(assets) - sum(liabilities)
    savingsRate = (snapshot.income - snapshot.expenses) / snapshot.income
    emergencyMonths = snapshot.savings / snapshot.expenses

  actions = []

  # Emergency Fund Rule
  if emergencyMonths < 3:
    actions.append(
      "Build emergency fund to 3 months expenses first"
    )

  # Debt Priority Rule
  highInterestDebt = liabilities where interest_rate > 12%
  if highInterestDebt exists:
    actions.append(
      "Pay high-interest debt using avalanche or snowball"
    )

  # Savings Discipline Rule
  if savingsRate < 0.2:
    actions.append(
      "Pay yourself first — auto-save monthly"
    )

  # Goal Allocation Rule
  for goal in goals:
    if goal.duration < 3 years:
      assign low-risk bucket
    else if goal.duration >= 5 years:
      assign growth bucket

  # Risk Adjustment
  if profile.risk == low:
    reduce equity exposure
  else if profile.risk == high:
    increase equity exposure

  # Final Plan
  plan = {
    monthly_saving_target,
    monthly_invest_target,
    top_3_actions = actions.take(3)
  }

  return plan
