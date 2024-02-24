import streamlit as st  # pip install streamlit
from deta import Deta  # pip install deta
#from serial import Serial
from datetime import date, datetime
import calendar
import time


# Get today's date
my_date = date.today()
day = calendar.day_name[my_date.weekday()]

# Load the environment variables
DETA_KEY = "a0wq3cud5fq_gE78mR9NwdMaBhMQV2nUm7dfQ2VtgyGy"

# Initialize with a project key
deta = Deta(DETA_KEY)

# This is how to create/connect a database
db = deta.Base("hydration-system")


def insert_period(day, intensity_value, personal_data, diet_data, default_temp, init_water_drank):
    return db.put({"key": day, "Exercise Intensity": intensity_value, "Personals": personal_data, "Diet": diet_data, "Temperature": default_temp, "Water Drank": init_water_drank})


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
    


def water_simulation():

    # Constants
    AVG_SWEAT_RATE = 0.8 # liters per hour
    URINE_OUTPUT = 1.5 # liters per day
    FIBER_MULTIPLIER = 0.1 # liters per 10 grams of fiber
    SALT_MULTIPLIER = 0.6 # liters per 5 grams of salt
    CAFFEINE_MULTIPLIER = 0.25 # liters per 100 mg of caffeine
    EXERCISE_FLUID_MULTIPLIER = 0.5 # liters per hour of exercise per level

    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    results = []

    for day in days:

        data = []
        res = db.fetch()
        data_full = res.items
        print(data_full)
        for entry in data_full:
            if entry['key'].lower() == day.lower():
                data.append(entry)

        # Inputs
        env_temp = data[0]['Temperature'] # degrees Celsius
        exercise_level = data[0]['Exercise Intensity']

        age = data[0]['Personals']['Age'] # years
        height = data[0]['Personals']['Height'] # cm
        weight = data[0]['Personals']['Weight'] # kg

        caffeine_intake = data[0]['Diet']['Caffeine'] # mg
        daily_fiber = data[0]['Diet']['Fibre'] # grams
        salt_intake = data[0]['Diet']['Salt'] # grams

        print(data)

        # Calculate BMR using Harris-Benedict equation
        BMR = 66.5 + (13.75 * weight) + (5.003 * height) - (6.75 * age)

        # Calculate sweating
        sweating = AVG_SWEAT_RATE * env_temp * 24

        total_fluid_intake = sweating + URINE_OUTPUT + (daily_fiber / 10) * FIBER_MULTIPLIER * 1000 + (salt_intake / 5) * SALT_MULTIPLIER * 1000 + (caffeine_intake / 100) * CAFFEINE_MULTIPLIER * 1000

        total_fluid_intake += exercise_level*100

        #print("Total fluid intake needed:", total_fluid_intake, "ml/day")
        results.append(total_fluid_intake)
    return results
