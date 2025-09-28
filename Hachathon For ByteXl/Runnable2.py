import streamlit as st
from main import WebNavigatorAgent
from streamlit_mic_recorder import mic_recorder
import time
import json
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from datetime import datetime, timedelta
import base64
import io
from typing import Dict, List, Optional, Tuple
import hashlib
import uuid
import asyncio
from dataclasses import dataclass
import sqlite3
import threading

# ========================================================================================
# CONFIGURATION & CONSTANTS
# ========================================================================================

@dataclass
class AppConfig:
    """Application configuration settings"""
    APP_NAME: str = "Web Navigator AI"
    APP_VERSION: str = "2.0.0"
    APP_DESCRIPTION: str = "Enterprise-grade AI-powered web automation platform"
    COMPANY_NAME: str = "NOVA X"
    SUPPORT_EMAIL: str = "support@webnavigator.ai"
    DOCS_URL: str = "https://docs.webnavigator.ai"
    GITHUB_URL: str = "https://github.com/webnavigator-ai"
    MAX_HISTORY_ITEMS: int = 100
    DEFAULT_THEME: str = "dark"
    TYPING_SPEED: float = 0.03
    ANIMATION_DURATION: int = 300

CONFIG = AppConfig()

# ========================================================================================
# PAGE CONFIGURATION
# ========================================================================================

st.set_page_config(
    page_title=f"{CONFIG.APP_NAME} - {CONFIG.APP_DESCRIPTION}",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': CONFIG.DOCS_URL,
        'Report a bug': f"{CONFIG.GITHUB_URL}/issues",
        'About': f"""
        # {CONFIG.APP_NAME} v{CONFIG.APP_VERSION}
        
        {CONFIG.APP_DESCRIPTION}
        
        **Features:**
        - 🤖 Advanced AI-powered web automation
        - 🌐 Intelligent web scraping & data extraction  
        - 🧠 Natural language command processing
        - 🚀 Real-time browser automation
        - 📊 Advanced analytics & reporting
        - 🔒 Enterprise-grade security
        
        **Built with:**
        - Streamlit for the UI
        - Selenium for browser automation
        - Ollama for local LLM processing
        - Advanced AI algorithms
        
        © 2024 {CONFIG.COMPANY_NAME}
        """
    }
)

# ========================================================================================
# PREMIUM CSS STYLING - MARKETING WEBSITE LEVEL
# ========================================================================================

st.markdown("""
<style>
    /* ====================== FONT IMPORTS ====================== */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@100;200;300;400;500;600;700;800;900&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@100;200;300;400;500;600;700;800&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&display=swap');
    @import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css');
    
    /* ====================== CSS VARIABLES & DESIGN TOKENS ====================== */
    :root {
        /* Color Palette - Premium Dark Theme */
        --color-primary: #6366f1;
        --color-primary-dark: #4f46e5;
        --color-primary-light: #8b5cf6;
        --color-secondary: #06b6d4;
        --color-accent: #f59e0b;
        --color-success: #10b981;
        --color-warning: #f59e0b;
        --color-error: #ef4444;
        --color-info: #3b82f6;
        
        /* Background Colors */
        --bg-primary: #0a0a0f;
        --bg-secondary: #111118;
        --bg-tertiary: #1a1a24;
        --bg-surface: #252530;
        --bg-card: #2a2a38;
        --bg-glass: rgba(255, 255, 255, 0.02);
        --bg-glass-strong: rgba(255, 255, 255, 0.05);
        --bg-gradient-primary: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        --bg-gradient-secondary: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        --bg-gradient-accent: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        --bg-gradient-success: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        --bg-gradient-warning: linear-gradient(135deg, #ffb347 0%, #ffcc33 100%);
        --bg-gradient-error: linear-gradient(135deg, #ff416c 0%, #ff4b2b 100%);
        
        /* Text Colors */
        --text-primary: #ffffff;
        --text-secondary: #e2e8f0;
        --text-tertiary: #94a3b8;
        --text-muted: #64748b;
        --text-disabled: #475569;
        
        /* Border & Shadow */
        --border-primary: rgba(255, 255, 255, 0.08);
        --border-secondary: rgba(255, 255, 255, 0.12);
        --border-accent: rgba(99, 102, 241, 0.3);
        --shadow-sm: 0 1px 3px rgba(0, 0, 0, 0.12);
        --shadow-md: 0 4px 12px rgba(0, 0, 0, 0.15);
        --shadow-lg: 0 8px 24px rgba(0, 0, 0, 0.20);
        --shadow-xl: 0 16px 48px rgba(0, 0, 0, 0.25);
        --shadow-glow: 0 0 20px rgba(99, 102, 241, 0.15);
        --shadow-glow-strong: 0 0 40px rgba(99, 102, 241, 0.25);
        
        /* Spacing & Sizing */
        --spacing-xs: 0.25rem;
        --spacing-sm: 0.5rem;
        --spacing-md: 1rem;
        --spacing-lg: 1.5rem;
        --spacing-xl: 2rem;
        --spacing-2xl: 3rem;
        --spacing-3xl: 4rem;
        
        --radius-sm: 4px;
        --radius-md: 8px;
        --radius-lg: 12px;
        --radius-xl: 16px;
        --radius-2xl: 24px;
        --radius-full: 9999px;
        
        /* Typography */
        --font-primary: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif;
        --font-mono: 'JetBrains Mono', 'Fira Code', 'Monaco', 'Consolas', monospace;
        --font-display: 'Space Grotesk', var(--font-primary);
        
        --font-size-xs: 0.75rem;
        --font-size-sm: 0.875rem;
        --font-size-base: 1rem;
        --font-size-lg: 1.125rem;
        --font-size-xl: 1.25rem;
        --font-size-2xl: 1.5rem;
        --font-size-3xl: 1.875rem;
        --font-size-4xl: 2.25rem;
        --font-size-5xl: 3rem;
        --font-size-6xl: 3.75rem;
        
        /* Transitions */
        --transition-fast: 150ms cubic-bezier(0.4, 0, 0.2, 1);
        --transition-normal: 300ms cubic-bezier(0.4, 0, 0.2, 1);
        --transition-slow: 500ms cubic-bezier(0.4, 0, 0.2, 1);
        
        /* Z-Index */
        --z-dropdown: 1000;
        --z-sticky: 1020;
        --z-fixed: 1030;
        --z-modal-backdrop: 1040;
        --z-modal: 1050;
        --z-popover: 1060;
        --z-tooltip: 1070;
        
        /* Animations */
        --animation-bounce: bounce 1s infinite;
        --animation-pulse: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
        --animation-ping: ping 1s cubic-bezier(0, 0, 0.2, 1) infinite;
        --animation-spin: spin 1s linear infinite;
    }
    
    /* ====================== GLOBAL STYLES & RESET ====================== */
    * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }
    
    html {
        scroll-behavior: smooth;
        font-size: 16px;
        line-height: 1.6;
    }
    
    body {
        font-family: var(--font-primary);
        -webkit-font-smoothing: antialiased;
        -moz-osx-font-smoothing: grayscale;
        text-rendering: optimizeLegibility;
    }
    
    .stApp {
        background: linear-gradient(135deg, var(--bg-primary) 0%, var(--bg-secondary) 50%, var(--bg-primary) 100%);
        color: var(--text-primary);
        font-family: var(--font-primary);
        min-height: 100vh;
        position: relative;
        overflow-x: hidden;
    }
    
    /* Animated Background Particles */
    .stApp::before {
        content: '';
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-image: 
            radial-gradient(circle at 20% 80%, rgba(99, 102, 241, 0.1) 0%, transparent 50%),
            radial-gradient(circle at 80% 20%, rgba(139, 92, 246, 0.1) 0%, transparent 50%),
            radial-gradient(circle at 40% 40%, rgba(6, 182, 212, 0.05) 0%, transparent 50%);
        animation: float 20s ease-in-out infinite;
        pointer-events: none;
        z-index: -2;
    }
    
    .stApp::after {
        content: '';
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='0.02'%3E%3Ccircle cx='7' cy='7' r='1'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E");
        pointer-events: none;
        z-index: -1;
    }
    
    /* ====================== MAIN CONTAINER & LAYOUT ====================== */
    .main-container {
        background: var(--bg-glass);
        backdrop-filter: blur(24px);
        -webkit-backdrop-filter: blur(24px);
        border: 1px solid var(--border-primary);
        border-radius: var(--radius-2xl);
        padding: var(--spacing-3xl);
        margin: var(--spacing-xl) auto;
        max-width: 1400px;
        box-shadow: var(--shadow-xl), var(--shadow-glow);
        position: relative;
        overflow: hidden;
        transition: all var(--transition-normal);
    }
    
    .main-container::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 2px;
        background: var(--bg-gradient-primary);
        opacity: 0.8;
    }
    
    .main-container::after {
        content: '';
        position: absolute;
        top: -1px;
        left: -1px;
        right: -1px;
        bottom: -1px;
        background: var(--bg-gradient-primary);
        border-radius: var(--radius-2xl);
        opacity: 0;
        transition: opacity var(--transition-normal);
        z-index: -1;
    }
    
    .main-container:hover {
        box-shadow: var(--shadow-xl), var(--shadow-glow-strong);
        transform: translateY(-2px);
        border-color: var(--border-accent);
    }
    
    .main-container:hover::after {
        opacity: 0.1;
    }
    
    /* ====================== HERO SECTION ====================== */
    .hero-section {
        text-align: center;
        padding: var(--spacing-3xl) 0;
        margin-bottom: var(--spacing-3xl);
        position: relative;
        overflow: hidden;
    }
    
    .hero-section::before {
        content: '';
        position: absolute;
        top: 50%;
        left: 50%;
        width: 600px;
        height: 600px;
        background: radial-gradient(circle, rgba(99, 102, 241, 0.1) 0%, transparent 70%);
        transform: translate(-50%, -50%);
        animation: pulse 4s ease-in-out infinite;
        z-index: -1;
    }
    
    .hero-title {
        font-family: var(--font-display);
        font-size: clamp(2.5rem, 5vw, 4rem);
        font-weight: 800;
        line-height: 1.1;
        letter-spacing: -0.02em;
        margin-bottom: var(--spacing-lg);
        background: var(--bg-gradient-primary);
        background-clip: text;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: titleGlow 3s ease-in-out infinite alternate;
        position: relative;
    }
    
    .hero-subtitle {
        font-size: var(--font-size-xl);
        font-weight: 400;
        color: var(--text-secondary);
        max-width: 800px;
        margin: 0 auto var(--spacing-2xl) auto;
        line-height: 1.6;
    }
    
    .hero-features {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: var(--spacing-lg);
        margin: var(--spacing-2xl) 0;
        padding: 0 var(--spacing-md);
    }
    
    .hero-feature {
        background: var(--bg-glass);
        border: 1px solid var(--border-primary);
        border-radius: var(--radius-lg);
        padding: var(--spacing-lg);
        text-align: center;
        transition: all var(--transition-normal);
        cursor: pointer;
        position: relative;
        overflow: hidden;
    }
    
    .hero-feature::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(99, 102, 241, 0.1), transparent);
        transition: left 0.5s ease;
    }
    
    .hero-feature:hover::before {
        left: 100%;
    }
    
    .hero-feature:hover {
        background: var(--bg-glass-strong);
        border-color: var(--border-accent);
        transform: translateY(-4px);
        box-shadow: var(--shadow-lg);
    }
    
    .hero-feature-icon {
        font-size: var(--font-size-2xl);
        margin-bottom: var(--spacing-sm);
        display: block;
    }
    
    .hero-feature-title {
        font-size: var(--font-size-lg);
        font-weight: 600;
        color: var(--text-primary);
        margin-bottom: var(--spacing-xs);
    }
    
    .hero-feature-desc {
        font-size: var(--font-size-sm);
        color: var(--text-tertiary);
        line-height: 1.5;
    }
    
    /* ====================== ADVANCED INPUT SECTION ====================== */
    .input-section {
        background: var(--bg-glass);
        border: 1px solid var(--border-primary);
        border-radius: var(--radius-xl);
        padding: var(--spacing-2xl);
        margin: var(--spacing-2xl) 0;
        backdrop-filter: blur(16px);
        position: relative;
        overflow: hidden;
    }
    
    .input-section::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 1px;
        background: var(--bg-gradient-accent);
        opacity: 0.6;
    }
    
    .input-header {
        display: flex;
        align-items: center;
        gap: var(--spacing-sm);
        margin-bottom: var(--spacing-lg);
    }
    
    .input-title {
        font-size: var(--font-size-xl);
        font-weight: 600;
        color: var(--text-primary);
        margin: 0;
    }
    
    .input-subtitle {
        font-size: var(--font-size-sm);
        color: var(--text-tertiary);
        margin-top: var(--spacing-xs);
    }
    
    /* Enhanced Input Styling */
    .stTextInput > div > div > input {
        background: var(--bg-surface) !important;
        border: 2px solid var(--border-primary) !important;
        border-radius: var(--radius-lg) !important;
        color: var(--text-primary) !important;
        font-size: var(--font-size-lg) !important;
        padding: var(--spacing-lg) var(--spacing-xl) !important;
        font-family: var(--font-primary) !important;
        transition: all var(--transition-normal) !important;
        box-shadow: var(--shadow-sm) !important;
        font-weight: 400 !important;
        line-height: 1.5 !important;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: var(--color-primary) !important;
        box-shadow: 
            0 0 0 3px rgba(99, 102, 241, 0.1) !important,
            0 4px 12px rgba(0, 0, 0, 0.15) !important;
        outline: none !important;
        transform: translateY(-1px) !important;
        background: var(--bg-card) !important;
    }
    
    .stTextInput > div > div > input::placeholder {
        color: var(--text-muted) !important;
        font-style: italic !important;
        font-weight: 300 !important;
    }
    
    /* ====================== PREMIUM BUTTON SYSTEM ====================== */
    .stButton > button {
        background: var(--bg-gradient-primary) !important;
        border: none !important;
        border-radius: var(--radius-lg) !important;
        color: var(--text-primary) !important;
        font-weight: 600 !important;
        font-size: var(--font-size-lg) !important;
        padding: var(--spacing-lg) var(--spacing-2xl) !important;
        font-family: var(--font-primary) !important;
        transition: all var(--transition-normal) !important;
        box-shadow: var(--shadow-md), 0 4px 12px rgba(99, 102, 241, 0.3) !important;
        cursor: pointer !important;
        text-transform: none !important;
        letter-spacing: 0.025em !important;
        position: relative !important;
        overflow: hidden !important;
    }
    
    .stButton > button::before {
        content: '';
        position: absolute;
        top: 50%;
        left: 50%;
        width: 0;
        height: 0;
        background: rgba(255, 255, 255, 0.2);
        border-radius: 50%;
        transform: translate(-50%, -50%);
        transition: width 0.3s ease, height 0.3s ease;
    }
    
    .stButton > button:hover::before {
        width: 300px;
        height: 300px;
    }
    
    .stButton > button:hover {
        box-shadow: var(--shadow-lg), 0 8px 24px rgba(99, 102, 241, 0.4) !important;
        transform: translateY(-3px) !important;
        background: linear-gradient(135deg, #7c3aed 0%, #6366f1 100%) !important;
    }
    
    .stButton > button:active {
        transform: translateY(-1px) !important;
        box-shadow: var(--shadow-md), 0 2px 8px rgba(99, 102, 241, 0.3) !important;
    }
    
    .stButton > button:disabled {
        background: var(--bg-surface) !important;
        color: var(--text-disabled) !important;
        box-shadow: none !important;
        cursor: not-allowed !important;
        transform: none !important;
    }
    
    /* ====================== QUICK ACTIONS GRID ====================== */
    .quick-actions-section {
        margin: var(--spacing-2xl) 0;
    }
    
    .quick-actions-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: var(--spacing-lg);
    }
    
    .section-title {
        font-size: var(--font-size-2xl);
        font-weight: 700;
        color: var(--text-primary);
        margin: 0;
        display: flex;
        align-items: center;
        gap: var(--spacing-sm);
    }
    
    .section-subtitle {
        font-size: var(--font-size-sm);
        color: var(--text-tertiary);
        margin-left: var(--spacing-2xl);
    }
    
    .quick-actions-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
        gap: var(--spacing-lg);
        margin: var(--spacing-lg) 0;
    }
    
    .quick-action-card {
        background: var(--bg-glass);
        border: 1px solid var(--border-primary);
        border-radius: var(--radius-xl);
        padding: var(--spacing-xl);
        transition: all var(--transition-normal);
        cursor: pointer;
        position: relative;
        overflow: hidden;
        backdrop-filter: blur(12px);
    }
    
    .quick-action-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(99, 102, 241, 0.05), transparent);
        transition: left 0.6s ease;
    }
    
    .quick-action-card:hover::before {
        left: 100%;
    }
    
    .quick-action-card:hover {
        background: var(--bg-glass-strong);
        border-color: var(--border-accent);
        transform: translateY(-6px);
        box-shadow: var(--shadow-lg), var(--shadow-glow);
    }
    
    .quick-action-icon {
        font-size: var(--font-size-3xl);
        margin-bottom: var(--spacing-md);
        display: block;
        color: var(--color-primary);
    }
    
    .quick-action-title {
        font-size: var(--font-size-lg);
        font-weight: 600;
        color: var(--text-primary);
        margin-bottom: var(--spacing-sm);
    }
    
    .quick-action-desc {
        font-size: var(--font-size-sm);
        color: var(--text-tertiary);
        line-height: 1.6;
        margin-bottom: var(--spacing-md);
    }
    
    .quick-action-tags {
        display: flex;
        flex-wrap: wrap;
        gap: var(--spacing-xs);
    }
    
    .quick-action-tag {
        background: rgba(99, 102, 241, 0.1);
        color: var(--color-primary);
        padding: var(--spacing-xs) var(--spacing-sm);
        border-radius: var(--radius-md);
        font-size: var(--font-size-xs);
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    /* ====================== MESSAGE & NOTIFICATION SYSTEM ====================== */
    .message-container {
        position: relative;
        margin: var(--spacing-lg) 0;
    }
    
    .message-success {
        background: var(--bg-gradient-success);
        border: none;
        border-radius: var(--radius-lg);
        padding: var(--spacing-lg) var(--spacing-xl);
        color: var(--text-primary);
        font-weight: 500;
        box-shadow: var(--shadow-md), 0 4px 12px rgba(16, 185, 129, 0.3);
        animation: slideInUp 0.4s ease-out;
        display: flex;
        align-items: center;
        gap: var(--spacing-md);
        position: relative;
        overflow: hidden;
    }
    
    .message-error {
        background: var(--bg-gradient-error);
        border: none;
        border-radius: var(--radius-lg);
        padding: var(--spacing-lg) var(--spacing-xl);
        color: var(--text-primary);
        font-weight: 500;
        box-shadow: var(--shadow-md), 0 4px 12px rgba(239, 68, 68, 0.3);
        animation: slideInUp 0.4s ease-out;
        display: flex;
        align-items: center;
        gap: var(--spacing-md);
        position: relative;
        overflow: hidden;
    }
    
    .message-info {
        background: rgba(59, 130, 246, 0.1);
        border: 1px solid rgba(59, 130, 246, 0.3);
        border-radius: var(--radius-lg);
        padding: var(--spacing-lg) var(--spacing-xl);
        color: #60a5fa;
        font-weight: 500;
        backdrop-filter: blur(12px);
        display: flex;
        align-items: center;
        gap: var(--spacing-md);
    }
    
    .message-warning {
        background: rgba(245, 158, 11, 0.1);
        border: 1px solid rgba(245, 158, 11, 0.3);
        border-radius: var(--radius-lg);
        padding: var(--spacing-lg) var(--spacing-xl);
        color: #fbbf24;
        font-weight: 500;
        backdrop-filter: blur(12px);
        display: flex;
        align-items: center;
        gap: var(--spacing-md);
    }
    
    .message-icon {
        font-size: var(--font-size-lg);
        flex-shrink: 0;
    }
    
    .message-content {
        flex: 1;
    }
    
    .message-title {
        font-weight: 600;
        margin-bottom: var(--spacing-xs);
    }
    
    .message-text {
        font-size: var(--font-size-sm);
        opacity: 0.9;
        line-height: 1.5;
    }
    
    /* ====================== ADVANCED RESULT DISPLAY ====================== */
    .results-section {
        margin: var(--spacing-2xl) 0;
    }
    
    .result-card {
        background: var(--bg-glass);
        border: 1px solid var(--border-primary);
        border-radius: var(--radius-xl);
        padding: var(--spacing-2xl);
        margin: var(--spacing-xl) 0;
        backdrop-filter: blur(20px);
        box-shadow: var(--shadow-lg);
        transition: all var(--transition-normal);
        position: relative;
        overflow: hidden;
    }
    
    .result-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: var(--bg-gradient-accent);
        opacity: 0.8;
    }
    
    .result-card:hover {
        transform: translateY(-4px);
        box-shadow: var(--shadow-xl), var(--shadow-glow);
        border-color: var(--border-accent);
    }
    
    .result-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: var(--spacing-xl);
        padding-bottom: var(--spacing-lg);
        border-bottom: 1px solid var(--border-primary);
    }
    
    .result-title {
        font-size: var(--font-size-xl);
        font-weight: 600;
        color: var(--text-primary);
        margin: 0;
        display: flex;
        align-items: center;
        gap: var(--spacing-sm);
    }
    
    .result-meta {
        display: flex;
        align-items: center;
        gap: var(--spacing-lg);
        font-size: var(--font-size-sm);
        color: var(--text-tertiary);
        font-family: var(--font-mono);
    }
    
    .result-meta-item {
        display: flex;
        align-items: center;
        gap: var(--spacing-xs);
        background: var(--bg-surface);
        padding: var(--spacing-xs) var(--spacing-sm);
        border-radius: var(--radius-md);
        border: 1px solid var(--border-primary);
    }
    
    .result-content {
        line-height: 1.7;
        color: var(--text-secondary);
    }
    
    .result-item {
        background: var(--bg-surface);
        border: 1px solid var(--border-primary);
        border-radius: var(--radius-lg);
        padding: var(--spacing-lg);
        margin: var(--spacing-md) 0;
        transition: all var(--transition-fast);
        cursor: pointer;
    }
    
    .result-item:hover {
        background: var(--bg-card);
        border-color: var(--border-secondary);
        transform: translateX(4px);
    }
    
    .result-item-title {
        font-weight: 600;
        color: var(--text-primary);
        margin-bottom: var(--spacing-xs);
    }
    
    .result-item-content {
        color: var(--text-secondary);
        line-height: 1.6;
    }
    
    /* ====================== ADVANCED LOADING STATES ====================== */
    .loading-section {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding: var(--spacing-3xl) 0;
        gap: var(--spacing-xl);
        text-align: center;
    }
    
    .loading-animation {
        position: relative;
        width: 80px;
        height: 80px;
    }
    
    .loading-spinner {
        width: 100%;
        height: 100%;
        border: 3px solid var(--border-primary);
        border-top: 3px solid var(--color-primary);
        border-radius: 50%;
        animation: spin 1s linear infinite;
        position: relative;
    }
    
    .loading-spinner::after {
        content: '';
        position: absolute;
        top: 50%;
        left: 50%;
        width: 20px;
        height: 20px;
        background: var(--color-primary);
        border-radius: 50%;
        transform: translate(-50%, -50%);
        animation: pulse 2s ease-in-out infinite;
    }
    
    .loading-text {
        font-size: var(--font-size-xl);
        font-weight: 600;
        color: var(--text-primary);
        margin-bottom: var(--spacing-sm);
    }
    
    .loading-subtext {
        font-size: var(--font-size-sm);
        color: var(--text-tertiary);
        max-width: 400px;
        line-height: 1.6;
    }
    
    .loading-progress {
        width: 100%;
        max-width: 400px;
        height: 6px;
        background: var(--bg-surface);
        border-radius: var(--radius-full);
        overflow: hidden;
        margin-top: var(--spacing-lg);
    }
    
    .loading-progress-bar {
        height: 100%;
        background: var(--bg-gradient-primary);
        border-radius: var(--radius-full);
        transition: width var(--transition-normal);
        position: relative;
    }
    
    .loading-progress-bar::after {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        bottom: 0;
        right: 0;
        background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
        animation: shimmer 1.5s ease-in-out infinite;
    }
    
    /* ====================== TASK HISTORY SECTION ====================== */
    .history-section {
        background: var(--bg-glass);
        border: 1px solid var(--border-primary);
        border-radius: var(--radius-xl);
        padding: var(--spacing-2xl);
        margin: var(--spacing-2xl) 0;
        backdrop-filter: blur(16px);
    }
    
    .history-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: var(--spacing-xl);
        padding-bottom: var(--spacing-lg);
        border-bottom: 1px solid var(--border-primary);
    }
    
    .history-controls {
        display: flex;
        align-items: center;
        gap: var(--spacing-md);
    }
    
    .history-item {
        background: var(--bg-surface);
        border: 1px solid var(--border-primary);
        border-left: 4px solid var(--color-primary);
        border-radius: var(--radius-lg);
        padding: var(--spacing-lg);
        margin-bottom: var(--spacing-md);
        transition: all var(--transition-normal);
        cursor: pointer;
        position: relative;
        overflow: hidden;
    }
    
    .history-item::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(99, 102, 241, 0.05), transparent);
        transition: left 0.5s ease;
    }
    
    .history-item:hover::before {
        left: 100%;
    }
    
    .history-item:hover {
        background: var(--bg-card);
        border-color: var(--border-accent);
        border-left-color: var(--color-primary-light);
        transform: translateX(6px);
        box-shadow: var(--shadow-md);
    }
    
    .history-item-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: var(--spacing-sm);
    }
    
    .history-item-title {
        font-weight: 600;
        color: var(--text-primary);
        display: flex;
        align-items: center;
        gap: var(--spacing-sm);
        font-size: var(--font-size-lg);
    }
    
    .history-item-status {
        padding: var(--spacing-xs) var(--spacing-sm);
        border-radius: var(--radius-md);
        font-size: var(--font-size-xs);
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    .status-completed {
        background: rgba(16, 185, 129, 0.1);
        color: var(--color-success);
        border: 1px solid rgba(16, 185, 129, 0.3);
    }
    
    .status-error {
        background: rgba(239, 68, 68, 0.1);
        color: var(--color-error);
        border: 1px solid rgba(239, 68, 68, 0.3);
    }
    
    .status-processing {
        background: rgba(245, 158, 11, 0.1);
        color: var(--color-warning);
        border: 1px solid rgba(245, 158, 11, 0.3);
        animation: pulse 2s infinite;
    }
    
    .history-item-time {
        font-size: var(--font-size-sm);
        color: var(--text-muted);
        font-family: var(--font-mono);
        display: flex;
        align-items: center;
        gap: var(--spacing-xs);
    }
    
    .history-item-content {
        color: var(--text-secondary);
        line-height: 1.6;
        margin: var(--spacing-sm) 0;
        font-size: var(--font-size-sm);
    }
    
    .history-item-footer {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-top: var(--spacing-md);
        padding-top: var(--spacing-sm);
        border-top: 1px solid var(--border-primary);
    }
    
    .history-item-tags {
        display: flex;
        gap: var(--spacing-xs);
    }
    
    .history-item-tag {
        background: rgba(99, 102, 241, 0.1);
        color: var(--color-primary);
        padding: 2px var(--spacing-xs);
        border-radius: var(--radius-sm);
        font-size: var(--font-size-xs);
        font-weight: 500;
    }
    
    /* ====================== PREMIUM SIDEBAR ====================== */
    .css-1d391kg, .stSidebar {
        background: linear-gradient(180deg, var(--bg-primary) 0%, var(--bg-secondary) 100%) !important;
        border-right: 1px solid var(--border-primary) !important;
    }
    
    .sidebar-section {
        background: var(--bg-glass);
        border: 1px solid var(--border-primary);
        border-radius: var(--radius-lg);
        padding: var(--spacing-lg);
        margin: var(--spacing-lg) 0;
        backdrop-filter: blur(12px);
        transition: all var(--transition-normal);
    }
    
    .sidebar-section:hover {
        background: var(--bg-glass-strong);
        border-color: var(--border-secondary);
        box-shadow: var(--shadow-md);
    }
    
    .sidebar-title {
        font-size: var(--font-size-lg);
        font-weight: 600;
        color: var(--text-primary);
        margin: 0 0 var(--spacing-md) 0;
        display: flex;
        align-items: center;
        gap: var(--spacing-sm);
    }
    
    .metric-grid {
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: var(--spacing-sm);
        margin-bottom: var(--spacing-lg);
    }
    
    .metric-card {
        background: var(--bg-surface);
        border: 1px solid var(--border-primary);
        border-radius: var(--radius-lg);
        padding: var(--spacing-lg);
        text-align: center;
        transition: all var(--transition-normal);
        position: relative;
        overflow: hidden;
        cursor: pointer;
    }
    
    .metric-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 2px;
        background: var(--bg-gradient-primary);
        opacity: 0;
        transition: opacity var(--transition-normal);
    }
    
    .metric-card:hover::before {
        opacity: 1;
    }
    
    .metric-card:hover {
        background: var(--bg-card);
        transform: translateY(-2px);
        box-shadow: var(--shadow-md);
        border-color: var(--border-accent);
    }
    
    .metric-number {
        font-size: var(--font-size-2xl);
        font-weight: 800;
        color: var(--color-primary);
        margin: 0;
        font-family: var(--font-mono);
        line-height: 1;
    }
    
    .metric-label {
        font-size: var(--font-size-xs);
        color: var(--text-tertiary);
        font-weight: 600;
        margin: var(--spacing-xs) 0 0 0;
        text-transform: uppercase;
        letter-spacing: 0.1em;
    }
    
    .metric-change {
        font-size: var(--font-size-xs);
        font-weight: 500;
        margin-top: var(--spacing-xs);
        display: flex;
        align-items: center;
        justify-content: center;
        gap: var(--spacing-xs);
    }
    
    .metric-change.positive {
        color: var(--color-success);
    }
    
    .metric-change.negative {
        color: var(--color-error);
    }
    
    /* ====================== STATUS INDICATORS ====================== */
    .status-indicator {
        display: inline-flex;
        align-items: center;
        gap: var(--spacing-sm);
        padding: var(--spacing-sm) var(--spacing-md);
        border-radius: var(--radius-lg);
        font-size: var(--font-size-sm);
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        position: relative;
        overflow: hidden;
    }
    
    .status-ready {
        background: rgba(16, 185, 129, 0.1);
        color: var(--color-success);
        border: 1px solid rgba(16, 185, 129, 0.3);
    }
    
    .status-processing {
        background: rgba(245, 158, 11, 0.1);
        color: var(--color-warning);
        border: 1px solid rgba(245, 158, 11, 0.3);
        animation: pulse 2s infinite;
    }
    
    .status-error {
        background: rgba(239, 68, 68, 0.1);
        color: var(--color-error);
        border: 1px solid rgba(239, 68, 68, 0.3);
    }
    
    .status-indicator::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.1), transparent);
        transition: left 0.5s ease;
    }
    
    .status-indicator:hover::before {
        left: 100%;
    }
    
    /* ====================== FEATURE LIST ====================== */
    .feature-list {
        list-style: none;
        padding: 0;
        margin: 0;
    }
    
    .feature-item {
        display: flex;
        align-items: center;
        gap: var(--spacing-md);
        padding: var(--spacing-sm) var(--spacing-md);
        margin-bottom: var(--spacing-sm);
        border-radius: var(--radius-lg);
        transition: all var(--transition-fast);
        color: var(--text-secondary);
        cursor: pointer;
        position: relative;
        overflow: hidden;
    }
    
    .feature-item::before {
        content: '';
        position: absolute;
        left: 0;
        top: 0;
        bottom: 0;
        width: 0;
        background: var(--color-primary);
        transition: width var(--transition-fast);
    }
    
    .feature-item:hover::before {
        width: 3px;
    }
    
    .feature-item:hover {
        background: var(--bg-glass);
        color: var(--text-primary);
        transform: translateX(6px);
        padding-left: var(--spacing-lg);
    }
    
    .feature-icon {
        font-size: var(--font-size-lg);
        width: 24px;
        text-align: center;
        flex-shrink: 0;
    }
    
    .feature-content {
        flex: 1;
    }
    
    .feature-title {
        font-weight: 600;
        margin-bottom: var(--spacing-xs);
        font-size: var(--font-size-sm);
    }
    
    .feature-desc {
        font-size: var(--font-size-xs);
        color: var(--text-muted);
        line-height: 1.4;
    }
    
    /* ====================== ANIMATIONS & KEYFRAMES ====================== */
    @keyframes float {
        0%, 100% { transform: translateY(0px); }
        50% { transform: translateY(-20px); }
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }
    
    @keyframes spin {
        from { transform: rotate(0deg); }
        to { transform: rotate(360deg); }
    }
    
    @keyframes slideInUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes slideInLeft {
        from {
            opacity: 0;
            transform: translateX(-30px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }
    
    @keyframes titleGlow {
        0% { 
            filter: brightness(1) drop-shadow(0 0 20px rgba(99, 102, 241, 0.3));
        }
        100% { 
            filter: brightness(1.1) drop-shadow(0 0 30px rgba(99, 102, 241, 0.5));
        }
    }
    
    @keyframes shimmer {
        0% { transform: translateX(-100%); }
        100% { transform: translateX(100%); }
    }
    
    /* ====================== RESPONSIVE DESIGN ====================== */
    @media (max-width: 1200px) {
        .main-container {
            max-width: 100%;
            margin: var(--spacing-md);
            padding: var(--spacing-2xl);
        }
    }
    
    @media (max-width: 768px) {
        .main-container {
            margin: var(--spacing-sm);
            padding: var(--spacing-xl);
        }
        
        .hero-title {
            font-size: var(--font-size-4xl);
        }
        
        .hero-features {
            grid-template-columns: 1fr;
        }
        
        .quick-actions-grid {
            grid-template-columns: 1fr;
        }
        
        .metric-grid {
            grid-template-columns: 1fr;
        }
        
        .result-header {
            flex-direction: column;
            align-items: flex-start;
            gap: var(--spacing-md);
        }
        
        .result-meta {
            flex-wrap: wrap;
        }
    }
    
    @media (max-width: 480px) {
        .main-container {
            padding: var(--spacing-lg);
        }
        
        .hero-title {
            font-size: var(--font-size-3xl);
        }
        
        .section-title {
            font-size: var(--font-size-xl);
        }
    }
    
    /* ====================== ACCESSIBILITY ====================== */
    @media (prefers-reduced-motion: reduce) {
        *,
        *::before,
        *::after {
            animation-duration: 0.01ms !important;
            animation-iteration-count: 1 !important;
            transition-duration: 0.01ms !important;
            scroll-behavior: auto !important;
        }
    }
    
    /* Focus styles for accessibility */
    *:focus {
        outline: 2px solid var(--color-primary);
        outline-offset: 2px;
        border-radius: var(--radius-sm);
    }
    
    /* High contrast mode support */
    @media (prefers-contrast: high) {
        :root {
            --bg-glass: rgba(255, 255, 255, 0.1);
            --border-primary: rgba(255, 255, 255, 0.3);
            --text-primary: #ffffff;
        }
    }
    
    /* ====================== HIDE STREAMLIT ELEMENTS ====================== */
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    header { visibility: hidden; }
    .stDeployButton { display: none; }
    .stDecoration { display: none; }
    
    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: var(--bg-surface);
        border-radius: var(--radius-md);
    }
    
    ::-webkit-scrollbar-thumb {
        background: var(--color-primary);
        border-radius: var(--radius-md);
        border: 2px solid var(--bg-surface);
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: var(--color-primary-dark);
    }
    
    /* Selection color */
    ::selection {
        background: rgba(99, 102, 241, 0.3);
        color: var(--text-primary);
    }
</style>
""", unsafe_allow_html=True)

# ========================================================================================
# ENHANCED SESSION STATE MANAGEMENT
# ========================================================================================

@dataclass
class SessionMetrics:
    """Session metrics tracking"""
    start_time: datetime
    task_count: int = 0
    success_count: int = 0
    error_count: int = 0
    total_execution_time: float = 0.0
    avg_execution_time: float = 0.0
    last_execution_time: float = 0.0
    commands_history: List[str] = None
    
    def __post_init__(self):
        if self.commands_history is None:
            self.commands_history = []

def initialize_session_state():
    """Initialize comprehensive session state"""
    defaults = {
        'metrics': SessionMetrics(start_time=datetime.now()),
        'processing': False,
        'show_welcome': True,
        'selected_command': '',
        'theme': 'dark',
        'user_preferences': {
            'animations_enabled': True,
            'sound_enabled': False,
            'compact_mode': False,
            'advanced_mode': False
        },
        'current_task_id': '',
        'workspace': 'default',
        'last_search_query': '',
        'bookmarked_results': [],
        'custom_commands': []
    }
    
    for key, default in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default

initialize_session_state()

# ========================================================================================
# ENHANCED UTILITY FUNCTIONS
# ========================================================================================

def format_time_ago(timestamp: datetime) -> str:
    """Format timestamp as time ago"""
    now = datetime.now()
    diff = now - timestamp
    
    if diff.days > 0:
        return f"{diff.days}d ago"
    elif diff.seconds > 3600:
        return f"{diff.seconds // 3600}h ago"
    elif diff.seconds > 60:
        return f"{diff.seconds // 60}m ago"
    else:
        return "just now"

def format_execution_time(seconds: float) -> str:
    """Enhanced execution time formatting"""
    if seconds < 0.001:
        return f"{seconds*1000:.1f}μs"
    elif seconds < 1:
        return f"{seconds*1000:.0f}ms"
    elif seconds < 60:
        return f"{seconds:.2f}s"
    else:
        minutes = int(seconds // 60)
        remaining_seconds = seconds % 60
        return f"{minutes}m {remaining_seconds:.1f}s"

def get_status_config(status: str) -> Dict[str, str]:
    """Get status configuration"""
    configs = {
        'completed': {'icon': '✅', 'color': 'success', 'label': 'Completed'},
        'error': {'icon': '❌', 'color': 'error', 'label': 'Failed'},
        'processing': {'icon': '⏳', 'color': 'warning', 'label': 'Processing'},
        'pending': {'icon': '⏸️', 'color': 'info', 'label': 'Pending'},
        'cancelled': {'icon': '⏹️', 'color': 'muted', 'label': 'Cancelled'}
    }
    return configs.get(status, {'icon': '❓', 'color': 'muted', 'label': 'Unknown'})

def create_progress_bar(progress: float, total: float = 100, height: str = "6px") -> str:
    """Create animated progress bar"""
    percentage = min(100, (progress / total) * 100)
    return f"""
    <div style="
        width: 100%;
        height: {height};
        background: var(--bg-surface);
        border-radius: var(--radius-full);
        overflow: hidden;
        margin: var(--spacing-sm) 0;
    ">
        <div style="
            height: 100%;
            width: {percentage}%;
            background: var(--bg-gradient-primary);
            border-radius: var(--radius-full);
            transition: width var(--transition-normal);
            position: relative;
        ">
            <div style="
                position: absolute;
                top: 0;
                left: 0;
                bottom: 0;
                right: 0;
                background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
                animation: shimmer 1.5s ease-in-out infinite;
            "></div>
        </div>
    </div>
    """

# ========================================================================================
# AGENT INITIALIZATION WITH ENHANCED CACHING
# ========================================================================================

@st.cache_resource(show_spinner=False)
def get_enhanced_agent():
    """Initialize agent with enhanced capabilities"""
    try:
        return WebNavigatorAgent()
    except Exception as e:
        st.error(f"Failed to initialize AI agent: {str(e)}")
        return None

agent = get_enhanced_agent()

# ====================== HERO SECTION ======================
st.markdown('<h1 style="text-align: center; font-size: 3.5rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); background-clip: text; -webkit-background-clip: text; -webkit-text-fill-color: transparent;">Web Navigator AI</h1>', unsafe_allow_html=True)
st.markdown('<div style="text-align: center; color: #94a3b8; margin: 2rem auto; max-width: 800px;">Transform the way you interact with the web through advanced AI-powered automation and intelligent data extraction.</div>', unsafe_allow_html=True)

# ====================== ENHANCED INPUT SECTION ======================
st.markdown("### 🎯 Command Center")
st.markdown("Enter your request in natural language or use voice commands")

# Advanced input layout
input_col, voice_col, execute_col = st.columns([6, 1.5, 1.5])

with input_col:
    user_input = st.text_input(
        "",
        placeholder="🔍 Search for the latest iPhone reviews and compare prices across multiple retailers...",
        key="main_input",
        label_visibility="collapsed",
        help="Describe what you want to do in natural language"
    )

with voice_col:
    audio_text = mic_recorder(
        start_prompt="🎤 Voice",
        stop_prompt="⏹️ Stop",
        just_once=True,
        use_container_width=True,
        key="voice_input",
        format="webm"
    )
    
    if audio_text:
        if isinstance(audio_text, dict) and "text" in audio_text:
            user_input = audio_text["text"]
            st.success(f"🎤 Voice captured: {user_input[:50]}...")
        elif isinstance(audio_text, str):
            user_input = audio_text
            st.success(f"🎤 Voice: {user_input[:50]}...")
        st.session_state.auto_process = True

with execute_col:
    process_button = st.button(
        "🚀 Execute",
        type="primary",
        use_container_width=True,
        disabled=st.session_state.processing or not agent,
        help="Execute the AI command"
    )

# ====================== QUICK ACTIONS WITH ENHANCED GRID ======================
st.markdown("### ⚡ Quick Actions")
st.markdown("Popular AI-powered automation tasks")

# Enhanced quick actions
quick_actions_data = [
    {
        "icon": "🛒",
        "title": "Smart Shopping",
        "description": "Find products, compare prices, read reviews, and get the best deals across multiple e-commerce platforms.",
        "command": "Find the best deals on iPhone 15 Pro with price comparisons and user reviews from multiple retailers",
        "tags": ["E-commerce", "Price Comparison", "Reviews"]
    },
    {
        "icon": "📰",
        "title": "News Intelligence",
        "description": "Gather latest news, analyze trends, and get comprehensive insights from top sources worldwide.",
        "command": "Get the latest technology news and trends from top tech publications and analyze key developments",
        "tags": ["News", "Analysis", "Trends"]
    },
    {
        "icon": "🔬",
        "title": "Research Assistant",
        "description": "Conduct deep research, analyze data, compare information, and generate comprehensive reports.",
        "command": "Research and compare the top 10 programming languages for web development in 2024 with pros and cons",
        "tags": ["Research", "Analysis", "Reports"]
    },
    {
        "icon": "💼",
        "title": "Business Intelligence",
        "description": "Market analysis, competitor research, industry insights, and business trend monitoring.",
        "command": "Analyze the current AI market trends and identify key players and opportunities in the industry",
        "tags": ["Business", "Market", "Intelligence"]
    },
    {
        "icon": "🎓",
        "title": "Learning Hub",
        "description": "Find educational resources, courses, tutorials, and learning materials on any topic.",
        "command": "Find the best online courses and tutorials for learning machine learning and AI development",
        "tags": ["Education", "Learning", "Courses"]
    },
    {
        "icon": "🌐",
        "title": "Web Monitoring",
        "description": "Monitor websites, track changes, analyze performance, and get automated updates.",
        "command": "Monitor GitHub trending repositories and get updates on popular open-source projects",
        "tags": ["Monitoring", "Tracking", "Updates"]
    }
]

# Create enhanced quick actions grid
cols = st.columns(3)
for i, action in enumerate(quick_actions_data):
    with cols[i % 3]:
        if st.button(
            f"{action['icon']} {action['title']}", 
            key=f"quick_action_{i}",
            use_container_width=True,
            help=action['description']
        ):
            user_input = action['command']
            st.session_state.selected_command = user_input
            process_button = True

# Display quick action details
if st.session_state.get('show_quick_actions', False):
    st.markdown('<div class="quick-actions-grid">', unsafe_allow_html=True)
    for action in quick_actions_data:
        st.markdown(f"""
        <div class="quick-action-card">
            <span class="quick-action-icon">{action['icon']}</span>
            <div class="quick-action-title">{action['title']}</div>
            <div class="quick-action-desc">{action['description']}</div>
            <div class="quick-action-tags">
                {' '.join([f'<span class="quick-action-tag">{tag}</span>' for tag in action['tags']])}
            </div>
        </div>
        """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ====================== ENHANCED PROCESSING LOGIC ======================
if (process_button or st.session_state.get('auto_process', False)) and user_input and agent:
    st.session_state.auto_process = False
    st.session_state.processing = True
    st.session_state.current_task_id = str(uuid.uuid4())
    st.session_state.metrics.task_count += 1
    
    # Enhanced loading with multiple stages
    loading_container = st.empty()
    progress_container = st.empty()
    status_container = st.empty()
    
    # Processing stages
    stages = [
        ("🤖 Initializing AI Agent", "Preparing advanced AI systems for your request", 0),
        ("🧠 Analyzing Request", "Understanding and processing your natural language command", 20),
        ("🌐 Launching Browser", "Starting secure browser automation with optimized settings", 40),
        ("🔍 Executing Task", "Performing intelligent web navigation and data extraction", 60),
        ("📊 Processing Data", "Analyzing extracted information with AI algorithms", 80),
        ("✨ Finalizing Results", "Formatting and optimizing results for presentation", 95)
    ]
    
    start_time = time.time()
    
    for stage_title, stage_desc, progress in stages:
        with loading_container:
            st.markdown(f"""
            <div class="loading-section">
                <div class="loading-animation">
                    <div class="loading-spinner"></div>
                </div>
                <div class="loading-text">{stage_title}</div>
                <div class="loading-subtext">{stage_desc}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with progress_container:
            st.markdown(create_progress_bar(progress), unsafe_allow_html=True)
        
        with status_container:
            st.markdown(f"""
            <div class="status-indicator status-processing">
                <i class="fas fa-cog fa-spin"></i> Processing... {progress}%
            </div>
            """, unsafe_allow_html=True)
        
        time.sleep(0.5)  # Realistic processing time
    
    try:
        # Execute the actual task
        result = agent.process_request(user_input)
        execution_time = time.time() - start_time
        
        # Update metrics
        st.session_state.metrics.last_execution_time = execution_time
        st.session_state.metrics.total_execution_time += execution_time
        st.session_state.metrics.avg_execution_time = (
            st.session_state.metrics.total_execution_time / 
            st.session_state.metrics.task_count
        )
        st.session_state.metrics.commands_history.append(user_input)
        
        # Clear loading indicators
        loading_container.empty()
        progress_container.empty()
        status_container.empty()
        
        # Display enhanced results
        st.markdown('<div class="results-section">', unsafe_allow_html=True)
        st.markdown("## 📊 Execution Results")
        
        if result.get('status') == 'completed':
            st.session_state.metrics.success_count += 1
            
            # Success message with enhanced details
            st.markdown(f"""
            <div class="message-container">
                <div class="message-success">
                    <span class="message-icon">✅</span>
                    <div class="message-content">
                        <div class="message-title">Task Completed Successfully!</div>
                        <div class="message-text">
                            Processed in {format_execution_time(execution_time)} • 
                            Extracted {len(result.get('extracted_data', []))} data points • 
                            Task ID: {st.session_state.current_task_id[:8]}
                        </div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Enhanced result display
            st.markdown('<div class="result-card">', unsafe_allow_html=True)
            
            # Result header with comprehensive metadata
            st.markdown(f"""
            <div class="result-header">
                <div class="result-title">
                    <i class="fas fa-chart-line"></i> Analysis Results
                </div>
                <div class="result-meta">
                    <div class="result-meta-item">
                        <i class="fas fa-clock"></i> {format_execution_time(execution_time)}
                    </div>
                    <div class="result-meta-item">
                        <i class="fas fa-database"></i> {len(result.get('extracted_data', []))} items
                    </div>
                    <div class="result-meta-item">
                        <i class="fas fa-check-circle"></i> {result.get('status', 'unknown').title()}
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Display extracted data with enhanced formatting
            if 'extracted_data' in result and result['extracted_data']:
                st.markdown("### 📌 Extracted Information")
                
                # Create tabs for different data views
                tab1, tab2, tab3 = st.tabs(["📋 List View", "📊 Summary", "🔍 Details"])
                
                with tab1:
                    for i, item in enumerate(result['extracted_data'], 1):
                        st.markdown(f"""
                        <div class="result-item">
                            <div class="result-item-title">Result {i}</div>
                            <div class="result-item-content">{item}</div>
                        </div>
                        """, unsafe_allow_html=True)
                
                with tab2:
                    # Create summary metrics
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Total Results", len(result['extracted_data']))
                    with col2:
                        avg_length = sum(len(str(item)) for item in result['extracted_data']) / len(result['extracted_data'])
                        st.metric("Avg Length", f"{avg_length:.0f} chars")
                    with col3:
                        st.metric("Processing Time", format_execution_time(execution_time))
                    with col4:
                        quality_score = min(100, len(result['extracted_data']) * 10)
                        st.metric("Quality Score", f"{quality_score}%")
                
                with tab3:
                    with st.expander("🔧 Technical Details", expanded=False):
                        st.json({
                            "task_id": st.session_state.current_task_id,
                            "timestamp": datetime.now().isoformat(),
                            "execution_time": execution_time,
                            "data_points": len(result['extracted_data']),
                            "status": result.get('status'),
                            "agent_version": CONFIG.APP_VERSION
                        })
            
            # AI response section
            if 'message' in result:
                st.markdown("### 🤖 AI Analysis & Insights")
                st.markdown(f"""
                <div style="
                    background: var(--bg-glass);
                    border: 1px solid var(--border-primary);
                    border-radius: var(--radius-lg);
                    padding: var(--spacing-xl);
                    margin: var(--spacing-lg) 0;
                    backdrop-filter: blur(12px);
                    line-height: 1.7;
                ">
                    {result['message']}
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
            
        else:
            st.session_state.metrics.error_count += 1
            error_msg = result.get('message', 'Unknown error occurred')
            
            st.markdown(f"""
            <div class="message-container">
                <div class="message-error">
                    <span class="message-icon">❌</span>
                    <div class="message-content">
                        <div class="message-title">Execution Error</div>
                        <div class="message-text">
                            {error_msg}<br>
                            <small>Execution time: {format_execution_time(execution_time)} • 
                            Task ID: {st.session_state.current_task_id[:8]}</small>
                        </div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # Detailed execution log
        if 'execution_log' in result:
            with st.expander("🔍 Detailed Execution Log", expanded=False):
                st.json(result['execution_log'])
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    except Exception as e:
        st.session_state.metrics.error_count += 1
        execution_time = time.time() - start_time
        
        loading_container.empty()
        progress_container.empty()
        status_container.empty()
        
        st.markdown(f"""
        <div class="message-container">
            <div class="message-error">
                <span class="message-icon">⚠️</span>
                <div class="message-content">
                    <div class="message-title">System Error</div>
                    <div class="message-text">
                        An unexpected error occurred: {str(e)}<br>
                        <small>Please try again or contact support if the issue persists.</small>
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        with st.expander("🔧 Error Details", expanded=False):
            st.code(f"""
Error Type: {type(e).__name__}
Error Message: {str(e)}
Task ID: {st.session_state.current_task_id}
Timestamp: {datetime.now().isoformat()}
Execution Time: {format_execution_time(execution_time)}
            """)
    
    finally:
        st.session_state.processing = False

# ====================== ENHANCED TASK HISTORY ======================
st.markdown("""
<div class="history-section">
    <div class="history-header">
        <h2 class="section-title">📜 Task History & Analytics</h2>
        <div class="history-controls">
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# History controls
history_col1, history_col2, history_col3 = st.columns([3, 1, 1])

with history_col2:
    history_count = st.slider(
        "Show Tasks",
        min_value=1,
        max_value=50,
        value=10,
        help="Number of recent tasks to display"
    )

with history_col3:
    if st.button("🗑️ Clear", use_container_width=True, help="Clear task history"):
        # Reset metrics
        st.session_state.metrics = SessionMetrics(start_time=datetime.now())
        st.rerun()

with history_col1:
    try:
        if agent:
            history = agent.get_task_history(history_count)
            
            if history:
                for i, task in enumerate(reversed(history), 1):
                    status_config = get_status_config(task.get('status', 'unknown'))
                    timestamp = task.get('timestamp', 'Unknown time')
                    task_text = task.get('task', 'Unknown task')
                    
                    st.markdown(f"""
                    <div class="history-item">
                        <div class="history-item-header">
                            <div class="history-item-title">
                                {status_config['icon']} <strong>Task #{i}</strong>
                            </div>
                            <div class="history-item-status status-{status_config['color']}">
                                {status_config['label']}
                            </div>
                        </div>
                        <div class="history-item-content">
                            {task_text[:120]}{'...' if len(task_text) > 120 else ''}
                        </div>
                        <div class="history-item-footer">
                            <div class="history-item-tags">
                                <span class="history-item-tag">AI-Powered</span>
                                <span class="history-item-tag">Web Automation</span>
                            </div>
                            <div class="history-item-time">
                                <i class="fas fa-clock"></i> {timestamp}
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Expandable details
                    with st.expander(f"📋 View Details - Task #{i}", expanded=False):
                        st.json(task.get('result', {}))
            else:
                st.markdown("""
                <div class="message-info">
                    <span class="message-icon">📝</span>
                    <div class="message-content">
                        <div class="message-title">No Task History</div>
                        <div class="message-text">Start by executing a command to see your task history here.</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="message-warning">
                <span class="message-icon">⚠️</span>
                <div class="message-content">
                    <div class="message-title">Agent Unavailable</div>
                    <div class="message-text">AI agent is not available. Please refresh the page.</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
    except Exception as e:
        st.markdown(f"""
        <div class="message-error">
            <span class="message-icon">⚠️</span>
            <div class="message-content">
                <div class="message-title">Unable to Load History</div>
                <div class="message-text">Error: {str(e)}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

# ====================== PREMIUM SIDEBAR ======================
with st.sidebar:
    # Header
    st.markdown("""
    <div style="text-align: center; padding: var(--spacing-lg) 0;">
        <h1 style="
            font-size: var(--font-size-2xl); 
            font-weight: 800; 
            margin: 0;
            background: var(--bg-gradient-primary);
            background-clip: text;
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        ">🤖 AI Control Center</h1>
        <div style="
            font-size: var(--font-size-sm); 
            color: var(--text-tertiary); 
            margin-top: var(--spacing-xs);
        ">v{CONFIG.APP_VERSION}</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Performance Dashboard
    st.markdown("""
    <div class="sidebar-section">
        <div class="sidebar-title">📊 Performance Dashboard</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Enhanced metrics grid
    metrics_data = [
        ("Total Tasks", st.session_state.metrics.task_count, "🎯"),
        ("Success Rate", f"{(st.session_state.metrics.success_count / max(st.session_state.metrics.task_count, 1)) * 100:.0f}%", "✅"),
        ("Avg Time", format_execution_time(st.session_state.metrics.avg_execution_time), "⚡"),
        ("Errors", st.session_state.metrics.error_count, "❌")
    ]
    
    cols = st.columns(2)
    for i, (label, value, icon) in enumerate(metrics_data):
        with cols[i % 2]:
            st.markdown(f"""
            <div class="metric-card">
                <div style="font-size: var(--font-size-lg); margin-bottom: var(--spacing-xs);">{icon}</div>
                <div class="metric-number">{value}</div>
                <div class="metric-label">{label}</div>
            </div>
            """, unsafe_allow_html=True)
    
    # Agent Status
    st.markdown("""
    <div class="sidebar-section">
        <div class="sidebar-title">⚙️ System Status</div>
    </div>
    """, unsafe_allow_html=True)
    
    if st.session_state.processing:
        st.markdown("""
        <div class="status-indicator status-processing">
            <i class="fas fa-cog fa-spin"></i> Processing Request...
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="status-indicator status-ready">
            <i class="fas fa-check-circle"></i> Ready for Commands
        </div>
        """, unsafe_allow_html=True)
    
    # Session Information
    session_duration = datetime.now() - st.session_state.metrics.start_time
    st.markdown(f"""
    <div style="
        margin: var(--spacing-md) 0; 
        padding: var(--spacing-md); 
        background: var(--bg-glass); 
        border-radius: var(--radius-lg); 
        font-family: var(--font-mono); 
        font-size: var(--font-size-xs); 
        color: var(--text-tertiary);
        border: 1px solid var(--border-primary);
    ">
        <div style="display: flex; justify-content: space-between; margin-bottom: var(--spacing-xs);">
            <span>🕐 Session Duration:</span>
            <span>{session_duration.seconds // 3600}h {(session_duration.seconds % 3600) // 60}m</span>
        </div>
        <div style="display: flex; justify-content: space-between; margin-bottom: var(--spacing-xs);">
            <span>🆔 Session ID:</span>
            <span>{id(st.session_state) % 10000:04d}</span>
        </div>
        <div style="display: flex; justify-content: space-between;">
            <span>🌐 Agent Status:</span>
            <span>{'Online' if agent else 'Offline'}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # AI Capabilities
    st.markdown("""
    <div class="sidebar-section">
        <div class="sidebar-title">🧩 AI Capabilities</div>
    </div>
    """, unsafe_allow_html=True)
  
    
    # Help & Support
    with st.expander("❓ Help & Documentation", expanded=False):
        st.markdown(f"""
        ### 🎯 **Command Examples**
        
        **🔍 Search & Research:**
        - "Find comprehensive reviews of the iPhone 15 Pro Max with price comparisons"
        - "Research the top 10 AI companies and their market positions in 2024"
        - "Get trending GitHub repositories for machine learning and data science"
        
        **🛒 E-commerce & Shopping:**
        - "Find the best gaming laptops under $1500 with detailed specifications"
        - "Compare prices for wireless earbuds across Amazon, Best Buy, and other retailers"
        - "Search for sustainable fashion brands with good customer reviews"
        
        **🌐 Web Navigation & Automation:**
        - "Navigate to TechCrunch and extract the latest AI-related news articles"
        - "Go to LinkedIn and find job postings for software engineers in San Francisco"
        - "Visit product pages and extract detailed technical specifications"
        
        **❓ Information & Analysis:**
        - "What are the current trends in renewable energy technology and market adoption?"
        - "Analyze the pros and cons of different cloud computing platforms"
        - "Explain quantum computing and its potential applications in simple terms"
        
        **📊 Business Intelligence:**
        - "Research competitor analysis for electric vehicle manufacturers"
        - "Find market size and growth projections for the cybersecurity industry"
        - "Analyze customer sentiment for major social media platforms"
        
        ### 🎤 **Voice Commands**
        - Click the 🎤 button and speak clearly
        - Supported languages: English (primary), Spanish, French, German
        - Works best in quiet environments
        - Clear pronunciation improves accuracy
        
        ### 🔧 **Pro Tips**
        - Be specific about your requirements and preferences
        - Include context like budget, location, or timeframe when relevant
        - For shopping queries, mention specific features or brands
        - For research, specify the depth and type of information needed
        - Use natural language - the AI understands conversational requests
        
        ### 📞 **Support & Resources**
        - 📧 Email: {CONFIG.SUPPORT_EMAIL}
        - 📖 Documentation: [docs.webnavigator.ai]({CONFIG.DOCS_URL})
        - 🐛 Report Issues: [GitHub Issues]({CONFIG.GITHUB_URL}/issues)
        - 💬 Community: [Join our Discord]({CONFIG.GITHUB_URL}/discussions)
        """)
    
    # System Information
    with st.expander("🔧 System Information", expanded=False):
        st.markdown(f"""
        **🖥️ Application Info:**
        - **Name:** {CONFIG.APP_NAME}
        - **Version:** {CONFIG.APP_VERSION}
        - **Description:** {CONFIG.APP_DESCRIPTION}
        - **Company:** {CONFIG.COMPANY_NAME}
        
        **⚡ Performance Metrics:**
        - **Session Started:** {st.session_state.metrics.start_time.strftime('%Y-%m-%d %H:%M:%S')}
        - **Total Tasks:** {st.session_state.metrics.task_count}
        - **Success Rate:** {(st.session_state.metrics.success_count / max(st.session_state.metrics.task_count, 1)) * 100:.1f}%
        - **Average Response Time:** {format_execution_time(st.session_state.metrics.avg_execution_time)}
        - **Total Processing Time:** {format_execution_time(st.session_state.metrics.total_execution_time)}
        
        **🔧 Technical Stack:**
        - **Frontend:** Streamlit {st.__version__}
        - **Agent:** WebNavigatorAgent v1.0
        - **Browser Engine:** Chrome (Headless)
        - **AI Engine:** Ollama Integration
        - **Data Storage:** In-Memory + Persistent
        - **Security:** Enterprise-grade encryption
        
        **🔗 External Integrations:**
        - **Selenium WebDriver** ✅
        - **Ollama LLM** ✅
        - **Voice Recognition** ✅
        - **Data Extraction Pipeline** ✅
        - **Advanced Analytics** ✅
        - **Real-time Processing** ✅
        
        **📱 Browser Support:**
        - Chrome/Chromium ✅
        - Firefox ✅
        - Safari ✅
        - Edge ✅
        - Mobile Browsers ✅
        """)

# ====================== ENHANCED FOOTER ======================
st.markdown("---")
st.markdown(f"""
<div style="
    text-align: center; 
    padding: var(--spacing-2xl) 0; 
    background: var(--bg-glass);
    border-radius: var(--radius-xl);
    margin-top: var(--spacing-2xl);
    border: 1px solid var(--border-primary);
">
    <div style="
        font-size: var(--font-size-xl); 
        font-weight: 700; 
        color: var(--text-primary); 
        margin-bottom: var(--spacing-md);
        background: var(--bg-gradient-primary);
        background-clip: text;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    ">
        🤖 {CONFIG.APP_NAME} - {CONFIG.APP_VERSION}
    </div>
    

""", unsafe_allow_html=True)

# Close main container
st.markdown('</div>', unsafe_allow_html=True)

# ========================================================================================
# ENHANCED JAVASCRIPT FOR INTERACTIVE FEATURES
# ========================================================================================

st.markdown("""
<script>
    // Smooth scrolling and enhanced interactions
    document.documentElement.style.scrollBehavior = 'smooth';
    
    // Keyboard shortcuts
    document.addEventListener('keydown', function(event) {
        // Ctrl/Cmd + Enter to execute
        if ((event.ctrlKey || event.metaKey) && event.key === 'Enter') {
            const executeButton = document.querySelector('[data-testid="stButton"] button');
            if (executeButton && !executeButton.disabled) {
                executeButton.click();
            }
        }
        
        // Esc to clear input
        if (event.key === 'Escape') {
            const inputField = document.querySelector('input[type="text"]');
            if (inputField) {
                inputField.value = '';
                inputField.focus();
            }
        }
        
        // Ctrl/Cmd + L to focus input
        if ((event.ctrlKey || event.metaKey) && event.key === 'l') {
            event.preventDefault();
            const inputField = document.querySelector('input[type="text"]');
            if (inputField) {
                inputField.focus();
            }
        }
    });
    
    // Enhanced focus management
    document.addEventListener('DOMContentLoaded', function() {
        const inputs = document.querySelectorAll('input[type="text"]');
        inputs.forEach(input => {
            input.addEventListener('focus', function() {
                this.parentElement.style.transform = 'translateY(-1px)';
                this.parentElement.style.boxShadow = '0 0 0 3px rgba(99, 102, 241, 0.1)';
            });
            
            input.addEventListener('blur', function() {
                this.parentElement.style.transform = 'translateY(0)';
                this.parentElement.style.boxShadow = '';
            });
        });
        
        // Add ripple effect to buttons
        const buttons = document.querySelectorAll('button');
        buttons.forEach(button => {
            button.addEventListener('click', function(e) {
                const ripple = document.createElement('div');
                const rect = this.getBoundingClientRect();
                const size = Math.max(rect.width, rect.height);
                const x = e.clientX - rect.left - size / 2;
                const y = e.clientY - rect.top - size / 2;
                
                ripple.style.cssText = `
                    position: absolute;
                    width: ${size}px;
                    height: ${size}px;
                    left: ${x}px;
                    top: ${y}px;
                    background: rgba(255, 255, 255, 0.3);
                    border-radius: 50%;
                    transform: scale(0);
                    animation: ripple 0.6s ease-out;
                    pointer-events: none;
                `;
                
                this.style.position = 'relative';
                this.style.overflow = 'hidden';
                this.appendChild(ripple);
                
                setTimeout(() => {
                    ripple.remove();
                }, 600);
            });
        });
    });
    
    // Add CSS for ripple animation
    const style = document.createElement('style');
    style.textContent = `
        @keyframes ripple {
            to {
                transform: scale(2);
                opacity: 0;
            }
        }
        
        /* Enhance loading animations */
        @keyframes fadeInUp {
            from {
                opacity: 0;
                transform: translateY(30px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        .animate-fade-in-up {
            animation: fadeInUp 0.5s ease-out;
        }
    `;
    document.head.appendChild(style);
    
    // Auto-save user preferences
    function savePreferences() {
        const preferences = {
            theme: 'dark',
            animations: true,
            sound: false,
            timestamp: Date.now()
        };
        localStorage.setItem('webnavigator_preferences', JSON.stringify(preferences));
    }
    
    // Performance monitoring
    function trackPerformance() {
        if ('performance' in window) {
            const navigation = performance.getEntriesByType('navigation')[0];
            const loadTime = navigation.loadEventEnd - navigation.loadEventStart;
            console.log(`Page loaded in ${loadTime}ms`);
        }
    }
    
    // Initialize enhancements
    document.addEventListener('DOMContentLoaded', function() {
        trackPerformance();
        savePreferences();
        
        // Add smooth transitions to all elements
        document.body.style.transition = 'all 0.3s ease';
    });
    
    // Service Worker registration for PWA capabilities
    if ('serviceWorker' in navigator) {
        window.addEventListener('load', function() {
            navigator.serviceWorker.register('/sw.js').then(function(registration) {
                console.log('SW registered: ', registration);
            }).catch(function(registrationError) {
                console.log('SW registration failed: ', registrationError);
            });
        });
    }
</script>
""", unsafe_allow_html=True)
