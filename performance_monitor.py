
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
import time
import psutil
import logging
from functools import wraps

logger = logging.getLogger(__name__)

def monitor_performance(func):
    """Decorator to monitor function performance"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        start_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
        
        try:
            result = func(*args, **kwargs)
            
            end_time = time.time()
            end_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
            
            execution_time = end_time - start_time
            memory_used = end_memory - start_memory
            
            if execution_time > 10:  # Log slow operations
                logger.warning(f"Slow operation {func.__name__}: {execution_time:.2f}s, Memory: {memory_used:.2f}MB")
            
            return result
            
        except Exception as e:
            logger.error(f"Error in {func.__name__}: {str(e)}")
            raise
    
    return wrapper

def get_system_stats():
    """Get current system statistics"""
    cpu_percent = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    
    return {
        'cpu_percent': cpu_percent,
        'memory_percent': memory.percent,
        'memory_available': memory.available / 1024 / 1024 / 1024,  # GB
        'disk_percent': disk.percent,
        'disk_free': disk.free / 1024 / 1024 / 1024  # GB
    }
