import streamlit as st  # pip install streamlit
from deta import Deta  # pip install deta
import serial


# Load the environment variables
DETA_KEY = "a0wq3cud5fq_gE78mR9NwdMaBhMQV2nUm7dfQ2VtgyGy"

# Initialize with a project key
deta = Deta(DETA_KEY)

# This is how to create/connect a database
db = deta.Base("hydration-system")


def insert_period(day, intensity_value, personal_data, diet_data):
    """Returns the report on a successful creation, otherwise raises an error"""
    return db.put({"key": day, "Exercise Intensity": intensity_value, "Personals": personal_data, "Diet": diet_data})


def fetch_all_periods():
    """Returns a dict of all periods"""
    res = db.fetch()
    return res.items


def get_period(day):
    """If not found, the function will return None"""
    return db.get(day)

def micro():
    

def water_simulation():
    AVG_SWEAT_RATE = 0.8 # liters per hour
    URINE_OUTPUT = 1.5 # liters per day
    FIBER_MULTIPLIER = 0.1 # liters per 10 grams of fiber
    SALT_MULTIPLIER = 0.6 # liters per 5 grams of salt
    CAFFEINE_MULTIPLIER = 0.25 # liters per 100 mg of caffeine

    # Inputs
    env_temp = 25 # degrees Celsius
    weight = 70 # kg
    age = 30 # years
    height = 170 # cm
    daily_fiber = 25 # grams
    salt_intake = 10 # grams
    caffeine_intake = 200 # mg

    # Define a function to simulate water loss due to sweating
    def sweat(env, rate):
        while True:
            yield env.timeout(1)
            yield rate

    # Define a function to simulate water loss due to urine output
    def urine(env, output):
        while True:
            yield env.timeout(24)
            yield output / 24

    # Define a function to calculate the recommended water intake for the day
    def calculate_intake(bmr, tdee, sweat_loss, urine_loss, fiber_loss, salt_loss, caffeine_loss):
        total_loss = sweat_loss + urine_loss + fiber_loss + salt_loss + caffeine_loss
        return tdee + total_loss

    # Create a SimPy environment
    env = simpy.Environment()

    # Calculate basal metabolic rate (BMR) using the Harris-Benedict equation
    bmr = 88.362 + (13.397 * weight) + (4.799 * height) - (5.677 * age)

    # Calculate total daily energy expenditure (TDEE) based on BMR and activity level
    activity_level = 1.2 # sedentary
    tdee = bmr * activity_level

    # Create a process to simulate sweating
    sweat_process = env.process(sweat(env, AVG_SWEAT_RATE * (env_temp - 25)))

    # Create a process to simulate urine output
    urine_process = env.process(urine(env, URINE_OUTPUT))

    # Calculate water loss due to fiber intake
    fiber_loss = daily_fiber * FIBER_MULTIPLIER

    # Calculate water loss due to salt intake
    salt_loss = (salt_intake / 5) * SALT_MULTIPLIER

    # Calculate water loss due to caffeine intake
    caffeine_loss = (caffeine_intake / 100) * CAFFEINE_MULTIPLIER

    # Wait for 24 hours to simulate a full day
    env.run(until=24)

    # Get the total water loss for the day
    sweat_loss = sweat_process.now
    urine_loss = urine_process.now
    total_loss = sweat_loss + urine_loss + fiber_loss + salt_loss + caffeine_loss

    # Calculate the recommended water intake for the day
    recommended_intake = calculate_intake(bmr, tdee, sweat_loss, urine_loss, fiber_loss, salt_loss, caffeine_loss)

    # Print results
    print("Based on your inputs, you should drink approximately", round(recommended_intake, 2), "liters of water today.")





ser = serial.Serial()
ser.baudrate = 115200
ser.port = 'COM6'
ser.open()


temp = []
light = []


csv_file_path = 'sensor_data.csv'


while True:
    data = ser.readline().decode('utf-8').strip()
    temperature, light_level = map(int, data.split(','))


    temp.append(temperature)
    light.append(light_level)


    print(f'Temperature: {temperature}°C, Light Level: {light_level}')





#day = "Monday"
#personals = {'Height': 170, 'Weight': 80, 'Age': 16}
#diets = {'Salt': 20, 'Fibre': 20, 'Caffeine': 600}

#insert_period(day, personals, diets)
#fetch_all_periods()
#get_period(day)
