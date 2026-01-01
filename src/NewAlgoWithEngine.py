import os
import glob
import time
import datetime
import concurrent.futures
import sys
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
import RPi.GPIO as GPIO  # Import Raspberry Pi GPIO library
from firm_operations import FirmOperations
from Start_Dialog import Ui_Start_Dialog
from Settings_Interface import Ui_Ui_Settings_Dialog
from report_operations import ReportOperations
from Main_Interface import Ui_MainWindow # Ana ekran


os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')
base_dir = '/sys/bus/w1/devices/'
os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')
base_dir = '/sys/bus/w1/devices/'
device_folders = glob.glob(base_dir + '28*')
device_files = [folder + '/w1_slave' for folder in device_folders]
#at_1=glob.glob(base_dir + '28-20320c34db81/w1_slave')
#at_2=glob.glob(base_dir + '28-20320c3631db/w1_slave')


#device_files.remove(at_1[0])
#device_files.remove(at_2[0])


def read_temp_raw(device_file):
    with open(device_file, 'r') as f:
        lines = f.readlines()
    return lines

def read_temp(device_file):
    lines = read_temp_raw(device_file)
    
    if lines and lines[0].strip()[-3:] == 'YES':
        equals_pos = lines[1].find('t=')
        if equals_pos != -1:
            temp_string = lines[1][equals_pos + 2:]
            temp_c = round(float(temp_string) / 1000.0, 2)
            if temp_c==85:
             read_temp(device_file=device_file)
            return temp_c
    else:
        print(device_file)
        return 404.0 #404_1
            

def read_temp_from_device(device_file):
    if device_file=="" or device_file==None:
     return "Q"
    temp = read_temp(device_file) #2
    return temp

def get_combo_index(combo_list, target_value):
        for value_pair in combo_list:
            if value_pair[1] == target_value:
                return value_pair[0]
        return None  # Eğer hedef değer listede bulunmuyorsa None döner


def motor_control(stop_event,rest_event,shutdown_event):
    GPIO.setwarnings(False)  # Ignore warning for now
    GPIO.setmode(GPIO.BOARD)  # Use physical pin numbering
    GPIO.setup(38, GPIO.OUT, initial=GPIO.LOW)  # Set pin 38 to be an output pin and set initial value to low (off)
    GPIO.setup(40, GPIO.OUT, initial=GPIO.LOW)  # Set pin 40 to be an output pin and set initial value to low (off)
    

    while not stop_event.is_set():
         
        if shutdown_event.is_set():
         GPIO.output(38, GPIO.LOW)  # Set to low
         GPIO.output(40, GPIO.LOW)  # Set to low
         break
    
        GPIO.output(38, GPIO.LOW) # Turn on
        GPIO.output(40, GPIO.HIGH) # Turn on
        time.sleep(settings.DESIRED_ENGINE_SECONDS) # Sleep for 1 second
        GPIO.output(38, GPIO.HIGH) # Turn off
        GPIO.output(40, GPIO.LOW) # Turn off
        time.sleep(settings.DESIRED_ENGINE_SECONDS) # Sleep for 1 second
    
   

    GPIO.output(38, GPIO.HIGH) #BAŞLANGIC YADA SON ICIN BURASI CASLISIYOR
    GPIO.output(40, GPIO.HIGH)


# Veri güncelleme iş parçacığı
class DataUpdateThread(QtCore.QThread):
    data_updated = QtCore.pyqtSignal(str, str, str, str, str, str, str, str, str, str, str, str, str, str, str, str, str)
    finished = QtCore.pyqtSignal()

    def __init__(self, desired_temp, desired_seconds, desired_success_count):
        super().__init__()
        self.desired_seconds = settings.DESIRED_SECONDS
        self.desired_success_count = settings.DESIRED_SUCCESS_COUNT
        self.previous = []
        self.current = []
        self.isLegit = False
        self.desiredTemp = settings.DESIRED_TEMP
        self.counter=0


    def run(self):
        all_measurements = []
        
        attempt = 0

        
        # Motor kontrol iş parçacığını başlat
        self.stop_event = threading.Event()
        self.rest_event = threading.Event()
        self.shutdown_event=threading.Event()
        #self.motor_thread = threading.Thread(target=motor_control, args=(self.stop_event,self.rest_event,self.shutdown_event))
        #self.motor_thread.start()
        
        while self.counter < self.desired_success_count:
            olcum = []
            with concurrent.futures.ThreadPoolExecutor() as executor:
                olcum = list(executor.map(read_temp_from_device, device_files))  # 1
                a_temp1 = read_temp_from_device(at_1[0])
                a_temp2 = read_temp_from_device(at_2[0])


            for i in range(13 - len(olcum)):
                olcum.append(404.0) # 404 2
            if a_temp1 is None:
                print("a_temp1 is none")
            if a_temp2 is None:
                print("a_temp2 is none")
            olcum.append(a_temp1)
            olcum.append(a_temp2)

            attempt = attempt+1
            print(attempt, ". Denemedir")
            all_measurements.append(olcum)
            
            if self.counter == 0:
                if self.temperature_check(olcum, self.desiredTemp):
                    print("İlk başarılı işlem İstenilen sıcaklık sağlandı")
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
                        print(self.counter, ". BAŞARILI ADIM")

                        now = datetime.datetime.now()
                        tarih_zaman = now.strftime('%Y-%m-%d %H:%M:%S')
                        self.data_updated.emit(tarih_zaman, *map(str, olcum), str(self.counter))
                        print(f"{self.counter}. başarılı işlem. Tarih ve Zaman: {tarih_zaman}, Sıcaklık Değerleri: {', '.join(map(str, olcum))}°C")
                        time.sleep(settings.DESIRED_SECONDS)

                    else:
                        print("Hızlı sıcaklık değişimi")
                        print("Başarısız sıfırlandı")
                        print("Bir önceki adıma göre sıcaklık farkı çok yüksek")
                        print(f" Sıcaklık Değerleri: {', '.join(map(str, olcum))}°C")
                        self.counter = 0
                        time.sleep(settings.DESIRED_SECONDS)
                else:
                    print("Sistem ısıtılmalıdır. İstenilen sıcaklığa ulaşılmadı")
                    now = datetime.datetime.now()
                    tarih_zaman = now.strftime('%Y-%m-%d %H:%M:%S')
                    self.data_updated.emit(tarih_zaman, *map(str, olcum), "Eşik değer altında")
                    print(
                        f"Adım sayısı sıfırlandı, mevcut sayı: {self.counter}. Tarih ve Zaman: {tarih_zaman}, Sıcaklık Değerleri: {', '.join(map(str, olcum))}°C")
                    self.counter = 0
                    time.sleep(settings.DESIRED_SECONDS)
        
        print("Ölçüm tamamlandı")
        self.finished.emit()
        self.stop_event.set()
        self.rest_event.set()
        self.shutdown_event.set()
        self.motor_thread.join()  # Motor iş parçacığını durdur
        print(f"Program sonlandı. Ard arda {self.desired_success_count} başarılı işlem yapıldı.")

    def check_legit(self, temps):
        for temp in temps:
            if temp <= self.desiredTemp:
                return False
        return True
    
    def temperature_check(self, liste, desired_temp):
        for element in liste:
            if element is None:
                print("bos")

            if element!=404.0 and element < desired_temp: #404 3
                return False
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
        
        diff_list = []
        for i in range(len(last_one)):
            diff_list.append(last_one[i] - last_two[i])
        
        for element in diff_list:
            if abs(element) > settings.DESIRED_TEMP_DIFFERENCE: # fark sıcaklık
                return False
        return True


# Ana pencere sınıfı
class Main(QMainWindow):
    
    def __init__(self):

        super().__init__()
        self.ui = Ui_MainWindow() #Ana tasarımı miras al
        self.ui.setupUi(self)# Ana tasarımı yükle

        self.firm_operations=FirmOperations() #Firma operasyonları sınıfını miras al
        self.report_operations=ReportOperations()
        ##self.first_measurement() #ana ekran için ilk ölçüm
    
        self.desired_temp = settings.DESIRED_TEMP
        self.desired_seconds = settings.DESIRED_SECONDS
        self.desired_success_count = settings.DESIRED_SUCCESS_COUNT
        self.ui.btn_Start.clicked.connect(self.start_popup) # Starta basınca ölçüm yap
        self.ui.btn_RecipeOpe.clicked.connect(self.settings_popup) # Starta basınca ölçüm yap
        self.ui.btn_ShowReports.clicked.connect(self.report_operations.openReportScreen) #Reporlar Ekranı
        self.data_thread = None
    
    def start_fan(self):
        if self.data_thread is not None:
            self.data_thread.rest_event.clear()
            self.data_thread.stop_event.clear()

    def stop_fan(self):
        if self.data_thread is not None:
            self.data_thread.shutdown_event.set()
        
    def first_measurement(self):
        temps = []

        txt_probs = [self.ui.txt_prob_status, self.ui.txt_prob_status_2, self.ui.txt_prob_status_3, self.ui.txt_prob_status_4, self.ui.txt_prob_status_5, self.ui.txt_prob_status_6, 
                    self.ui.txt_prob_status_7, self.ui.txt_prob_status_8, self.ui.txt_prob_status_9, self.ui.txt_prob_status_10, self.ui.txt_prob_status_11, self.ui.txt_prob_status_12, 
                    self.ui.txt_prob_status_13, self.ui.txt_prob_status_14, self.ui.txt_prob_status_15]

        with concurrent.futures.ThreadPoolExecutor() as executor:
            temps = list(executor.map(read_temp_from_device, device_files))

        for i in range(len(temps)):
            txt_probs[i].setText(str(temps[i]))

        average_temp = sum(temps) / len(temps) if temps else 0.0
        self.ui.txt_area_temp_avarage.setText(str(average_temp)[:4])
        print("İlk ölçüm yapıldı")    
  
    def success_popup(self):
        reportNo=report_index()
        set_report_end_time(reportNo)
        popupMessage="İşlem tamamlandı. Raporlar bölümünden kontrol ediniz. Rapor No :"+str(reportNo)
        popup = QMessageBox()
        popup.setWindowTitle("İşlem Tamamlandı")
        popup.setText(popupMessage)
        popup.setIcon(QMessageBox.Information)
        self.ui.tableWidget.setRowCount(0)
        popup.setStandardButtons(QMessageBox.Ok)
        

        popup_result = popup.exec_()
        if popup_result == QMessageBox.Ok:
            popup.close()

    #Başlat buttonuna basilir. Gerekli bilgiler için popupacilir 06.08.2024
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


        self.ui_settings_dialog.btn_SettingsSave.clicked.connect(self.save_settings)
        self.popup.exec_()
        
    def save_settings(self):
        try:
            new_values = {
                'DESIRED_TEMP': int(self.ui_settings_dialog.line_Ekds.text()),
                'DESIRED_ENGINE_SECONDS': int(self.ui_settings_dialog.line_Fan_Left.text()),
                'DESIRED_ENGINE_SECONDS_RIGHT': int(self.ui_settings_dialog.line_Fan_Right.text()),
                'ENGINE_RESTING_SECONDS': int(self.ui_settings_dialog.line_Fan_Stop.text()),
                'RESISTANCE_MAX': int(self.ui_settings_dialog.line_Resistance_Max.text()),
                'RESISTANCE_MIN': int(self.ui_settings_dialog.line_Resistance_Min.text()),
            }

            # settings.py dosyasının bulunduğu dizini alın
            script_dir = os.path.dirname(os.path.abspath(__file__))
            settings_path = os.path.join(script_dir, 'settings.py')

            # settings.py dosyasını okuyun
            with open(settings_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            # Ayarları güncelle
            updated_lines = []
            for line in lines:
                stripped_line = line.strip()
                if not stripped_line or stripped_line.startswith('#'):
                    # Boş satır veya yorum satırı, olduğu gibi ekle
                    updated_lines.append(line)
                    continue

                # Satırda '=' işareti var mı kontrol edin
                if '=' in line:
                    # Değişken ismini alın
                    var_name = line.split('=')[0].strip()
                    if var_name in new_values:
                        # Yeni değeri satıra yazın, yorumları koruyun
                        # Satırı '#' işaretine göre bölün
                        parts = line.split('#', 1)
                        code_part = parts[0].strip()
                        comment_part = '#' + parts[1] if len(parts) > 1 else ''

                        new_value = new_values[var_name]
                        # Değerin tipine göre tırnak işareti kullanın
                        if isinstance(new_value, str):
                            new_line = f'{var_name} = "{new_value}" {comment_part}\n'
                        else:
                            new_line = f'{var_name} = {new_value} {comment_part}\n'

                        updated_lines.append(new_line)
                        continue  # Sonraki satıra geç

                # Değişiklik yoksa satırı olduğu gibi ekle
                updated_lines.append(line)

            # Güncellenmiş satırları dosyaya yazın
            with open(settings_path, 'w', encoding='utf-8') as f:
                f.writelines(updated_lines)

            # settings modülünü yeniden yükleyin
            importlib.reload(settings)
            QtWidgets.QMessageBox.information(self, "Başarılı", "Ayarlar kaydedildi.")
            self.popup.close()

        except ValueError:
            QtWidgets.QMessageBox.warning(self, "Hata", "Lütfen tüm alanlara geçerli bir sayı girin.")
            
    def popup_measurement(self):
            m3=self.ui_start_dialog.txt_amount.text()
            piece=self.ui_start_dialog.txt_pieces.text()
            type=self.ui_start_dialog.txt_type.text()
            info=self.ui_start_dialog.txtArea_info.toPlainText()

            now = datetime.datetime.now()
            start_time = now.strftime('%Y-%m-%d %H:%M:%S')
            self.ui.txt_time.setText(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            insert_report("1",start_time,"IP",type,m3,piece,info)
            self.start_measurement()
            self.popup.close()

    def start_measurement(self):
                self.data_thread = DataUpdateThread(self.desired_temp,settings.DESIRED_SECONDS, self.desired_success_count)
                self.data_thread.data_updated.connect(self.update_table_colored)
                self.data_thread.start()
                self.data_thread.running = True
                self.data_thread.finished.connect(self.success_popup)
            
    def filetoCrud(self, rf_id, tempsdb, ri_time, success_step):
            insert_report_step(rf_id, tempsdb[0], tempsdb[1], tempsdb[2], tempsdb[3], tempsdb[4], tempsdb[5], tempsdb[6], tempsdb[7], tempsdb[8], tempsdb[9], tempsdb[10], tempsdb[11], tempsdb[12], tempsdb[13], tempsdb[14], "0", "0", ri_time, success_step)

    def update_table_colored(self, tarih_zaman, *temps):
            rowPosition = self.ui.tableWidget.rowCount()
            self.ui.tableWidget.insertRow(rowPosition)

            tempsdb = []  # tempsdb'yi burada tanımlıyoruz

            for i, temp in enumerate(temps):
                # Eğer temp 404.0 ise, o sütundaki bir önceki değeri al
                if temp == "404.0" and rowPosition > 0:
                    previous_item = self.ui.tableWidget.item(rowPosition - 1, i)
                    if previous_item:
                        previous_value = previous_item.text()
                        item = QTableWidgetItem(previous_value)
                        tempsdb.append(previous_value)  # tempsdb'ye de önceki değeri ekle
                    else:
                        item = QTableWidgetItem(str(0.0))  # Eğer önceki satırda bir değer yoksa, 0.0 kullan
                        tempsdb.append("x")  # Eğer önceki değer yoksa, tempsdb'ye "x" ekle
                else:
                    item = QTableWidgetItem(str(temp))
                    tempsdb.append(temp)  # tempsdb'ye mevcut değeri ekle

                # Sıcaklık değeri settings.desired_temp'in altındaysa hücreyi kırmızı yap
                try:
                    if temp != "404.0" and float(temp) < settings.DESIRED_TEMP:
                        item.setBackground(QBrush(QColor(255, 0, 0)))  # Kırmızı arkaplan rengi
                except ValueError:
                    pass  # Sıcaklık değeri float'a dönüştürülemezse (örneğin "x" gibi), bu hücreyi atla

                self.ui.tableWidget.setItem(rowPosition, i, item)

            count = self.data_thread.desired_success_count - self.data_thread.counter
            self.ui.tableWidget.setItem(rowPosition, 15, QTableWidgetItem(str(count)))
            self.ui.tableWidget.setItem(rowPosition, 16, QTableWidgetItem(tarih_zaman))
            self.ui.tableWidget.scrollToBottom()
            reportindex = report_index()
            self.filetoCrud(str(reportindex), tempsdb, tarih_zaman, count)


if __name__ == "__main__":
    app = QApplication([])
    main_instance = Main()

    main_instance.show()
    app.exec_()
