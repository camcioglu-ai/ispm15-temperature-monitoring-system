import sqlite3

def get_row_count_and_first_id():
    # SQLite veritabanına bağlanma
    conn = sqlite3.connect("mainDb")
    cursor = conn.cursor()
    
    # SQL sorgusunu çalıştırma
    cursor.execute('SELECT COUNT(ID), MIN(ID), MAX(ID) FROM REPORT_DETAILS WHERE REPORT_ID=105')
    row = cursor.fetchone()
    
    # Satır sayısı, ilk ID ve son ID'yi alma
    row_count = row[0]
    first_id = row[1]
    last_id = row[2]
    
    # Bağlantıyı kapatma
    conn.close()
    
    return row_count, first_id, last_id

# Satır sayısını, ilk ID'yi ve son ID'yi alma
row_count, first_id, last_id = get_row_count_and_first_id()

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

print("ID'ler:", ids)

conn = sqlite3.connect("mainDb")
cursor = conn.cursor()
cursor.execute('SELECT T1,T2,T3,T4,T5,T6,T7,T8,T9,T10,T11,T12,T13,AT1,AT2,STEPTIME FROM REPORT_DETAILS WHERE REPORT_ID='+id+' AND ID IN ('+ids_str+');')
data = cursor.fetchall()
print(data)