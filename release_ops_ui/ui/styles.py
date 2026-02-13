# ui/styles.py
import streamlit as st

def load_css():
    st.markdown("""
        <style>
        /* ============================================================
           🎨 MODERN DESIGN SYSTEM - Release Operations Platform
           Premium UI with Glassmorphism, Gradients & Micro-Animations
           ============================================================ */

        /* ----------------------------------------------------
           1. FONTS & CSS VARIABLES
           ---------------------------------------------------- */
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700;800&family=Inter:wght@300;400;500;600&display=swap');

        :root {
            /* 🌈 Vibrant Gradient Palette */
            --gradient-primary: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            --gradient-secondary: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            --gradient-accent: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
            --gradient-success: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
            --gradient-warning: linear-gradient(135deg, #f2994a 0%, #f2c94c 100%);
            --gradient-error: linear-gradient(135deg, #eb3349 0%, #f45c43 100%);
            --gradient-dark: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            --gradient-mesh: linear-gradient(135deg, #667eea15 0%, #764ba215 25%, #f093fb15 50%, #4facfe15 75%, #11998e15 100%);
            
            /* 🎯 Solid Colors */
            --primary-purple: #667eea;
            --primary-violet: #764ba2;
            --accent-pink: #f093fb;
            --accent-coral: #f5576c;
            --accent-cyan: #00f2fe;
            --accent-teal: #11998e;
            --accent-emerald: #38ef7d;
            
            /* 📝 Text Colors */
            --text-primary: #1e1e2f;
            --text-secondary: #6b7280;
            --text-muted: #9ca3af;
            --text-light: #ffffff;
            
            /* 🎴 Surface Colors */
            --bg-base: #f8faff;
            --bg-card: rgba(255, 255, 255, 0.85);
            --bg-glass: rgba(255, 255, 255, 0.25);
            --border-glass: rgba(255, 255, 255, 0.35);
            --border-subtle: rgba(102, 126, 234, 0.15);
            
            /* 🔤 Typography */
            --font-display: 'Poppins', sans-serif;
            --font-body: 'Inter', sans-serif;
            
            /* 📐 Spacing & Radius */
            --radius-sm: 8px;
            --radius-md: 12px;
            --radius-lg: 20px;
            --radius-xl: 28px;
            --radius-full: 9999px;
            
            /* 🌫️ Shadows & Effects */
            --shadow-sm: 0 2px 8px rgba(102, 126, 234, 0.08);
            --shadow-md: 0 8px 24px rgba(102, 126, 234, 0.12);
            --shadow-lg: 0 16px 48px rgba(102, 126, 234, 0.16);
            --shadow-glow: 0 0 20px rgba(102, 126, 234, 0.4);
            --shadow-glow-pink: 0 0 20px rgba(240, 147, 251, 0.4);
            --shadow-glow-cyan: 0 0 20px rgba(0, 242, 254, 0.4);
            
            /* ⏱️ Transitions */
            --transition-fast: 0.15s ease;
            --transition-base: 0.25s ease;
            --transition-slow: 0.4s ease;
        }

        /* ----------------------------------------------------
           2. GLOBAL STYLES & ANIMATED BACKGROUND
           ---------------------------------------------------- */
        .stApp {
            background: 
                radial-gradient(ellipse at 20% 0%, rgba(102, 126, 234, 0.15) 0%, transparent 50%),
                radial-gradient(ellipse at 80% 20%, rgba(240, 147, 251, 0.12) 0%, transparent 40%),
                radial-gradient(ellipse at 40% 80%, rgba(79, 172, 254, 0.1) 0%, transparent 50%),
                radial-gradient(ellipse at 90% 90%, rgba(17, 153, 142, 0.08) 0%, transparent 40%),
                linear-gradient(180deg, #f8faff 0%, #ffffff 100%);
            min-height: 100vh;
        }
        
        html, body, [class*="css"] {
            font-family: var(--font-body);
            color: var(--text-primary);
        }
        
        .block-container {
            padding: 2rem 3rem 4rem !important;
            max-width: 1400px;
        }

        /* ----------------------------------------------------
           3. TYPOGRAPHY - Premium Headers
           ---------------------------------------------------- */
        h1, h2, h3 {
            font-family: var(--font-display) !important;
            font-weight: 700 !important;
            letter-spacing: -0.02em;
        }
        
        h1 {
            background: var(--gradient-primary);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            font-size: 2.5rem !important;
            margin-bottom: 1.5rem !important;
        }
        
        h2 {
            color: var(--text-primary) !important;
            font-size: 1.5rem !important;
            position: relative;
            padding-left: 1rem;
        }
        
        h2::before {
            content: '';
            position: absolute;
            left: 0;
            top: 50%;
            transform: translateY(-50%);
            width: 4px;
            height: 70%;
            background: var(--gradient-primary);
            border-radius: var(--radius-full);
        }
        
        h3 {
            color: var(--primary-purple) !important;
            font-size: 1.2rem !important;
        }

        /* ----------------------------------------------------
           4. GLASSMORPHIC CARDS
           ---------------------------------------------------- */
        .ui-card {
            background: var(--bg-card);
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            border: 1px solid var(--border-glass);
            border-radius: var(--radius-lg);
            padding: 1.75rem;
            box-shadow: var(--shadow-md);
            transition: all var(--transition-base);
            position: relative;
            overflow: hidden;
        }
        
        .ui-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 3px;
            background: var(--gradient-primary);
            opacity: 0;
            transition: opacity var(--transition-base);
        }
        
        .ui-card:hover {
            transform: translateY(-4px);
            box-shadow: var(--shadow-lg);
            border-color: rgba(102, 126, 234, 0.3);
        }
        
        .ui-card:hover::before {
            opacity: 1;
        }
        
        .ui-card-header {
            font-family: var(--font-display);
            font-size: 1.15rem;
            font-weight: 600;
            color: var(--text-primary);
            margin-bottom: 0.75rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }

        /* ----------------------------------------------------
           5. MODERN BUTTONS
           ---------------------------------------------------- */
        .stButton > button {
            background: var(--gradient-primary) !important;
            color: white !important;
            border: none !important;
            border-radius: var(--radius-md) !important;
            padding: 0.65rem 1.5rem !important;
            font-family: var(--font-display) !important;
            font-weight: 600 !important;
            font-size: 0.95rem !important;
            box-shadow: var(--shadow-sm) !important;
            transition: all var(--transition-base) !important;
            position: relative;
            overflow: hidden;
        }
        
        .stButton > button:hover {
            transform: translateY(-2px) !important;
            box-shadow: var(--shadow-glow) !important;
        }
        
        .stButton > button:active {
            transform: translateY(0) !important;
        }
        
        /* Secondary button style */
        .stButton > button[kind="secondary"] {
            background: transparent !important;
            border: 2px solid var(--primary-purple) !important;
            color: var(--primary-purple) !important;
        }
        
        .stButton > button[kind="secondary"]:hover {
            background: rgba(102, 126, 234, 0.1) !important;
        }

        /* ----------------------------------------------------
           6. STYLED INPUTS
           ---------------------------------------------------- */
        .stTextInput > div > div > input,
        .stSelectbox > div > div > div,
        .stTextArea > div > div > textarea {
            background: var(--bg-card) !important;
            border: 2px solid var(--border-subtle) !important;
            border-radius: var(--radius-md) !important;
            color: var(--text-primary) !important; /* Ensure text is visible */
            font-family: var(--font-body) !important;
            padding: 0.75rem 1rem !important;
            line-height: 1.5 !important; /* Improve line height */
            height: auto !important; /* Allow height to adjust */
            min-height: 48px !important; /* Minimum comfortable touch target */
            transition: all var(--transition-fast) !important;
        }
        
        /* Fix for selectbox text color specifically */
        .stSelectbox div[data-baseweb="select"] > div {
             color: var(--text-primary) !important;
        }

        .stTextInput > div > div > input:focus,
        .stSelectbox > div > div > div:focus-within,
        .stTextArea > div > div > textarea:focus {
            border-color: var(--primary-purple) !important;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.15) !important;
            background: #ffffff !important; /* White background on focus for clarity */
        }
        
        /* Ensure dropdown options are visible */
        ul[data-baseweb="menu"] {
            background: #ffffff !important;
            color: var(--text-primary) !important;
        }
        
        /* Fix label visibility */
        .stTextInput label, .stSelectbox label, .stTextArea label {
            color: var(--text-secondary) !important;
            font-weight: 500 !important;
            margin-bottom: 0.5rem !important;
        }

        /* ----------------------------------------------------
           7. ENVIRONMENT BADGES - Gradient Style
           ---------------------------------------------------- */
        .badge-cit {
            background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
            color: white;
            padding: 0.5rem 1.25rem;
            border-radius: var(--radius-full);
            font-family: var(--font-display);
            font-weight: 600;
            font-size: 0.9rem;
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            box-shadow: var(--shadow-glow-cyan);
            animation: pulse-glow 2s ease-in-out infinite;
        }
        
        .badge-bfx {
            background: linear-gradient(135deg, #f2994a 0%, #f2c94c 100%);
            color: white;
            padding: 0.5rem 1.25rem;
            border-radius: var(--radius-full);
            font-family: var(--font-display);
            font-weight: 600;
            font-size: 0.9rem;
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            box-shadow: 0 0 20px rgba(242, 153, 74, 0.4);
            animation: pulse-glow 2s ease-in-out infinite;
        }
        
        @keyframes pulse-glow {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.85; }
        }

        /* ----------------------------------------------------
           8. TABS - Modern Style
           ---------------------------------------------------- */
        .stTabs [data-baseweb="tab-list"] {
            background: var(--bg-glass);
            backdrop-filter: blur(8px);
            border-radius: var(--radius-lg);
            padding: 0.5rem;
            gap: 0.5rem;
            border: 1px solid var(--border-glass);
        }
        
        .stTabs [data-baseweb="tab"] {
            background: transparent;
            border-radius: var(--radius-md);
            font-family: var(--font-display);
            font-weight: 500;
            color: var(--text-secondary);
            padding: 0.75rem 1.5rem;
            transition: all var(--transition-base);
        }
        
        .stTabs [aria-selected="true"] {
            background: var(--gradient-primary) !important;
            color: white !important;
            box-shadow: var(--shadow-sm);
        }
        
        .stTabs [data-baseweb="tab-highlight"] {
            display: none;
        }
        
        .stTabs [data-baseweb="tab-border"] {
            display: none;
        }

        /* ----------------------------------------------------
           9. ALERTS & STATUS BOXES
           ---------------------------------------------------- */
        .stAlert {
            border-radius: var(--radius-md) !important;
            border: none !important;
            backdrop-filter: blur(8px);
        }
        
        [data-testid="stSuccessMessage"] {
            background: linear-gradient(135deg, rgba(17, 153, 142, 0.1) 0%, rgba(56, 239, 125, 0.1) 100%) !important;
            border-left: 4px solid var(--accent-teal) !important;
        }
        
        [data-testid="stWarningMessage"] {
            background: linear-gradient(135deg, rgba(242, 153, 74, 0.1) 0%, rgba(242, 201, 76, 0.1) 100%) !important;
            border-left: 4px solid #f2994a !important;
        }
        
        [data-testid="stErrorMessage"] {
            background: linear-gradient(135deg, rgba(235, 51, 73, 0.1) 0%, rgba(244, 92, 67, 0.1) 100%) !important;
            border-left: 4px solid #eb3349 !important;
        }
        
        [data-testid="stInfoMessage"] {
            background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%) !important;
            border-left: 4px solid var(--primary-purple) !important;
        }

        /* ----------------------------------------------------
           10. CHAT INTERFACE STYLING
           ---------------------------------------------------- */
        [data-testid="stChatMessage"] {
            background: var(--bg-card) !important;
            backdrop-filter: blur(12px);
            border: 1px solid var(--border-glass) !important;
            border-radius: var(--radius-lg) !important;
            padding: 1rem 1.25rem !important;
            margin-bottom: 1rem !important;
            animation: slideIn 0.3s ease-out;
        }
        
        [data-testid="stChatMessage"][data-testid*="user"] {
            background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%) !important;
            border-left: 3px solid var(--primary-purple) !important;
        }
        
        [data-testid="stChatMessage"][data-testid*="assistant"] {
            background: linear-gradient(135deg, rgba(240, 147, 251, 0.08) 0%, rgba(245, 87, 108, 0.08) 100%) !important;
            border-left: 3px solid var(--accent-pink) !important;
        }
        
        @keyframes slideIn {
            from {
                opacity: 0;
                transform: translateY(10px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        [data-testid="stChatInput"] > div {
            background: var(--bg-card) !important;
            border: 2px solid var(--border-subtle) !important;
            border-radius: var(--radius-lg) !important;
            transition: all var(--transition-base);
        }
        
        [data-testid="stChatInput"] > div:focus-within {
            border-color: var(--primary-purple) !important;
            box-shadow: var(--shadow-glow) !important;
        }

        /* ----------------------------------------------------
           11. DIVIDERS & SEPARATORS
           ---------------------------------------------------- */
        hr {
            border: none;
            height: 2px;
            background: linear-gradient(90deg, transparent, var(--border-subtle), transparent);
            margin: 2rem 0;
        }

        /* ----------------------------------------------------
           12. CHECKBOXES & RADIO BUTTONS
           ---------------------------------------------------- */
        .stCheckbox label span:first-child,
        .stRadio label span:first-child {
            border-color: var(--primary-purple) !important;
        }
        
        .stCheckbox label span:first-child:has(input:checked),
        .stRadio label span:first-child:has(input:checked) {
            background: var(--gradient-primary) !important;
            border-color: var(--primary-purple) !important;
        }

        /* ----------------------------------------------------
           13. EXPANDERS
           ---------------------------------------------------- */
        .streamlit-expanderHeader {
            background: var(--bg-glass) !important;
            border-radius: var(--radius-md) !important;
            font-family: var(--font-display) !important;
            font-weight: 600;
            transition: all var(--transition-base);
        }
        
        .streamlit-expanderHeader:hover {
            background: rgba(102, 126, 234, 0.1) !important;
        }

        /* ----------------------------------------------------
           14. PROGRESS INDICATORS
           ---------------------------------------------------- */
        .stProgress > div > div {
            background: var(--gradient-primary) !important;
            border-radius: var(--radius-full);
        }
        
        .stSpinner > div {
            border-color: var(--primary-purple) transparent transparent transparent !important;
        }

        /* ----------------------------------------------------
           15. DATA DISPLAY
           ---------------------------------------------------- */
        .stDataFrame, .stTable {
            border-radius: var(--radius-md);
            overflow: hidden;
            box-shadow: var(--shadow-sm);
        }
        
        .stCode {
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%) !important;
            border-radius: var(--radius-md) !important;
            border: 1px solid rgba(102, 126, 234, 0.2) !important;
        }

        /* ----------------------------------------------------
           16. MODE SELECTION CARDS (Custom)
           ---------------------------------------------------- */
        .mode-card {
            background: var(--bg-card);
            backdrop-filter: blur(16px);
            border: 1px solid var(--border-glass);
            border-radius: var(--radius-xl);
            padding: 2rem;
            text-align: center;
            transition: all var(--transition-base);
            cursor: pointer;
        }
        
        .mode-card:hover {
            transform: translateY(-8px);
            box-shadow: var(--shadow-lg);
        }
        
        .mode-card-icon {
            font-size: 3rem;
            margin-bottom: 1rem;
            display: block;
        }
        
        .mode-card-title {
            font-family: var(--font-display);
            font-size: 1.5rem;
            font-weight: 700;
            background: var(--gradient-primary);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 0.5rem;
        }
        
        .mode-card-desc {
            color: var(--text-secondary);
            font-size: 0.95rem;
            line-height: 1.6;
        }

        /* ----------------------------------------------------
           17. SCROLLBAR
           ---------------------------------------------------- */
        ::-webkit-scrollbar {
            width: 8px;
            height: 8px;
        }
        
        ::-webkit-scrollbar-track {
            background: transparent;
        }
        
        ::-webkit-scrollbar-thumb {
            background: linear-gradient(180deg, var(--primary-purple), var(--primary-violet));
            border-radius: var(--radius-full);
        }
        
        ::-webkit-scrollbar-thumb:hover {
            background: var(--primary-violet);
        }

        /* ----------------------------------------------------
           18. FLOATING ACTION ANIMATIONS
           ---------------------------------------------------- */
        @keyframes float {
            0%, 100% { transform: translateY(0); }
            50% { transform: translateY(-5px); }
        }
        
        .floating {
            animation: float 3s ease-in-out infinite;
        }

        </style>
    """, unsafe_allow_html=True)
