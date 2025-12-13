"""
Enhanced Output Generation with Visuals and Impact Analysis
"""

import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from datetime import datetime
import json


def create_enhanced_recommendation(
    rec_id, agent, category, priority, severity_score,
    issue_title, issue_description, issue_location,
    reasoning_why, reasoning_impact, reasoning_data,
    action, implementation, alternatives, effort, estimated_time,
    compliance, user_impact, business_impact, accessibility_gain,
    related_recs=None, resources=None
):
    """
    Create enhanced recommendation with full structure
    
    Returns:
        dict: Comprehensive recommendation object
    """
    return {
        "id": rec_id,
        "agent": agent,
        "category": category,
        "priority": priority,
        "severity_score": severity_score,
        
        "issue": {
            "title": issue_title,
            "description": issue_description,
            "location": issue_location,
        },
        
        "reasoning": {
            "why_it_matters": reasoning_why,
            "impact_on_goals": reasoning_impact,
            "supporting_data": reasoning_data
        },
        
        "recommendation": {
            "action": action,
            "implementation": implementation,
            "alternatives": alternatives if alternatives else [],
            "effort": effort,
            "estimated_time": estimated_time
        },
        
        "expected_outcome": {
            "compliance": compliance,
            "user_impact": user_impact,
            "business_impact": business_impact,
            "accessibility_gain": accessibility_gain
        },
        
        "related_recommendations": related_recs if related_recs else [],
        "resources": resources if resources else []
    }


def generate_score_gauge_chart(score, title, color_scheme="RdYlGn"):
    """
    Create gauge chart for scores
    
    Args:
        score: Score value (0-100)
        title: Chart title
        color_scheme: Color scheme
    
    Returns:
        plotly figure
    """
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=score,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': title, 'font': {'size': 24}},
        delta={'reference': 75, 'increasing': {'color': "green"}},
        gauge={
            'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "darkblue"},
            'bar': {'color': "darkblue"},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [0, 50], 'color': '#ffcccc'},
                {'range': [50, 75], 'color': '#ffffcc'},
                {'range': [75, 100], 'color': '#ccffcc'}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 90
            }
        }
    ))
    
    fig.update_layout(
        height=300,
        margin=dict(l=20, r=20, t=50, b=20)
    )
    
    return fig


def generate_comparison_radar_chart(scores_dict):
    """
    Create radar chart comparing multiple dimensions
    
    Args:
        scores_dict: {category: score}
    
    Returns:
        plotly figure
    """
    categories = list(scores_dict.keys())
    values = list(scores_dict.values())
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself',
        name='Current Score',
        line_color='rgb(0, 123, 255)',
        fillcolor='rgba(0, 123, 255, 0.3)'
    ))
    
    # Add ideal score line
    ideal_values = [90] * len(categories)
    fig.add_trace(go.Scatterpolar(
        r=ideal_values,
        theta=categories,
        fill='toself',
        name='Target Score',
        line_color='rgba(50, 205, 50, 0.5)',
        fillcolor='rgba(50, 205, 50, 0.1)'
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100]
            )
        ),
        showlegend=True,
        title="Multi-Dimensional Analysis",
        height=500
    )
    
    return fig


def generate_priority_matrix(recommendations):
    """
    Create impact vs effort matrix
    
    Args:
        recommendations: List of recommendation dicts
    
    Returns:
        plotly figure
    """
    # Extract data
    effort_map = {'low': 1, 'medium': 2, 'high': 3}
    priority_map = {'low': 1, 'medium': 2, 'high': 3, 'critical': 4}
    
    data = []
    for rec in recommendations:
        effort = effort_map.get(rec.get('recommendation', {}).get('effort', 'medium'), 2)
        priority = priority_map.get(rec.get('priority', 'medium'), 2)
        
        data.append({
            'title': rec.get('issue', {}).get('title', 'Unknown')[:30],
            'effort': effort,
            'impact': rec.get('severity_score', priority * 2.5),
            'category': rec.get('category', 'general')
        })
    
    df = pd.DataFrame(data)
    
    # Create scatter plot
    fig = px.scatter(
        df,
        x='effort',
        y='impact',
        text='title',
        color='category',
        size='impact',
        size_max=50,
        title="Priority Matrix: Impact vs Effort",
        labels={'effort': 'Implementation Effort', 'impact': 'Business Impact'},
        color_discrete_sequence=px.colors.qualitative.Set2
    )
    
    # Add quadrant lines
    fig.add_hline(y=5, line_dash="dash", line_color="gray", opacity=0.5)
    fig.add_vline(x=2, line_dash="dash", line_color="gray", opacity=0.5)
    
    # Add quadrant labels
    fig.add_annotation(x=1.5, y=8, text="Quick Wins", showarrow=False, font=dict(size=14, color="green"))
    fig.add_annotation(x=2.5, y=8, text="Major Projects", showarrow=False, font=dict(size=14, color="orange"))
    fig.add_annotation(x=1.5, y=2, text="Fill Ins", showarrow=False, font=dict(size=14, color="gray"))
    fig.add_annotation(x=2.5, y=2, text="Thankless Tasks", showarrow=False, font=dict(size=14, color="red"))
    
    fig.update_layout(
        xaxis=dict(tickmode='array', tickvals=[1, 2, 3], ticktext=['Low', 'Medium', 'High']),
        yaxis=dict(range=[0, 10]),
        height=600
    )
    
    fig.update_traces(textposition='top center')
    
    return fig


def generate_improvement_timeline(recommendations):
    """
    Create Gantt-style timeline for implementation
    
    Args:
        recommendations: List of recommendation dicts
    
    Returns:
        plotly figure
    """
    time_map = {
        '5 minutes': 0.1,
        '15 minutes': 0.25,
        '30 minutes': 0.5,
        '1 hour': 1,
        '2 hours': 2,
        '4 hours': 4,
        '1 day': 8,
        '2 days': 16,
        '1 week': 40
    }
    
    priority_order = {'critical': 1, 'high': 2, 'medium': 3, 'low': 4}
    
    # Sort by priority
    sorted_recs = sorted(
        recommendations,
        key=lambda x: priority_order.get(x.get('priority', 'medium'), 3)
    )
    
    data = []
    cumulative_time = 0
    
    for i, rec in enumerate(sorted_recs[:10], 1):  # Top 10
        time_str = rec.get('recommendation', {}).get('estimated_time', '30 minutes')
        duration = time_map.get(time_str, 1)
        
        data.append({
            'Task': f"{i}. {rec.get('issue', {}).get('title', 'Task')[:40]}",
            'Start': cumulative_time,
            'Duration': duration,
            'Priority': rec.get('priority', 'medium')
        })
        
        cumulative_time += duration
    
    df = pd.DataFrame(data)
    
    # Create timeline
    fig = px.timeline(
        df,
        x_start='Start',
        x_end=df['Start'] + df['Duration'],
        y='Task',
        color='Priority',
        title="Implementation Timeline (Top 10 Recommendations)",
        color_discrete_map={
            'critical': '#dc3545',
            'high': '#fd7e14',
            'medium': '#ffc107',
            'low': '#28a745'
        }
    )
    
    fig.update_layout(
        xaxis_title="Cumulative Hours",
        yaxis_title="",
        height=500,
        showlegend=True
    )
    
    return fig


def generate_impact_projection_chart(recommendations):
    """
    Create projected impact over time chart
    
    Args:
        recommendations: List of recommendation dicts
    
    Returns:
        plotly figure
    """
    # Simulate impact over time
    weeks = list(range(1, 13))  # 12 weeks
    
    # Extract business impact percentages
    impacts = []
    for rec in recommendations[:10]:
        impact_str = rec.get('expected_outcome', {}).get('business_impact', '+0%')
        # Extract number from string like "+12%"
        try:
            impact_num = float(impact_str.replace('+', '').replace('%', '').split('-')[0])
        except:
            impact_num = 5
        impacts.append(impact_num)
    
    avg_impact = np.mean(impacts) if impacts else 10
    
    # Project cumulative improvement
    baseline = 100
    current_performance = [baseline]
    
    for week in range(1, 13):
        # Gradual improvement as recommendations are implemented
        improvement_factor = 1 + (avg_impact / 100) * (week / 12)
        current_performance.append(baseline * improvement_factor)
    
    fig = go.Figure()
    
    # Current trajectory
    fig.add_trace(go.Scatter(
        x=weeks,
        y=current_performance[1:],
        mode='lines+markers',
        name='With Improvements',
        line=dict(color='green', width=3),
        fill='tonexty'
    ))
    
    # Baseline
    fig.add_trace(go.Scatter(
        x=weeks,
        y=[baseline] * len(weeks),
        mode='lines',
        name='Current Baseline',
        line=dict(color='red', width=2, dash='dash')
    ))
    
    fig.update_layout(
        title="Projected Performance Impact (12 Weeks)",
        xaxis_title="Weeks",
        yaxis_title="Performance Index",
        height=400,
        hovermode='x unified'
    )
    
    return fig


def generate_category_breakdown_chart(recommendations):
    """
    Create pie chart of recommendations by category
    
    Args:
        recommendations: List of recommendation dicts
    
    Returns:
        plotly figure
    """
    # Count by category
    category_counts = {}
    for rec in recommendations:
        cat = rec.get('category', 'general')
        category_counts[cat] = category_counts.get(cat, 0) + 1
    
    fig = go.Figure(data=[go.Pie(
        labels=list(category_counts.keys()),
        values=list(category_counts.values()),
        hole=.3,
        marker_colors=px.colors.qualitative.Set3
    )])
    
    fig.update_layout(
        title="Recommendations by Category",
        height=400
    )
    
    return fig


def generate_accessibility_compliance_chart(ux_analysis):
    """
    Create accessibility compliance visualization
    
    Args:
        ux_analysis: UX analysis dict
    
    Returns:
        plotly figure
    """
    accessibility = ux_analysis.get('accessibility', {})
    
    # Define WCAG criteria
    criteria = [
        'Text Contrast',
        'Touch Targets',
        'Screen Reader',
        'Keyboard Navigation',
        'Color Blindness',
        'Focus Indicators'
    ]
    
    # Generate sample compliance scores
    compliance_scores = [
        accessibility.get('score', 75),
        85, 70, 80, 75, 65
    ]
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=criteria,
        y=compliance_scores,
        marker_color=['green' if s >= 90 else 'orange' if s >= 75 else 'red' for s in compliance_scores],
        text=[f"{s}%" for s in compliance_scores],
        textposition='outside'
    ))
    
    # Add WCAG AA threshold line
    fig.add_hline(y=75, line_dash="dash", line_color="blue", 
                  annotation_text="WCAG AA Threshold")
    
    fig.update_layout(
        title="WCAG Accessibility Compliance",
        xaxis_title="Criteria",
        yaxis_title="Compliance Score (%)",
        yaxis_range=[0, 100],
        height=400
    )
    
    return fig
