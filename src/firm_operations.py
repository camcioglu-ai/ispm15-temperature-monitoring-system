# firm_operation.py
from PyQt5.QtWidgets import QTableWidgetItem
from PyQt5.QtWidgets import *
from Firm_Dialog import Ui_Firm_Dialog
from sql_operation import insert_firm, delete_firm, update_firm, get_firm

class FirmOperations:
    def __init__(self):
        #self.ui_firm_dialog = ui_firm_dialog
        self.ui_firm_dialog = Ui_Firm_Dialog()


    def openFirmScreen(self):
            self.popup = QDialog()
            self.ui_firm_dialog.setupUi(self.popup)
            self.load_data_to_table()
            self.ui_firm_dialog.Firm_tableWidget.cellClicked.connect(self.on_table_cell_clicked)
            self.ui_firm_dialog.btn_firm_delete.clicked.connect(self.delete_selected_row)
            self.ui_firm_dialog.btn_firm_add.clicked.connect(self.add_firm_screen)
            self.ui_firm_dialog.btn_firm_update.clicked.connect(self.update_selected_row)
            self.popup.exec_()


    def load_data_to_table(self):
        db_data = get_firm()
        self.ui_firm_dialog.Firm_tableWidget.setRowCount(len(db_data))
        for row, data in enumerate(db_data):
            for col, value in enumerate(data):
                item = QTableWidgetItem(str(value))
                self.ui_firm_dialog.Firm_tableWidget.setItem(row, col, item)

    def clear_firm_screen(self):
        self.ui_firm_dialog.lineEdit_firm_name.setText("")
        self.ui_firm_dialog.lineEdit_firm_city.setText("")
        self.ui_firm_dialog.lineEdit_firm_district.setText("")
        self.ui_firm_dialog.lineEdit_firm_address.setText("")
        self.ui_firm_dialog.lineEdit_firm_phone.setText("")
        self.ui_firm_dialog.lineEdit_firm_mail.setText("")

    def add_firm_screen(self):
        firm_name = self.ui_firm_dialog.lineEdit_firm_name.text()
        firm_city = self.ui_firm_dialog.lineEdit_firm_city.text()
        firm_district = self.ui_firm_dialog.lineEdit_firm_district.text()
        firm_address = self.ui_firm_dialog.lineEdit_firm_address.text()
        firm_phone = self.ui_firm_dialog.lineEdit_firm_phone.text()
        firm_mail = self.ui_firm_dialog.lineEdit_firm_mail.text()

        insert_firm(firm_name, firm_city, firm_district, firm_address, firm_phone, firm_mail)
        self.clear_firm_screen()
        self.load_data_to_table()

    def delete_selected_row(self):
        selected_row = self.ui_firm_dialog.Firm_tableWidget.currentRow()
        row_data = []
        if selected_row >= 0:
            column_count = self.ui_firm_dialog.Firm_tableWidget.columnCount()
            for col in range(column_count):
                cell_item = self.ui_firm_dialog.Firm_tableWidget.item(selected_row, col)
                if cell_item is not None:
                    cell_data = cell_item.text()
                    row_data.append(cell_data)

            self.ui_firm_dialog.Firm_tableWidget.removeRow(selected_row)
            print(row_data)

            delete_firm(row_data[0])  # Bu kısmı kontrol edin, silinecek verinin nasıl tanımlandığına göre düzenleyin
            self.clear_firm_screen()

    def update_selected_row(self):
        selected_row = self.ui_firm_dialog.Firm_tableWidget.currentRow()
        row_data = []
        if selected_row >= 0:
            column_count = self.ui_firm_dialog.Firm_tableWidget.columnCount()
            for col in range(column_count):
                cell_item = self.ui_firm_dialog.Firm_tableWidget.item(selected_row, col)
                if cell_item is not None:
                    cell_data = cell_item.text()
                    row_data.append(cell_data)

        firm_name = self.ui_firm_dialog.lineEdit_firm_name.text()
        firm_city = self.ui_firm_dialog.lineEdit_firm_city.text()
        firm_district = self.ui_firm_dialog.lineEdit_firm_district.text()
        firm_address = self.ui_firm_dialog.lineEdit_firm_address.text()
        firm_phone = self.ui_firm_dialog.lineEdit_firm_phone.text()
        firm_mail = self.ui_firm_dialog.lineEdit_firm_mail.text()

        update_firm(row_data[0], firm_name, firm_city, firm_district, firm_address, firm_phone, firm_mail)
        self.clear_firm_screen()
        self.load_data_to_table()

    def on_table_cell_clicked(self, row, col):
        self.selected_row = row
        self.selected_column = col

        cell_data = []
        for i in range(self.ui_firm_dialog.Firm_tableWidget.columnCount()):
            item = self.ui_firm_dialog.Firm_tableWidget.item(row, i)
            cell_data.append(item.text())

        self.ui_firm_dialog.lineEdit_firm_name.setText(cell_data[1])
        self.ui_firm_dialog.lineEdit_firm_city.setText(cell_data[4])
        self.ui_firm_dialog.lineEdit_firm_district.setText(cell_data[5])
        self.ui_firm_dialog.lineEdit_firm_address.setText(cell_data[6])
        self.ui_firm_dialog.lineEdit_firm_phone.setText(cell_data[2])
        self.ui_firm_dialog.lineEdit_firm_mail.setText(cell_data[3])
