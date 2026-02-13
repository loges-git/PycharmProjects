import streamlit as st

def load_css():
    st.markdown("""
        <style>
        /* ----------------------------------------------------
           1. FONTS & VARIABLES
           ---------------------------------------------------- */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

        :root {
            /* Professional Color Palette */
            --primary-color: #0F172A;       /* Slate 900 (Deep Navy) */
            --secondary-color: #334155;     /* Slate 700 */
            --accent-color: #2563EB;        /* Blue 600 (Vibrant Action) */
            --accent-hover: #1D4ED8;        /* Blue 700 */
            
            --success-color: #059669;       /* Emerald 600 */
            --warning-color: #D97706;       /* Amber 600 */
            --error-color: #DC2626;         /* Red 600 */
            
            --bg-color: #EFF6FF;            /* Very light blue tint */
            --card-bg: #FFFFFF;             /* White */
            
            --text-main: #1E293B;           /* Slate 800 */
            --text-secondary: #64748B;      /* Slate 500 */
            
            --font-main: 'Inter', sans-serif;
            --radius: 8px;
            --shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.05);
            --shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1);
            --shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1);
        }

        /* ----------------------------------------------------
           2. GLOBAL RESETS & TYPOGRAPHY
           ---------------------------------------------------- */
        html, body, [class*="css"] {
            font-family: var(--font-main);
            color: var(--text-main);
            background-color: var(--bg-color);
        }
        
        h1, h2, h3, h4, h5, h6 {
            font-family: var(--font-main);
            font-weight: 600;
            color: var(--primary-color);
            letter-spacing: -0.025em;
        }

        /* Streamlit generic container styling override */
        .block-container {
            padding-top: 2rem;
            padding-bottom: 3rem;
        }

        /* Gradient Background for Main App */
        .stApp {
            background: linear-gradient(135deg, #EFF6FF 0%, #FFFFFF 100%);
        }

        /* ----------------------------------------------------
           3. CARD COMPONENT
           ---------------------------------------------------- */
        .ui-card {
            background-color: var(--card-bg);
            border-radius: var(--radius);
            padding: 1.5rem;
            box-shadow: var(--shadow-md);
            border: 1px solid #E2E8F0;
            margin-bottom: 1rem;
        }
        
        .ui-card-header {
            font-size: 1.1rem;
            font-weight: 600;
            margin-bottom: 1rem;
            color: var(--secondary-color);
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }

        /* ----------------------------------------------------
           4. STREAMLIT WIDGETS OVERRIDES
           ---------------------------------------------------- */
        
        /* Buttons */
        .stButton > button {
            background-color: var(--accent-color);
            color: white;
            border-radius: var(--radius);
            border: none;
            padding: 0.5rem 1rem;
            font-weight: 500;
            box-shadow: var(--shadow-sm);
            transition: all 0.2s ease;
        }
        
        .stButton > button:hover {
            background-color: var(--accent-hover);
            box-shadow: var(--shadow-md);
            transform: translateY(-1px);
        }

        /* Inputs */
        .stTextInput > div > div > input {
            border-radius: var(--radius);
            border: 1px solid #CBD5E1;
            color: var(--text-main);
        }
        
        .stTextInput > div > div > input:focus {
            border-color: var(--accent-color);
            box-shadow: 0 0 0 1px var(--accent-color);
        }
        
        /* Alerts / Info boxes override */
        .stAlert {
            border-radius: var(--radius);
            box-shadow: var(--shadow-sm);
        }

        /* ----------------------------------------------------
           5. SPECIAL COMPONENT CLASSES
           ---------------------------------------------------- */
           
        /* Environment Badges */
        .badge-cit {
            background-color: #E0F2FE; /* Sky 100 */
            color: #0369A1;           /* Sky 700 */
            padding: 0.25rem 0.75rem;
            border-radius: 9999px;
            font-weight: 600;
            font-size: 0.875rem;
            border: 1px solid #BAE6FD;
            display: inline-flex;
            align-items: center;
            gap: 0.25rem;
        }
        
        .badge-bfx {
            background-color: #FFEDD5; /* Orange 100 */
            color: #C2410C;            /* Orange 700 */
            padding: 0.25rem 0.75rem;
            border-radius: 9999px;
            font-weight: 600;
            font-size: 0.875rem;
            border: 1px solid #FED7AA;
            display: inline-flex;
            align-items: center;
            gap: 0.25rem;
        }
        
        /* ----------------------------------------------------
           6. SEPARATOR
           ---------------------------------------------------- */
        hr {
            margin: 2rem 0;
            border-color: #E2E8F0;
        }
        
        </style>
    """, unsafe_allow_html=True)
