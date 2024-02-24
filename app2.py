import plotly.graph_objects as go  # pip install plotly
import streamlit as st  # pip install streamlit
from streamlit_option_menu import option_menu  # pip install streamlit-option-menu
import plotly.graph_objects as go
from datetime import date, datetime
import calendar
import database as db
from database import insert_period, fetch_all_periods, get_period, water_simulation, get_water_drank

my_date = date.today()
today = calendar.day_name[my_date.weekday()]

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
            default_temp = 25
            init_water_drank = 0
            db.insert_period(day_value, intensity_value, personal_data, diet_data, default_temp, init_water_drank)
            st.success("Data saved!")


# --- PLOT PERIODS ---
if selected == "Data Visualization":
    days = ['Friday', 'Monday', 'Saturday', 'Sunday', 'Thursday', 'Tuesday', 'Wednesday']
    today_index = days.index(today)

    water_goal = water_simulation()
    water_drank = get_water_drank()

    difference = water_drank[today_index] - water_drank[today_index-1]

    #water_goal = days_sorted(water_goal1)
    #water_drank = days_sorted(water_drank1)

    # Create the main bar chart for water goals
    fig = go.Figure()
    
    wd_colours = ["rgba(0, 188, 212, 1)" if i == today else "rgba(0, 188, 212, 0.5)" for i in days]
    wg_colours = ["rgba(33, 150, 243, 1)" if i == today else "rgba(33, 150, 243, 0.5)" for i in days]

    #Create a second trace for the amount of water drank
    fig.add_trace(go.Bar(x=days, y=water_drank, name='Water Drank', marker=dict(color=wd_colours)))
    fig.add_trace(go.Bar(x=days, y=water_goal, name='Water Goal', marker=dict(color=wg_colours)))

    # Update layout
    fig.update_layout(
        title='Water Consumption',
        xaxis=dict(title='Days'),
        yaxis=dict(title='Water (ml)'),
        barmode='group',
        hoverlabel=dict(font=dict(color='white'))
    )

    #Display the plot in Streamlit
    st.plotly_chart(fig)
    
    st.write("**Recommendation**: Drink more water")

    left_column, middle_column, right_column = st.columns(3)
    with left_column:
        st.subheader("Water Drank")
        st.metric(label="Water drank today", value=f"{water_drank[today_index]}ml", label_visibility="collapsed", delta=f"{difference}ml from yesterday")


