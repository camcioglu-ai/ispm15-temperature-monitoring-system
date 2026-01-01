from datetime import datetime
import sys
import numpy as np
from PyQt5.QtWidgets import QApplication, QDialog, QVBoxLayout, QPushButton
import sqlite3
from PIL import Image as PILImage

from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.backends.backend_qt5agg import FigureCanvas 
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import os



class MatplotlibDialog(QDialog):
    def __init__(self):
        super(MatplotlibDialog, self).__init__()
        self.setWindowTitle("Grafik")
        self.setGeometry(100, 100, 1280, 720)

        layout = QVBoxLayout(self)

        self.canvas = FigureCanvas(Figure())
        layout.addWidget(self.canvas)

        self.toolbar = NavigationToolbar(self.canvas, self)
        layout.addWidget(self.toolbar)

    def convert_time(self, time_string):
        time_obj = datetime.strptime(time_string, "%Y-%m-%d %H:%M:%S")
        return time_obj.strftime("%H:%M:%S")    
    
    def update_graph(self, id):
        db_path = os.path.join(os.path.dirname(__file__), "mainDb.sqlite")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT T1,T2,T3,T4,T5,T6,T7,T8,T9,T10,T11,T12,T13,AT1,AT2,STEPTIME FROM REPORT_DETAILS WHERE REPORT_ID='+id)
        data = cursor.fetchall()
        conn.close()

        # Sütunları ayrı dizilere yerleştirin
        time_data = [self.convert_time(row[15]) for row in data]
        print(time_data)
        
        y_data = [list(row[:15]) for row in data]

        # Çizimi oluşturun
        axes = self.canvas.figure.add_subplot(111)
        axes.clear()

        for i in range(15):
            if i == 13 or i == 14:
                values_to_plot = [y[i] if y[i] != "404.0" else None for y in y_data]
                if any(val is not None for val in values_to_plot):
                    if i==13:
                     axes.plot(time_data, values_to_plot, marker='*', label=f'Ortam 1')
                    else:
                        axes.plot(time_data, values_to_plot, marker='*', label=f'Ortam 2')
            else:
                values_to_plot = [y[i] if y[i] != "404.0" else None for y in y_data]
                if any(val is not None for val in values_to_plot):
                    axes.plot(time_data, values_to_plot, marker='o', label=f'Prob{i + 1}')

        axes.set_title('Grafik Detayi')
        axes.set_xticklabels(time_data, rotation=45)
        axes.legend(loc='upper right', bbox_to_anchor=(1, 0.5))
        # Çizimi güncelleyin ve gösterin
        self.canvas.draw()
   

    def get_row_count_and_first_id(self,id):
        # SQLite veritabanına bağlanma
        db_path = os.path.join(os.path.dirname(__file__), "mainDb.sqlite")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # SQL sorgusunu çalıştırma
        cursor.execute('SELECT COUNT(ID), MIN(ID), MAX(ID) FROM REPORT_DETAILS WHERE REPORT_ID='+id+'')
        row = cursor.fetchone()

        # Satır sayısı, ilk ID ve son ID'yi alma
        row_count = row[0]
        first_id = row[1]
        last_id = row[2]

        # Bağlantıyı kapatma
        conn.close()
            
        return row_count, first_id, last_id


    def update_graph_minimiz(self, id):
        row_count, first_id, last_id = self.get_row_count_and_first_id(id)
    
        print("Satır Sayısı:", row_count)
        print("İlk ID:", first_id)
        print("Son ID:", last_id)

        # Parçaların adım sayısını hesapla
        num_sections = 10
        step_per_section = (last_id - first_id) / num_sections

        print("Her Bölümdeki Adım Sayısı:", step_per_section)

        # İlk ID'den başlayarak 11 adet ID elde etme
        ids = [int(first_id + step_per_section * i) for i in range(11)]

        ids_str = ','.join(map(str, ids))

        db_path = os.path.join(os.path.dirname(__file__), "mainDb.sqlite")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT T1,T2,T3,T4,T5,T6,T7,T8,T9,T10,T11,T12,T13,AT1,AT2,STEPTIME FROM REPORT_DETAILS WHERE REPORT_ID='+id+' AND ID IN ('+ids_str+');')
        data = cursor.fetchall()
        conn.close()

        # Sütunları ayrı dizilere yerleştirin
        time_data = [self.convert_time(row[15]) for row in data]
        print(time_data)
        
        y_data = [list(row[:15]) for row in data]

        # Çizimi oluşturun
        axes = self.canvas.figure.add_subplot(111)
        axes.clear()

        for i in range(15):
            # 404.0 değerini içermeyen verileri çiz
            values_to_plot = [y[i] if y[i] != 404.0 else None for y in y_data]
            if any(val is not None for val in values_to_plot):
                if i == 13:
                    axes.plot(time_data, values_to_plot, marker='*', label=f'Ortam 1')
                elif i == 14:
                    axes.plot(time_data, values_to_plot, marker='*', label=f'Ortam 2')
                else:
                    axes.plot(time_data, values_to_plot, marker='o', label=f'Prob{i + 1}')

        axes.set_title('Grafik Detayi')
        axes.set_xticklabels(time_data, rotation=45)
        axes.legend(loc='upper right', bbox_to_anchor=(1, 0.5))
        # Çizimi güncelleyin ve gösterin
        self.canvas.draw()


    def save_filtered_graph_png(self, id):
        # Veritabanından verileri çekin
        db_path = os.path.join(os.path.dirname(__file__), "mainDb.sqlite")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT T1,T2,T3,T4,T5,T6,T7,T8,T9,T10,T11,T12,T13,AT1,AT2,STEPTIME FROM REPORT_DETAILS WHERE REPORT_ID=' + id)
        data = cursor.fetchall()
        conn.close()

        # Sütunları ayrı dizilere yerleştirin
        time_data = [self.convert_time(row[15]) for row in data]
        y_data = [list(row[:15]) for row in data]

        # Çizimi oluşturun
        plt.figure(figsize=(16, 9))  # Grafiğin boyutunu ayarlayabilirsiniz

        for i in range(15):
            # 404.0 değerini içermeyen verileri çiz
            values_to_plot = [float(y[i]) if y[i] != 404.0 else None for y in y_data]
            if any(val is not None for val in values_to_plot):
                if i == 13:
                    plt.plot(time_data, values_to_plot, marker='*', label=f'Ortam 1')
                elif i == 14:
                    plt.plot(time_data, values_to_plot, marker='*', label=f'Ortam 2')
                else:
                    plt.plot(time_data, values_to_plot, marker='o', label=f'Prob{i + 1}')

        graphtitle = "Parti " + str(id) + " Grafik Detayi"
        plt.title(graphtitle)
        plt.xticks(rotation=45)
        plt.legend(loc='upper right', bbox_to_anchor=(1, 0.5))

        save_path = "filtered_graph_real.png"
        plt.savefig(save_path)

        img = PILImage.open(save_path)
        rotated_img = img.rotate(-90, expand=True)
        rotated_img.save(save_path)

        return save_path




if __name__ == "__main__":
    app = QApplication(sys.argv)
    dialog = MatplotlibDialog()
    dialog.exec_()
    sys.exit(app.exec_())


