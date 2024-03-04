import streamlit as st
from deta import Deta
from datetime import date
import calendar

# Today
my_date = date.today()
day = calendar.day_name[my_date.weekday()]

# Initialise database
DETA_KEY = "a0wq3cud5fq_gE78mR9NwdMaBhMQV2nUm7dfQ2VtgyGy"
deta = Deta(DETA_KEY)
db = deta.Base("hydration-system")


# The following functions are used by app.py, and are kept in a seperate file for organisation

def insert_period(day, intensity_value, personal_data, diet_data, default_temp, init_water_drank, gender_value):
    return db.put({"key": day, "Exercise Intensity": intensity_value, "Personals": personal_data, "Diet": diet_data, "Temperature": default_temp, "Water Drank": init_water_drank, "Gender": gender_value})

def fetch_all_periods():
    res = db.fetch()
    return res.items

def get_water_drank():
    water_drank_list = []
    res = db.fetch()
    for item in res.items:
        water_drank_list.append(item["Water Drank"])
    return water_drank_list

def get_period(day):   

    return db.get(day)


# What if Q1
def water_simulation():

    # Constants
    AVG_SWEAT_RATE = 0.3 # liters per hour
    URINE_OUTPUT = 1.5 # liters per day
    FIBER_MULTIPLIER = 0.1 # liters per 10 grams of fiber
    SALT_MULTIPLIER = 0.6 # liters per 5 grams of salt
    CAFFEINE_MULTIPLIER = 0.1 # liters per 100 mg of caffeine

    days = ['Friday', 'Monday', 'Saturday', 'Sunday', 'Thursday', 'Tuesday', 'Wednesday']
    results = []

    for day in days:

        data = []
        res = db.fetch()
        data_full = res.items
        for entry in data_full:
            if entry['key'].lower() == day.lower():
                data.append(entry)

        # Inputs
        env_temp = data[0]['Temperature'] # degrees Celsius
        exercise_level = data[0]['Exercise Intensity']
        gender = data[0]['Gender']
        age = data[0]['Personals']['Age'] # years
        height = data[0]['Personals']['Height'] # cm
        weight = data[0]['Personals']['Weight'] # kg
        caffeine_intake = data[0]['Diet']['Caffeine'] # mg
        daily_fiber = data[0]['Diet']['Fibre'] # grams
        salt_intake = data[0]['Diet']['Salt'] # grams

        
        # Calculations with Validated parameters (note: already validated in app.py)

        # BMR using Harris-Benedict equation
        if gender == "Male":
            BMR = 66.5 + (13.75 * weight) + (5.003 * height) - (6.75 * age)
        elif gender == "Female":
            BMR = 655.1 + (9.563 * weight) + (1.850 * height) - (4.676 * age)
        sweating = AVG_SWEAT_RATE * int(env_temp) * 24

        total_fluid_intake = (BMR * 0.5)  + URINE_OUTPUT + (daily_fiber / 10) * FIBER_MULTIPLIER * 1000 + (salt_intake / 5) * SALT_MULTIPLIER * 1000 - (caffeine_intake / 100) * CAFFEINE_MULTIPLIER * 1000 + sweating
        total_fluid_intake += exercise_level*100

        results.append(total_fluid_intake)

    return results
