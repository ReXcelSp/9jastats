import requests
import pandas as pd
import streamlit as st
from datetime import datetime

class WorldBankData:
    """Fetches data from World Bank API for Nigeria and comparison countries."""
    
    BASE_URL = "https://api.worldbank.org/v2"
    
    @staticmethod
    @st.cache_data(ttl=3600)
    def get_indicator_data(country_code, indicator_code, start_year=2000, end_year=2025):
        """
        Fetch indicator data from World Bank API.
        
        Args:
            country_code: ISO country code (e.g., 'NGA' for Nigeria)
            indicator_code: World Bank indicator code
            start_year: Start year for data
            end_year: End year for data
        
        Returns:
            pandas DataFrame with year, value, and country columns
        """
        url = f"{WorldBankData.BASE_URL}/country/{country_code}/indicator/{indicator_code}"
        params = {
            'format': 'json',
            'date': f'{start_year}:{end_year}',
            'per_page': 500
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if len(data) < 2 or data[1] is None:
                return pd.DataFrame()
            
            records = []
            for item in data[1]:
                try:
                    if item['value'] is not None and item.get('date') and item.get('country') and item.get('countryiso3code'):
                        records.append({
                            'year': int(item['date']),
                            'value': float(item['value']),
                            'country': item['country']['value'],
                            'country_code': item['countryiso3code']
                        })
                except (KeyError, ValueError, TypeError) as item_error:
                    continue
            
            if records:
                df = pd.DataFrame(records)
                return df.sort_values('year')
            return pd.DataFrame()
        
        except Exception as e:
            return pd.DataFrame()
    
    @staticmethod
    @st.cache_data(ttl=3600)
    def get_multi_country_indicator(country_codes, indicator_code, start_year=2010, end_year=2025):
        """
        Fetch indicator data for multiple countries.
        
        Args:
            country_codes: List of ISO country codes
            indicator_code: World Bank indicator code
            start_year: Start year for data
            end_year: End year for data
        
        Returns:
            pandas DataFrame with combined data
        """
        all_data = []
        for country_code in country_codes:
            df = WorldBankData.get_indicator_data(country_code, indicator_code, start_year, end_year)
            if not df.empty:
                all_data.append(df)
        
        if all_data:
            return pd.concat(all_data, ignore_index=True)
        return pd.DataFrame()
    
    @staticmethod
    @st.cache_data(ttl=3600)
    def get_latest_value(country_code, indicator_code, years=10):
        """Get the most recent available value for an indicator."""
        current_year = datetime.now().year
        df = WorldBankData.get_indicator_data(
            country_code, 
            indicator_code, 
            current_year - years, 
            current_year
        )
        
        if not df.empty:
            latest = df.loc[df['value'].notna()].iloc[-1] if not df[df['value'].notna()].empty else None
            if latest is not None:
                return latest['value'], int(latest['year'])
        return None, None


# World Bank Indicator Codes
INDICATORS = {
    # Economic Indicators
    'gdp': 'NY.GDP.MKTP.CD',  # GDP (current US$)
    'gdp_growth': 'NY.GDP.MKTP.KD.ZG',  # GDP growth (annual %)
    'gdp_per_capita': 'NY.GDP.PCAP.CD',  # GDP per capita (current US$)
    'inflation': 'FP.CPI.TOTL.ZG',  # Inflation, consumer prices (annual %)
    'unemployment': 'SL.UEM.TOTL.ZS',  # Unemployment, total (% of labor force)
    'fdi': 'BX.KLT.DINV.CD.WD',  # Foreign direct investment, net inflows
    'trade': 'NE.TRD.GNFS.ZS',  # Trade (% of GDP)
    'agriculture_gdp': 'NV.AGR.TOTL.ZS',  # Agriculture, value added (% of GDP)
    'industry_gdp': 'NV.IND.TOTL.ZS',  # Industry, value added (% of GDP)
    'services_gdp': 'NV.SRV.TOTL.ZS',  # Services, value added (% of GDP)
    
    # Social Indicators
    'population': 'SP.POP.TOTL',  # Population, total
    'life_expectancy': 'SP.DYN.LE00.IN',  # Life expectancy at birth
    'infant_mortality': 'SP.DYN.IMRT.IN',  # Infant mortality rate
    'literacy': 'SE.ADT.LITR.ZS',  # Literacy rate, adult total
    'school_enrollment_primary': 'SE.PRM.NENR',  # School enrollment, primary
    'school_enrollment_secondary': 'SE.SEC.NENR',  # School enrollment, secondary
    'poverty_headcount': 'SI.POV.DDAY',  # Poverty headcount ratio at $2.15 a day
    'gini_index': 'SI.POV.GINI',  # Gini index
    
    # Infrastructure & Technology
    'electricity_access': 'EG.ELC.ACCS.ZS',  # Access to electricity (% of population)
    'internet_users': 'IT.NET.USER.ZS',  # Individuals using the Internet (% of population)
    'mobile_subscriptions': 'IT.CEL.SETS.P2',  # Mobile cellular subscriptions (per 100 people)
    'roads_paved': 'IS.ROD.PVED.ZS',  # Roads, paved (% of total roads)
    'renewable_energy': 'EG.FEC.RNEW.ZS',  # Renewable energy consumption
    
    # Governance & Environment
    'co2_emissions': 'EN.ATM.CO2E.PC',  # CO2 emissions (metric tons per capita)
    'forest_area': 'AG.LND.FRST.ZS',  # Forest area (% of land area)
    'water_access': 'SH.H2O.SMDW.ZS',  # People using safely managed drinking water services
}

# SDG (Sustainable Development Goals) Indicators
SDG_INDICATORS = {
    'sdg1_poverty': {
        'code': 'SI.POV.DDAY',
        'name': 'SDG 1: No Poverty',
        'description': 'Poverty headcount ratio at $2.15/day (% of population)',
        'target': 'Lower is better'
    },
    'sdg2_hunger': {
        'code': 'SN.ITK.DEFC.ZS',
        'name': 'SDG 2: Zero Hunger',
        'description': 'Prevalence of undernourishment (% of population)',
        'target': 'Lower is better'
    },
    'sdg3_health_maternal': {
        'code': 'SH.STA.MMRT',
        'name': 'SDG 3: Good Health',
        'description': 'Maternal mortality ratio (per 100,000 live births)',
        'target': 'Lower is better'
    },
    'sdg3_health_child': {
        'code': 'SH.DYN.MORT',
        'name': 'SDG 3: Good Health',
        'description': 'Under-5 mortality rate (per 1,000 live births)',
        'target': 'Lower is better'
    },
    'sdg4_education': {
        'code': 'SE.PRM.CMPT.ZS',
        'name': 'SDG 4: Quality Education',
        'description': 'Primary completion rate (% of relevant age group)',
        'target': 'Higher is better'
    },
    'sdg5_gender': {
        'code': 'SL.TLF.CACT.FE.ZS',
        'name': 'SDG 5: Gender Equality',
        'description': 'Female labor force participation rate (%)',
        'target': 'Higher is better'
    },
    'sdg6_water': {
        'code': 'SH.H2O.BASW.ZS',
        'name': 'SDG 6: Clean Water',
        'description': 'Access to basic drinking water (% of population)',
        'target': 'Higher is better'
    },
    'sdg7_energy': {
        'code': 'EG.ELC.ACCS.ZS',
        'name': 'SDG 7: Affordable Energy',
        'description': 'Access to electricity (% of population)',
        'target': 'Higher is better'
    },
    'sdg8_growth': {
        'code': 'NY.GDP.MKTP.KD.ZG',
        'name': 'SDG 8: Economic Growth',
        'description': 'GDP growth (annual %)',
        'target': 'Higher is better'
    },
    'sdg8_unemployment': {
        'code': 'SL.UEM.TOTL.ZS',
        'name': 'SDG 8: Decent Work',
        'description': 'Unemployment rate (% of total labor force)',
        'target': 'Lower is better'
    },
    'sdg10_inequality': {
        'code': 'SI.POV.GINI',
        'name': 'SDG 10: Reduced Inequalities',
        'description': 'Gini index (income inequality)',
        'target': 'Lower is better'
    },
    'sdg13_climate': {
        'code': 'EN.ATM.CO2E.PC',
        'name': 'SDG 13: Climate Action',
        'description': 'CO2 emissions (metric tons per capita)',
        'target': 'Lower is better'
    }
}

# Comparison Countries
COMPARISON_COUNTRIES = {
    'NGA': 'Nigeria',
    'ZAF': 'South Africa',
    'EGY': 'Egypt',
    'KEN': 'Kenya',
    'GHA': 'Ghana',
    'ETH': 'Ethiopia'
}
