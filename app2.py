import plotly.graph_objects as go  # pip install plotly
import streamlit as st  # pip install streamlit
from streamlit_option_menu import option_menu  # pip install streamlit-option-menu

import database as db
from database import insert_period, fetch_all_periods, get_period


# -------------- SETTINGS --------------
personals = ["Height", "Weight", "Age"]
diets = ["Salt", "Fibre", "Caffeine"]
page_title = "Hydration Tracker"
page_icon = ":potable_water:"  # emojis: https://www.webfx.com/tools/emoji-cheat-sheet/
layout = "centered"
# --------------------------------------

st.set_page_config(page_title=page_title, page_icon=page_icon, layout=layout)
st.title(page_title + " " + page_icon)


day = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
exercise = [i for i in range(1,11)]


# --- DATABASE INTERFACE ---
def get_all_periods():
    items = db.fetch_all_periods()
    periods = [item["key"] for item in items]
    return periods


# --- HIDE STREAMLIT STYLE ---
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

# --- NAVIGATION MENU ---
selected = option_menu(
    menu_title=None,
    options=["Data Entry", "Data Visualization"],
    icons=["pencil-fill", "bar-chart-fill"],  # https://icons.getbootstrap.com/
    orientation="horizontal",
)

# --- INPUT & SAVE PERIODS ---
if selected == "Data Entry":
    st.header(f"Data Entry")
    with st.form("entry_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        col1.selectbox("Select Day:", day, key="days")
        col2.selectbox("Select Exercise intensity (1-10):", exercise, key="intensity")

        "---"
        with st.expander("Personal Specifications"):
            for i, item in enumerate(personals):
                st.number_input(f"{item}:", min_value=0, format="%i", step=1, key=f"{item}_{i}")
        
        with st.expander("Diet (in grams)"):
            for j, diet in enumerate(diets):
                st.number_input(f"{diet}:", min_value=0, format="%i", step=10, key=f"{diet}_{j}")

        "---"
        submitted = st.form_submit_button()
        if submitted:
            day_value = st.session_state["days"]
            intensity_value = st.session_state["intensity"]
            personal_data = {item: st.session_state[f"{item}_{i}"] for i, item in enumerate(personals)}
            diet_data = {diet: st.session_state[f"{diet}_{j}"] for j, diet in enumerate(diets)}
            st.write(f"Day: {day_value}")
            st.write(f"Exercise intensity: {intensity_value}")
            st.write(f"Personals: {personal_data}")
            st.write(f"Diet: {diet_data}")
            db.insert_period(day_value, intensity_value, personal_data, diet_data)
            st.success("Data saved!")


# --- PLOT PERIODS ---
if selected == "Data Visualization":
    st.header("Under construction")
