import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from data_fetcher import WorldBankData, INDICATORS
from ui_helpers import get_theme_colors, render_chart

def show_predictive_analytics():
    """Display predictive analytics with trend projections."""
    st.markdown('<div class="section-title">🔮 Predictive Analytics & Trend Projections</div>', unsafe_allow_html=True)
    
    st.info("View projected trends for key development indicators based on historical data using linear regression.")
    
    st.markdown("### Select Indicator for Prediction")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        selected_indicator = st.selectbox(
            "Choose an indicator:",
            options=list(INDICATORS.keys()),
            index=list(INDICATORS.keys()).index('gdp'),
            format_func=lambda x: x.replace('_', ' ').title()
        )
        
        historical_years = st.slider(
            "Historical data years",
            min_value=5,
            max_value=20,
            value=15,
            help="Number of years of historical data to use for prediction"
        )
        
        forecast_years = st.slider(
            "Forecast years ahead",
            min_value=1,
            max_value=10,
            value=5,
            help="Number of years to project into the future"
        )
        
        show_confidence = st.checkbox(
            "Show confidence interval",
            value=True,
            help="Display prediction confidence bands"
        )
    
    with col2:
        st.markdown(f"### {selected_indicator.replace('_', ' ').title()} - Prediction")
        
        indicator_code = INDICATORS[selected_indicator]
        current_year = 2025
        start_year = current_year - historical_years
        
        with st.spinner('Loading historical data and generating predictions...'):
            df = WorldBankData.get_indicator_data('NGA', indicator_code, start_year, current_year)
            
            if not df.empty and len(df) >= 3:
                predictions_df = generate_predictions(df, forecast_years)
                
                if predictions_df is not None:
                    fig = create_prediction_chart(
                        df, 
                        predictions_df, 
                        selected_indicator, 
                        show_confidence
                    )
                    if fig:
                        render_chart(fig)
                        
                        st.markdown("#### Prediction Summary")
                        
                        latest_actual = df.iloc[-1]['value']
                        latest_year = int(df.iloc[-1]['year'])
                        future_value = predictions_df.iloc[-1]['predicted']
                        future_year = int(predictions_df.iloc[-1]['year'])
                        
                        change = ((future_value - latest_actual) / latest_actual) * 100
                        
                        col_a, col_b, col_c = st.columns(3)
                        with col_a:
                            st.metric(
                                label=f"Current ({latest_year})",
                                value=f"{latest_actual:.2f}"
                            )
                        with col_b:
                            st.metric(
                                label=f"Projected ({future_year})",
                                value=f"{future_value:.2f}",
                                delta=f"{change:.1f}%"
                            )
                        with col_c:
                            trend = "Increasing" if change > 0 else "Decreasing"
                            st.metric(
                                label="Trend Direction",
                                value=trend
                            )
                        
                        st.markdown("#### Download Predictions")
                        combined_df = pd.DataFrame({
                            'Year': list(df['year']) + list(predictions_df['year']),
                            'Actual': list(df['value']) + [None] * len(predictions_df),
                            'Predicted': [None] * len(df) + list(predictions_df['predicted']),
                            'Type': ['Historical'] * len(df) + ['Forecast'] * len(predictions_df)
                        })
                        
                        csv = combined_df.to_csv(index=False).encode('utf-8')
                        st.download_button(
                            label="📥 Download Forecast Data",
                            data=csv,
                            file_name=f'{selected_indicator}_forecast.csv',
                            mime='text/csv'
                        )
                    else:
                        st.error("Could not generate prediction chart")
                else:
                    st.error("Unable to generate predictions with current data")
            else:
                st.warning(f"Insufficient historical data for {selected_indicator}. Need at least 3 data points.")
    
    st.markdown("---")
    st.markdown("### 📊 Multi-Indicator Forecast Comparison")
    
    st.markdown("Compare projected trends across multiple indicators")
    
    selected_indicators_multi = st.multiselect(
        "Select indicators to compare:",
        options=list(INDICATORS.keys()),
        default=['gdp_growth', 'population', 'life_expectancy'],
        format_func=lambda x: x.replace('_', ' ').title()
    )
    
    if selected_indicators_multi:
        forecast_data = []
        for indicator in selected_indicators_multi:
            indicator_code = INDICATORS[indicator]
            df = WorldBankData.get_indicator_data('NGA', indicator_code, 2010, 2025)
            if not df.empty and len(df) >= 3:
                predictions_df = generate_predictions(df, 5)
                if predictions_df is not None:
                    latest_actual = df.iloc[-1]['value']
                    future_value = predictions_df.iloc[-1]['predicted']
                    change = ((future_value - latest_actual) / latest_actual) * 100
                    
                    forecast_data.append({
                        'Indicator': indicator.replace('_', ' ').title(),
                        'Current Value': f"{latest_actual:.2f}",
                        '5-Year Forecast': f"{future_value:.2f}",
                        'Projected Change (%)': f"{change:.1f}%"
                    })
        
        if forecast_data:
            forecast_df = pd.DataFrame(forecast_data)
            st.dataframe(forecast_df, width='stretch', hide_index=True)

def generate_predictions(df, forecast_years=5):
    """Generate predictions using simple linear regression."""
    try:
        if df.empty or len(df) < 3:
            return None
        
        df = df.sort_values('year')
        
        X = df['year'].values
        y = df['value'].values
        
        n = len(X)
        X_mean = np.mean(X)
        y_mean = np.mean(y)
        
        numerator = np.sum((X - X_mean) * (y - y_mean))
        denominator = np.sum((X - X_mean) ** 2)
        
        if denominator == 0:
            return None
        
        slope = numerator / denominator
        intercept = y_mean - slope * X_mean
        
        last_year = int(X[-1])
        future_years = np.array([last_year + i for i in range(1, forecast_years + 1)])
        predictions = slope * future_years + intercept
        
        residuals = y - (slope * X + intercept)
        std_error = np.sqrt(np.sum(residuals ** 2) / (n - 2))
        
        predictions_df = pd.DataFrame({
            'year': future_years,
            'predicted': predictions,
            'lower_bound': predictions - 1.96 * std_error,
            'upper_bound': predictions + 1.96 * std_error
        })
        
        return predictions_df
    
    except Exception as e:
        st.error(f"Error generating predictions: {str(e)}")
        return None

def create_prediction_chart(historical_df, predictions_df, indicator_name, show_confidence=True):
    """Create chart showing historical data and predictions."""
    if historical_df.empty or predictions_df is None:
        return None
    
    theme = get_theme_colors()
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=historical_df['year'],
        y=historical_df['value'],
        mode='lines+markers',
        name='Historical Data',
        line=dict(color=theme['primary'], width=3, shape='spline'),
        marker=dict(size=7),
        hovertemplate='<b>Historical</b><br>Year: %{x}<br>Value: %{y:,.2f}<extra></extra>'
    ))

    fig.add_trace(go.Scatter(
        x=predictions_df['year'],
        y=predictions_df['predicted'],
        mode='lines+markers',
        name='Forecast',
        line=dict(color='#FF6B6B', width=3, dash='dash'),
        marker=dict(size=8, symbol='diamond-open'),
        hovertemplate='<b>Forecast</b><br>Year: %{x}<br>Predicted: %{y:,.2f}<extra></extra>'
    ))
    
    if show_confidence:
        upper_years = predictions_df['year'].tolist()
        lower_years = predictions_df['year'].tolist()[::-1]
        upper_bounds = predictions_df['upper_bound'].tolist()
        lower_bounds = predictions_df['lower_bound'].tolist()[::-1]
        
        fig.add_trace(go.Scatter(
            x=upper_years + lower_years,
            y=upper_bounds + lower_bounds,
            fill='toself',
            fillcolor='rgba(255, 107, 107, 0.2)',
            line=dict(color='rgba(255,255,255,0)'),
            showlegend=True,
            name='95% Confidence Interval',
            hovertemplate='<b>Confidence Interval</b><br>Year: %{x}<br>Range: %{y:.2f}<extra></extra>'
        ))
    
    fig.update_layout(
        title=f"{indicator_name.replace('_', ' ').title()} - Historical & Forecast",
        xaxis_title="Year",
        yaxis_title="Value",
        hovermode='x unified',
        plot_bgcolor=theme['plot_bg'],
        paper_bgcolor=theme['paper_bg'],
        font=dict(size=12, color=theme['text']),
        height=500,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.2,
            xanchor="center",
            x=0.5,
            font=dict(color=theme['text'])
        ),
        hoverlabel=dict(bgcolor=theme['secondary_bg'], font=dict(color=theme['text'])),
        margin=dict(l=40, r=20, t=60, b=80),
        transition=dict(duration=400),
        uirevision=indicator_name,
    )

    fig.update_xaxes(showgrid=True, gridcolor=theme['grid'])
    fig.update_yaxes(showgrid=True, gridcolor=theme['grid'])
    
    return fig
