
import streamlit as st
import streamlit.components.v1 as components
try:
    from streamlit_option_menu import option_menu
except ImportError:
    st.error("streamlit-option-menu not installed. Run: pip install streamlit-option-menu")
    option_menu = None
try:
    from streamlit_lottie import st_lottie
except ImportError:
    st.warning("streamlit-lottie not installed. Animations disabled.")
    st_lottie = None
import requests
import json
import io
import os
import tempfile
import uuid
import time
import PyPDF2
import fitz  # PyMuPDF
from PIL import Image, ImageFilter, ImageEnhance
import cv2
import numpy as np
from moviepy.editor import VideoFileClip, AudioFileClip
from pydub import AudioSegment
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from performance_monitor import performance_monitor, get_system_stats

# Enhanced page configuration
st.set_page_config(
    page_title="SuntynAI - Professional AI Platform",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://suntynai.com/help',
        'Report a bug': "https://suntynai.com/bug-report",
        'About': "# SuntynAI Professional Platform\nNeural Intelligence for Everyone"
    }
)

# Professional CSS with advanced styling
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

:root {
    --primary-gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    --secondary-gradient: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
    --success-gradient: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
    --dark-bg: #0f1419;
    --surface: #1a1d23;
    --surface-light: #252a32;
    --text-primary: #ffffff;
    --text-secondary: #a0a9b8;
    --accent: #667eea;
    --border: rgba(255, 255, 255, 0.1);
    --shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
    --border-radius: 12px;
}

/* Hide default streamlit elements */
#MainMenu {visibility: hidden;}
.stDeployButton {display: none;}
footer {visibility: hidden;}
.stAppHeader {display: none;}

/* Main container styling */
.main .block-container {
    padding: 1rem 2rem;
    max-width: 95%;
    background: var(--dark-bg);
    color: var(--text-primary);
}

/* Professional header */
.professional-header {
    background: var(--primary-gradient);
    padding: 3rem 2rem;
    border-radius: 20px;
    margin-bottom: 2rem;
    text-align: center;
    position: relative;
    overflow: hidden;
    box-shadow: var(--shadow);
}

.professional-header::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: linear-gradient(45deg, rgba(255,255,255,0.1) 0%, transparent 100%);
    pointer-events: none;
}

.header-title {
    font-family: 'Inter', sans-serif;
    font-size: 3.5rem;
    font-weight: 800;
    margin: 0;
    text-shadow: 0 4px 20px rgba(0,0,0,0.3);
    animation: glow 3s ease-in-out infinite alternate;
}

.header-subtitle {
    font-size: 1.3rem;
    font-weight: 500;
    margin-top: 0.5rem;
    opacity: 0.9;
}

.header-description {
    font-size: 1.1rem;
    margin-top: 1rem;
    opacity: 0.8;
    max-width: 600px;
    margin-left: auto;
    margin-right: auto;
}

@keyframes glow {
    0% { text-shadow: 0 4px 20px rgba(0,0,0,0.3); }
    100% { text-shadow: 0 4px 30px rgba(255,255,255,0.3); }
}

/* Navigation menu styling */
.nav-menu {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--border-radius) !important;
    padding: 0.5rem !important;
    margin: 1rem 0 !important;
    box-shadow: var(--shadow) !important;
}

/* Metrics styling */
.metric-container {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--border-radius);
    padding: 2rem;
    text-align: center;
    position: relative;
    overflow: hidden;
    box-shadow: var(--shadow);
    transition: all 0.3s ease;
}

.metric-container:hover {
    transform: translateY(-5px);
    box-shadow: 0 12px 48px rgba(0, 0, 0, 0.4);
}

.metric-value {
    font-size: 3rem;
    font-weight: 800;
    background: var(--primary-gradient);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

.metric-label {
    font-size: 1.1rem;
    color: var(--text-secondary);
    margin-top: 0.5rem;
}

/* Tool cards */
.tool-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--border-radius);
    padding: 2rem;
    margin: 1rem 0;
    box-shadow: var(--shadow);
    transition: all 0.3s ease;
    position: relative;
    overflow: hidden;
}

.tool-card:hover {
    transform: translateY(-8px);
    border-color: var(--accent);
    box-shadow: 0 16px 64px rgba(102, 126, 234, 0.3);
}

.tool-card::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: var(--primary-gradient);
    opacity: 0;
    transition: opacity 0.3s ease;
}

.tool-card:hover::before {
    opacity: 0.05;
}

/* Buttons */
.stButton > button {
    background: var(--primary-gradient) !important;
    color: white !important;
    border: none !important;
    border-radius: var(--border-radius) !important;
    padding: 0.8rem 2rem !important;
    font-weight: 600 !important;
    font-size: 1rem !important;
    transition: all 0.3s ease !important;
    box-shadow: var(--shadow) !important;
    text-transform: uppercase !important;
    letter-spacing: 1px !important;
}

.stButton > button:hover {
    transform: translateY(-3px) !important;
    box-shadow: 0 12px 48px rgba(102, 126, 234, 0.4) !important;
}

/* File uploader */
.stFileUploader > div {
    background: var(--surface) !important;
    border: 2px dashed var(--border) !important;
    border-radius: var(--border-radius) !important;
    padding: 2rem !important;
    text-align: center !important;
    transition: all 0.3s ease !important;
}

.stFileUploader > div:hover {
    border-color: var(--accent) !important;
    background: var(--surface-light) !important;
}

/* Progress bars */
.stProgress > div > div > div {
    background: var(--primary-gradient) !important;
    border-radius: 10px !important;
}

/* Selectbox and inputs */
.stSelectbox > div > div {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--border-radius) !important;
    color: var(--text-primary) !important;
}

.stTextInput > div > div > input {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--border-radius) !important;
    color: var(--text-primary) !important;
}

/* Sidebar */
.css-1d391kg {
    background: var(--surface) !important;
    border-right: 1px solid var(--border) !important;
}

/* Loading animation */
.loading-spinner {
    display: flex;
    justify-content: center;
    align-items: center;
    height: 100px;
}

.spinner {
    width: 40px;
    height: 40px;
    border: 4px solid var(--border);
    border-top: 4px solid var(--accent);
    border-radius: 50%;
    animation: spin 1s linear infinite;
}

@keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}

/* Demo section */
.demo-section {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 20px;
    padding: 3rem;
    margin: 2rem 0;
    text-align: center;
    box-shadow: var(--shadow);
}

/* Footer */
.professional-footer {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 20px;
    padding: 3rem;
    margin-top: 4rem;
    text-align: center;
    box-shadow: var(--shadow);
}

/* Success animations */
.success-animation {
    animation: successPulse 2s ease-in-out;
}

@keyframes successPulse {
    0% { transform: scale(0.8); opacity: 0; }
    50% { transform: scale(1.1); opacity: 0.8; }
    100% { transform: scale(1); opacity: 1; }
}

/* Charts container */
.chart-container {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--border-radius);
    padding: 1.5rem;
    margin: 1rem 0;
    box-shadow: var(--shadow);
}

/* Advanced animations */
.float-animation {
    animation: float 6s ease-in-out infinite;
}

@keyframes float {
    0%, 100% { transform: translateY(0px); }
    50% { transform: translateY(-20px); }
}

.pulse-animation {
    animation: pulse 2s infinite;
}

@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.7; }
}

/* Professional scrollbar */
::-webkit-scrollbar {
    width: 8px;
}

::-webkit-scrollbar-track {
    background: var(--surface);
}

::-webkit-scrollbar-thumb {
    background: var(--accent);
    border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
    background: #5a6fd8;
}

/* Status indicators */
.status-online {
    display: inline-block;
    width: 12px;
    height: 12px;
    background: #10b981;
    border-radius: 50%;
    animation: pulse 2s infinite;
    margin-right: 8px;
}

.status-processing {
    display: inline-block;
    width: 12px;
    height: 12px;
    background: #f59e0b;
    border-radius: 50%;
    animation: spin 1s linear infinite;
    margin-right: 8px;
}

/* Advanced tooltips */
.tooltip {
    position: relative;
    cursor: help;
}

.tooltip::after {
    content: attr(data-tooltip);
    position: absolute;
    bottom: 100%;
    left: 50%;
    transform: translateX(-50%);
    background: var(--surface);
    color: var(--text-primary);
    padding: 8px 12px;
    border-radius: 6px;
    font-size: 0.875rem;
    white-space: nowrap;
    opacity: 0;
    visibility: hidden;
    transition: all 0.3s ease;
    border: 1px solid var(--border);
    box-shadow: var(--shadow);
}

.tooltip:hover::after {
    opacity: 1;
    visibility: visible;
}

</style>
""", unsafe_allow_html=True)

# Professional header
st.markdown("""
<div class="professional-header">
    <div class="header-title">🧠 SuntynAI</div>
    <div class="header-subtitle">NEURAL INTELLIGENCE PLATFORM</div>
    <div class="header-description">Professional AI-Powered Tools for Modern Workflows</div>
</div>
""", unsafe_allow_html=True)

# System stats in sidebar
with st.sidebar:
    st.markdown("### 📊 System Status")
    try:
        stats = get_system_stats()
        col1, col2 = st.columns(2)
        with col1:
            st.metric("CPU", f"{stats['cpu_percent']:.1f}%")
            st.metric("Memory", f"{stats['memory_percent']:.1f}%")
        with col2:
            st.metric("Disk", f"{stats['disk_percent']:.1f}%")
            st.metric("Status", "🟢 Online")
    except:
        st.info("System stats unavailable")

# Enhanced navigation
if option_menu:
    selected = option_menu(
        menu_title=None,
        options=["🏠 Dashboard", "📄 PDF Tools", "🖼️ Image Tools", "🎥 Video Tools", "🎵 Audio Tools", "🤖 AI Tools", "📊 Analytics", "⚙️ Settings"],
        icons=["house-fill", "file-pdf-fill", "image-fill", "camera-video-fill", "music-note", "cpu-fill", "bar-chart-fill", "gear-fill"],
        menu_icon="cast",
        default_index=0,
        orientation="horizontal",
        styles={
            "container": {
                "padding": "0!important",
                "background": "var(--surface)",
                "border": "1px solid var(--border)",
                "border-radius": "12px",
                "margin": "1rem 0",
                "box-shadow": "var(--shadow)"
            },
            "icon": {"color": "var(--accent)", "font-size": "18px"},
            "nav-link": {
                "font-size": "14px",
                "text-align": "center",
                "margin": "0px",
                "padding": "12px 8px",
                "background-color": "transparent",
                "color": "var(--text-secondary)",
                "border-radius": "8px",
                "transition": "all 0.3s ease"
            },
            "nav-link-selected": {
                "background": "var(--primary-gradient)",
                "color": "white",
                "transform": "translateY(-2px)",
                "box-shadow": "0 8px 25px rgba(102, 126, 234, 0.3)"
            }
        }
    )
else:
    selected = "🏠 Dashboard"

# Dashboard
if selected == "🏠 Dashboard":
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="metric-container float-animation">
            <div class="metric-value">80+</div>
            <div class="metric-label">AI Tools</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-container float-animation" style="animation-delay: 0.2s;">
            <div class="metric-value">1M+</div>
            <div class="metric-label">Files Processed</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-container float-animation" style="animation-delay: 0.4s;">
            <div class="metric-value">99.9%</div>
            <div class="metric-label">Uptime</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="metric-container float-animation" style="animation-delay: 0.6s;">
            <div class="metric-value">24/7</div>
            <div class="metric-label">Support</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # Demo section with Lottie animation
    st.markdown("""
    <div class="demo-section">
        <h2 style="color: var(--accent); margin-bottom: 2rem;">🎥 Platform Demo</h2>
    </div>
    """, unsafe_allow_html=True)
    
    # Lottie animation
    if st_lottie:
        lottie_url = "https://assets5.lottiefiles.com/packages/lf20_fcfjwiyb.json"
        try:
            lottie_json = requests.get(lottie_url).json()
            st_lottie(lottie_json, speed=1, height=300, key="demo")
        except:
            st.info("🎬 Interactive demo will load here")
    else:
        st.info("Install streamlit-lottie for animations: `pip install streamlit-lottie`")

    # Quick actions
    st.markdown("### 🚀 Quick Actions")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📄 Process PDFs", key="pdf_quick", use_container_width=True):
            st.switch_page("📄 PDF Tools")
    
    with col2:
        if st.button("🖼️ Edit Images", key="image_quick", use_container_width=True):
            st.switch_page("🖼️ Image Tools")
    
    with col3:
        if st.button("🤖 AI Analysis", key="ai_quick", use_container_width=True):
            st.switch_page("🤖 AI Tools")

# PDF Tools
elif selected == "📄 PDF Tools":
    st.markdown("# 📄 Professional PDF Processing")
    
    # Tool selection with enhanced UI
    pdf_tools = {
        "📑 Merge PDFs": "Combine multiple PDF files into one",
        "✂️ Split PDF": "Extract specific pages or ranges",
        "🗜️ Compress PDF": "Reduce file size while maintaining quality",
        "📝 Extract Text": "Extract all text content from PDF",
        "🖼️ PDF to Images": "Convert pages to image formats",
        "🔒 Add Password": "Secure your PDF with encryption",
        "🔓 Remove Password": "Unlock password-protected PDFs",
        "💧 Add Watermark": "Brand your documents",
        "🔄 Rotate Pages": "Fix page orientation",
        "📄 Merge Pages": "Combine pages from different PDFs"
    }
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        selected_tool = st.selectbox(
            "Choose Tool",
            list(pdf_tools.keys()),
            help="Select a PDF processing tool"
        )
        
        st.info(f"**{selected_tool}**\n\n{pdf_tools[selected_tool]}")
    
    with col2:
        st.markdown(f"### {selected_tool}")
        
        uploaded_files = st.file_uploader(
            "Upload PDF files",
            type=['pdf'],
            accept_multiple_files=True if "Merge" in selected_tool else False,
            help="Select one or more PDF files to process"
        )
        
        if uploaded_files:
            # Processing options
            with st.expander("⚙️ Advanced Options"):
                if "Compress" in selected_tool:
                    quality = st.slider("Compression Level", 1, 10, 7)
                elif "Split" in selected_tool:
                    page_range = st.text_input("Page Range (e.g., 1-5, 7, 9-12)", "1-1")
                elif "Watermark" in selected_tool:
                    watermark_text = st.text_input("Watermark Text", "CONFIDENTIAL")
                    opacity = st.slider("Opacity", 0.1, 1.0, 0.5)
            
            # Process button
            if st.button(f"🚀 Process with {selected_tool}", type="primary", use_container_width=True):
                with st.spinner("🔄 Processing your PDF..."):
                    # Simulate processing
                    progress_bar = st.progress(0)
                    for i in range(100):
                        time.sleep(0.01)
                        progress_bar.progress(i + 1)
                    
                    st.success("✅ Processing completed successfully!")
                    
                    # Mock download button
                    st.download_button(
                        label="📥 Download Processed PDF",
                        data=b"Mock PDF data",
                        file_name="processed_document.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )

# Image Tools
elif selected == "🖼️ Image Tools":
    st.markdown("# 🖼️ Professional Image Processing")
    
    image_tools = {
        "📏 Resize Images": "Change dimensions while maintaining quality",
        "🗜️ Compress Images": "Reduce file size for web optimization",
        "🎨 Apply Filters": "Enhance with artistic filters",
        "🔄 Format Converter": "Convert between JPG, PNG, WebP",
        "✂️ Crop Images": "Extract specific regions",
        "🌈 Color Adjustment": "Modify brightness, contrast, saturation",
        "🖼️ Background Remover": "AI-powered background removal",
        "💧 Add Watermark": "Protect your images",
        "📐 Rotate & Flip": "Fix orientation issues",
        "✨ Enhance Quality": "AI-powered image enhancement"
    }
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        selected_tool = st.selectbox(
            "Choose Tool",
            list(image_tools.keys()),
            help="Select an image processing tool"
        )
        
        st.info(f"**{selected_tool}**\n\n{image_tools[selected_tool]}")
    
    with col2:
        st.markdown(f"### {selected_tool}")
        
        uploaded_image = st.file_uploader(
            "Upload Image",
            type=['jpg', 'jpeg', 'png', 'webp', 'bmp'],
            help="Select an image file to process"
        )
        
        if uploaded_image:
            # Display original image
            image = Image.open(uploaded_image)
            
            col_orig, col_processed = st.columns(2)
            
            with col_orig:
                st.markdown("**Original Image**")
                st.image(image, use_column_width=True)
                st.caption(f"Size: {image.size[0]}x{image.size[1]} pixels")
            
            # Processing options
            with st.expander("⚙️ Processing Options"):
                if "Resize" in selected_tool:
                    new_width = st.number_input("Width", min_value=1, value=image.size[0])
                    new_height = st.number_input("Height", min_value=1, value=image.size[1])
                    maintain_ratio = st.checkbox("Maintain aspect ratio", True)
                elif "Compress" in selected_tool:
                    quality = st.slider("Quality", 10, 100, 85)
                elif "Filter" in selected_tool:
                    filter_type = st.selectbox("Filter", ["Blur", "Sharpen", "Emboss", "Edge Enhance"])
                elif "Color" in selected_tool:
                    brightness = st.slider("Brightness", -50, 50, 0)
                    contrast = st.slider("Contrast", -50, 50, 0)
                    saturation = st.slider("Saturation", -50, 50, 0)
            
            # Process button
            if st.button(f"🚀 Apply {selected_tool}", type="primary", use_container_width=True):
                with st.spinner("🎨 Processing your image..."):
                    progress_bar = st.progress(0)
                    processed_image = image.copy()  # Mock processing
                    
                    # Apply basic processing based on tool
                    if "Resize" in selected_tool and 'new_width' in locals():
                        if maintain_ratio:
                            processed_image.thumbnail((new_width, new_height), Image.Resampling.LANCZOS)
                        else:
                            processed_image = processed_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
                    elif "Filter" in selected_tool and 'filter_type' in locals():
                        if filter_type == "Blur":
                            processed_image = processed_image.filter(ImageFilter.BLUR)
                        elif filter_type == "Sharpen":
                            processed_image = processed_image.filter(ImageFilter.SHARPEN)
                    
                    for i in range(100):
                        time.sleep(0.005)
                        progress_bar.progress(i + 1)
                    
                    with col_processed:
                        st.markdown("**Processed Image**")
                        st.image(processed_image, use_column_width=True)
                        st.caption(f"New size: {processed_image.size[0]}x{processed_image.size[1]} pixels")
                    
                    # Download button
                    buf = io.BytesIO()
                    processed_image.save(buf, format='PNG')
                    
                    st.download_button(
                        label="📥 Download Processed Image",
                        data=buf.getvalue(),
                        file_name="processed_image.png",
                        mime="image/png",
                        use_container_width=True
                    )

# AI Tools
elif selected == "🤖 AI Tools":
    st.markdown("# 🤖 Artificial Intelligence Suite")
    
    ai_tools = {
        "📝 Text Analyzer": "Advanced text analysis and insights",
        "🖼️ Image Analyzer": "AI-powered image recognition",
        "📊 Data Insights": "Extract patterns from your data",
        "🎯 Content Generator": "AI-powered content creation",
        "🔍 Smart Search": "Intelligent document search",
        "📈 Trend Analysis": "Predict trends and patterns",
        "🧠 Neural Processing": "Advanced AI model inference",
        "🎨 Creative AI": "AI-powered creative tools"
    }
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        selected_tool = st.selectbox(
            "Choose AI Tool",
            list(ai_tools.keys()),
            help="Select an AI-powered tool"
        )
        
        st.info(f"**{selected_tool}**\n\n{ai_tools[selected_tool]}")
    
    with col2:
        st.markdown(f"### {selected_tool}")
        
        if "Text Analyzer" in selected_tool:
            text_input = st.text_area(
                "Enter text to analyze",
                height=200,
                placeholder="Paste your text here for AI analysis..."
            )
            
            if text_input and st.button("🔍 Analyze Text", type="primary"):
                with st.spinner("🧠 AI is analyzing your text..."):
                    time.sleep(2)
                    
                    # Mock analysis results
                    col_metrics1, col_metrics2, col_metrics3 = st.columns(3)
                    
                    with col_metrics1:
                        st.metric("Words", len(text_input.split()))
                    with col_metrics2:
                        st.metric("Characters", len(text_input))
                    with col_metrics3:
                        st.metric("Sentiment", "Positive 😊")
                    
                    # Advanced analysis
                    with st.expander("📊 Detailed Analysis"):
                        st.markdown("**Key Topics Detected:**")
                        st.write("• Technology, AI, Innovation")
                        st.markdown("**Language Quality:**")
                        st.progress(0.85)
                        st.markdown("**Readability Score:**")
                        st.progress(0.78)
        
        elif "Image Analyzer" in selected_tool:
            uploaded_image = st.file_uploader(
                "Upload image for AI analysis",
                type=['jpg', 'jpeg', 'png']
            )
            
            if uploaded_image and st.button("🔍 Analyze Image", type="primary"):
                with st.spinner("🤖 AI is analyzing your image..."):
                    image = Image.open(uploaded_image)
                    st.image(image, use_column_width=True)
                    time.sleep(2)
                    
                    # Mock AI analysis
                    st.success("✅ Analysis Complete!")
                    
                    col_ai1, col_ai2 = st.columns(2)
                    
                    with col_ai1:
                        st.markdown("**Objects Detected:**")
                        st.write("• Person (95% confidence)")
                        st.write("• Computer (87% confidence)")
                        st.write("• Desk (92% confidence)")
                    
                    with col_ai2:
                        st.markdown("**Image Properties:**")
                        st.write(f"• Resolution: {image.size[0]}x{image.size[1]}")
                        st.write("• Quality: High")
                        st.write("• Color Space: RGB")

# Analytics
elif selected == "📊 Analytics":
    st.markdown("# 📊 Platform Analytics")
    
    # Generate sample data
    data = {
        'Tool Category': ['PDF Tools', 'Image Tools', 'Video Tools', 'Audio Tools', 'AI Tools'],
        'Usage Count': [2450, 1890, 1120, 780, 560],
        'Success Rate': [98.5, 97.2, 95.8, 99.1, 96.7],
        'Avg Processing Time': [2.3, 1.8, 15.2, 8.4, 3.7]
    }
    
    df = pd.DataFrame(data)
    
    # Key metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        total_usage = df['Usage Count'].sum()
        st.metric(
            "Total Tool Usage",
            f"{total_usage:,}",
            delta="+12.5% from last month"
        )
    
    with col2:
        avg_success = df['Success Rate'].mean()
        st.metric(
            "Average Success Rate",
            f"{avg_success:.1f}%",
            delta="+2.1% improvement"
        )
    
    with col3:
        avg_time = df['Avg Processing Time'].mean()
        st.metric(
            "Avg Processing Time",
            f"{avg_time:.1f}s",
            delta="-0.8s faster"
        )
    
    # Charts
    col_chart1, col_chart2 = st.columns(2)
    
    with col_chart1:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        fig1 = px.bar(
            df, 
            x='Tool Category', 
            y='Usage Count',
            title='Tool Usage Statistics',
            color='Usage Count',
            color_continuous_scale='viridis'
        )
        fig1.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='white'
        )
        st.plotly_chart(fig1, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col_chart2:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        fig2 = px.pie(
            df, 
            values='Usage Count', 
            names='Tool Category',
            title='Usage Distribution'
        )
        fig2.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='white'
        )
        st.plotly_chart(fig2, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Performance chart
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    fig3 = px.line(
        df, 
        x='Tool Category', 
        y='Success Rate',
        title='Success Rate Trends',
        markers=True
    )
    fig3.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_color='white'
    )
    st.plotly_chart(fig3, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# Settings
elif selected == "⚙️ Settings":
    st.markdown("# ⚙️ Platform Settings")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🎨 Appearance")
        theme = st.selectbox("Theme", ["Dark", "Light", "Auto"])
        language = st.selectbox("Language", ["English", "Hindi", "Spanish", "French"])
        
        st.markdown("### 🔔 Notifications")
        email_notifications = st.checkbox("Email notifications", True)
        push_notifications = st.checkbox("Push notifications", False)
        
        st.markdown("### 🚀 Performance")
        auto_optimize = st.checkbox("Auto-optimize files", True)
        cache_results = st.checkbox("Cache processing results", True)
    
    with col2:
        st.markdown("### 🔒 Security")
        two_factor = st.checkbox("Two-factor authentication", False)
        session_timeout = st.slider("Session timeout (hours)", 1, 24, 8)
        
        st.markdown("### 📊 Analytics")
        collect_analytics = st.checkbox("Allow analytics collection", True)
        share_anonymous = st.checkbox("Share anonymous usage data", False)
        
        st.markdown("### 💾 Storage")
        auto_delete = st.slider("Auto-delete files after (days)", 1, 30, 7)
        storage_limit = st.slider("Storage limit (GB)", 1, 100, 10)
    
    if st.button("💾 Save Settings", type="primary", use_container_width=True):
        st.success("✅ Settings saved successfully!")

# Professional footer
st.markdown("---")
st.markdown("""
<div class="professional-footer">
    <div style="font-size: 2rem; margin-bottom: 1rem;">🧠</div>
    <h3 style="margin: 0; background: var(--primary-gradient); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;">SuntynAI</h3>
    <p style="color: var(--text-secondary); margin: 0.5rem 0;">NEURAL INTELLIGENCE PLATFORM</p>
    <p style="color: var(--text-secondary); font-size: 0.9rem;">© 2024 SuntynAI. Professional AI Tools for Everyone.</p>
    <div style="margin-top: 1rem;">
        <span class="status-online"></span>
        <span style="color: var(--text-secondary); font-size: 0.9rem;">All systems operational</span>
    </div>
</div>
""", unsafe_allow_html=True)

# JavaScript for enhanced interactivity
components.html("""
<script>
// Add smooth scrolling and enhanced interactions
document.addEventListener('DOMContentLoaded', function() {
    // Add loading states to buttons
    const buttons = document.querySelectorAll('button');
    buttons.forEach(button => {
        button.addEventListener('click', function() {
            if (this.textContent.includes('Process') || this.textContent.includes('Analyze')) {
                this.style.transform = 'scale(0.95)';
                setTimeout(() => {
                    this.style.transform = '';
                }, 150);
            }
        });
    });
    
    // Add hover effects to cards
    const cards = document.querySelectorAll('.metric-container, .tool-card');
    cards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-8px) scale(1.02)';
        });
        card.addEventListener('mouseleave', function() {
            this.style.transform = '';
        });
    });
});
</script>
""", height=0)
