import time
import board
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn

# I2C bus'ını başlat
i2c = board.I2C()

# 4 adet ADS1115 modülünü farklı I2C adresleriyle başlat
ads1 = ADS.ADS1115(i2c, address=0x48)
ads2 = ADS.ADS1115(i2c, address=0x49)
ads3 = ADS.ADS1115(i2c, address=0x4A)
ads4 = ADS.ADS1115(i2c, address=0x4B)

# SPS ayarı (Örnekleme Hızı)
SPS = 128

ads1.data_rate = SPS
ads2.data_rate = SPS
ads3.data_rate = SPS
ads4.data_rate = SPS

# LM35 için sıcaklık hesaplama sabitleri
SCALE = 100.0  # LM35 için 1°C ≈ 10 mV, dolayısıyla SCALE = 100


# ADS1115 üzerindeki kanallara bağlı LM35 sensörlerini tanımla
channels = [
    AnalogIn(ads1, ADS.P0), AnalogIn(ads1, ADS.P1), AnalogIn(ads1, ADS.P2), AnalogIn(ads1, ADS.P3),
    AnalogIn(ads2, ADS.P0), AnalogIn(ads2, ADS.P1), AnalogIn(ads2, ADS.P2), AnalogIn(ads2, ADS.P3),
    AnalogIn(ads3, ADS.P0), AnalogIn(ads3, ADS.P1), AnalogIn(ads3, ADS.P2), AnalogIn(ads3, ADS.P3),
    AnalogIn(ads4, ADS.P0), AnalogIn(ads4, ADS.P1), AnalogIn(ads4, ADS.P2),
    
]
while True:
    try:
        # Her bir kanaldan sıcaklık verilerini oku ve ekrana yazdır
        for i, chan in enumerate(channels):
            raw_value = chan.value
            voltage = chan.voltage
            temperature_celsius = voltage * SCALE # LM35 10mV/°C oranına sahiptir
            
            print(f'LM35 Sensor {i+1}: Raw ADC Value: {raw_value} | Voltage: {voltage:.2f}V | Temperature: {temperature_celsius:.2f}°C')
        
        print('-' * 60)  # Veriler arasına ayraç ekle
        time.sleep(10)  # 10 saniye bekle

    except KeyboardInterrupt:
        print("Program sonlandırıldı.")
        break