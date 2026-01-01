import RPi.GPIO as GPIO
import time

# GPIO ayarlari
GPIO.setmode(GPIO.BCM)  # BCM pin numaralarini kullanacagiz
relay_pins = [20, 21]   # R�leye bagli GPIO pinleri

# R�le pinlerini �ikis olarak ayarla
GPIO.setup(relay_pins, GPIO.OUT)

def relay_test():
    try:
        while True:
         

            # R�leleri kapat
            GPIO.output(relay_pins[0], GPIO.LOW)
            GPIO.output(relay_pins[1], GPIO.LOW)

    
    except KeyboardInterrupt:
        print("Program sonlandirildi")
    
    finally:
        GPIO.cleanup()  # GPIO pinlerini sifirla

# Test programini �alistir
relay_test()
