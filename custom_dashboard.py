import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from data_fetcher import WorldBankData, INDICATORS, SDG_INDICATORS, COMPARISON_COUNTRIES

def get_theme_colors():
    """Get color scheme based on current theme."""
    if 'dark_mode' not in st.session_state:
        st.session_state.dark_mode = False
    
    if st.session_state.dark_mode:
        return {
            'bg': '#1e1e1e',
            'text': '#e0e0e0',
            'primary': '#00b06f',
            'grid': '#3d3d3d',
            'plot_bg': 'rgba(45,45,45,0.5)',
            'paper_bg': 'rgba(30,30,30,0)'
        }
    else:
        return {
            'bg': '#ffffff',
            'text': '#000000',
            'primary': '#008751',
            'grid': '#f0f0f0',
            'plot_bg': 'rgba(0,0,0,0)',
            'paper_bg': 'rgba(0,0,0,0)'
        }

def show_custom_dashboard():
    """Display custom dashboard builder where users can select their own metrics."""
    st.markdown('<div class="section-title">🎨 Custom Dashboard Builder</div>', unsafe_allow_html=True)
    
    st.info("Build your personalized dashboard by selecting the metrics that matter most to you.")
    
    st.markdown("### Select Your Metrics")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown("#### Available Indicators")
        
        selected_indicators = st.multiselect(
            "Choose indicators to display:",
            options=list(INDICATORS.keys()),
            default=['gdp', 'population', 'gdp_growth', 'life_expectancy'],
            format_func=lambda x: x.replace('_', ' ').title(),
            help="Select multiple indicators to track"
        )
        
        st.markdown("#### Display Options")
        
        time_range = st.slider(
            "Year Range",
            min_value=2000,
            max_value=2025,
            value=(2010, 2025),
            help="Select the time period for analysis"
        )
        
        chart_type = st.radio(
            "Chart Type",
            options=["Line Chart", "Bar Chart", "Area Chart"],
            help="Choose how to visualize the data"
        )
        
        show_comparison = st.checkbox(
            "Compare with other countries",
            value=False,
            help="Add peer African nations for comparison"
        )
        
        if show_comparison:
            selected_countries = st.multiselect(
                "Select countries:",
                options=list(COMPARISON_COUNTRIES.keys()),
                default=['NGA', 'ZAF', 'KEN'],
                format_func=lambda x: COMPARISON_COUNTRIES[x]
            )
        else:
            selected_countries = ['NGA']
    
    with col2:
        st.markdown("#### Your Custom Dashboard")
        
        if not selected_indicators:
            st.warning("Please select at least one indicator to display")
        else:
            for indicator_name in selected_indicators:
                indicator_code = INDICATORS[indicator_name]
                
                st.markdown(f"##### {indicator_name.replace('_', ' ').title()}")
                
                with st.spinner(f'Loading {indicator_name}...'):
                    if show_comparison and len(selected_countries) > 1:
                        df = WorldBankData.get_multi_country_indicator(
                            selected_countries, 
                            indicator_code, 
                            time_range[0], 
                            time_range[1]
                        )
                    else:
                        df = WorldBankData.get_indicator_data(
                            'NGA', 
                            indicator_code, 
                            time_range[0], 
                            time_range[1]
                        )
                    
                    if not df.empty:
                        fig = create_custom_chart(df, indicator_name, chart_type, show_comparison)
                        if fig:
                            st.plotly_chart(fig, width='stretch')
                            
                            csv = df.to_csv(index=False).encode('utf-8')
                            st.download_button(
                                label=f"📥 Download {indicator_name} data",
                                data=csv,
                                file_name=f'{indicator_name}_{time_range[0]}_{time_range[1]}.csv',
                                mime='text/csv',
                                key=f'download_{indicator_name}'
                            )
                    else:
                        st.info(f"No data available for {indicator_name}")
                
                st.markdown("---")
    
    st.markdown("### 📊 Summary Statistics")
    
    if selected_indicators:
        summary_data = []
        for indicator_name in selected_indicators:
            indicator_code = INDICATORS[indicator_name]
            val, year = WorldBankData.get_latest_value('NGA', indicator_code)
            if val is not None:
                df_hist = WorldBankData.get_indicator_data('NGA', indicator_code, time_range[0], time_range[1])
                if not df_hist.empty:
                    summary_data.append({
                        'Indicator': indicator_name.replace('_', ' ').title(),
                        'Latest Value': f"{val:.2f}",
                        'Year': year,
                        'Min': f"{df_hist['value'].min():.2f}",
                        'Max': f"{df_hist['value'].max():.2f}",
                        'Average': f"{df_hist['value'].mean():.2f}"
                    })
        
        if summary_data:
            summary_df = pd.DataFrame(summary_data)
            st.dataframe(summary_df, width='stretch', hide_index=True)
            
            csv = summary_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download Summary Statistics",
                data=csv,
                file_name=f'summary_stats_{time_range[0]}_{time_range[1]}.csv',
                mime='text/csv',
            )

def create_custom_chart(df, indicator_name, chart_type, multi_country=False):
    """Create custom chart based on user selection."""
    if df.empty:
        return None
    
    theme = get_theme_colors()
    colors = {'NGA': theme['primary'], 'ZAF': '#FF6B6B', 'EGY': '#4ECDC4', 
              'KEN': '#FFD93D', 'GHA': '#A8E6CF', 'ETH': '#FFB6B9'}
    
    fig = go.Figure()
    
    if multi_country and 'country_code' in df.columns:
        for country_code in df['country_code'].unique():
            country_data = df[df['country_code'] == country_code]
            color = colors.get(country_code, '#888888')
            country_name = COMPARISON_COUNTRIES.get(country_code, country_code)
            
            if chart_type == "Line Chart":
                fig.add_trace(go.Scatter(
                    x=country_data['year'],
                    y=country_data['value'],
                    mode='lines+markers',
                    name=country_name,
                    line=dict(color=color, width=2),
                    marker=dict(size=6),
                    hovertemplate=f'<b>{country_name}</b><br>Year: %{{x}}<br>Value: %{{y:.2f}}<extra></extra>'
                ))
            elif chart_type == "Bar Chart":
                fig.add_trace(go.Bar(
                    x=country_data['year'],
                    y=country_data['value'],
                    name=country_name,
                    marker=dict(color=color),
                    hovertemplate=f'<b>{country_name}</b><br>Year: %{{x}}<br>Value: %{{y:.2f}}<extra></extra>'
                ))
            else:  # Area Chart
                fig.add_trace(go.Scatter(
                    x=country_data['year'],
                    y=country_data['value'],
                    mode='lines',
                    name=country_name,
                    fill='tonexty' if country_code != df['country_code'].unique()[0] else 'tozeroy',
                    line=dict(color=color),
                    hovertemplate=f'<b>{country_name}</b><br>Year: %{{x}}<br>Value: %{{y:.2f}}<extra></extra>'
                ))
    else:
        indicator_title = indicator_name.replace('_', ' ').title()
        if chart_type == "Line Chart":
            fig.add_trace(go.Scatter(
                x=df['year'],
                y=df['value'],
                mode='lines+markers',
                name=indicator_title,
                line=dict(color=theme['primary'], width=3),
                marker=dict(size=8),
                hovertemplate='<b>Year:</b> %{x}<br><b>Value:</b> %{y:.2f}<extra></extra>'
            ))
        elif chart_type == "Bar Chart":
            fig.add_trace(go.Bar(
                x=df['year'],
                y=df['value'],
                name=indicator_title,
                marker=dict(color=theme['primary']),
                hovertemplate='<b>Year:</b> %{x}<br><b>Value:</b> %{y:.2f}<extra></extra>'
            ))
        else:  # Area Chart
            fig.add_trace(go.Scatter(
                x=df['year'],
                y=df['value'],
                mode='lines',
                name=indicator_title,
                fill='tozeroy',
                line=dict(color=theme['primary']),
                hovertemplate='<b>Year:</b> %{x}<br><b>Value:</b> %{y:.2f}<extra></extra>'
            ))
    
    fig.update_layout(
        title=indicator_name.replace('_', ' ').title(),
        xaxis_title="Year",
        yaxis_title="Value",
        hovermode='x unified',
        plot_bgcolor=theme['plot_bg'],
        paper_bgcolor=theme['paper_bg'],
        font=dict(size=12, color=theme['text']),
        height=400,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.3,
            xanchor="center",
            x=0.5,
            font=dict(color=theme['text'])
        ) if multi_country else dict(),
        modebar=dict(
            bgcolor='rgba(0,0,0,0)',
            color=theme['text'],
            activecolor=theme['primary']
        )
    )
    
    fig.update_xaxes(showgrid=True, gridcolor=theme['grid'])
    fig.update_yaxes(showgrid=True, gridcolor=theme['grid'])
    
    return fig
