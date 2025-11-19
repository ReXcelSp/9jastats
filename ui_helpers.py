from typing import Optional

import streamlit as st


def ensure_theme_state() -> None:
    """Make sure the dark_mode flag exists in session state."""
    if 'dark_mode' not in st.session_state:
        st.session_state.dark_mode = False


def get_theme_colors() -> dict:
    """Return palette tokens shared across the UI."""
    ensure_theme_state()
    if st.session_state.dark_mode:
        return {
            'bg': '#0f1419',
            'secondary_bg': '#15202b',
            'surface': '#1d2733',
            'text': '#e7e9ea',
            'subtext': '#8899a6',
            'primary': '#1d9bf0',
            'grid': '#243447',
            'plot_bg': 'rgba(21,32,43,0.85)',
            'paper_bg': 'rgba(15,20,25,0)',
        }
    return {
        'bg': '#f7f9f9',
        'secondary_bg': '#ffffff',
        'surface': '#eef1f4',
        'text': '#0f1419',
        'subtext': '#536471',
        'primary': '#1d9bf0',
        'grid': '#e6ecf0',
        'plot_bg': 'rgba(255,255,255,0.75)',
        'paper_bg': 'rgba(247,249,249,0)',
    }


def inject_custom_css() -> None:
    """Inject CSS tweaks that mimic the clean Twitter analytics aesthetic."""
    theme = get_theme_colors()
    st.markdown(
        f"""
        <style>
            :root {{
                --bg-color: {theme['bg']};
                --surface-color: {theme['secondary_bg']};
                --card-color: {theme['surface']};
                --text-color: {theme['text']};
                --subtext-color: {theme['subtext']};
                --accent-color: {theme['primary']};
            }}
            html, body, .stApp {{
                background-color: var(--bg-color);
                color: var(--text-color);
                font-family: 'Inter', 'Segoe UI', system-ui, -apple-system, BlinkMacSystemFont, sans-serif;
            }}
            .stApp header {{
                background-color: var(--bg-color);
            }}
            .block-container {{
                padding-top: 1rem;
                padding-bottom: 2rem;
                max-width: 1100px;
            }}
            [data-testid="stSidebar"] {{
                background: var(--surface-color) !important;
                border-right: 1px solid rgba(136,153,166,0.2);
            }}
            [data-testid="stSidebar"] .block-container {{
                padding-top: 1.5rem;
            }}
            .main-header {{
                font-size: clamp(1.8rem, 2.5vw, 2.8rem);
                font-weight: 800;
                color: var(--accent-color);
                text-align: center;
                margin-bottom: 0.5rem;
            }}
            .sub-header {{
                font-size: 1rem;
                color: var(--subtext-color);
                text-align: center;
                margin-bottom: 1.5rem;
            }}
            .section-title {{
                color: var(--text-color);
                font-size: 1.4rem;
                font-weight: 700;
                margin: 1.5rem 0 1rem;
                border-bottom: 2px solid rgba(136,153,166,0.3);
                padding-bottom: 0.35rem;
            }}
            div[data-testid="metric-container"] {{
                background: var(--card-color);
                padding: 1rem;
                border-radius: 18px;
                box-shadow: 0 12px 25px rgba(15,23,42,0.08);
                border: 1px solid rgba(136,153,166,0.15);
            }}
            div[data-testid="metric-container"] label {{
                color: var(--subtext-color);
                font-size: 0.85rem;
            }}
            .stMetric, .stMetric > div {{
                width: 100%;
            }}
            .js-plotly-plot {{
                border-radius: 18px;
                background: var(--card-color);
                padding: 0.4rem;
                box-shadow: 0 15px 30px rgba(15,23,42,0.08);
            }}
            .stButton>button {{
                background: var(--accent-color);
                color: #fff;
                border-radius: 999px;
                border: none;
                font-weight: 600;
                min-height: 44px;
                padding: 0 1.25rem;
                transition: transform 0.2s ease, box-shadow 0.2s ease;
            }}
            .stButton>button:hover {{
                transform: translateY(-1px);
                box-shadow: 0 8px 15px rgba(29,155,240,0.25);
            }}
            .stButton>button:focus-visible {{
                outline: 2px solid var(--accent-color);
            }}
            .stDownloadButton button {{
                width: 100%;
                border-radius: 12px;
            }}
            .dataframe {{
                border-radius: 18px !important;
            }}
            /* Sticky mobile nav akin to Twitter analytics */
            @media (max-width: 768px) {{
                .block-container {{
                    padding: 0.5rem;
                }}
                [data-testid="stSidebar"] {{
                    width: 100%;
                    min-width: unset;
                }}
                .stAppViewContainer {{
                    padding-top: 1rem;
                }}
                div[data-testid="metric-container"] {{
                    padding: 0.75rem;
                    border-radius: 16px;
                }}
                .js-plotly-plot {{
                    padding: 0.1rem;
                }}
                [data-testid="column"] {{
                    width: 100% !important;
                    flex-direction: column;
                }}
                div[role="radiogroup"] > div {{
                    min-height: 48px !important;
                }}
            }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def get_chart_config() -> dict:
    """Shared Plotly config that keeps charts lightweight and touch friendly."""
    return {
        'displaylogo': False,
        'responsive': True,
        'scrollZoom': False,
        'modeBarButtonsToRemove': ['lasso2d', 'select2d', 'autoScale2d', 'hoverClosestCartesian'],
        'toImageButtonOptions': {
            'format': 'png',
            'filename': '9jastats_chart',
            'height': 500,
            'scale': 2,
        },
    }


def render_chart(fig, *, caption: Optional[str] = None) -> None:
    """Render Plotly charts with consistent responsive behaviour."""
    if fig is None:
        return
    st.plotly_chart(fig, use_container_width=True, config=get_chart_config())
    if caption:
        st.caption(caption)
