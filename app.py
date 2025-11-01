import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from data_fetcher import WorldBankData, INDICATORS, COMPARISON_COUNTRIES, SDG_INDICATORS
from custom_dashboard import show_custom_dashboard
from predictions import show_predictive_analytics

st.set_page_config(
    page_title="9jaStats - Nigeria Development Dashboard",
    page_icon="🇳🇬",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
        .main-header {
            font-size: 2.5rem;
            font-weight: 700;
            color: #008751;
            text-align: center;
            margin-bottom: 0.5rem;
        }
        .sub-header {
            font-size: 1.2rem;
            color: #666;
            text-align: center;
            margin-bottom: 2rem;
        }
        .metric-card {
            background: linear-gradient(135deg, #008751 0%, #00b06f 100%);
            padding: 1.5rem;
            border-radius: 10px;
            color: white;
            text-align: center;
            margin-bottom: 1rem;
        }
        .section-title {
            color: #008751;
            font-size: 1.8rem;
            font-weight: 600;
            margin-top: 2rem;
            margin-bottom: 1rem;
            border-bottom: 3px solid #008751;
            padding-bottom: 0.5rem;
        }
        @media (max-width: 768px) {
            .main-header {
                font-size: 1.8rem;
            }
            .sub-header {
                font-size: 1rem;
            }
        }
    </style>
""", unsafe_allow_html=True)

def format_number(num, prefix="", suffix="", decimals=2):
    """Format large numbers for display."""
    if num is None:
        return "N/A"
    
    if abs(num) >= 1e12:
        return f"{prefix}{num/1e12:.{decimals}f}T{suffix}"
    elif abs(num) >= 1e9:
        return f"{prefix}{num/1e9:.{decimals}f}B{suffix}"
    elif abs(num) >= 1e6:
        return f"{prefix}{num/1e6:.{decimals}f}M{suffix}"
    elif abs(num) >= 1e3:
        return f"{prefix}{num/1e3:.{decimals}f}K{suffix}"
    else:
        return f"{prefix}{num:.{decimals}f}{suffix}"

def export_to_csv(df, filename):
    """Convert dataframe to CSV for download."""
    if df.empty:
        return None
    return df.to_csv(index=False).encode('utf-8')

def create_trend_chart(df, title, yaxis_title, color='#008751'):
    """Create a line chart for trend data."""
    if df.empty:
        return None
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df['year'],
        y=df['value'],
        mode='lines+markers',
        name=title,
        line=dict(color=color, width=3),
        marker=dict(size=8, color=color),
        hovertemplate='<b>Year:</b> %{x}<br><b>Value:</b> %{y:.2f}<extra></extra>'
    ))
    
    fig.update_layout(
        title=title,
        xaxis_title="Year",
        yaxis_title=yaxis_title,
        hovermode='closest',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(size=12),
        height=400,
        margin=dict(l=50, r=50, t=50, b=50)
    )
    
    fig.update_xaxes(showgrid=True, gridcolor='#f0f0f0')
    fig.update_yaxes(showgrid=True, gridcolor='#f0f0f0')
    
    return fig

def create_comparison_chart(df, title, yaxis_title, latest_year=True):
    """Create a bar chart comparing multiple countries."""
    if df.empty:
        return None
    
    if latest_year:
        df = df.sort_values('year').groupby('country_code').tail(1)
    
    df = df.sort_values('value', ascending=True)
    
    colors = ['#008751' if code == 'NGA' else '#cccccc' for code in df['country_code']]
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=df['value'],
        y=df['country'],
        orientation='h',
        marker=dict(color=colors),
        text=df['value'].round(2),
        textposition='auto',
        hovertemplate='<b>%{y}</b><br>Value: %{x:.2f}<br>Year: %{customdata[0]}<extra></extra>',
        customdata=df[['year']].values
    ))
    
    fig.update_layout(
        title=title,
        xaxis_title=yaxis_title,
        yaxis_title="",
        hovermode='closest',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(size=12),
        height=400,
        margin=dict(l=150, r=50, t=50, b=50),
        showlegend=False
    )
    
    fig.update_xaxes(showgrid=True, gridcolor='#f0f0f0')
    
    return fig

def create_multi_line_chart(df, title, yaxis_title):
    """Create a multi-line chart for country comparisons over time."""
    if df.empty:
        return None
    
    fig = go.Figure()
    
    colors = {'NGA': '#008751', 'ZAF': '#FF6B6B', 'EGY': '#4ECDC4', 
              'KEN': '#FFD93D', 'GHA': '#A8E6CF', 'ETH': '#FFB6B9'}
    
    for country_code in df['country_code'].unique():
        country_data = df[df['country_code'] == country_code]
        country_name = COMPARISON_COUNTRIES.get(country_code, country_code)
        fig.add_trace(go.Scatter(
            x=country_data['year'],
            y=country_data['value'],
            mode='lines+markers',
            name=country_name,
            line=dict(color=colors.get(country_code, '#888888'), width=2),
            marker=dict(size=6),
            hovertemplate=f'<b>{country_name}</b><br>Year: %{{x}}<br>Value: %{{y:.2f}}<extra></extra>'
        ))
    
    fig.update_layout(
        title=title,
        xaxis_title="Year",
        yaxis_title=yaxis_title,
        hovermode='x unified',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(size=12),
        height=450,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.3,
            xanchor="center",
            x=0.5
        )
    )
    
    fig.update_xaxes(showgrid=True, gridcolor='#f0f0f0')
    fig.update_yaxes(showgrid=True, gridcolor='#f0f0f0')
    
    return fig

def show_overview():
    """Display overview dashboard with key indicators."""
    st.markdown('<h1 class="main-header">🇳🇬 9jaStats</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Nigeria\'s National Development & Global Competitiveness Dashboard</p>', unsafe_allow_html=True)
    
    st.markdown('<div class="section-title">📊 Key Performance Indicators</div>', unsafe_allow_html=True)
    
    with st.spinner('Loading key indicators...'):
        col1, col2, col3, col4 = st.columns(4)
        
        gdp_val, gdp_year = WorldBankData.get_latest_value('NGA', INDICATORS['gdp'])
        pop_val, pop_year = WorldBankData.get_latest_value('NGA', INDICATORS['population'])
        gdp_growth_val, gdp_growth_year = WorldBankData.get_latest_value('NGA', INDICATORS['gdp_growth'])
        life_exp_val, life_exp_year = WorldBankData.get_latest_value('NGA', INDICATORS['life_expectancy'])
        
        with col1:
            st.metric(
                label="GDP (Current US$)",
                value=format_number(gdp_val, prefix="$"),
                delta=f"Year: {gdp_year}" if gdp_year else None
            )
        
        with col2:
            st.metric(
                label="Population",
                value=format_number(pop_val),
                delta=f"Year: {pop_year}" if pop_year else None
            )
        
        with col3:
            st.metric(
                label="GDP Growth Rate",
                value=f"{gdp_growth_val:.2f}%" if gdp_growth_val is not None else "N/A",
                delta=f"Year: {gdp_growth_year}" if gdp_growth_year else None
            )
        
        with col4:
            st.metric(
                label="Life Expectancy",
                value=f"{life_exp_val:.1f} years" if life_exp_val is not None else "N/A",
                delta=f"Year: {life_exp_year}" if life_exp_year else None
            )
    
    st.markdown('<div class="section-title">📈 Economic Overview (Last 20 Years)</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        with st.spinner('Loading GDP data...'):
            gdp_df = WorldBankData.get_indicator_data('NGA', INDICATORS['gdp'], 2004, 2025)
            if not gdp_df.empty:
                fig = create_trend_chart(gdp_df, "Nigeria GDP Trend", "GDP (Current US$)", '#008751')
                if fig:
                    st.plotly_chart(fig, width='stretch')
            else:
                st.info("GDP data not available")
    
    with col2:
        with st.spinner('Loading GDP growth data...'):
            growth_df = WorldBankData.get_indicator_data('NGA', INDICATORS['gdp_growth'], 2004, 2025)
            if not growth_df.empty:
                fig = create_trend_chart(growth_df, "GDP Growth Rate (%)", "Annual % Growth", '#FF6B6B')
                if fig:
                    st.plotly_chart(fig, width='stretch')
            else:
                st.info("GDP growth data not available")
    
    st.markdown('<div class="section-title">👥 Social Indicators</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        elec_val, elec_year = WorldBankData.get_latest_value('NGA', INDICATORS['electricity_access'])
        st.metric(
            label="Electricity Access",
            value=f"{elec_val:.1f}%" if elec_val is not None else "N/A",
            delta=f"Year: {elec_year}" if elec_year else None
        )
    
    with col2:
        internet_val, internet_year = WorldBankData.get_latest_value('NGA', INDICATORS['internet_users'])
        st.metric(
            label="Internet Users",
            value=f"{internet_val:.1f}%" if internet_val is not None else "N/A",
            delta=f"Year: {internet_year}" if internet_year else None
        )
    
    with col3:
        mobile_val, mobile_year = WorldBankData.get_latest_value('NGA', INDICATORS['mobile_subscriptions'])
        st.metric(
            label="Mobile Subscriptions",
            value=f"{mobile_val:.1f} per 100" if mobile_val is not None else "N/A",
            delta=f"Year: {mobile_year}" if mobile_year else None
        )

def show_economic_development():
    """Display economic development section."""
    st.markdown('<div class="section-title">💰 Economic Development Analysis</div>', unsafe_allow_html=True)
    
    st.markdown("### GDP Per Capita Trend")
    with st.spinner('Loading GDP per capita data...'):
        gdp_pc_df = WorldBankData.get_indicator_data('NGA', INDICATORS['gdp_per_capita'], 2000, 2025)
        if not gdp_pc_df.empty:
            fig = create_trend_chart(gdp_pc_df, "GDP Per Capita", "Current US$", '#008751')
            if fig:
                st.plotly_chart(fig, width='stretch')
        else:
            st.info("GDP per capita data not available")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Sectoral Contribution to GDP")
        with st.spinner('Loading sectoral data...'):
            agr_val, agr_year = WorldBankData.get_latest_value('NGA', INDICATORS['agriculture_gdp'])
            ind_val, ind_year = WorldBankData.get_latest_value('NGA', INDICATORS['industry_gdp'])
            serv_val, serv_year = WorldBankData.get_latest_value('NGA', INDICATORS['services_gdp'])
            
            if agr_val is not None and ind_val is not None and serv_val is not None:
                sectors_df = pd.DataFrame({
                    'Sector': ['Agriculture', 'Industry', 'Services'],
                    'Percentage': [agr_val, ind_val, serv_val]
                })
                
                fig = px.pie(
                    sectors_df,
                    values='Percentage',
                    names='Sector',
                    title=f'Sectoral GDP Contribution ({max(agr_year, ind_year, serv_year)})',
                    color_discrete_sequence=['#008751', '#FFD93D', '#4ECDC4']
                )
                fig.update_layout(height=400)
                st.plotly_chart(fig, width='stretch')
            else:
                st.info("Sectoral data not available")
    
    with col2:
        st.markdown("### Inflation & Unemployment")
        with st.spinner('Loading inflation data...'):
            inflation_df = WorldBankData.get_indicator_data('NGA', INDICATORS['inflation'], 2010, 2025)
            if not inflation_df.empty:
                fig = create_trend_chart(inflation_df, "Inflation Rate", "Annual %", '#FF6B6B')
                if fig:
                    st.plotly_chart(fig, width='stretch')
            else:
                st.info("Inflation data not available")
    
    st.markdown("### Foreign Direct Investment (FDI)")
    with st.spinner('Loading FDI data...'):
        fdi_df = WorldBankData.get_indicator_data('NGA', INDICATORS['fdi'], 2005, 2025)
        if not fdi_df.empty:
            fig = create_trend_chart(fdi_df, "FDI Net Inflows", "Current US$", '#4ECDC4')
            if fig:
                st.plotly_chart(fig, width='stretch')
        else:
            st.info("FDI data not available")

def show_social_development():
    """Display social development section."""
    st.markdown('<div class="section-title">👨‍👩‍👧‍👦 Social Development Indicators</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Life Expectancy Trend")
        with st.spinner('Loading life expectancy data...'):
            life_exp_df = WorldBankData.get_indicator_data('NGA', INDICATORS['life_expectancy'], 2000, 2025)
            if not life_exp_df.empty:
                fig = create_trend_chart(life_exp_df, "Life Expectancy at Birth", "Years", '#008751')
                if fig:
                    st.plotly_chart(fig, width='stretch')
            else:
                st.info("Life expectancy data not available")
    
    with col2:
        st.markdown("### Infant Mortality Rate")
        with st.spinner('Loading infant mortality data...'):
            infant_mort_df = WorldBankData.get_indicator_data('NGA', INDICATORS['infant_mortality'], 2000, 2025)
            if not infant_mort_df.empty:
                fig = create_trend_chart(infant_mort_df, "Infant Mortality Rate", "Per 1,000 live births", '#FF6B6B')
                if fig:
                    st.plotly_chart(fig, width='stretch')
            else:
                st.info("Infant mortality data not available")
    
    st.markdown("### Education Enrollment")
    col1, col2 = st.columns(2)
    
    with col1:
        with st.spinner('Loading primary enrollment data...'):
            primary_df = WorldBankData.get_indicator_data('NGA', INDICATORS['school_enrollment_primary'], 2000, 2025)
            if not primary_df.empty:
                fig = create_trend_chart(primary_df, "Primary School Enrollment", "% Net", '#4ECDC4')
                if fig:
                    st.plotly_chart(fig, width='stretch')
            else:
                st.info("Primary enrollment data not available")
    
    with col2:
        with st.spinner('Loading secondary enrollment data...'):
            secondary_df = WorldBankData.get_indicator_data('NGA', INDICATORS['school_enrollment_secondary'], 2000, 2025)
            if not secondary_df.empty:
                fig = create_trend_chart(secondary_df, "Secondary School Enrollment", "% Net", '#FFD93D')
                if fig:
                    st.plotly_chart(fig, width='stretch')
            else:
                st.info("Secondary enrollment data not available")
    
    st.markdown("### Key Social Metrics")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        literacy_val, literacy_year = WorldBankData.get_latest_value('NGA', INDICATORS['literacy'])
        st.metric(
            label="Adult Literacy Rate",
            value=f"{literacy_val:.1f}%" if literacy_val is not None else "N/A",
            delta=f"Year: {literacy_year}" if literacy_year else None
        )
    
    with col2:
        water_val, water_year = WorldBankData.get_latest_value('NGA', INDICATORS['water_access'])
        st.metric(
            label="Safe Water Access",
            value=f"{water_val:.1f}%" if water_val is not None else "N/A",
            delta=f"Year: {water_year}" if water_year else None
        )
    
    with col3:
        poverty_val, poverty_year = WorldBankData.get_latest_value('NGA', INDICATORS['poverty_headcount'])
        st.metric(
            label="Poverty Rate ($2.15/day)",
            value=f"{poverty_val:.1f}%" if poverty_val is not None else "N/A",
            delta=f"Year: {poverty_year}" if poverty_year else None
        )

def show_infrastructure():
    """Display infrastructure and technology section."""
    st.markdown('<div class="section-title">🏗️ Infrastructure & Technology</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Electricity Access")
        with st.spinner('Loading electricity access data...'):
            elec_df = WorldBankData.get_indicator_data('NGA', INDICATORS['electricity_access'], 2000, 2025)
            if not elec_df.empty:
                fig = create_trend_chart(elec_df, "Access to Electricity", "% of Population", '#008751')
                if fig:
                    st.plotly_chart(fig, width='stretch')
            else:
                st.info("Electricity access data not available")
    
    with col2:
        st.markdown("### Internet Penetration")
        with st.spinner('Loading internet users data...'):
            internet_df = WorldBankData.get_indicator_data('NGA', INDICATORS['internet_users'], 2000, 2025)
            if not internet_df.empty:
                fig = create_trend_chart(internet_df, "Internet Users", "% of Population", '#4ECDC4')
                if fig:
                    st.plotly_chart(fig, width='stretch')
            else:
                st.info("Internet users data not available")
    
    st.markdown("### Mobile & Connectivity")
    col1, col2 = st.columns(2)
    
    with col1:
        with st.spinner('Loading mobile subscriptions data...'):
            mobile_df = WorldBankData.get_indicator_data('NGA', INDICATORS['mobile_subscriptions'], 2000, 2025)
            if not mobile_df.empty:
                fig = create_trend_chart(mobile_df, "Mobile Cellular Subscriptions", "Per 100 People", '#FFD93D')
                if fig:
                    st.plotly_chart(fig, width='stretch')
            else:
                st.info("Mobile subscriptions data not available")
    
    with col2:
        with st.spinner('Loading renewable energy data...'):
            renewable_df = WorldBankData.get_indicator_data('NGA', INDICATORS['renewable_energy'], 2000, 2025)
            if not renewable_df.empty:
                fig = create_trend_chart(renewable_df, "Renewable Energy Consumption", "% of Total", '#A8E6CF')
                if fig:
                    st.plotly_chart(fig, width='stretch')
            else:
                st.info("Renewable energy data not available")

def show_global_comparison():
    """Display global competitiveness comparison."""
    st.markdown('<div class="section-title">🌍 Global Competitiveness Analysis</div>', unsafe_allow_html=True)
    
    st.info("Comparing Nigeria with peer African nations: South Africa, Egypt, Kenya, Ghana, and Ethiopia")
    
    countries = list(COMPARISON_COUNTRIES.keys())
    
    st.markdown("### GDP Comparison (Latest Year)")
    with st.spinner('Loading GDP comparison...'):
        gdp_comp_df = WorldBankData.get_multi_country_indicator(countries, INDICATORS['gdp'], 2015, 2025)
        if not gdp_comp_df.empty:
            fig = create_comparison_chart(gdp_comp_df, "GDP Comparison - African Nations", "GDP (Current US$)")
            if fig:
                st.plotly_chart(fig, width='stretch')
        else:
            st.info("GDP comparison data not available")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### GDP Per Capita Comparison")
        with st.spinner('Loading GDP per capita comparison...'):
            gdp_pc_comp_df = WorldBankData.get_multi_country_indicator(countries, INDICATORS['gdp_per_capita'], 2015, 2025)
            if not gdp_pc_comp_df.empty:
                fig = create_comparison_chart(gdp_pc_comp_df, "GDP Per Capita", "Current US$")
                if fig:
                    st.plotly_chart(fig, width='stretch')
            else:
                st.info("GDP per capita comparison not available")
    
    with col2:
        st.markdown("### Life Expectancy Comparison")
        with st.spinner('Loading life expectancy comparison...'):
            life_comp_df = WorldBankData.get_multi_country_indicator(countries, INDICATORS['life_expectancy'], 2015, 2025)
            if not life_comp_df.empty:
                fig = create_comparison_chart(life_comp_df, "Life Expectancy", "Years")
                if fig:
                    st.plotly_chart(fig, width='stretch')
            else:
                st.info("Life expectancy comparison not available")
    
    st.markdown("### GDP Growth Over Time - Multi-Country Comparison")
    with st.spinner('Loading GDP growth trends...'):
        growth_comp_df = WorldBankData.get_multi_country_indicator(countries, INDICATORS['gdp_growth'], 2010, 2025)
        if not growth_comp_df.empty:
            fig = create_multi_line_chart(growth_comp_df, "GDP Growth Rate - Regional Comparison", "Annual % Growth")
            if fig:
                st.plotly_chart(fig, width='stretch')
        else:
            st.info("GDP growth comparison not available")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Internet Access Comparison")
        with st.spinner('Loading internet comparison...'):
            internet_comp_df = WorldBankData.get_multi_country_indicator(countries, INDICATORS['internet_users'], 2015, 2025)
            if not internet_comp_df.empty:
                fig = create_comparison_chart(internet_comp_df, "Internet Users", "% of Population")
                if fig:
                    st.plotly_chart(fig, width='stretch')
            else:
                st.info("Internet comparison not available")
    
    with col2:
        st.markdown("### Electricity Access Comparison")
        with st.spinner('Loading electricity comparison...'):
            elec_comp_df = WorldBankData.get_multi_country_indicator(countries, INDICATORS['electricity_access'], 2015, 2025)
            if not elec_comp_df.empty:
                fig = create_comparison_chart(elec_comp_df, "Electricity Access", "% of Population")
                if fig:
                    st.plotly_chart(fig, width='stretch')
            else:
                st.info("Electricity comparison not available")

def show_sdg_progress():
    """Display SDG Progress tracker."""
    st.markdown('<div class="section-title">🎯 Sustainable Development Goals (SDG) Progress</div>', unsafe_allow_html=True)
    
    st.info("Tracking Nigeria's progress on UN Sustainable Development Goals using World Bank indicators")
    
    st.markdown("### SDG Performance Dashboard")
    
    sdg_data = []
    for sdg_key, sdg_info in SDG_INDICATORS.items():
        val, year = WorldBankData.get_latest_value('NGA', sdg_info['code'])
        if val is not None:
            sdg_data.append({
                'Goal': sdg_info['name'],
                'Indicator': sdg_info['description'],
                'Latest Value': f"{val:.2f}",
                'Year': year,
                'Target': sdg_info['target']
            })
    
    if sdg_data:
        sdg_df = pd.DataFrame(sdg_data)
        st.dataframe(sdg_df, width='stretch', hide_index=True)
    else:
        st.warning("SDG data not available")
    
    st.markdown("### SDG Trends Over Time")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### SDG 1: No Poverty")
        with st.spinner('Loading poverty data...'):
            poverty_df = WorldBankData.get_indicator_data('NGA', SDG_INDICATORS['sdg1_poverty']['code'], 2000, 2025)
            if not poverty_df.empty:
                fig = create_trend_chart(poverty_df, "Poverty Rate Trend", "% of Population at $2.15/day", '#FF6B6B')
                if fig:
                    st.plotly_chart(fig, width='stretch')
            else:
                st.info("Poverty data not available")
    
    with col2:
        st.markdown("#### SDG 4: Quality Education")
        with st.spinner('Loading education data...'):
            edu_df = WorldBankData.get_indicator_data('NGA', SDG_INDICATORS['sdg4_education']['code'], 2000, 2025)
            if not edu_df.empty:
                fig = create_trend_chart(edu_df, "Primary Education Completion", "% of Relevant Age Group", '#008751')
                if fig:
                    st.plotly_chart(fig, width='stretch')
            else:
                st.info("Education data not available")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### SDG 3: Good Health - Maternal Mortality")
        with st.spinner('Loading maternal mortality data...'):
            maternal_df = WorldBankData.get_indicator_data('NGA', SDG_INDICATORS['sdg3_health_maternal']['code'], 2000, 2025)
            if not maternal_df.empty:
                fig = create_trend_chart(maternal_df, "Maternal Mortality Ratio", "Per 100,000 Live Births", '#FF6B6B')
                if fig:
                    st.plotly_chart(fig, width='stretch')
            else:
                st.info("Maternal mortality data not available")
    
    with col2:
        st.markdown("#### SDG 3: Good Health - Child Mortality")
        with st.spinner('Loading child mortality data...'):
            child_df = WorldBankData.get_indicator_data('NGA', SDG_INDICATORS['sdg3_health_child']['code'], 2000, 2025)
            if not child_df.empty:
                fig = create_trend_chart(child_df, "Under-5 Mortality Rate", "Per 1,000 Live Births", '#FFD93D')
                if fig:
                    st.plotly_chart(fig, width='stretch')
            else:
                st.info("Child mortality data not available")
    
    st.markdown("### SDG Gender & Energy Access")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### SDG 5: Gender Equality")
        with st.spinner('Loading gender equality data...'):
            gender_df = WorldBankData.get_indicator_data('NGA', SDG_INDICATORS['sdg5_gender']['code'], 2000, 2025)
            if not gender_df.empty:
                fig = create_trend_chart(gender_df, "Female Labor Force Participation", "% of Female Population", '#4ECDC4')
                if fig:
                    st.plotly_chart(fig, width='stretch')
            else:
                st.info("Gender equality data not available")
    
    with col2:
        st.markdown("#### SDG 7: Affordable Energy")
        with st.spinner('Loading energy access data...'):
            energy_df = WorldBankData.get_indicator_data('NGA', SDG_INDICATORS['sdg7_energy']['code'], 2000, 2025)
            if not energy_df.empty:
                fig = create_trend_chart(energy_df, "Electricity Access", "% of Population", '#008751')
                if fig:
                    st.plotly_chart(fig, width='stretch')
            else:
                st.info("Energy access data not available")
    
    st.markdown("### SDG Regional Comparison")
    
    countries = list(COMPARISON_COUNTRIES.keys())
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Poverty Rates Comparison")
        with st.spinner('Loading poverty comparison...'):
            poverty_comp_df = WorldBankData.get_multi_country_indicator(countries, SDG_INDICATORS['sdg1_poverty']['code'], 2010, 2025)
            if not poverty_comp_df.empty:
                fig = create_comparison_chart(poverty_comp_df, "Poverty Rate - African Nations", "% of Population")
                if fig:
                    st.plotly_chart(fig, width='stretch')
            else:
                st.info("Poverty comparison not available")
    
    with col2:
        st.markdown("#### Education Completion Comparison")
        with st.spinner('Loading education comparison...'):
            edu_comp_df = WorldBankData.get_multi_country_indicator(countries, SDG_INDICATORS['sdg4_education']['code'], 2010, 2025)
            if not edu_comp_df.empty:
                fig = create_comparison_chart(edu_comp_df, "Primary Completion Rate", "% of Age Group")
                if fig:
                    st.plotly_chart(fig, width='stretch')
            else:
                st.info("Education comparison not available")

def main():
    """Main application function."""
    
    st.sidebar.title("📊 Navigation")
    st.sidebar.markdown("---")
    
    page = st.sidebar.radio(
        "Select Section:",
        ["🏠 Overview", "💰 Economic Development", "👨‍👩‍👧‍👦 Social Development", 
         "🏗️ Infrastructure & Tech", "🌍 Global Comparison", "🎯 SDG Progress", 
         "🎨 Custom Dashboard", "🔮 Predictive Analytics"],
        label_visibility="collapsed"
    )
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("### About 9jaStats")
    st.sidebar.info(
        "9jaStats provides a comprehensive 360-degree view of Nigeria's national development "
        "and global competitiveness. Data is sourced from the World Bank Development Indicators."
    )
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📥 Export Data")
    
    with st.sidebar.expander("Download All Indicators"):
        if st.button("📊 Export All Nigeria Data"):
            all_data = []
            for indicator_name, indicator_code in INDICATORS.items():
                df = WorldBankData.get_indicator_data('NGA', indicator_code, 2000, 2025)
                if not df.empty:
                    df['indicator'] = indicator_name
                    all_data.append(df)
            
            if all_data:
                combined_df = pd.concat(all_data, ignore_index=True)
                csv = export_to_csv(combined_df, 'nigeria_all_data.csv')
                if csv:
                    st.sidebar.download_button(
                        label="⬇️ Download CSV",
                        data=csv,
                        file_name='nigeria_all_indicators.csv',
                        mime='text/csv',
                    )
                    st.sidebar.success("Data ready for download!")
            else:
                st.sidebar.error("No data available")
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("**Data Source:** World Bank Open Data")
    st.sidebar.markdown("**Last Updated:** 2025")
    
    if page == "🏠 Overview":
        show_overview()
    elif page == "💰 Economic Development":
        show_economic_development()
    elif page == "👨‍👩‍👧‍👦 Social Development":
        show_social_development()
    elif page == "🏗️ Infrastructure & Tech":
        show_infrastructure()
    elif page == "🌍 Global Comparison":
        show_global_comparison()
    elif page == "🎯 SDG Progress":
        show_sdg_progress()
    elif page == "🎨 Custom Dashboard":
        show_custom_dashboard()
    elif page == "🔮 Predictive Analytics":
        show_predictive_analytics()

if __name__ == "__main__":
    main()
