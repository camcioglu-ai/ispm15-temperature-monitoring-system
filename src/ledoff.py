import RPi.GPIO as GPIO
import time

# GPIO pin numaralarını tanımlayın
fan_right_pin = 21
fan_left_pin = 20
resistance_pin = 16
alert_red_pin = 23
alert_green_pin = 24

# GPIO modunu ayarlayın
GPIO.setmode(GPIO.BCM)  # BCM numaralandırmasını kullan

# Pinleri çıkış olarak ayarlayın
GPIO.setup(fan_right_pin, GPIO.OUT)
GPIO.setup(fan_left_pin, GPIO.OUT)
GPIO.setup(resistance_pin, GPIO.OUT)
GPIO.setup(alert_red_pin, GPIO.OUT)
GPIO.setup(alert_green_pin, GPIO.OUT)

try:

    
    GPIO.output(fan_right_pin, GPIO.LOW)
    GPIO.output(fan_left_pin, GPIO.LOW)
    GPIO.output(resistance_pin, GPIO.LOW)
    GPIO.output(alert_red_pin, GPIO.LOW)
    GPIO.output(alert_green_pin, GPIO.LOW)


except KeyboardInterrupt:
    print("Program durduruldu.")

finally:
    GPIO.cleanup()  # GPIO pinlerini temizle
