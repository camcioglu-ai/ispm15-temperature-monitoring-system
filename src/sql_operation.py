import sqlite3
import os
#Firm
def getdata_firm():
    # Veritabanına bağlanın
    db_path = os.path.join(os.path.dirname(__file__), "mainDb.sqlite")
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()

    # Tüm verileri alın
    cursor.execute("SELECT * FROM Firm")
    data = cursor.fetchall()

    # Bağlantıyı kapatın
    connection.close()

    return data

def insert_firm(firm_name, city, district, neighborhood, street, building_name, building_no, building_info, web, phone, mail):
    # Veritabanına bağlanın
    db_path = os.path.join(os.path.dirname(__file__), "mainDb.sqlite")
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()

    # Verileri veritabanına ekleyin
    cursor.execute("INSERT INTO Firm (F_Name, F_City, F_District, F_Neighborhood, F_Street, F_Building_Name, F_Building_No, F_Building_Info, F_Web, F_Phone, F_Mail) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                   (firm_name, city, district, neighborhood, street, building_name, building_no, building_info, web, phone, mail))

    # Değişiklikleri kaydet ve bağlantıyı kapatın
    connection.commit()
    connection.close()
    print("islemt tamamlandi")

def get_firm():
    db_path = os.path.join(os.path.dirname(__file__), "mainDb.sqlite")
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()

    # "FIRM" tablosundan tüm verileri seçin
    cursor.execute('SELECT * FROM FIRM')
    data = cursor.fetchall()

    result = []
    for row in data:
        # Her satırı ilgili sütunlara ayırın
        index=row[0]
        firm_name = row[1]
        firm_phone = row[2]
        firm_mail = row[3]
        firm_city = row[4]
        firm_district = row[5]
        firm_address_detail = row[6]
        result.append((index,firm_name, firm_phone, firm_mail, firm_city, firm_district, firm_address_detail))
    
    connection.close()  # Bağlantıyı kapatmayı unutmayın
    return result

def delete_firm(index):
    try:
        # Veritabanına bağlanın
        db_path = os.path.join(os.path.dirname(__file__), "mainDb.sqlite")
        connection = sqlite3.connect(db_path)
        cursor = connection.cursor()

        # Verileri veritabanından silin
        cursor.execute("DELETE FROM FIRM WHERE ID=?",(index))

        print(cursor)
        connection.commit()
        print("Silme işlemi tamamlandı")
    except sqlite3.Error as e:
        print("Veritabanı hatası:", e)
    finally:
        # Bağlantıyı kapatın, hata olsa da olmasa da her zaman çalışır
        if connection:
            connection.close()

def update_firm(id, new_firm_name, new_firm_city, new_firm_district, new_firm_address, new_firm_phone, new_firm_mail):
    # Veritabanına bağlanın
    db_path = os.path.join(os.path.dirname(__file__), "mainDb.sqlite")
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()

    # Verileri güncelleyin
    cursor.execute("UPDATE FIRM SET FIRM_NAME=?, FIRM_CITY=?, FIRM_DISTRICT=?, FIRM_ADDRESS=?, FIRM_PHONE=?, FIRM_MAIL=? WHERE id=?",
                   (new_firm_name, new_firm_city, new_firm_district, new_firm_address, new_firm_phone, new_firm_mail, id))

    connection.commit()
    connection.close()
    print("Güncelleme işlemi tamamlandı")



#Report
#ölçtüğün adımı yaz
def insert_report_step(REPORT_ID,T1,T2,T3,T4,T5,T6,T7,T8,T9,T10,T11,T12,T13,AT1,AT2,AH1,AH2,STEPTIME,STEPNO):
    # Veritabanına bağlanın
    db_path = os.path.join(os.path.dirname(__file__), "mainDb.sqlite")
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()

    # Verileri veritabanına ekleyin
    cursor.execute("INSERT INTO Report_Details (REPORT_ID,T1,T2,T3,T4,T5,T6,T7,T8,T9,T10,T11,T12,T13,AT1,AT2,AH1,AH2,STEPTIME,STEPNO) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                   (REPORT_ID,T1,T2,T3,T4,T5,T6,T7,T8,T9,T10,T11,T12,T13,AT1,AT2,AH1,AH2,STEPTIME,STEPNO))

    connection.commit()
    connection.close()
    print("RaporAdimi eklemesi tamamlandi")
# Parti no ekle
def insert_report(id,firm_id,start_time,end_time,type,m3,pieces,report_info):
    # Veritabanına bağlanın
    db_path = os.path.join(os.path.dirname(__file__), "mainDb.sqlite")
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()

    # Verileri veritabanına ekleyin
    cursor.execute("INSERT INTO REPORT(ID,FIRM_ID,START_TIME,END_TIME,TYPE,M3,PIECES,REPORT_INFO) VALUES (?,?,?,?,?,?,?,?)",
                   (id,firm_id,start_time,end_time,type,m3,pieces,report_info))

    connection.commit()
    connection.close()
    print("Rapor eklemesi tamamlandi")

def get_temperature_data():
    try:
        # Veritabanına bağlanın
        db_path = os.path.join(os.path.dirname(__file__), "mainDb.sqlite")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Verileri çekin (örneğin, zaman ve sıcaklık sütunları varsa)
        cursor.execute('SELECT STEPNO, T1,T2,T3,T4,T5,T6,T7,T8,T9,T10,T11,T12,T13,AT1,AT2 FROM REPORT_DETAILS ') #limit 1
        data = cursor.fetchall()

        # Verileri düzenleyin ve listeye ekleyin
        x_data = []
        temperature_data = [[] for _ in range(15)]  # 15 sıcaklık ölçer için boş liste oluşturun

        for row in data:
            x_data.append(row[0])  # Adım sayısını
            for i in range(15):
                temperature_data[i].append((row[i + 1]))  # Sıcaklık ölçer verisi

        conn.close()
        return x_data, temperature_data
    except sqlite3.Error as e:
        print("Veritabanı hatası:", e)

def report_index():
    
    db_path = os.path.join(os.path.dirname(__file__), "mainDb.sqlite")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Verileri çekin (örneğin, zaman ve sıcaklık sütunları varsa)
    cursor.execute('SELECT ID FROM REPORT ORDER BY ID DESC LIMIT 1')
    data = cursor.fetchone()

    # Verileri düzenleyin ve listeye ekleyin
    
    if data:
        data=data[0]

        
    ss=str(data)
    conn.close()
    return ss

def get_index_fromtable(table_name):
    
    # Veritabanına bağlanın
    db_path = os.path.join(os.path.dirname(__file__), "mainDb.sqlite")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Verileri çekin (örneğin, zaman ve sıcaklık sütunları varsa)
    cursor.execute('SELECT ID FROM '+table_name+' ORDER BY ID DESC LIMIT 1')
    
    data = cursor.fetchone()

    # Verileri düzenleyin ve listeye ekleyin
    
    if data:
        data=data[0]
    

    ss=str(data)
    conn.close()
    return ss
            
def insert_firm(firm_name,firm_city,firm_district,firm_address_detail,firm_phone,firm_mail):
    # Veritabanına bağlanın
    db_path = os.path.join(os.path.dirname(__file__), "mainDb.sqlite")
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()

    # Verileri veritabanına ekleyin
    cursor.execute("INSERT INTO FIRM(FIRM_NAME,FIRM_PHONE,FIRM_MAIL,FIRM_CITY,FIRM_DISTRICT,FIRM_ADDRESS) VALUES (?,?,?,?,?,?)",
                   (firm_name,firm_phone,firm_mail,firm_city,firm_district,firm_address_detail))


    connection.commit()
    connection.close()
    print("Firma eklemesi tamamlandi")


#IP GETİRME
def get_report():
    db_path = os.path.join(os.path.dirname(__file__), "mainDb.sqlite")
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()

    cursor.execute('SELECT ID, START_TIME, END_TIME, TYPE, M3, PIECES, REPORT_INFO FROM REPORT WHERE END_TIME <> "IP"')
    data = cursor.fetchall()

    result = []
    for row in data:
        # Her satırı ilgili sütunlara ayırın
        index=row[0]
        start_time = row[1]
        end_time= row[2]
        type= row[3]
        m3= row[4]
        pieces= row[5]
        info= row[6]

        result.append((index, start_time, end_time, type, m3, pieces,info))
    
    connection.close()  # Bağlantıyı kapatmayı unutmayın
    return result

def get_parti(id):
    db_path = os.path.join(os.path.dirname(__file__), "mainDb.sqlite")
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()

    # "FIRM" tablosundan tüm verileri seçin
    cursor.execute('SELECT ID,START_TIME,END_TIME,TYPE,M3,PIECES,REPORT_INFO FROM REPORT WHERE id='+id)
    data = cursor.fetchall()

    result = []
    for row in data:
        # Her satırı ilgili sütunlara ayırın
        index=row[0]
        start_time = row[1]
        end_time= row[2]
        type= row[3]
        m3= row[4]
        pieces= row[5]
        info= row[6]

        result.append((index, start_time, end_time, type, m3, pieces,info))
    
    connection.close()  # Bağlantıyı kapatmayı unutmayın
    return result

def update_report(id, type, m3, pieces, report_info):
    # Veritabanına bağlanın
    db_path = os.path.join(os.path.dirname(__file__), "mainDb.sqlite")
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()

    # Verileri güncelleyin
    cursor.execute("UPDATE REPORT SET M3=?,TYPE=?, PIECES=?, REPORT_INFO=? WHERE id=?",( m3,type, pieces, report_info, id))

    connection.commit()
    connection.close()
    print("RAPOR DETAYLARI GÜNCELLENDİ")    

def set_report_end_time(rn):

    db_path = os.path.join(os.path.dirname(__file__), "mainDb.sqlite")
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()
    cursor.execute('Select STEPTIME from REPORT_DETAILS INNER JOIN REPORT ON REPORT.ID=REPORT_DETAILS.REPORT_ID WHERE REPORT_DETAILS.REPORT_ID='+rn+' AND REPORT_DETAILS.STEPNO=0')
    time = cursor.fetchone()
    print("**")
    print(time)
    print("**")
    strtime=str(time[0])
    cursor.execute("UPDATE REPORT SET END_TIME=? WHERE id=?",(strtime,rn))
    connection.commit()
    connection.close()
    print("Tarih Güncellendi")

def get_report_details(id):

    db_path = os.path.join(os.path.dirname(__file__), "mainDb.sqlite")
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()

    cursor.execute('SELECT T1,T2,T3,T4,T5,T6,T7,T8,T9,T10,T11,T12,T13,AT1,AT2,STEPNO,STEPTIME FROM REPORT_DETAILS WHERE REPORT_ID='+id)
    data = cursor.fetchall()

    result = []
    for row in data:
        # Her satırı ilgili sütunlara ayırın
        T1=row[0]
        T2=row[1]
        T3=row[2]
        T4=row[3]
        T5=row[4]
        T6=row[5]
        T7=row[6]
        T8=row[7]
        T9=row[8]
        T10=row[9]
        T11=row[10]
        T12=row[11]
        T13=row[12]
        AT1=row[13]
        AT2=row[14]
        STEPNO=row[15]
        STEPTIME=row[16]
        result.append((T1,T2,T3,T4,T5,T6,T7,T8,T9,T10,T11,T12,T13,AT1,AT2,STEPNO,STEPTIME))
    
    connection.close()  # Bağlantıyı kapatmayı unutmayın
    return result

def get_incomplete_reports():
    db_path = os.path.join(os.path.dirname(__file__), "mainDb.sqlite")
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()
    cursor.execute('SELECT ID FROM report WHERE end_time="IP"')
    reports = cursor.fetchall()
    connection.close()
    return [report[0] for report in reports]

def delete_report_steps(report_id):
    db_path = os.path.join(os.path.dirname(__file__), "mainDb.sqlite")
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()
    cursor.execute("DELETE FROM report_details WHERE REPORT_ID = ?", (report_id,))
    connection.commit()
    connection.close()

def delete_report(report_id):
    db_path = os.path.join(os.path.dirname(__file__), "mainDb.sqlite")
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()
    cursor.execute("DELETE FROM report WHERE ID = ?", (report_id,))
    connection.commit()
    connection.close()

def reset_autoincrement(table_name):
    db_path = os.path.join(os.path.dirname(__file__), "mainDb.sqlite")
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()
    # Tablodaki mevcut en yüksek report_id değerini alın
    cursor.execute(f"SELECT MAX(ID) FROM {table_name}")
    max_id = cursor.fetchone()[0]
    if max_id is None:
        max_id = 0  # Eğer tablo boşsa, sıfıra ayarlayın
        # sqlite_sequence tablosundaki girdiyi silin
        cursor.execute("DELETE FROM sqlite_sequence WHERE name = ?", (table_name,))
    else:
        # sqlite_sequence tablosunu güncelleyin
        cursor.execute("UPDATE sqlite_sequence SET seq = ? WHERE name = ?", (max_id, table_name))
    connection.commit()
    connection.close()