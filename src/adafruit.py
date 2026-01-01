import time
import board
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn

print("Kütüphaneler başarıyla import edildi.")

# I2C bus'ını başlat
i2c = board.I2C()

# ADS1115 modülünü başlat
ads = ADS.ADS1115(i2c)

# Kazanç ayarını yap
ads.gain = 1  # +/-4.096V giriş aralığı için

# Kanalı tanımla
chan = AnalogIn(ads, ADS.P0_GND)  # Tek uçlu ölçüm için

# Değerleri oku
print(f"Raw ADC Value: {chan.value}")
print(f"Voltage: {chan.voltage:.6f} V")
