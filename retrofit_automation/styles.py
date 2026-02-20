"""
Luxury CSS Styles for Retrofit Automation Tool
(Ported from Unit Extraction Tool)
"""


def get_custom_css():
    return """
    <style>
        /* Import Google Fonts */
        @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;600;700&family=Inter:wght@300;400;500;600&display=swap');

        /* Main Background */
        .stApp {
            background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
        }

        /* Typography */
        h1, h2, h3 {
            font-family: 'Playfair Display', serif !important;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            font-weight: 700;
            letter-spacing: 1px;
        }

        h1 {
            font-size: 3.5rem !important;
            margin-bottom: 0.5rem !important;
            text-shadow: 0 0 30px rgba(102, 126, 234, 0.5);
        }

        p, label, .stMarkdown {
            font-family: 'Inter', sans-serif !important;
            color: #e0e0e0 !important;
        }

        /* Glass Morphism Cards */
        .glass-card {
            background: rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            border: 1px solid rgba(255, 255, 255, 0.1);
            padding: 2rem;
            box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
            margin-bottom: 1.5rem;
        }

        /* Input Fields */
        .stTextInput > div > div > input,
        .stTextArea > div > div > textarea {
            background: rgba(255, 255, 255, 0.08) !important;
            border: 1px solid rgba(102, 126, 234, 0.3) !important;
            border-radius: 12px !important;
            color: #ffffff !important;
            font-family: 'Inter', sans-serif !important;
        }

        /* Selectbox specific fixes for visibility */
        .stSelectbox > div[data-baseweb="select"] > div {
            background-color: rgba(255, 255, 255, 0.08) !important;
            color: white !important;
            border: 1px solid rgba(102, 126, 234, 0.3) !important;
            border-radius: 12px !important;
        }

        .stSelectbox > div[data-baseweb="select"] span {
            color: white !important;
        }

        /* Dropdown menu items */
        ul[data-baseweb="menu"] {
            background-color: #24243e !important;
        }
        
        li[data-baseweb="option"] {
            color: white !important;
        }

        .stTextInput > div > div > input:focus,
        .stTextArea > div > div > textarea:focus {
            border: 1px solid rgba(102, 126, 234, 0.8) !important;
            box-shadow: 0 0 20px rgba(102, 126, 234, 0.4) !important;
            transform: translateY(-2px);
        }

        /* Buttons */
        .stButton > button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
            color: white !important;
            border: none !important;
            border-radius: 12px !important;
            padding: 12px 32px !important;
            font-weight: 600 !important;
            font-family: 'Inter', sans-serif !important;
            box-shadow: 0 10px 30px rgba(102, 126, 234, 0.4) !important;
            transition: all 0.3s ease !important;
            letter-spacing: 0.5px !important;
        }

        .stButton > button:hover {
            transform: translateY(-3px) !important;
            box-shadow: 0 15px 40px rgba(102, 126, 234, 0.6) !important;
        }

        /* Alert Boxes */
        div[data-baseweb="notification"] {
            background: rgba(255, 255, 255, 0.05) !important;
            backdrop-filter: blur(10px) !important;
            border-radius: 12px !important;
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
            padding: 1rem 1.5rem !important;
        }

        /* Progress Bar */
        .stProgress > div > div > div > div {
            background: linear-gradient(90deg, #667eea 0%, #764ba2 50%, #f093fb 100%) !important;
            border-radius: 10px !important;
        }

        /* Metrics */
        [data-testid="stMetricValue"] {
            font-size: 2.5rem !important;
            font-weight: 700 !important;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }

        [data-testid="stMetricLabel"] {
            font-size: 0.9rem !important;
            color: #a0a0a0 !important;
            text-transform: uppercase;
            letter-spacing: 1px;
            font-weight: 500;
        }

        /* Divider */
        hr {
            border: none !important;
            height: 2px !important;
            background: linear-gradient(90deg, transparent, rgba(102, 126, 234, 0.5), transparent) !important;
            margin: 2rem 0 !important;
        }

        /* Scrollbar */
        ::-webkit-scrollbar {
            width: 10px;
            height: 10px;
        }

        ::-webkit-scrollbar-track {
            background: rgba(255, 255, 255, 0.05);
            border-radius: 10px;
        }

        ::-webkit-scrollbar-thumb {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 10px;
        }
        
        /* Mermaid Diagram Background */
        .mermaid {
            background: rgba(255, 255, 255, 0.05);
            padding: 1rem;
            border-radius: 12px;
        }
    </style>
    """
