

'''
Created on 15 de mar de 2018

@author: Vitor Soares
'''

import os
import sys
import sqlite3
import threading
import traceback
import numpy as np
from PyQt5 import QtWidgets, QtCore
from horarios_ui import Ui_Horarios

class ApplicationWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(ApplicationWindow, self).__init__()

        self.ui = Ui_Horarios()
        self.ui.setupUi(self)
        
#         os.chdir('/home/vps/Documentos/Horarios/Programa')
        #cria db se necessario
        self.create_tables()
        
        #carrega data da compensacão
        self.get_compensation()
        
        self.flag_entry_exists = False
        #carrega data atual
        self.calendar_update()

        self.signals()
        
        #caso costume almoçar no cnpem, descomente esta linha:
        #self.ui.checkBox.setChecked(True)
        
        
    def signals(self):
        self.ui.pb_calculate.clicked.connect(self.calculations)
        self.ui.pb_save.clicked.connect(self.db_save)
        self.ui.pb_configure.clicked.connect(self.db_save_compensation)
        self.ui.pb_update.clicked.connect(self.calendar_update)
        self.ui.pb_clear.clicked.connect(self.clear)
        self.ui.pb_load.clicked.connect(self.load)
        self.ui.calendarWidget.selectionChanged.connect(self.db_load_entry)

    def calendar_update(self):
        self.d0 = self.ui.de_begin.date()
        self.d = QtCore.QDate.currentDate()
        self.df = self.ui.de_end.date()
        self.ui.calendarWidget.setSelectedDate(self.d)
        self.db_load_entry()

    def create_tables(self):
        _con = sqlite3.connect('horarios.db')
        _cur = _con.cursor()
        _cur.execute("""SELECT name FROM sqlite_master WHERE type='table' AND name='horarios';""")
        if not len(_cur.fetchall()):
            _create_table = """CREATE TABLE `compensacao` (
                               `inicio`    TEXT NOT NULL,
                               `fim`    TEXT NOT NULL);"""
            _cur.execute(_create_table)

            self.d0 = self.ui.de_begin.date()
            self.df = self.ui.de_end.date()
            _db_values = [self.d0.toString('dd/MM/yyyy'), self.df.toString('dd/MM/yyyy')]
            _cur.execute("INSERT INTO compensacao VALUES (?, ?)", _db_values)
            _con.commit()

            _create_table = """CREATE TABLE `horarios` (
                               `Id`    INTEGER,
                               `Data`    TEXT NOT NULL UNIQUE,
                               `Entrada1`    TEXT NOT NULL,
                               `Saida1`    TEXT NOT NULL,
                               `Entrada2`    TEXT,
                               `Saida2`    TEXT,
                               `Entrada3`    TEXT,
                               `Saida3`    TEXT,
                               `Hora Extra`    TEXT NOT NULL,
                               `Ausencia`    TEXT NOT NULL,
                               `Comentario`    TEXT,
                               `Almoco`    INTEGER NOT NULL,
                               `Compensacao`    INTEGER NOT NULL,
                               PRIMARY KEY(`Id`));"""
            _cur.execute(_create_table)
        _con.close()

    def clear(self):
        _tw = self.ui.tableWidget
        _ncells = _tw.rowCount()
        for i in range(_ncells):
            self.set_table_item(_tw, i, 0, None)
        self.ui.checkBox.setChecked(False)

    def get_compensation(self):
        _con = sqlite3.connect('horarios.db')
        _cur = _con.cursor()
        _cur.execute('SELECT * FROM compensacao')
        _ans = _cur.fetchall()
        _con.close()

        _d_begin = _ans[0][0].split('/')
        self.d0 = QtCore.QDate(int(_d_begin[2]),int(_d_begin[1]),int(_d_begin[0]))
        self.ui.de_begin.setDate(self.d0)

        _d_end = _ans[0][1].split('/')
        self.df = QtCore.QDate(int(_d_end[2]),int(_d_end[1]),int(_d_end[0]))
        self.ui.de_end.setDate(self.df)

    def calculations(self):
        #implementar falta, feriados, ferias, atestado, sábado
        #checar se 0<=hora<=23 e se 0<=min<=59
        _tw = self.ui.tableWidget
        _ncells = _tw.rowCount()
        _hor_array = np.array([])
        _min_array = np.array([])
        self.d0 = self.ui.de_begin.date()
        self.d = self.ui.calendarWidget.selectedDate()
        self.df = self.ui.de_end.date()
        _compensation = self.d0 <= self.d <= self.df

        for i in range(6):
            _tw.setCurrentCell(i,0)
            if _tw.currentItem() == None:
                _hor_array = np.append(_hor_array, None)
                _min_array = np.append(_min_array, None)
            else:
                _item = _tw.currentItem().text()
                if _item == '' or _item == ' ':
                    _hor_array = np.append(_hor_array, None)
                    _min_array = np.append(_min_array, None)
                else:
                    _hor_array = np.append(_hor_array, _item)
                    try:
                        _item = _item.split(':')
                        _item = [int(_item[0]), int(_item[1])]
                        if 0 <= _item[0] <= 23 and 0 <= _item[1] <= 59:
                            _min_array = np.append(_min_array, _item[0]*60 +_item[1])
                        else:
                            raise ValueError
                    except:
                        QtWidgets.QMessageBox.warning(self, 'Aviso', "Campos devem estar no formato 'hh:mm'.", QtWidgets.QMessageBox.Ok)
                        return

        try:
            _min_sum = 0
            for i in range(3):
                if _min_array[2*i] != None:
                    if _min_array[2*i+1] < _min_array[2*i]:
                        QtWidgets.QMessageBox.warning(self, 'Aviso', "Hora de saída não pode ser antes da entrada.", QtWidgets.QMessageBox.Ok)
                        return
                    _min_sum = _min_sum + _min_array[2*i+1] - _min_array[2*i]
        except:
            traceback.print_exc(file=sys.stdout)
            QtWidgets.QMessageBox.warning(self, 'Aviso', "Confira se hora de entrada e saída estão anotadas.", QtWidgets.QMessageBox.Ok)
            return

        _min_day = 8*60
        if self.ui.checkBox.isChecked():
            _min_day = _min_day + 60
        if _compensation:
            _min_day = _min_day + 10
        if self.d.dayOfWeek() == 6:
            #sabados só faz hora extra
            _min_day = 0

        try:
            _tw.setCurrentCell(8, 0)
            _comment = _tw.currentItem().text().lower()
            if _comment == 'atestado':
                _min_sum = _min_day
            elif _comment == 'falta':
                _min_sum = 0
            elif _comment == 'feriado' or _comment == 'ferias' or _comment == 'férias':
                _min_sum = _min_day
        except:
            pass

        _min_sum = _min_sum - _min_day

        if -10 <= _min_sum <= 10:
            _min_sum = 0
            self.set_table_item(_tw, 6, 0, '00:00')
            self.set_table_item(_tw, 7, 0, '00:00')
        elif _min_sum < 0:
            _hor = np.divmod(int(-_min_sum),60)
            self.set_table_item(_tw, 6, 0, '00:00')
            self.set_table_item(_tw, 7, 0, ('{0:02}:{1:02}'.format(_hor[0],_hor[1])))
        elif _min_sum > 0:
            _hor = np.divmod(int(_min_sum),60)
            self.set_table_item(_tw, 6, 0, ('{0:02}:{1:02}'.format(_hor[0],_hor[1])))
            self.set_table_item(_tw, 7, 0, '00:00')

    def set_table_item(self,table,row,col,val):
        _item = QtWidgets.QTableWidgetItem()
        _item.setText(val)
        table.setItem(row, col, _item)

    def db_save(self):
        self.calculations()

        _db_values = [None]
        _db_values.append(self.d.toString('dd/MM/yyyy'))
        _tw = self.ui.tableWidget
        _ncells = _tw.rowCount()
        for i in range(_ncells):
            _tw.setCurrentCell(i,0)
            if _tw.currentItem() == None:
                _db_values.append(None)
            else:
                _item = _tw.currentItem().text()
                if _item == '' or _item == ' ':
                    _db_values.append(None)
                else:
                    _db_values.append(_item)
        _lunch = int(self.ui.checkBox.isChecked())
        _compensation = int(self.d0<=self.d<=self.df)
        _db_values.append(_lunch)
        _db_values.append(_compensation)

        #checa se existe data na db e cria/altera conforme necessidade
        if self.flag_entry_exists:
            _ans = self.db_update_entry(_db_values)
        else:
            _ans = self.db_save_entry(_db_values)
        if _ans:
            QtWidgets.QMessageBox.information(self, 'Aviso', "Horário salvo no banco de dados.", QtWidgets.QMessageBox.Ok)
        else:
            QtWidgets.QMessageBox.warning(self, 'Aviso', "Não foi possível acessar o banco de dados.", QtWidgets.QMessageBox.Ok)

    def db_save_compensation(self):
        self.d0 = self.ui.de_begin.date()
        self.df = self.ui.de_end.date()

        _con = sqlite3.connect('horarios.db')
        _cur = _con.cursor()
        _db_values = [self.d0.toString('dd/MM/yyyy'), self.df.toString('dd/MM/yyyy')]
        _cur.execute("UPDATE compensacao SET inicio = ?, fim = ? WHERE _rowid_ = 1", _db_values)
        _con.commit()
        _con.close()

    def db_save_entry(self, db_values):
        try:
            _con = sqlite3.connect('horarios.db')
            _cur = _con.cursor()
            _cur.execute("INSERT INTO horarios VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)", db_values)
            _con.commit()
            _con.close()
            self.flag_entry_exists = True
            return True
        except:
            _con.close()
            traceback.print_exc(file=sys.stdout)
            return False

    def db_load_entry(self):
        _tw = self.ui.tableWidget
        _ncells = _tw.rowCount()

        self.d = self.ui.calendarWidget.selectedDate()
        _date = [self.d.toString('dd/MM/yyyy'), ]

        _con = sqlite3.connect('horarios.db')
        _cur = _con.cursor()
        _cur.execute("SELECT * FROM horarios WHERE data = ?", _date)
        try:
            _entry = _cur.fetchall()[0]
        except:
            #in case there's no entry yet:
            _con.close()
            self.clear()
            self.flag_entry_exists = False
            return
        self.flag_entry_exists = True
        _con.close()
        
        for i in range(_ncells):
            self.set_table_item(_tw, i, 0, _entry[i+2])
            
        self.ui.checkBox.setChecked(_entry[_ncells+2])

    def db_update_entry(self, db_values):
        try:
            _date = db_values[1]
            _db_values = db_values[2:]
            _db_values.append(_date)
            
            _con = sqlite3.connect('horarios.db')
            _cur = _con.cursor()
            _cur.execute("UPDATE horarios SET entrada1 = ?, saida1 = ?,\
                          entrada2 = ?, saida2 = ?, entrada3 = ?, saida3 = ?,\
                          `hora extra` = ?, ausencia = ?, comentario = ?,\
                          almoco = ?, compensacao = ? WHERE data = ?", _db_values)
            _con.commit()
            _con.close()

            return True
        except:
            _con.close()
            traceback.print_exc(file=sys.stdout)
            return False

    def load(self):
        #carrega e exibe horarios em intervalo de datas, soma h.e. e ausencias
        _d0 = self.ui.de_from.date()
        _df = self.ui.de_to.date()

        if _df < _d0:
            QtWidgets.QMessageBox.warning(self, 'Aviso', "Data final não pode ser antes da data inicial.", QtWidgets.QMessageBox.Ok)
            return

        _tw = self.ui.tableWidget_2
        _tw.setRowCount(0)
        _row_count = 0

        _he = 0
        _ab = 0

        while _d0 <= _df:
            #tenta carregar data:
            _flag_loaded = False
            _date = [_d0.toString('dd/MM/yyyy'), ]
    
            _con = sqlite3.connect('horarios.db')
            _cur = _con.cursor()
            _cur.execute("SELECT * FROM horarios WHERE data = ?", _date)
            try:
                _entry = _cur.fetchall()[0]
                _flag_loaded = True
            except:
                _flag_loaded = False
            _con.close()    
            #se carregou data, exibe e soma extrato de horas
            if _flag_loaded:
                _row_count = _row_count + 1
                _tw.setRowCount(_row_count)
                _header = QtWidgets.QTableWidgetItem(_entry[1])
                _tw.setVerticalHeaderItem(_row_count-1, _header)
                for i in range(2,13):
                    if _entry[i] != None:
                        self.set_table_item(_tw, _row_count-1, i-2, str(_entry[i]))
                    else:
                        self.set_table_item(_tw, _row_count-1, i-2, '--')
                _aux = _entry[8].split(':')
                _he = _he + int(_aux[0])*60 + int(_aux[1])
                _aux = _entry[9].split(':')
                _ab = _ab + int(_aux[0])*60 + int(_aux[1])
            _d0 = _d0.addDays(1)

        #exibe extrato de horas
        _aux = np.divmod(_he, 60)
        self.ui.le_he.setText('{0:02}:{1:02}'.format(_aux[0],_aux[1]))
        _aux = np.divmod(_ab, 60)
        self.ui.le_absent.setText('{0:02}:{1:02}'.format(_aux[0],_aux[1]))        
        _sum = _he - _ab
        if _sum >= 0:
            _aux = np.divmod(_sum, 60)
            self.ui.le_positive.setText('{0:02}:{1:02}'.format(_aux[0],_aux[1]))
            self.ui.le_negative.setText('00:00')
        else:
            _aux = np.divmod(-_sum, 60)
            self.ui.le_negative.setText('{0:02}:{1:02}'.format(_aux[0],_aux[1]))
            self.ui.le_positive.setText('00:00')

class main(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.start()

    def run(self):
        self.app = QtWidgets.QApplication(sys.argv)
        self.myapp = ApplicationWindow()
        self.myapp.show()
        sys.exit(self.app.exec_())

if __name__ == '__main__':
    print(__name__ + ' ok' )
    App = main()
else:
    print(__name__ + ' fail' )
