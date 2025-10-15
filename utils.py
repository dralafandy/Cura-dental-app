# utils.py
import streamlit as st
import streamlit_javascript as st_js

def get_screen_width():
    width = st_js.st_javascript("window.innerWidth")
    if width is None:
        return 800
    return width

def determine_num_columns(screen_width):
    if screen_width < 600:
        return 1
    elif screen_width < 1000:
        return 2
    else:
        return 3
