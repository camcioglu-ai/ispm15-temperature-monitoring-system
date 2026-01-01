import time
import board
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn

# I2C bus'ını başlat
i2c = board.I2C()

# Tek bir ADS1115 modülünü başlat (adres: 0x48)
ads1 = ADS.ADS1115(i2c, address=0x48)

# SPS ayarı (Örnekleme Hızı)
SPS = 64  # Daha düşük bir hız seçildi
ads1.data_rate = SPS

# LM35 için sıcaklık hesaplama sabitleri
SCALE = 100.0  # LM35 için 1°C ≈ 10 mV, dolayısıyla SCALE = 100

# ADS1115 üzerindeki kanallara bağlı LM35 sensörlerini tanımla
channels = [
    AnalogIn(ads1, ADS.P0), AnalogIn(ads1, ADS.P1), AnalogIn(ads1, ADS.P2), AnalogIn(ads1, ADS.P3)
]

# Sensörlerden alınan voltaj değeri üst sınırı (örn. anormal yüksek sıcaklıklar için)
 # LM35 genellikle 0-1.5V arasında çalışır

while True:
    try:
        # Her bir kanaldan sıcaklık verilerini oku ve ekrana yazdır
        for i, chan in enumerate(channels):
            raw_value = chan.value  # Ham ADC değerini al
            voltage = chan.voltage  # Voltajı al
            temperature_celsius = voltage * SCALE  # LM35'in 10mV/°C oranını kullanarak sıcaklık hesapla
        
            # Her sensör arasında kısa bir gecikme ekle
            time.sleep(0.5)
        
        print('-' * 60)  # Veriler arasına ayraç ekle
        time.sleep(10)  # 10 saniye bekle

    except KeyboardInterrupt:
        print("Program sonlandırıldı.")
        break
