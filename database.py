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
