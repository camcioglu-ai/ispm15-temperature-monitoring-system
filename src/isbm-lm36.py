import os
import time
import datetime
from PyQt5 import QtCore
from PyQt5.QtWidgets import *
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMessageBox
from sql_operation import *
from firm_operations import *
import settings
from PyQt5.QtGui import QBrush, QColor
import importlib
import threading
import RPi.GPIO as GPIO
import atexit
#
from firm_operations import FirmOperations
from Start_Dialog import Ui_Start_Dialog
from SettingsSensor_Interface import Ui_Ui_Settings_Dialog
from report_operations import ReportOperations
from Main_Interface import Ui_MainWindow  # Ana ekran

import board
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn

# LM35 için sıcaklık hesaplama sabitleri
SCALE = 100.0  # LM35 için 1°C ≈ 10 mV, dolayısıyla SCALE = 100

# I2C bus'ını başlat
i2c = board.I2C()

# 4 adet ADS1115 modülünü farklı I2C adresleriyle başlat
ads1 = ADS.ADS1115(i2c, address=0x48)
ads2 = ADS.ADS1115(i2c, address=0x49)
ads3 = ADS.ADS1115(i2c, address=0x4A)
ads4 = ADS.ADS1115(i2c, address=0x4B)

# SPS ayarı (Örnekleme Hızı)
SPS = 475
ads1.data_rate = SPS
ads2.data_rate = SPS
ads3.data_rate = SPS
ads4.data_rate = SPS

# ADS1115 üzerindeki kanallara bağlı LM35 sensörlerini tanımla
channels = [
    AnalogIn(ads1, ADS.P0), AnalogIn(ads1, ADS.P1), AnalogIn(ads1, ADS.P2), AnalogIn(ads1, ADS.P3),
    AnalogIn(ads2, ADS.P0), AnalogIn(ads2, ADS.P1), AnalogIn(ads2, ADS.P2), AnalogIn(ads2, ADS.P3),
    AnalogIn(ads3, ADS.P0), AnalogIn(ads3, ADS.P1), AnalogIn(ads3, ADS.P2), AnalogIn(ads3, ADS.P3),
    AnalogIn(ads4, ADS.P0), AnalogIn(ads4, ADS.P1), AnalogIn(ads4, ADS.P2)
]


def read_temp_from_channel(channel):
    try:
        voltage = channel.voltage
        print("volatage:"+str(voltage))
        temperature_celsius = (voltage * SCALE)  # LM35 10mV/°C
        temperature_celsius = round(temperature_celsius, 2) # İki ondalık basamağa yuvarla
        return temperature_celsius
    except Exception as e:
        print(f"Kanal okuma hatası: {e}")
        return 404.0  # Hata durumunda 404.0 döndür
        



def motor_control_R(stop_event, rest_event, shutdown_event):
    GPIO.setwarnings(False)  # Ignore warning for now
    GPIO.setmode(GPIO.BCM)  # Use physical pin numbering
    
    # Sag ve sol motorlar i�in pinleri ayarla
    GPIO.setup(settings.fan_right_pin, GPIO.OUT, initial=GPIO.HIGH)  # Sag motor pini Sari
    GPIO.setup(settings.fan_left_pin, GPIO.OUT, initial=GPIO.HIGH)  # Sol motor pini Sol
    time.sleep(1)  # Belirtilen s�re kadar �alistir

    # Program zorla kapatildiginda motorlari kapatmak i�in
    atexit.register(cleanup_gpio_R)

    while not stop_event.is_set():

        if shutdown_event.is_set():
            # Eger durdurma sinyali verilmisse motorlari kapat ve d�ng�y� sonlandir
            GPIO.output(settings.fan_right_pin, GPIO.HIGH)  # Sag motor kapat
            GPIO.output(settings.fan_left_pin, GPIO.HIGH)  # Sol motor kapat
            break

        # Sag motor a� ve �alistir
        GPIO.output(settings.fan_right_pin, GPIO.LOW)  # Sag motor a�
        time.sleep(settings.DESIRED_ENGINE_SECONDS)  # Belirtilen s�re kadar �alistir
        GPIO.output(settings.fan_right_pin, GPIO.HIGH)  # Sag motor kapat
        time.sleep(settings.ENGINE_RESTING_SECONDS)  # Belirtilen s�re kadar bekle

        # Sol motor a� ve �alistir
        GPIO.output(settings.fan_left_pin, GPIO.LOW)  # Sol motor a�
        time.sleep(settings.DESIRED_ENGINE_SECONDS)  # Belirtilen s�re kadar �alistir
        GPIO.output(settings.fan_left_pin, GPIO.HIGH)  # Sol motor kapat
        time.sleep(settings.ENGINE_RESTING_SECONDS)  # Belirtilen s�re kadar bekle

    # Durdurma durumunda motorlari kapat
    GPIO.output(settings.fan_right_pin, GPIO.HIGH)  # Sag motor kapat
    GPIO.output(settings.fan_left_pin, GPIO.HIGH)  # Sol motor kapat

def cleanup_gpio_R():
    GPIO.output(settings.fan_right_pin, GPIO.HIGH)  # Sag motor kapat
    GPIO.output(settings.fan_left_pin, GPIO.HIGH)  # Sol motor kapat
    GPIO.output(16, GPIO.HIGH)  # Sag motor kapat
    GPIO.output(23, GPIO.HIGH)  # Sol motor kapat
    GPIO.output(24, GPIO.HIGH)  # Sol motor kapat
    GPIO.cleanup()  # GPIO pinlerini temizle

def cleanup_red():
     GPIO.setmode(GPIO.BCM)  # Use physical pin numbering
     GPIO.output(23, GPIO.LOW)  # 23 aç
     GPIO.cleanup()  # GPIO pinlerini temizle



# Veri güncelleme iş parçacığı
class DataUpdateThread(QtCore.QThread):
    data_updated = QtCore.pyqtSignal(str, *[str]*16)
    finished = QtCore.pyqtSignal()

    def __init__(self, desired_temp, desired_seconds, desired_success_count):
        super().__init__()
        self.desired_seconds = settings.DESIRED_SECONDS
        self.desired_success_count = settings.DESIRED_SUCCESS_COUNT
        self.previous = []
        self.current = []
        self.isLegit = False
        self.desiredTemp = settings.DESIRED_TEMP
        self.counter = 0

    def run(self):
        
        all_measurements = []
        attempt = 0

        # Motor kontrol iş parçacığını başlat
        self.stop_event = threading.Event()
        self.rest_event = threading.Event()
        self.shutdown_event = threading.Event()
        self.motor_thread = threading.Thread(target=motor_control_R, args=(self.stop_event, self.rest_event, self.shutdown_event))
        self.motor_thread.start()
        Main.red_light_off(self)
        Main.green_light(self)
        
        GPIO.setmode(GPIO.BCM)  # Use physical pin numbering
        GPIO.setup(16, GPIO.OUT, initial=GPIO.HIGH) #rez low
    

    
        while self.counter < self.desired_success_count:

            olcum = []
            sensor_values=[]

            checkbox_values = [
             settings.sensor1, settings.sensor2, settings.sensor3, settings.sensor4, settings.sensor5,
             settings.sensor6, settings.sensor7, settings.sensor8, settings.sensor9, settings.sensor10,
             settings.sensor11, settings.sensor12, settings.sensor13, settings.sensor14, settings.sensor15           
            ]

            for i, chan in enumerate(channels):
             sensor_values.append(read_temp_from_channel(chan))


            for i in range(len(checkbox_values)):
                if not checkbox_values[i]:  # Eğer checkbox_values dizisinin n. indexi False ise
                    olcum.append(404.0)  # 404.0 değerini ekle
                else:  # Eğer checkbox_values dizisinin n. indexi True ise
                    olcum.append(sensor_values[i])  # sensor_values'taki n. indexin değerini ekle

            ortalama=sum(olcum)/len(olcum)

    
            print("ortalama:",ortalama)


            if(ortalama>=settings.RESISTANCE_MAX):
                GPIO.output(16, GPIO.HIGH)  # FOR REAL

            if(ortalama <= settings.RESISTANCE_MIN):
                print("resistance")
                GPIO.output(16, GPIO.LOW)  # Set to ONN
                
    
            attempt += 1
            print(f"{attempt}. Denemedir")
            all_measurements.append(olcum)

            if self.counter == 0:
                if self.temperature_check(olcum, self.desiredTemp):
                    print("İlk başarılı işlem: İstenilen sıcaklık sağlandı")
                    self.counter += 1

                    now = datetime.datetime.now()
                    tarih_zaman = now.strftime('%Y-%m-%d %H:%M:%S')
                    self.data_updated.emit(tarih_zaman, *map(str, olcum), str(self.counter))
                    print(f"{self.counter}. başarılı işlem. Tarih ve Zaman: {tarih_zaman}, Sıcaklık Değerleri: {', '.join(map(str, olcum))}°C")
                    time.sleep(settings.DESIRED_SECONDS)

                else:
                    self.counter = 0
                    now = datetime.datetime.now()
                    tarih_zaman = now.strftime('%Y-%m-%d %H:%M:%S')
                    self.data_updated.emit(tarih_zaman, *map(str, olcum), str(self.counter))
                    print(f"{self.counter}. başarılı işlem. Tarih ve Zaman: {tarih_zaman}, Sıcaklık Değerleri: {', '.join(map(str, olcum))}°C")
                    time.sleep(settings.DESIRED_SECONDS)

            else:
                if self.temperature_check(olcum, self.desiredTemp):
                    print("İstenilen sıcaklık sağlandı")
                    if self.check_last_two_diff(all_measurements):
                        print("Sıcaklık değişimi uygundur")
                        print("Başarılı arttır")
                        self.counter += 1
                        print(f"{self.counter}. BAŞARILI ADIM")

                        now = datetime.datetime.now()
                        tarih_zaman = now.strftime('%Y-%m-%d %H:%M:%S')
                        self.data_updated.emit(tarih_zaman, *map(str, olcum), str(self.counter))
                        print(f"{self.counter}. başarılı işlem. Tarih ve Zaman: {tarih_zaman}, Sıcaklık Değerleri: {', '.join(map(str, olcum))}°C")
                        time.sleep(settings.DESIRED_SECONDS)

                    else:
                        print("Hızlı sıcaklık değişimi")
                        print("Başarısız sıfırlandı")
                        print("Bir önceki adıma göre sıcaklık farkı çok yüksek")
                        print(f"Sıcaklık Değerleri: {', '.join(map(str, olcum))}°C")
                        self.counter = 0
                        time.sleep(settings.DESIRED_SECONDS)
                else:
                    print("Sistem ısıtılmalıdır. İstenilen sıcaklığa ulaşılmadı")
                    now = datetime.datetime.now()
                    tarih_zaman = now.strftime('%Y-%m-%d %H:%M:%S')
                    self.data_updated.emit(tarih_zaman, *map(str, olcum), "Eşik değer altında")
                    print(f"Adım sayısı sıfırlandı, mevcut sayı: {self.counter}. Tarih ve Zaman: {tarih_zaman}, Sıcaklık Değerleri: {', '.join(map(str, olcum))}°C")
                    self.counter = 0
                    time.sleep(settings.DESIRED_SECONDS)

        print("Ölçüm tamamlandı")
        self.finished.emit()
        #self.stop_event.set()
        self.shutdown_event.set()

        print(f"Program sonlandı. Ard arda {self.desired_success_count} başarılı işlem yapıldı.")

    def check_legit(self, temps):
        for temp in temps:
            try:
                temp_value = float(temp)
                if temp_value <= self.desiredTemp:
                    return False
            except ValueError:
                continue  # 'x' değerlerini atla
        return True

    def temperature_check(self, liste, desired_temp):
        for element in liste:
            try:
                temp_value = float(element)
                if temp_value != 404.0 and temp_value < desired_temp:
                    return False
            except ValueError:
                continue  # 'x' değerlerini atla
        return True

    def check_last_two_diff(self, list_of_lists):
        if len(list_of_lists) < 2:
            print("Hata: En az iki alt liste gerekli.")
            return False

        last_one = list_of_lists[-1]
        last_two = list_of_lists[-2]

        if len(last_one) != len(last_two):
            print("Hata: Alt listelerin uzunlukları eşit değil.")
            return False

        for i in range(len(last_one)):
            try:
                value_one = float(last_one[i])
                value_two = float(last_two[i])
                diff = abs(value_one - value_two)
                if diff > settings.DESIRED_TEMP_DIFFERENCE:
                    return False
            except ValueError:
                continue  # 'x' değerlerini atla

        return True

# Ana pencere sınıfı
class Main(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()  # Ana tasarımı miras al
        self.ui.setupUi(self)  # Ana tasarımı yükle

        self.firm_operations = FirmOperations()  # Firma operasyonları sınıfını miras al
        self.report_operations = ReportOperations()
        self.first_measurement() # ana ekran için ilk ölçüm

        self.desired_temp = settings.DESIRED_TEMP
        self.desired_seconds = settings.DESIRED_SECONDS
        self.desired_success_count = settings.DESIRED_SUCCESS_COUNT
        self.ui.btn_Start.clicked.connect(self.start_popup)  # Starta basınca ölçüm yap
        self.ui.btn_RecipeOpe.clicked.connect(self.settings_popup)  # Ayarlar popup
        self.ui.btn_ShowReports.clicked.connect(self.report_operations.openReportScreen)  # Raporlar Ekranı
        self.data_thread = None
        self.cleanup_incomplete_reports()
        self.red_light()
        atexit.register(cleanup_red)

    def red_light(self):
        GPIO.setmode(GPIO.BCM)  # Use physical pin numbering
        GPIO.setup(settings.alert_red_pin, GPIO.OUT, initial=GPIO.LOW)  
        GPIO.output(settings.alert_red_pin, GPIO.LOW) 

    def red_light_off(self):
        GPIO.setmode(GPIO.BCM)  # Use physical pin numbering
        GPIO.output(settings.alert_red_pin, GPIO.HIGH)  

    def green_light(self):
        GPIO.setmode(GPIO.BCM)  # Use physical pin numbering
        GPIO.setup(settings.alert_green_pin, GPIO.OUT, initial=GPIO.LOW)  
        GPIO.output(settings.alert_green_pin, GPIO.LOW)  
    
    def green_light_off(self):
        GPIO.setmode(GPIO.BCM)  # Use physical pin numbering
        GPIO.output(settings.alert_green_pin, GPIO.HIGH)  

    def stop_motor(self): #motor kapat
        GPIO.output(settings.resistance_pin, GPIO.HIGH)  
        GPIO.output(settings.fan_right_pin, GPIO.HIGH)  # Sağ motor kapat
        GPIO.output(settings.fan_left_pin, GPIO.HIGH)  # Sol motor kapat
        GPIO.cleanup()  # GPIO pinlerini temizle
        self.red_light()

       

    def cleanup_incomplete_reports(self):
        incomplete_reports = get_incomplete_reports()
        for report_id in incomplete_reports:
            delete_report_steps(report_id)
            delete_report(report_id)
            print(f"Tamamlanmamış rapor ve adımları silindi: Rapor ID {report_id}")
        if incomplete_reports:
            reset_autoincrement('report')

    def first_measurement(self):
        temps = []

        txt_probs = [self.ui.txt_prob_status, self.ui.txt_prob_status_2, self.ui.txt_prob_status_3, self.ui.txt_prob_status_4, self.ui.txt_prob_status_5, self.ui.txt_prob_status_6,
                     self.ui.txt_prob_status_7, self.ui.txt_prob_status_8, self.ui.txt_prob_status_9, self.ui.txt_prob_status_10, self.ui.txt_prob_status_11, self.ui.txt_prob_status_12,
                     self.ui.txt_prob_status_13, self.ui.txt_prob_status_14, self.ui.txt_prob_status_15]

        for i, chan in enumerate(channels):
         temps.append(read_temp_from_channel(chan))

        # Olcum listesini 15 elemana tamamla
        if len(temps) < 15:
            temps.extend(['x'] * (15 - len(temps)))

        for i in range(len(temps)):
            txt_probs[i].setText(str(temps[i]))

        # Sadece sayısal değerleri kullanarak ortalama hesapla
        numeric_temps = []
        for temp in temps:
            try:
                numeric_temps.append(float(temp))
            except ValueError:
                continue  # 'x' değerlerini atla

        average_temp = sum(numeric_temps) / len(numeric_temps) if numeric_temps else 0.0
        average_temp = round(average_temp, 2)  # İki ondalık basamağa yuvarla
        self.ui.txt_area_temp_avarage.setText(str(average_temp))
        print("İlk ölçüm yapıldı")

    def success_popup(self):
        reportNo = report_index()
        set_report_end_time(reportNo)
        popupMessage = f"İşlem tamamlandı. Raporlar bölümünden kontrol ediniz. Rapor No: {reportNo}"
        popup = QMessageBox()
        popup.setWindowTitle("İşlem Tamamlandı")
        popup.setText(popupMessage)
        popup.setIcon(QMessageBox.Information)
        self.ui.tableWidget.setRowCount(0)
        popup.setStandardButtons(QMessageBox.Ok)
        self.green_light_off()
        self.red_light()
        self.stop_motor()

        popup_result = popup.exec_()
        if popup_result == QMessageBox.Ok:
            popup.close()

    # Başlat butonuna basılır. Gerekli bilgiler için popup açılır
    def start_popup(self):
        self.popup = QDialog()
        self.ui_start_dialog = Ui_Start_Dialog()
        self.ui_start_dialog.setupUi(self.popup)
        self.ui_start_dialog.btn_Start_P.clicked.connect(self.popup_measurement)
        self.popup.exec_()

    def settings_popup(self):
        self.popup = QDialog()
        self.ui_settings_dialog = Ui_Ui_Settings_Dialog()
        self.ui_settings_dialog.setupUi(self.popup)
        self.ui_settings_dialog.line_Ekds.setText(str(settings.DESIRED_TEMP))
        self.ui_settings_dialog.line_Fan_Left.setText(str(settings.DESIRED_ENGINE_SECONDS))
        self.ui_settings_dialog.line_Fan_Right.setText(str(settings.DESIRED_ENGINE_SECONDS))
        self.ui_settings_dialog.line_Fan_Stop.setText(str(settings.ENGINE_RESTING_SECONDS))
        self.ui_settings_dialog.line_Resistance_Max.setText(str(settings.RESISTANCE_MAX))
        self.ui_settings_dialog.line_Resistance_Min.setText(str(settings.RESISTANCE_MIN))

        self.ui_settings_dialog.sensor_1.setChecked(settings.sensor1)
        self.ui_settings_dialog.sensor_2.setChecked(settings.sensor2)
        self.ui_settings_dialog.sensor_3.setChecked(settings.sensor3)
        self.ui_settings_dialog.sensor_4.setChecked(settings.sensor4)
        self.ui_settings_dialog.sensor_5.setChecked(settings.sensor5)
        self.ui_settings_dialog.sensor_6.setChecked(settings.sensor6)
        self.ui_settings_dialog.sensor_7.setChecked(settings.sensor7)
        self.ui_settings_dialog.sensor_8.setChecked(settings.sensor8)
        self.ui_settings_dialog.sensor_9.setChecked(settings.sensor9)
        self.ui_settings_dialog.sensor_10.setChecked(settings.sensor10)
        self.ui_settings_dialog.sensor_11.setChecked(settings.sensor11)
        self.ui_settings_dialog.sensor_12.setChecked(settings.sensor12)
        self.ui_settings_dialog.sensor_13.setChecked(settings.sensor13)
        self.ui_settings_dialog.sensor_14.setChecked(settings.sensor14)
        self.ui_settings_dialog.sensor_15.setChecked(settings.sensor15)

        self.ui_settings_dialog.btn_SettingsSave.clicked.connect(self.save_settings)
        self.popup.exec_()



    def save_settings(self):
        try:
            # Arayüzden yeni değerleri al
            new_values = {
                'DESIRED_TEMP': int(self.ui_settings_dialog.line_Ekds.text()),
                'DESIRED_ENGINE_SECONDS': int(self.ui_settings_dialog.line_Fan_Left.text()),
                'DESIRED_ENGINE_SECONDS_RIGHT': int(self.ui_settings_dialog.line_Fan_Right.text()),
                'ENGINE_RESTING_SECONDS': int(self.ui_settings_dialog.line_Fan_Stop.text()),
                'RESISTANCE_MAX': float(self.ui_settings_dialog.line_Resistance_Max.text()),
                'RESISTANCE_MIN': float(self.ui_settings_dialog.line_Resistance_Min.text()),
                'sensor1': self.ui_settings_dialog.sensor_1.isChecked(),
                'sensor2': self.ui_settings_dialog.sensor_2.isChecked(),
                'sensor3': self.ui_settings_dialog.sensor_3.isChecked(),
                'sensor4': self.ui_settings_dialog.sensor_4.isChecked(),
                'sensor5': self.ui_settings_dialog.sensor_5.isChecked(),
                'sensor6': self.ui_settings_dialog.sensor_6.isChecked(),
                'sensor7': self.ui_settings_dialog.sensor_7.isChecked(),
                'sensor8': self.ui_settings_dialog.sensor_8.isChecked(),
                'sensor9': self.ui_settings_dialog.sensor_9.isChecked(),
                'sensor10': self.ui_settings_dialog.sensor_10.isChecked(),
                'sensor11': self.ui_settings_dialog.sensor_11.isChecked(),
                'sensor12': self.ui_settings_dialog.sensor_12.isChecked(),
                'sensor13': self.ui_settings_dialog.sensor_13.isChecked(),
                'sensor14': self.ui_settings_dialog.sensor_14.isChecked(),
                'sensor15': self.ui_settings_dialog.sensor_15.isChecked(),
            }

            # settings.py dosyasının bulunduğu dizini al
            script_dir = os.path.dirname(os.path.abspath(__file__))
            settings_path = os.path.join(script_dir, 'settings.py')

            # settings.py dosyasını okuyun
            with open(settings_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            # Ayarları güncelle
            updated_lines = []
            for line in lines:
                stripped_line = line.strip()
                if not stripped_line or stripped_line.startswith('#') or any(pin_var in stripped_line for pin_var in ['fan_right_pin', 'fan_left_pin', 'resistance_pin', 'alert_red_pin', 'alert_green_pin']):
                    # Boş, yorum satırları veya sabit pin değişkenlerini olduğu gibi ekle
                    updated_lines.append(line)
                    continue

                # Satırda '=' işareti var mı kontrol et
                if '=' in line:
                    # Değişken ismini al
                    var_name = line.split('=')[0].strip()
                    if var_name in new_values:
                        # Yeni değeri satıra yaz, yorumları koru
                        parts = line.split('#', 1)
                        code_part = parts[0].strip()
                        comment_part = '#' + parts[1] if len(parts) > 1 else ''

                        new_value = new_values[var_name]
                        # Değerin tipine göre tırnak işareti kullan
                        if isinstance(new_value, str):
                            new_line = f'{var_name} = "{new_value}" {comment_part}\n'
                        elif isinstance(new_value, bool):
                            new_line = f'{var_name} = {str(new_value)} {comment_part}\n'
                        else:
                            new_line = f'{var_name} = {new_value} {comment_part}\n'

                        updated_lines.append(new_line)
                        continue  # Sonraki satıra geç

                # Değişiklik yapılmadıysa satırı olduğu gibi ekle
                updated_lines.append(line)

            # Güncellenmiş satırları dosyaya yaz
            with open(settings_path, 'w', encoding='utf-8') as f:
                f.writelines(updated_lines)

            # settings modülünü yeniden yükle
            importlib.reload(settings)
            QtWidgets.QMessageBox.information(self, "Başarılı", "Ayarlar kaydedildi.")
            self.popup.close()

        except ValueError:
            QtWidgets.QMessageBox.warning(self, "Hata", "Lütfen tüm sayısal alanlara geçerli bir sayı girin.")


    def popup_measurement(self):
        m3 = self.ui_start_dialog.txt_amount.text()
        piece = self.ui_start_dialog.txt_pieces.text()
        type = self.ui_start_dialog.txt_type.text()
        info = self.ui_start_dialog.txtArea_info.toPlainText()

        now = datetime.datetime.now()
        start_time = now.strftime('%Y-%m-%d %H:%M:%S')
        self.ui.txt_time.setText(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        reportindex = report_index()
        reportID=int(reportindex)+1

        insert_report(str(reportID),"1", start_time, "IP", type, m3, piece, info) #DB ilk islem
        self.start_measurement()
        self.popup.close()

    def start_measurement(self):
        self.data_thread = DataUpdateThread(self.desired_temp, settings.DESIRED_SECONDS, self.desired_success_count)
        self.data_thread.data_updated.connect(self.update_table_colored)
        self.data_thread.start()
        self.data_thread.running = True
        self.data_thread.finished.connect(self.success_popup)

    def filetoCrud(self, rf_id, tempsdb, ri_time, success_step):
        insert_report_step(rf_id, tempsdb[0], tempsdb[1], tempsdb[2], tempsdb[3], tempsdb[4], tempsdb[5], tempsdb[6],
                           tempsdb[7], tempsdb[8], tempsdb[9], tempsdb[10], tempsdb[11], tempsdb[12], tempsdb[13],
                           tempsdb[14], "0", "0", ri_time, success_step)

    def update_table_colored(self, tarih_zaman, *temps):
        rowPosition = self.ui.tableWidget.rowCount()
        self.ui.tableWidget.insertRow(rowPosition)

        tempsdb = []  # tempsdb'yi burada tanımlıyoruz

        for i, temp in enumerate(temps[:-1]):  # Son parametre counter, onu atlıyoruz
            # Eğer temp 'x' veya '404.0' ise, o sütundaki bir önceki değeri al
            if (temp == "404.0" or temp == "x") and rowPosition > 0:
                previous_item = self.ui.tableWidget.item(rowPosition - 1, i)
                if previous_item:
                    previous_value = previous_item.text()
                    item = QTableWidgetItem(previous_value)
                    tempsdb.append(previous_value)  # tempsdb'ye de önceki değeri ekle
                else:
                    item = QTableWidgetItem("x")  # Eğer önceki satırda bir değer yoksa, 'x' kullan
                    tempsdb.append("x")  # Eğer önceki değer yoksa, tempsdb'ye "x" ekle
            else:
                # Ölçüm değerini iki ondalık basamağa yuvarla
                try:
                    temp_value = round(float(temp), 2)
                    formatted_temp_value = f"{temp_value:.2f}"  # Sayiyi 2 ondalik basamakla formatla
                    item = QTableWidgetItem(formatted_temp_value)
                    tempsdb.append(formatted_temp_value)
                except ValueError:
                    item = QTableWidgetItem(str(temp))
                    tempsdb.append(temp)

            # Sıcaklık değeri settings.DESIRED_TEMP'in altındaysa hücreyi kırmızı yap
            try:
                temp_value = float(temp)
                if temp_value != 404.0 and temp_value < settings.DESIRED_TEMP:
                    item.setBackground(QBrush(QColor(255, 0, 0)))  # Kırmızı arkaplan rengi
            except ValueError:
                pass  # Sıcaklık değeri float'a dönüştürülemezse (örneğin "x" gibi), bu hücreyi atla

            self.ui.tableWidget.setItem(rowPosition, i, item)

        count = self.data_thread.desired_success_count - self.data_thread.counter
        self.ui.tableWidget.setItem(rowPosition, 15, QTableWidgetItem(str(count)))
        self.ui.tableWidget.setItem(rowPosition, 16, QTableWidgetItem(tarih_zaman))
        self.ui.tableWidget.scrollToBottom()
        reportindex = report_index()
        self.filetoCrud(str(reportindex), tempsdb, tarih_zaman, count) #db 2. islem

if __name__ == "__main__":
    app = QApplication([])
    main_instance = Main()
    main_instance.show()
    app.exec_()
