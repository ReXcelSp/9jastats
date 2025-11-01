# 9jaStats - Nigeria Development Dashboard

## Overview

9jaStats is a data visualization dashboard built with Streamlit that displays development indicators for Nigeria using World Bank API data. The application allows users to explore various economic, social, and development metrics for Nigeria and compare them with other countries. The dashboard features interactive charts powered by Plotly and provides cached data fetching for optimal performance.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture

**Framework:** Streamlit
- **Rationale:** Streamlit provides a rapid development framework for data-driven web applications with minimal boilerplate code. It's particularly well-suited for creating interactive dashboards with Python.
- **Pros:** Fast prototyping, native Python support, built-in state management, easy deployment
- **Cons:** Limited customization compared to traditional web frameworks, less control over UI components

**Visualization Library:** Plotly (plotly.graph_objects and plotly.express)
- **Rationale:** Plotly offers rich, interactive visualizations with built-in responsiveness and extensive chart types. The combination of graph_objects (low-level) and express (high-level) provides flexibility for both simple and complex visualizations.
- **Pros:** Interactive charts, professional appearance, extensive chart types, subplot support
- **Cons:** Larger bundle size compared to simpler charting libraries
- **Hover Functionality:** Enhanced hover templates on all charts display exact data labels with year and precise values (formatted to 2 decimal places) for improved data exploration

**UI Customization:** Custom CSS through Streamlit markdown
- **Rationale:** Uses inline CSS styling to customize the appearance beyond Streamlit's default theming, including responsive design considerations.
- **Design Pattern:** The application uses a color scheme based on Nigeria's flag colors (#008751 green) for branding consistency.

### Backend Architecture

**Data Layer:** World Bank API integration
- **Architecture Pattern:** Data fetcher class (WorldBankData) implementing a simple service layer pattern
- **Rationale:** Separates data fetching logic from presentation logic, making the codebase more maintainable and testable.
- **Caching Strategy:** Streamlit's `@st.cache_data` decorator with 1-hour TTL (time-to-live)
  - **Problem Addressed:** Reduces API calls to World Bank API and improves application performance
  - **Pros:** Automatic cache invalidation, reduced latency, lower API usage
  - **Cons:** May show stale data for up to 1 hour

**Data Processing:** Pandas DataFrames
- **Rationale:** Pandas provides robust data manipulation capabilities and integrates seamlessly with Plotly for visualization.
- **Data Flow:** API response → JSON parsing → DataFrame conversion → Visualization

**Error Handling:** Try-catch blocks with timeout handling
- **Approach:** Requests include 10-second timeout, with graceful degradation (returns empty DataFrame on failure)
- **Rationale:** Prevents application hanging on slow/failed API requests while maintaining user experience

### Application Structure

**Modular Design:**
- `app.py`: Main application file containing UI layout and Streamlit configuration
- `data_fetcher.py`: Data access layer for World Bank API with SDG indicators
- `custom_dashboard.py`: Custom dashboard builder for personalized metric selection
- `predictions.py`: Predictive analytics module using linear regression
- `main.py`: Entry point (appears to be template/placeholder)

**Configuration Management:**
- Predefined constants: INDICATORS and COMPARISON_COUNTRIES (imported but not shown in provided code)
- Page configuration: Wide layout, expanded sidebar, custom title and icon

### Design Patterns

1. **Separation of Concerns:** UI logic separated from data fetching logic
2. **Caching Pattern:** Memoization of API calls to reduce redundant requests
3. **Static Method Pattern:** WorldBankData uses static methods as it doesn't maintain state
4. **Responsive Design:** Mobile-first CSS with media queries for screens under 768px width

## External Dependencies

### Third-Party APIs

**World Bank API v2**
- **Endpoint:** `https://api.worldbank.org/v2`
- **Purpose:** Fetches development indicators (economic, social, demographic data)
- **Data Format:** JSON
- **Rate Limiting:** Implemented through caching (1-hour TTL)
- **Parameters Used:**
  - Country code (ISO 3-letter format, e.g., 'NGA')
  - Indicator code (World Bank specific)
  - Date range (default: 2000-2025)
  - Results per page: 500

### Python Libraries

**Core Dependencies:**
- `streamlit`: Web application framework and UI components
- `plotly`: Interactive visualization library (graph_objects and express modules)
- `pandas`: Data manipulation and analysis
- `numpy`: Numerical computing (imported but usage not visible in provided code)
- `requests`: HTTP client for API calls

**Data Flow:**
1. User interacts with Streamlit UI
2. App triggers data fetch from WorldBankData class
3. API request sent to World Bank with caching check
4. JSON response parsed into Pandas DataFrame
5. DataFrame passed to Plotly for visualization
6. Interactive chart rendered in Streamlit app

### No Database

The application does not use a persistent database. All data is fetched on-demand from the World Bank API and cached in-memory using Streamlit's caching mechanism.