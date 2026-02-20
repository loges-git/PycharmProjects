# ui/styles.py
import streamlit as st


def load_css():
    st.markdown("""
        <style>
        /* ============================================================
           🎨 LUXURY DARK THEME - Release Operations Platform
           Unified UI with Unit Extraction Tool & Retrofit Automation
           ============================================================ */

        /* ----------------------------------------------------
           1. FONTS & CSS VARIABLES (Dark Mode Mappings)
           ---------------------------------------------------- */
        @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;600;700&family=Inter:wght@300;400;500;600&display=swap');
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');

        :root {
            /* 🌈 Gradients (Same as Retrofit) */
            --gradient-primary: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            --gradient-secondary: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            --gradient-accent: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
            --gradient-success: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
            --gradient-warning: linear-gradient(135deg, #f2994a 0%, #f2c94c 100%);
            --gradient-error: linear-gradient(135deg, #eb3349 0%, #f45c43 100%);
            
            /* 🎯 Solid Colors */
            --primary-purple: #667eea;
            --primary-violet: #764ba2;
            --accent-pink: #f093fb;
            --accent-teal: #11998e;
            
            /* 📝 Text Colors (Dark Mode) */
            --text-primary: #ffffff;
            --text-secondary: #e0e0e0;
            --text-muted: #a0a0a0;
            --text-light: #ffffff;
            
            /* 🎴 Surface Colors (Glassmorphism) */
            --bg-base: #0f0c29;
            --bg-card: rgba(255, 255, 255, 0.05); /* Glass card */
            --bg-glass: rgba(255, 255, 255, 0.05);
            --border-glass: rgba(255, 255, 255, 0.1);
            --border-subtle: rgba(102, 126, 234, 0.3);
            
            /* 🔤 Typography */
            --font-display: 'Playfair Display', serif;
            --font-body: 'Inter', sans-serif;
            
            /* 📐 Spacing & Radius */
            --radius-md: 12px;
            --radius-lg: 20px;
            --radius-full: 9999px;
            
            /* 🌫️ Shadows */
            --shadow-md: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
            --shadow-glow: 0 0 20px rgba(102, 126, 234, 0.4);
            
            /* ⏱️ Transitions */
            --transition-base: 0.3s ease;
            --transition-fast: 0.15s ease;
        }

        /* ----------------------------------------------------
           2. GLOBAL STYLES (Dark Background)
           ---------------------------------------------------- */
        .stApp {
            background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%) !important;
            color: var(--text-primary);
        }
        
        .block-container {
            padding: 2rem 3rem 4rem !important;
            max-width: 1400px;
        }

        /* ----------------------------------------------------
           3. TYPOGRAPHY
           ---------------------------------------------------- */
        h1, h2, h3 {
            font-family: var(--font-display) !important;
            font-weight: 700 !important;
            letter-spacing: 1px;
        }
        
        h1 {
            background: var(--gradient-primary);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            font-size: 3.5rem !important;
            text-shadow: 0 0 30px rgba(102, 126, 234, 0.5);
            margin-bottom: 1rem !important;
        }
        
        h2 {
            font-size: 1.8rem !important;
            color: var(--text-primary) !important;
            border-left: none !important; /* Remove old style */
        }
        
        h2::before { display: none; } /* Remove old style */
        
        h3 {
            font-size: 1.4rem !important;
            color: var(--primary-purple) !important;
        }
        
        p, label, .stMarkdown, div[data-testid="stMarkdownContainer"] p {
            font-family: var(--font-body) !important;
            color: var(--text-secondary) !important;
        }

        /* ----------------------------------------------------
           4. GLASSMORPHIC CARDS (.ui-card)
           ---------------------------------------------------- */
        .ui-card, .glass-card {
            background: var(--bg-card);
            backdrop-filter: blur(10px);
            -webkit-backdrop-filter: blur(10px);
            border: 1px solid var(--border-glass);
            border-radius: var(--radius-lg);
            padding: 2rem;
            box-shadow: var(--shadow-md);
            margin-bottom: 1.5rem;
            transition: all var(--transition-base);
        }
        
        .ui-card:hover {
            transform: translateY(-4px);
            box-shadow: var(--shadow-glow);
            border-color: rgba(102, 126, 234, 0.4);
        }

        /* ----------------------------------------------------
           5. BUTTONS (Luxury Style)
           ---------------------------------------------------- */
        .stButton > button {
            background: var(--gradient-primary) !important;
            color: white !important;
            border: none !important;
            border-radius: var(--radius-md) !important;
            padding: 12px 32px !important;
            font-weight: 600 !important;
            font-family: var(--font-body) !important;
            box-shadow: 0 10px 30px rgba(102, 126, 234, 0.4) !important;
            transition: all 0.3s ease !important;
            letter-spacing: 0.5px !important;
        }
        
        .stButton > button:hover {
            transform: translateY(-3px) !important;
            box-shadow: 0 15px 40px rgba(102, 126, 234, 0.6) !important;
        }
        
        /* Secondary Button (Chat) */
        .stButton > button[kind="secondary"] {
            background: transparent !important;
            border: 2px solid var(--primary-purple) !important;
            box-shadow: none !important;
        }

        /* ----------------------------------------------------
           6. INPUT FIELDS (High Contrast)
           ---------------------------------------------------- */
        .stTextInput > div > div > input,
        .stTextArea > div > div > textarea,
        .stSelectbox > div > div > div {
            background: var(--bg-card) !important;
            border: 1px solid var(--border-subtle) !important;
            border-radius: var(--radius-md) !important;
            color: var(--text-primary) !important;
            font-family: var(--font-body) !important;
            padding: 12px 20px !important;
        }

        .stTextInput > div > div > input:focus,
        .stTextArea > div > div > textarea:focus,
        .stSelectbox > div > div > div:focus-within {
             border: 1px solid rgba(102, 126, 234, 0.8) !important;
             box-shadow: 0 0 20px rgba(102, 126, 234, 0.4) !important;
             background: rgba(255,255,255,0.1) !important;
        }

        /* Selectbox specific fixes for visibility (Dark Mode) */
        .stSelectbox div[data-baseweb="select"] > div {
            background-color: transparent !important;
            color: white !important;
            border: none !important;
        }
        
        .stSelectbox div[data-baseweb="select"] span {
            color: white !important;
        }
        
        /* Dropdown menu items */
        ul[data-baseweb="menu"] {
            background-color: #24243e !important;
        }
        
        li[data-baseweb="option"] {
            color: white !important;
            background-color: transparent !important;
        }
        
        li[data-baseweb="option"]:hover, li[data-baseweb="option"][aria-selected="true"] {
            background-color: rgba(102, 126, 234, 0.3) !important;
        }

        /* ----------------------------------------------------
           7. PROGRESS & METRICS
           ---------------------------------------------------- */
        .stProgress > div > div > div > div {
            background: var(--gradient-primary) !important;
            border-radius: 10px !important;
        }
        
        [data-testid="stMetricValue"] {
            font-size: 2.5rem !important;
            font-weight: 700 !important;
            background: var(--gradient-primary);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }

        /* ----------------------------------------------------
           8. ALERTS (Glass)
           ---------------------------------------------------- */
        .stAlert {
            background: rgba(255, 255, 255, 0.05) !important;
            backdrop-filter: blur(10px) !important;
            border: 1px solid var(--border-glass) !important;
            color: white !important;
        }

        /* ----------------------------------------------------
           9. TABS (Modern)
           ---------------------------------------------------- */
        .stTabs [data-baseweb="tab-list"] {
            background: rgba(255, 255, 255, 0.05);
            border-radius: var(--radius-md);
            padding: 5px;
            border: 1px solid var(--border-glass);
        }
        
        .stTabs [data-baseweb="tab"] {
            color: var(--text-secondary);
        }
        
        .stTabs [aria-selected="true"] {
            background: var(--gradient-primary) !important;
            color: white !important;
            border-radius: 8px;
        }

        /* ----------------------------------------------------
           10. SCROLLBAR
           ---------------------------------------------------- */
        ::-webkit-scrollbar { width: 10px; }
        ::-webkit-scrollbar-track { background: rgba(255, 255, 255, 0.05); }
        ::-webkit-scrollbar-thumb { background: var(--gradient-primary); border-radius: 10px; }

        </style>
    """, unsafe_allow_html=True)
