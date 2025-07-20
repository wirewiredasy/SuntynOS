
import time
import psutil
import streamlit as st
from functools import wraps

def performance_monitor(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        start_memory = psutil.Process().memory_info().rss / 1024 / 1024
        
        result = func(*args, **kwargs)
        
        end_time = time.time()
        end_memory = psutil.Process().memory_info().rss / 1024 / 1024
        
        processing_time = end_time - start_time
        memory_used = end_memory - start_memory
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("⏱️ Processing Time", f"{processing_time:.2f}s")
        with col2:
            st.metric("💾 Memory Used", f"{memory_used:.1f} MB")
        with col3:
            st.metric("📊 Status", "✅ Complete")
        
        return result
    return wrapper
