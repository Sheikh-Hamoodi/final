import plotly.graph_objects as go  # pip install plotly
import streamlit as st  # pip install streamlit
from streamlit_option_menu import option_menu  # pip install streamlit-option-menu
import plotly.graph_objects as go
from datetime import date, datetime
import calendar
from deta import Deta
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
    options=["Data Entry", "Model"],
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
        
        with st.expander("Diet"):
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
if selected == "Model":
    DETA_KEY = "a0wq3cud5fq_gE78mR9NwdMaBhMQV2nUm7dfQ2VtgyGy"
    deta = Deta(DETA_KEY)
    db = deta.Base("hydration-system")
    days = ['Friday', 'Monday', 'Saturday', 'Sunday', 'Thursday', 'Tuesday', 'Wednesday']
    today_index = days.index(today)

    water_goal = water_simulation()
    water_drank = get_water_drank()

    

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

    data = []
    res = db.fetch()
    data_full = res.items
    print(data_full)
    for entry in data_full:
        if entry['key'].lower() == today.lower():
            data.append(entry)

    
    caffeine_intake = data[0]['Diet']['Caffeine']
    age = data[0]['Personals']['Age']
    exercise_level = data[0]['Exercise Intensity']

    age_group = "children" if age <= 12 else "adolescents" if age <= 18 else "adults"
    recommendations = {"children": 45, "adolescents": 85, "adults": 400}

    water_deviation = water_drank[today_index] - water_drank[today_index-1]
    caffeine_deviation = caffeine_intake - recommendations[age_group]
    today_water = (water_goal[today_index] - water_drank[today_index])/100


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

    yesterday_difference = water_drank[today_index-1] - water_goal[today_index-1]
    percentage = round((water_drank[today_index-1] / water_goal[today_index-1]) * 100, 0)
    extra_needed = round(abs(yesterday_difference)/100, 0)

    #Recomendation/Prediction
    st.subheader("**:blue[Recommendation/Prediction:]**")
    
    if today_water>0:
        st.write(f"**{str(round(int(today_water),0))}** cups left for today.")
    if percentage >= 100:
        st.write("You drank enough water yesterday. Keep up the good work!")
    else:
        st.write(f"You drank only **{percentage}%** of your daily goal yesterday.")
        if percentage >= 75:
            st.write(f"You might experience: **Slight dehydration**.")
        elif percentage >= 50:
            st.write(f"You might experience: **tiredness**.")
        else:
            st.write(f"You may experience: **fatigue**.")
        st.write(f"Try to drink **{int(extra_needed)}** cups of water today to compensate.")

    st.write(data)
