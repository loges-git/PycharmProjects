
import streamlit as st

def load_css():
    st.markdown("""
        <style>
        /* ============================================================
           🎨 LUXURY DARK THEME - Deployment Log Verification
           Unified UI with Unit Extraction Tool & Retrofit Automation
           ============================================================ */

        /* ----------------------------------------------------
           1. FONTS & CSS VARIABLES
           ---------------------------------------------------- */
        @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;600;700&family=Inter:wght@300;400;500;600&display=swap');

        :root {
            /* 🌈 Gradients */
            --gradient-primary: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            --gradient-secondary: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            
            /* 🎯 Solid Colors */
            --primary-purple: #667eea;
            --primary-violet: #764ba2;
            
            /* 📝 Text Colors */
            --text-primary: #ffffff;
            --text-secondary: #e0e0e0;
            
            /* 🎴 Surface Colors */
            --bg-base: #0f0c29;
            --bg-card: rgba(255, 255, 255, 0.05);
            --border-glass: rgba(255, 255, 255, 0.1);
            --border-subtle: rgba(102, 126, 234, 0.3);
            
            /* 🔤 Typography */
            --font-display: 'Playfair Display', serif;
            --font-body: 'Inter', sans-serif;
            
            /* 📐 Radius */
            --radius-md: 12px;
            --radius-lg: 20px;
        }

        /* ----------------------------------------------------
           2. GLOBAL STYLES
           ---------------------------------------------------- */
        .stApp {
            background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%) !important;
            color: var(--text-primary);
        }
        
        .block-container {
            padding: 2rem 3rem 4rem !important;
            max-width: 1400px;
        }

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
            text-shadow: 0 0 30px rgba(102, 126, 234, 0.5);
            margin-bottom: 2rem !important;
        }
        
        p, label, .stMarkdown, div[data-testid="stMarkdownContainer"] p {
            font-family: var(--font-body) !important;
            color: var(--text-secondary) !important;
        }

        /* ----------------------------------------------------
           3. GLASSMORPHIC CARDS
           ---------------------------------------------------- */
        .glass-card {
            background: var(--bg-card);
            backdrop-filter: blur(10px);
            -webkit-backdrop-filter: blur(10px);
            border: 1px solid var(--border-glass);
            border-radius: var(--radius-lg);
            padding: 2rem;
            box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
            margin-bottom: 1.5rem;
        }

        /* ----------------------------------------------------
           4. BUTTONS
           ---------------------------------------------------- */
        .stButton > button {
            background: var(--gradient-primary) !important;
            color: white !important;
            border: none !important;
            border-radius: var(--radius-md) !important;
            padding: 10px 24px !important;
            font-weight: 600 !important;
            font-family: var(--font-body) !important;
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4) !important;
            transition: all 0.3s ease !important;
        }
        
        .stButton > button:hover {
            transform: translateY(-2px) !important;
            box-shadow: 0 8px 25px rgba(102, 126, 234, 0.6) !important;
        }

        /* ----------------------------------------------------
           5. INPUT FIELDS (High Contrast)
           ---------------------------------------------------- */
        .stTextInput > div > div > input,
        .stTextArea > div > div > textarea,
        .stNumberInput > div > div > input {
            background: var(--bg-card) !important;
            border: 1px solid var(--border-subtle) !important;
            border-radius: var(--radius-md) !important;
            color: var(--text-primary) !important;
            font-family: var(--font-body) !important;
            padding: 10px 15px !important;
        }

        .stTextInput > div > div > input:focus,
        .stTextArea > div > div > textarea:focus,
        .stNumberInput > div > div > input:focus {
             border: 1px solid rgba(102, 126, 234, 0.8) !important;
             box-shadow: 0 0 15px rgba(102, 126, 234, 0.4) !important;
             background: rgba(255,255,255,0.1) !important;
        }
        
        /* ----------------------------------------------------
           6. ALERTS & LOGS
           ---------------------------------------------------- */
        .stAlert {
            background: rgba(255, 255, 255, 0.05) !important;
            backdrop-filter: blur(10px) !important;
            border: 1px solid var(--border-glass) !important;
            color: white !important;
        }
        
        /* ----------------------------------------------------
           7. SCROLLBAR
           ---------------------------------------------------- */
        ::-webkit-scrollbar { width: 10px; }
        ::-webkit-scrollbar-track { background: rgba(255, 255, 255, 0.05); }
        ::-webkit-scrollbar-thumb { background: var(--gradient-primary); border-radius: 10px; }

        </style>
    """, unsafe_allow_html=True)
