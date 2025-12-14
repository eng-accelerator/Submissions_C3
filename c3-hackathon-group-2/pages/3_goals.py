"""
Enhanced Goals Page with Projections and Timeline
"""
import streamlit as st
from datetime import datetime, timedelta
import plotly.graph_objects as go

st.set_page_config(
    page_title="Goals - Finance Coach",
    page_icon="🎯",
    layout="wide",
)

# Initialize goals in session state
if 'guest_data' not in st.session_state:
    st.session_state.guest_data = {'goals': []}
if 'goals' not in st.session_state.guest_data:
    st.session_state.guest_data['goals'] = []

# Sidebar
with st.sidebar:
    st.title("💰 Finance AI Coach")
    st.markdown("---")
    st.markdown("### 📍 Pages")
    
    if st.button("📝 Get Started", use_container_width=True, key="nav_onboard"):
        st.switch_page("pages/1_onboarding.py")
    
    if st.button("📊 Dashboard", use_container_width=True, key="nav_dash"):
        st.switch_page("pages/2_dashboard.py")
    
    # Current page indicator
    st.button("🎯 Goals", use_container_width=True, disabled=True, key="current_page")

# Main content
st.title("🎯 Your Financial Goals")

# Get financial data for projections
monthly_surplus = 0
if 'guest_data' in st.session_state and 'analysis' in st.session_state.guest_data:
    analysis = st.session_state.guest_data['analysis']
    monthly_surplus = analysis['metrics'].get('monthly_surplus', 0)

# Smart Goal Suggestions
if monthly_surplus > 0:
    st.info(f"💡 **You have ₹{monthly_surplus:,.0f}/month available for goals** based on your current finances")

# Add new goal
with st.expander("➕ Add New Goal", expanded=len(st.session_state.guest_data['goals']) == 0):
    with st.form("goal_form"):
        goal_name = st.text_input("Goal Name", placeholder="e.g., House Down Payment, Car Purchase, Vacation")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            target_amount = st.number_input("Target Amount (₹)", min_value=0, step=10000, value=100000)
        with col2:
            months = st.number_input("Months to Achieve", min_value=1, max_value=360, value=12)
        with col3:
            current_progress = st.number_input("Current Progress (₹)", min_value=0, step=5000, value=0)
        
        category = st.selectbox(
            "Category",
            ["Emergency", "Short-term (< 3 years)", "Medium-term (3-5 years)", "Long-term (5+ years)", "Retirement"]
        )
        
        # Calculate projections
        if target_amount > 0 and months > 0:
            remaining = target_amount - current_progress
            required_monthly = remaining / months if remaining > 0 else 0
            
            st.markdown("---")
            st.markdown("#### 📊 Goal Projection")
            
            proj_col1, proj_col2, proj_col3 = st.columns(3)
            with proj_col1:
                st.metric("Required Monthly Savings", f"₹{required_monthly:,.0f}")
            with proj_col2:
                feasible = "✅ Achievable" if required_monthly <= monthly_surplus else "⚠️ Review Budget"
                st.metric("Feasibility", feasible)
            with proj_col3:
                completion_months = remaining / monthly_surplus if monthly_surplus > 0 and remaining > 0 else 0
                st.metric("Realistic Timeline", f"{completion_months:.0f} months" if completion_months > 0 else "N/A")
        
        if st.form_submit_button("Add Goal", use_container_width=True, type="primary"):
            if goal_name and target_amount > 0:
                st.session_state.guest_data['goals'].append({
                    'name': goal_name,
                    'target_amount': target_amount,
                    'current_progress': current_progress,
                    'target_date': (datetime.now() + timedelta(days=months*30)).strftime("%Y-%m-%d"),
                    'category': category,
                    'required_monthly': required_monthly if 'required_monthly' in locals() else 0,
                'created_at': datetime.now().strftime("%Y-%m-%d")
                })
                
                # Save execution
                if st.session_state.get("user"):
                    from services.auth_service import AuthService
                    AuthService.save_guest_data(st.session_state.user["user_id"], st.session_state.guest_data)
                    
                st.success(f"✅ Added goal: {goal_name}")
                st.rerun()
            else:
                st.error("Please enter goal name and target amount")

# Show existing goals
if st.session_state.guest_data['goals']:
    st.markdown("---")
    st.markdown("### Your Active Goals")
    
    # Goals summary chart
    if len(st.session_state.guest_data['goals']) > 1:
        fig = go.Figure()
        
        for goal in st.session_state.guest_data['goals']:
            progress_pct = (goal.get('current_progress', 0) / goal['target_amount'] * 100) if goal['target_amount'] > 0 else 0
            
            fig.add_trace(go.Bar(
                name=goal['name'],
                x=[goal['name']],
                y=[goal['target_amount']],
                text=[f"₹{goal['target_amount']:,.0f}"],
                textposition='auto',
                marker_color='lightgray',
                showlegend=False
            ))
            
            fig.add_trace(go.Bar(
                name=f"{goal['name']} Progress",
                x=[goal['name']],
                y=[goal.get('current_progress', 0)],
                text=[f"₹{goal.get('current_progress', 0):,.0f}"],
                textposition='auto',
                marker_color='#6366f1',
                showlegend=False
            ))
        
        fig.update_layout(
            title="Goals Progress Overview",
            barmode='overlay',
            height=300,
            yaxis_title="Amount (₹)",
            template="plotly_white"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Individual goal cards
    for idx, goal in enumerate(st.session_state.guest_data['goals']):
        with st.container():
            col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
            
            with col1:
                st.markdown(f"### {goal['name']}")
                st.caption(f"📁 {goal['category']}")
                st.caption(f"🗓️ Target Date: {goal['target_date']}")
            
            with col2:
                progress_pct = (goal.get('current_progress', 0) / goal['target_amount'] * 100) if goal['target_amount'] > 0 else 0
                st.metric("Progress", f"{progress_pct:.1f}%")
                st.progress(min(progress_pct / 100, 1.0))
            
            with col3:
                st.metric("Saved", f"₹{goal.get('current_progress', 0):,.0f}")
                st.caption(f"Target: ₹{goal['target_amount']:,.0f}")
            
            with col4:
                if st.button("🗑️", key=f"del_goal_{idx}"):
                    st.session_state.guest_data['goals'].pop(idx)
                    
                    # Save execution
                    if st.session_state.get("user"):
                        from services.auth_service import AuthService
                        AuthService.save_guest_data(st.session_state.user["user_id"], st.session_state.guest_data)
                        
                    st.rerun()
                
                if st.button("✏️", key=f"edit_goal_{idx}"):
                    st.info("Edit feature coming soon!")
            
            # Goal timeline projection
            remaining = goal['target_amount'] - goal.get('current_progress', 0)
            required_monthly = goal.get('required_monthly', 0)
            
            if remaining > 0:
                proj_col1, proj_col2, proj_col3 = st.columns(3)
                
                with proj_col1:
                    st.caption("📊 Required Monthly")
                    st.write(f"**₹{required_monthly:,.0f}**")
                
                with proj_col2:
                    st.caption("💰 Remaining")
                    st.write(f"**₹{remaining:,.0f}**")
                
                with proj_col3:
                    if monthly_surplus > 0:
                        realistic_months = remaining / monthly_surplus
                        realistic_date = (datetime.now() + timedelta(days=realistic_months*30)).strftime("%Y-%m-%d")
                        st.caption("⏱️ Realistic Completion")
                        st.write(f"**{realistic_date}**")
                        
                        # Show if achievable
                        target_date_obj = datetime.strptime(goal['target_date'], "%Y-%m-%d")
                        realistic_date_obj = datetime.strptime(realistic_date, "%Y-%m-%d")
                        
                        if realistic_date_obj <= target_date_obj:
                            st.success("✅ On track!")
                        else:
                            days_over = (realistic_date_obj - target_date_obj).days
                            st.warning(f"⚠️ {days_over} days over target")
            else:
                st.success("🎉 Goal achieved!")
            
            st.markdown("---")
else:
    st.info("📝 No goals added yet. Add your first financial goal above!")
    
    # Suggested goals based on analysis
    if 'guest_data' in st.session_state and 'analysis' in st.session_state.guest_data:
        st.markdown("### 💡 Suggested Goals")
        analysis = st.session_state.guest_data['analysis']
        metrics = analysis['metrics']
        
        suggested = []
        
        # Emergency fund suggestion
        if metrics.get('emergency_months', 0) < 6:
            target = st.session_state.guest_data['snapshot']['monthly_expenses'] * 6
            current = st.session_state.guest_data['snapshot']['current_savings']
            suggested.append({
                'name': 'Emergency Fund (6 months)',
                'target': target,
                'current': current,
                'priority': 'High'
            })
        
        # Debt payoff suggestion
        if metrics.get('total_liabilities', 0) > 0:
            suggested.append({
                'name': 'Become Debt-Free',
                'target': metrics['total_liabilities'],
                'current': 0,
                'priority': 'High'
            })
        
        if suggested:
            for sug in suggested:
                with st.expander(f"**{sug['name']}** - Priority: {sug['priority']}"):
                    st.write(f"Target: ₹{sug['target']:,.0f}")
                    st.write(f"Current: ₹{sug['current']:,.0f}")
                    if st.button(f"Add this goal", key=f"add_sug_{sug['name']}"):
                        st.info("Click '➕ Add New Goal' above and fill in the details!")

# Footer action
st.markdown("---")
if st.button("📊 View Financial Analysis", use_container_width=True):
    st.switch_page("pages/2_dashboard.py")
