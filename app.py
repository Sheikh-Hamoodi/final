
# "streamlit run app.py" in console to run locally, need wifi connection for database to work

import plotly.graph_objects as go
import streamlit as st
from streamlit_option_menu import option_menu
import plotly.graph_objects as go
from datetime import date
import calendar
from deta import Deta
import database as db
from database import insert_period, fetch_all_periods, get_period, water_simulation, get_water_drank # From database.py file

# Fetching what day it is today (as a string) - helps with automation
my_date = date.today()
today = calendar.day_name[my_date.weekday()]

# Streamlit settings
st.set_page_config(page_title= "Hydration Tracker", page_icon= ":potable_water:", layout= "centered")
st.title("Hydration Tracker" + " " + ":potable_water:")
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

# Input categories (that will show in the app)
day = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
exercise = [i for i in range(1,11)]
personals = ["Height", "Weight", "Age"]
diets = ["Salt", "Fibre", "Caffeine"]
genders = ["Male", "Female"]

# Fetching database
def get_all_periods():
    items = db.fetch_all_periods()
    periods = [item["key"] for item in items]
    return periods

# Option menu/Nav Bar
selected = option_menu(
    menu_title=None,
    options=["Data Entry", "Model"],
    icons=["pencil-fill", "bar-chart-fill"],
    orientation="horizontal",
)

# Input Fields
if selected == "Data Entry":
    st.header(f"Data Entry")
    with st.form("entry_form", clear_on_submit=True):
        col1, col2, col3 = st.columns(3)
        col1.selectbox("Select Day:", day, key="days")
        col2.selectbox("Select Exercise intensity:", exercise, key="intensity")
        col3.selectbox("Select Gender:", genders, key="gneder")

        "---"
        with st.expander("Personal Specifications"):
            for i, item in enumerate(personals):
                st.number_input(f"{item}:", min_value=0, format="%i", step=1, key=f"{item}_{i}")
        
        with st.expander("Diet"):
            for j, diet in enumerate(diets):
                st.number_input(f"{diet}:", min_value=0, format="%i", step=10, key=f"{diet}_{j}")

        "---"
        submitted = st.form_submit_button()
        if submitted:
            day_value = st.session_state["days"]
            intensity_value = st.session_state["intensity"]
            gender_value = st.session_state["gneder"]
            personal_data = {item: st.session_state[f"{item}_{i}"] for i, item in enumerate(personals)}
            diet_data = {diet: st.session_state[f"{diet}_{j}"] for j, diet in enumerate(diets)}
            default_temp = 25
            init_water_drank = 0

            # Validation
            if all(isinstance(value, (float, int)) for value in [intensity_value] + list(personal_data.values()) + list(diet_data.values())):
                db.insert_period(day_value, intensity_value, personal_data, diet_data, default_temp, init_water_drank, gender_value)
                st.success("Data saved!")
            else:
                st.error("Error: Incorrect format.")
                st.write([day_value, intensity_value] + list(personal_data.values()) + list(diet_data.values()))


# Model
if selected == "Model":
    
    DETA_KEY = "a0wq3cud5fq_gE78mR9NwdMaBhMQV2nUm7dfQ2VtgyGy"
    deta = Deta(DETA_KEY)
    db = deta.Base("hydration-system")

    days = ['Friday', 'Monday', 'Saturday', 'Sunday', 'Thursday', 'Tuesday', 'Wednesday']
    today_index = days.index(today)

    water_goal = water_simulation()
    water_drank = get_water_drank()
    percentage_goal_reached = [round(100 * wd / wg, 0) for wd, wg in zip(water_drank, water_goal)]


    # Graphing of model: Results of what if Q1 & Q2
    fig = go.Figure()
    
    wd_colours = ["rgba(0, 188, 212, 1)" if i == today else "rgba(0, 188, 212, 0.5)" for i in days]
    wg_colours = ["rgba(33, 150, 243, 1)" if i == today else "rgba(33, 150, 243, 0.5)" for i in days]

    fig.add_trace(go.Bar(x=days, y=water_drank, name='Water Drank', marker=dict(color=wd_colours), yaxis='y'))
    fig.add_trace(go.Bar(x=days, y=water_goal, name='Water Goal', marker=dict(color=wg_colours), yaxis='y'))
    fig.add_trace(go.Scatter(x=days, y=percentage_goal_reached, mode='markers+lines', name='% of Goal', marker_color='white', yaxis='y2'))

    fig.update_layout(
        title='Water Consumption',
        xaxis=dict(title='Days'),
        yaxis=dict(title='Water (ml)'),
        yaxis2=dict(title='Percentage (%)', overlaying='y', side='right', range=[0, 100]),
        barmode='group',
        hoverlabel=dict(font=dict(color='white')),
        legend=dict(orientation="h"),
        height = 600
    )

    st.plotly_chart(fig)

    data = []
    res = db.fetch()
    data_full = res.items
    for entry in data_full:
        if entry['key'].lower() == today.lower():
            data.append(entry)

    

    # Recomendation/Prediction
    caffeine_intake = data[0]['Diet']['Caffeine']
    age = data[0]['Personals']['Age']
    exercise_level = data[0]['Exercise Intensity']
    
    if age <= 12:
        age_recommendations = 45
    elif age <= 18:
        age_recommendations = 85
    else:
        age_recommendations = 400

    water_deviation = water_drank[today_index] - water_drank[today_index-1]
    caffeine_deviation = caffeine_intake - age_recommendations
    today_water = water_goal[today_index] - water_drank[today_index]
    yesterday_difference = water_drank[today_index-1] - water_goal[today_index-1]
    percentage = round((water_drank[today_index-1] / water_goal[today_index-1]) * 100, 0)
    extra_needed = round(abs(yesterday_difference)/100, 0)

    if exercise_level-5 < 0:
        exc_recommend = "Under average, need to do more exercise."
    else:
        exc_recommend = "Keep it up!"

    # What if Q2
    left_column, middle_column, right_column = st.columns(3)
    with left_column:
        st.subheader("**:blue[Water Drank:]**")
        st.metric(label="water", value=f"{water_drank[today_index]}ml", label_visibility="collapsed", delta=f"{water_deviation}ml from yesterday")

    with middle_column:
        st.subheader("**:blue[Caffeine:]**")
        st.metric(label="caffeine", value=f"{caffeine_intake}mg", label_visibility="collapsed", delta=f"{caffeine_deviation}mg from your age limit", delta_color="inverse")

    with right_column:
        st.subheader("**:blue[Excercise:]**")
        st.metric(label="excercise", value=f"{exercise_level}/10", label_visibility="collapsed", delta=f"{exercise_level-5} from average (5)")

    
    st.subheader("**:blue[Recommendation/Prediction:]**")
    
    if today_water>0:
        st.write(f"**{round((today_water/100),0)}** cups (:blue[{round(today_water, 0)}ml]) left for today. So far **{percentage_goal_reached[today_index]}%** of todays goal was reached.")
    if percentage >= 100:
        st.write("You drank enough water yesterday. Keep up the good work!")
    else:
        st.write(f"You drank only **{percentage}%** of your daily goal yesterday.")
        if percentage >= 75:
            st.write(f"You might experience: :blue[**Slight dehydration**].")
        elif percentage >= 50:
            st.write(f"You might experience: :blue[**tiredness**].")
        else:
            st.write(f"You may experience: :blue[**fatigue**].")

        st.write(f"Try to drink **{int(extra_needed)}** cups of water today to compensate.")
        st.write(f"Exercise recommendation: **:blue[{exc_recommend}]**")
