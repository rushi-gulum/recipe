# Loading components for Streamlit app
import streamlit as st
import time
from typing import Optional

def show_loading_spinner(message: str = "Loading...", duration: Optional[float] = None):
    """Show a loading spinner with custom message"""
    with st.spinner(message):
        if duration:
            time.sleep(duration)

def progress_bar(steps: list, current_step: int):
    """Show progress bar for multi-step operations"""
    progress = current_step / len(steps)
    st.progress(progress)
    
    if current_step < len(steps):
        st.info(f"Step {current_step + 1}/{len(steps)}: {steps[current_step]}")
    else:
        st.success("Completed!")

def loading_placeholder(placeholder_text: str = "Loading content..."):
    """Create a loading placeholder that can be replaced with content"""
    return st.empty().info(placeholder_text)