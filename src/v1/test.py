from time import sleep
from w1thermsensor import W1ThermSensor
import os

def refresh_one_wire():
    os.system('sudo modprobe -r w1_gpio')
    os.system('sudo modprobe -r w1_therm')
    os.system('sudo modprobe w1_gpio')
    os.system('sudo modprobe w1_therm')

def read_temperatures():
    # Use GPIO 4 for One-Wire communication
    sensors = W1ThermSensor.get_available_sensors([W1ThermSensor.THERM_SENSOR_DS18B20], {"gpio_pin": 4})
    temperatures = {}
    for sensor in sensors:
        temperature = sensor.get_temperature()
        temperatures[sensor.id] = temperature
    return temperatures

if __name__ == "__main__":
    while True:
        refresh_one_wire()  # Refresh One-Wire interface
        temperatures = read_temperatures()
        for sensor_id, temperature in temperatures.items():
            print(f"Sensor {sensor_id}: Temperature {temperature}°C")
        
        # Wait for some time before refreshing the readings
        sleep(10)  # Adjust the refresh rate as needed
