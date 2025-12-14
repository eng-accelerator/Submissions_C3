"""
Enhanced Dashboard with Plotly Charts and Recommendations
"""
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px

st.set_page_config(
    page_title="Dashboard - Finance Coach",
    page_icon="📊",
    layout="wide",
)

# Sidebar
with st.sidebar:
    st.title("💰 Finance AI Coach")
    st.markdown("---")
    st.markdown("### 📍 Pages")
    
    if st.button("📝 Get Started", use_container_width=True, key="nav_onboard"):
        st.switch_page("pages/1_onboarding.py")
    
    # Current page indicator
    st.button("📊 Dashboard", use_container_width=True, disabled=True, key="current_page")
    
    if st.button("🎯 Goals", use_container_width=True, key="nav_goals"):
        st.switch_page("pages/3_goals.py")

# Main content
st.title("📊 Your Financial Dashboard")

# Check if analysis exists
# Auto-calculate if data exists but analysis is missing (for returning guests)
if 'guest_data' in st.session_state and st.session_state.guest_data.get('snapshot') and not st.session_state.guest_data.get('analysis'):
    from services.calculator import FinancialCalculator
    try:
        analysis = FinancialCalculator.analyze_financial_health(
            st.session_state.guest_data['snapshot'],
            st.session_state.guest_data['assets'],
            st.session_state.guest_data['liabilities']
        )
        st.session_state.guest_data['analysis'] = analysis
        st.rerun()
    except Exception as e:
        print(f"Auto-calc error: {e}")

if 'guest_data' not in st.session_state or not st.session_state.guest_data.get('analysis'):
    st.warning("⚠️ No analysis data available. Please complete the onboarding first!")
    if st.button("📝 Go to Onboarding"):
        st.switch_page("pages/1_onboarding.py")
else:
    analysis = st.session_state.guest_data['analysis']
    metrics = analysis['metrics']
    scores = analysis['scores']
    snapshot = st.session_state.guest_data['snapshot']
    
    # Key Metrics
    st.markdown("### 💰 Your Financial Snapshot")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        delta_color = "normal" if metrics['net_worth'] >= 0 else "inverse"
        st.metric(
            "Net Worth",
            f"₹{metrics['net_worth']:,.0f}",
            delta=f"{'Positive' if metrics['net_worth'] >= 0 else 'Negative'}",
            delta_color=delta_color
        )
    
    with col2:
        delta_color = "normal" if metrics['savings_rate'] >= 20 else "inverse"
        st.metric(
            "Savings Rate",
            f"{metrics['savings_rate']:.1f}%",
            delta="Healthy" if metrics['savings_rate'] >= 20 else "Needs Improvement",
            delta_color=delta_color
        )
    
    with col3:
        delta_color = "normal" if metrics['emergency_months'] >= 3 else "inverse"
        st.metric(
            "Emergency Fund",
            f"{metrics['emergency_months']:.1f} months",
            delta="Safe" if metrics['emergency_months'] >= 3 else "Build Up",
            delta_color=delta_color
        )
    
    with col4:
        delta_color = "normal" if metrics['monthly_surplus'] > 0 else "inverse"
        st.metric(
            "Monthly Surplus",
            f"₹{metrics['monthly_surplus']:,.0f}",
            delta="Saving" if metrics['monthly_surplus'] > 0 else "Deficit",
            delta_color=delta_color
        )
    
    # Charts Row 1
    st.markdown("---")
    chart_col1, chart_col2 = st.columns(2)
    
    with chart_col1:
        st.markdown("#### 📊 Income vs Expenses")
        
        # Income vs Expenses Bar Chart
        fig_income_expense = go.Figure()
        fig_income_expense.add_trace(go.Bar(
            name='Monthly',
            x=['Income', 'Expenses', 'Surplus'],
            y=[snapshot['monthly_income'], snapshot['monthly_expenses'], metrics['monthly_surplus']],
            marker_color=['#10b981', '#ef4444', '#6366f1']
        ))
        fig_income_expense.update_layout(
            height=300,
            showlegend=False,
            yaxis_title="Amount (₹)",
            template="plotly_white"
        )
        st.plotly_chart(fig_income_expense, use_container_width=True)
    
    with chart_col2:
        st.markdown("#### 💼 Assets vs Liabilities")
        
        # Assets vs Liabilities Pie Chart
        fig_assets_liab = go.Figure(data=[go.Pie(
            labels=['Assets', 'Liabilities'],
            values=[metrics['total_assets'], metrics['total_liabilities']],
            marker_colors=['#10b981', '#ef4444'],
            hole=0.4
        )])
        fig_assets_liab.update_layout(
            height=300,
            showlegend=True,
            template="plotly_white"
        )
        st.plotly_chart(fig_assets_liab, use_container_width=True)
    
    # Health Scores with Visual Gauge
    st.markdown("---")
    st.markdown("### 📈 Financial Health Scores")
    
    score_col1, score_col2, score_col3, score_col4 = st.columns(4)
    
    def create_gauge(value, title):
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=value,
            title={'text': title},
            gauge={
                'axis': {'range': [None, 100]},
                'bar': {'color': "#6366f1"},
                'steps': [
                    {'range': [0, 33], 'color': "#fecaca"},
                    {'range': [33, 66], 'color': "#fde68a"},
                    {'range': [66, 100], 'color': "#bbf7d0"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 75
                }
            }
        ))
        fig.update_layout(height=200, margin=dict(l=20, r=20, t=40, b=20))
        return fig
    
    with score_col1:
        st.plotly_chart(create_gauge(scores['emergency_fund'], "Emergency Fund"), use_container_width=True)
    
    with score_col2:
        st.plotly_chart(create_gauge(scores['savings'], "Savings Rate"), use_container_width=True)
    
    with score_col3:
        st.plotly_chart(create_gauge(scores['debt'], "Debt Health"), use_container_width=True)
    
    with score_col4:
        st.plotly_chart(create_gauge(scores['overall_health'], "Overall Health"), use_container_width=True)
    
    # Overall Health Summary
    st.markdown("---")
    if scores['overall_health'] >= 75:
        st.success(f"✅ **Excellent financial health!** Overall Score: **{scores['overall_health']:.0f}/100**")
        st.info("Keep up the great work! You're on track to achieve your financial goals.")
    elif scores['overall_health'] >= 50:
        st.info(f"💡 **Good progress!** Overall Score: **{scores['overall_health']:.0f}/100**")
        st.warning("A few improvements will boost your financial health significantly.")
    else:
        st.warning(f"⚠️ **Needs attention.** Overall Score: **{scores['overall_health']:.0f}/100**")
        st.error("Follow the recommendations below to improve your financial situation.")
    
    # Personalized Recommendations
    st.markdown("---")
    st.markdown("### 🎯 Your Top 3 Priorities")
    
    recommendations = []
    
    # Priority 1: Emergency Fund
    if metrics['emergency_months'] < 3:
        target_emergency = snapshot['monthly_expenses'] * 3
        gap = target_emergency - snapshot['current_savings']
        months_needed = gap / metrics['monthly_surplus'] if metrics['monthly_surplus'] > 0 else 0
        recommendations.append({
            'priority': 1,
            'title': '🚨 Build Emergency Fund',
            'description': f"You need **₹{gap:,.0f} more** to reach 3 months of expenses",
            'action': f"Save ₹{gap/6:,.0f}/month for 6 months" if gap > 0 else "Maintain current level",
            'impact': f"Achieve in {months_needed:.0f} months at current savings rate" if months_needed > 0 else "Already achieved!"
        })
    
    # Priority 2: High-Interest Debt
    high_interest_debts = [d for d in st.session_state.guest_data['liabilities'] if d['interest_rate'] > 0.15]
    if high_interest_debts:
        total_high_interest = sum(d['outstanding'] for d in high_interest_debts)
        recommendations.append({
            'priority': 2,
            'title': '💳 Pay Off High-Interest Debt',
            'description': f"You have **₹{total_high_interest:,.0f}** in high-interest debt (>15% APR)",
            'action': f"Focus extra ₹{metrics['monthly_surplus']*0.7:,.0f}/month on highest interest debt",
            'impact': f"Save thousands in interest payments"
        })
    
    # Priority 3: Increase Savings Rate
    if metrics['savings_rate'] < 20:
        target_rate = 20
        target_savings = snapshot['monthly_income'] * (target_rate / 100)
        gap = target_savings - (snapshot['monthly_income'] - snapshot['monthly_expenses'])
        recommendations.append({
            'priority': 3,
            'title': '📊 Increase Savings Rate',
            'description': f"Current: **{metrics['savings_rate']:.1f}%**, Target: **{target_rate}%**",
            'action': f"Reduce expenses by ₹{gap:,.0f}/month",
            'impact': f"Save an additional ₹{gap*12:,.0f}/year"
        })
    
    # If financially healthy, suggest investment goals
    if not recommendations and scores['overall_health'] >= 75:
        recommendations.append({
            'priority': 1,
            'title': '🚀 Invest for Growth',
            'description': "Your financial foundation is strong!",
            'action': f"Invest ₹{metrics['monthly_surplus']*0.8:,.0f}/month in mutual funds or index funds",
            'impact': "Build long-term wealth and achieve financial freedom faster"
        })
    
    # Display recommendations
    for rec in recommendations[:3]:  # Top 3 only
        with st.expander(f"**Priority {rec['priority']}: {rec['title']}**", expanded=True):
            st.markdown(f"**Situation:** {rec['description']}")
            st.markdown(f"**Action:** {rec['action']}")
            st.markdown(f"**Impact:** {rec['impact']}")
    
    # Breakdown
    st.markdown("---")
    st.markdown("### 💼 Detailed Breakdown")
    
    breakdown_col1, breakdown_col2 = st.columns(2)
    
    with breakdown_col1:
        st.subheader(f"💰 Assets: ₹{metrics['total_assets']:,.0f}")
        if st.session_state.guest_data['assets']:
            for asset in st.session_state.guest_data['assets']:
                percentage = (asset['value'] / metrics['total_assets'] * 100) if metrics['total_assets'] > 0 else 0
                st.write(f"• **{asset['name']}**: ₹{asset['value']:,.0f} ({percentage:.1f}%)")
        else:
            st.caption("No assets added yet")
    
    with breakdown_col2:
        st.subheader(f"💳 Liabilities: ₹{metrics['total_liabilities']:,.0f}")
        if st.session_state.guest_data['liabilities']:
            for debt in st.session_state.guest_data['liabilities']:
                percentage = (debt['outstanding'] / metrics['total_liabilities'] * 100) if metrics['total_liabilities'] > 0 else 0
                st.write(f"• **{debt['name']}**: ₹{debt['outstanding']:,.0f} @ {debt['interest_rate']*100:.1f}% APR ({percentage:.1f}%)")
        else:
            st.caption("No liabilities - Great job!")
    
    # Link to Goals
    st.markdown("---")
    if st.button("🎯 Set Financial Goals Based on This Analysis", use_container_width=True, type="primary"):
        st.switch_page("pages/3_goals.py")
