import sys
from PyQt5.QtWidgets import *
from PyQt5 import QtCore
from PyQt5.uic import loadUi
import os.path
from pathlib import Path
import sqlite3
from sqlite3 import Error
from PyQt5.QtCore import QDate, QTime, QDateTime, Qt, QTimer

class Login(QDialog):
    def __init__(self):
        super(Login,self).__init__()
        loadUi('ui\login.ui',self)

        self.btnLogin.clicked.connect(self.login_buttonclicked)

    def login_buttonclicked(self):
        if self.txtUsername.text() == "admin" and self.txtPassword.text() == "password":
            self.index = Index()
            self.index.showMaximized()
            self.close()

        else:
            QMessageBox.about(self,"Error","Incorrect username or password.")
            self.txtUsername.setText("")
            self.txtPassword.setText("")
            self.txtUsername.setFocus()


class Index(QMainWindow):

    c = sqlite3.connect('System.sqlite')

    def __init__(self):
        super(Index,self).__init__()
        loadUi('ui\index.ui', self)

        self.showEmployee.triggered.connect(self.show_Employee)
        self.showJob.triggered.connect(self.show_Job)
        self.actionExit.triggered.connect(self.exit_App)
        self.showDeduction.triggered.connect(self.show_Deduction)
        self.btnTime.clicked.connect(self.showTimeForm)
        self.btnPayroll.clicked.connect(self.showPayroll)
        self.showAttendance.triggered.connect(self.show_Attendance)
        self.showReport.triggered.connect(self.show_Report)

        activity = QTimer(self)
        activity.timeout.connect(self.showActivity)
        activity.start(100)

        date = QDate.currentDate()
        self.lblDate.setText(date.toString(Qt.DefaultLocaleLongDate))

        timer = QTimer(self)
        timer.timeout.connect(self.showTime)
        timer.start(1000)
        time = QTime.currentTime()
        self.lblTime.setText(time.toString(Qt.DefaultLocaleLongDate))

        update = QTimer(self)
        update.timeout.connect(self.statusEmployee)
        update.start(100)

        DB = Path('System.sqlite')
        if not DB.is_file():

            try:
                conn = sqlite3.connect('System.sqlite')
                cur = conn.cursor()

                cur.executescript('''
                CREATE TABLE Job(
                JobCode VARCHAR(10) NOT NULL,
                JobName VARCHAR(100) NOT NULL,
                Rate FLOAT(50) NOT NULL,
                PRIMARY KEY (JobCode)
                );

                CREATE TABLE Employee(
                EmployeeCode VARCHAR(10) NOT NULL,
                LastName VARCHAR(100) NOT NULL,
                FirstName VARCHAR(100) NOT NULL,
                MiddleName VARCHAR(100),
                Email VARCHAR(100) NOT NULL,
                ContactNo VARCHAR(100) NOT NULL,
                Job VARCHAR(100) NOT NULL,
                PRIMARY KEY (EmployeeCode)
                FOREIGN KEY (Job) REFERENCES Job(JobName)
                );

                CREATE TABLE Attendance(
                AttenID INTEGER PRIMARY KEY,
                EmployeeCode VARCHAR(10) NOT NULL,
                AttenDate VARCHAR(50) NOT NULL,
                TimeIn VARCHAR(50) NOT NULL,
                TimeOut VARCHAR(50) NOT NULL,
                FOREIGN KEY (EmployeeCode) REFERENCES Employee(EmployeeCode)
                );

                CREATE TABLE Activity(
                ActID INTEGER PRIMARY KEY,
                EmployeeCode VARCHAR(10) NOT NULL,
                ActDate VARCHAR(50) NOT NULL,
                ActTime VARCHAR(50) NOT NULL,
                Status VARCHAR(50) NOT NULL,
                FOREIGN KEY (EmployeeCode) REFERENCES Employee(EmployeeCode)
                );

                CREATE TABLE Deductions(
                DeductionID VARCHAR(10) PRIMARY KEY,
                DeductionName VARCHAR(100) NOT NULL,
                DeductionFee FLOAT NOT NULL
                );

                CREATE TABLE Payroll(
                PayrollID INTEGER PRIMARY KEY,
                PayDate VARCHAR(50) NOT NULL,
                EmployeeCode VARCHAR(10) NOT NULL,
                Payment FLOAT(50) NOT NULL,
                FOREIGN KEY (EmployeeCode) REFERENCES Employee(EmployeeCode)
                );
                ''')

                conn.commit()
                conn.close()
            except Error as e:
                QMessageBox.about(self,"Error",str(e))
    def showTimeForm(self):
        form = TimeForm()
        form.exec()

    def showPayroll(self):
        payroll = Payroll()
        payroll.exec()


    def statusEmployee(self):
        totalJob=0
        totalEmp=0
        cur=self.c.cursor()
        empRows = cur.execute("Select * From Employee")
        for row in empRows:
            totalEmp+=1
        self.lblTotal.setText(str(totalEmp))
        jobRows = cur.execute("Select * From Job")
        for row in jobRows:
            totalJob+=1
        self.lblTotalJobs.setText(str(totalJob))

    def showActivity(self):
        try:
            cur=self.c.cursor()
            self.tableActivity.clear()
            rows = cur.execute('SELECT ActDate,ActTime,Status,Employee.LastName,Employee.FirstName,Employee.MiddleName,Employee.Job FROM Activity Inner Join Employee On Activity.EmployeeCode  = Employee.EmployeeCode ORDER BY ActID DESC')
            self.tableActivity.setHorizontalHeaderLabels(["Date", "Time","Status","Last Name","First Name","Middle Name","Job"])
            self.tableActivity.setRowCount(0)
            for row,row_data in enumerate(rows):
                self.tableActivity.insertRow(row)
                for column,column_data in enumerate(row_data):
                    self.tableActivity.setItem(row, column, QTableWidgetItem(column_data))

        except Error as e:
            QMessagebox.about(self,"Error",str(e))

    def showTime(self):
        time = QTime.currentTime()
        self.lblTime.setText(time.toString(Qt.DefaultLocaleLongDate))
        date = QDate.currentDate()
        self.lblDate.setText(date.toString(Qt.DefaultLocaleLongDate))

    def show_Employee(self):
        employee=Employee()
        employee.exec()

    def show_Job(self):
        job=Job()
        job.exec()

    def show_Deduction(self):
        deduction = Deduction()
        deduction.exec()

    def show_Attendance(self):
        attendance = DailyAttendance()
        attendance.exec()

    def show_Report(self):
        report = MonthlyReport()
        report.exec()

    def exit_App(self):
        self.close()

class Employee(QDialog):

    c = sqlite3.connect('System.sqlite')

    def __init__(self):
        super(Employee,self).__init__()
        loadUi('ui\employee.ui',self)

        self.btnAdd.clicked.connect(self.on_AddButton_clicked)
        self.btnClear.clicked.connect(self.on_ClearButton_clicked)
        self.btnEdit.clicked.connect(self.on_EditButton_clicked)
        self.btnDelete.clicked.connect(self.on_DeleteButton_clicked)
        self.tableEmployee.clicked.connect(self.tableEmployeeItem_changed)

        self.updateEmployeeList()

        cur = self.c.cursor()
        rows = cur.execute("Select * From Job")
        for row in rows:
            self.cboJob.addItem(row[1])


    def updateEmployeeList(self):
        cur = self.c.cursor()
        self.tableEmployee.clear()
        rows = cur.execute("Select * From Employee")
        self.tableEmployee.setHorizontalHeaderLabels(["Code", "Last Name","First Name","Middle Name","Email","Contact No,","Job"])
        self.tableEmployee.setRowCount(0)
        for row,row_data in enumerate(rows):
            self.tableEmployee.insertRow(row)
            for column,column_data in enumerate(row_data):
                self.tableEmployee.setItem(row, column, QTableWidgetItem(column_data))

    def tableEmployeeItem_changed(self):
        cur = self.c.cursor()
        row = self.tableEmployee.currentRow()
        if row > -1:
            code = self.tableEmployee.item(row,0).text()
            rows = cur.execute('Select * From Employee Where EmployeeCode = ?', (code,))
            row = rows.fetchone()
            self.txtEmpCode.setText(str(row[0]))
            self.txtLName.setText(str(row[1]))
            self.txtFName.setText(str(row[2]))
            self.txtMName.setText(str(row[3]))
            self.txtEmail.setText(str(row[4]))
            self.txtNumber.setText(str(row[5]))
            self.cboJob.setCurrentText(str(row[6]))

    def on_ClearButton_clicked(self):
        self.txtEmpCode.clear()
        self.txtLName.clear()
        self.txtFName.clear()
        self.txtMName.clear()
        self.txtEmail.clear()
        self.txtNumber.clear()
        self.tableEmployee.clearSelection()
        self.txtEmpCode.setFocus()

    def on_AddButton_clicked(self):
        try:
            cur = self.c.cursor()
            code = self.txtEmpCode.text()
            lname = self.txtLName.text()
            fname = self.txtFName.text()
            mname = self.txtMName.text()
            email = self.txtEmail.text()
            contactno = self.txtNumber.text()
            job = self.cboJob.currentText()
            cur.execute('INSERT INTO Employee (EmployeeCode,LastName,FirstName,MiddleName,Email,ContactNo,Job) VALUES (?,?,?,?,?,?,?)', (code,lname,fname,mname,email,contactno,job))
            self.c.commit()
            self.on_ClearButton_clicked()
            self.updateEmployeeList()
        except Error as e:
            QMessagebox.about(self,"Error",str(e))

    def on_EditButton_clicked(self):
        try:
            reply = QMessageBox.question(self, "Edit", "Do you want to edit this record?", QMessageBox.Yes, QMessageBox.No)

            if reply == QMessageBox.Yes:
                cur = self.c.cursor()
                code = self.txtEmpCode.text()
                lname = self.txtLName.text()
                fname = self.txtFName.text()
                mname = self.txtMName.text()
                email = self.txtEmail.text()
                contactno = self.txtNumber.text()
                job = self.cboJob.currentText()

                cur.execute('UPDATE Employee SET LastName = ?, FirstName = ?,MiddleName = ?,Email = ?,ContactNo = ?,Job = ? WHERE EmployeeCode = ?', (lname,fname,mname,email,contactno,job,code))
                self.c.commit()
                self.on_ClearButton_clicked()
                self.updateEmployeeList()
        except Error as e:
            QMessageBox.about(self,"Error",str(e))
    def on_DeleteButton_clicked(self):
        try:

            #Display question dialog box to confirm if user really want to delete record
            reply = QMessageBox.question(self, "Delete", "Do you want to delete this record?", QMessageBox.Yes, QMessageBox.No)

            if reply == QMessageBox.Yes:
                cur = self.c.cursor()
                code = self.txtEmpCode.text()

                cur.execute('DELETE FROM Employee WHERE EmployeeCode = ?', (code,))
                self.c.commit()
                self.updateEmployeeList()


        except Error as e:
            QMessageBox.about(self,"Error",str(e))

class Job(QDialog):
    c = sqlite3.connect('System.sqlite')

    def __init__(self):
        super(Job,self).__init__()
        loadUi('ui\job.ui',self)

        self.btnAdd.clicked.connect(self.on_AddButton_clicked)
        self.btnClear.clicked.connect(self.on_ClearButton_clicked)
        self.btnEdit.clicked.connect(self.on_EditButton_clicked)
        self.btnDelete.clicked.connect(self.on_DeleteButton_clicked)
        self.tableJob.clicked.connect(self.tableJobItem_changed)
        self.updateJobList()

    def updateJobList(self):
        cur = self.c.cursor()
        self.tableJob.clear()
        rows = cur.execute("Select * From Job")
        self.tableJob.setHorizontalHeaderLabels(["Code", "Job Name","Rate"])
        self.tableJob.setRowCount(0)
        for row,row_data in enumerate(rows):
            self.tableJob.insertRow(row)
            for column,column_data in enumerate(row_data):
                self.tableJob.setItem(row, column, QTableWidgetItem(str(column_data)))

    def on_ClearButton_clicked(self):
        self.txtJobCode.clear()
        self.txtJName.clear()
        self.txtRate.clear()
        self.txtJobCode.setFocus()

    def on_AddButton_clicked(self):
        try:
            cur = self.c.cursor()
            code = self.txtJobCode.text()
            jname = self.txtJName.text()
            rate = self.txtRate.text()
            cur.execute('INSERT INTO Job (JobCode,JobName,Rate) VALUES (?,?,?)', (code,jname,float(rate),))
            self.c.commit()
            self.on_ClearButton_clicked()
            self.updateJobList()
        except Error as e:
            QMessagebox.about(self,"Error",str(e))

    def on_EditButton_clicked(self):
        try:
            reply = QMessageBox.question(self, "Edit", "Do you want to edit this record?", QMessageBox.Yes, QMessageBox.No)

            if reply == QMessageBox.Yes:
                cur = self.c.cursor()
                code = self.txtJobCode.text()
                jname = self.txtJName.text()
                rate = self.txtRate.text()

                cur.execute('UPDATE Job SET JobName = ?, Rate = ? WHERE JobCode = ?', (jname,rate,code,))
                self.c.commit()
                self.on_ClearButton_clicked()
                self.updateJobList()
        except Error as e:
            QMessageBox.about(self,"Error",str(e))

    def on_DeleteButton_clicked(self):
        try:
            reply = QMessageBox.question(self, "Delete", "Do you want to delete this record?", QMessageBox.Yes, QMessageBox.No)

            if reply == QMessageBox.Yes:
                cur = self.c.cursor()
                code = self.txtJobCode.text()

                cur.execute('DELETE FROM Job WHERE JobCode = ?', (code,))
                self.c.commit()
                self.updateJobList()


        except Error as e:
            QMessageBox.about(self,"Error",str(e))

    def tableJobItem_changed(self):
        cur = self.c.cursor()
        row = self.tableJob.currentRow()
        if row > -1:
            code = self.tableJob.item(row,0).text()
            rows = cur.execute('Select * From Job Where JobCode = ?', (code,))
            row = rows.fetchone()
            self.txtJobCode.setText(str(row[0]))
            self.txtJName.setText(str(row[1]))
            self.txtRate.setText(str(row[2]))

class Deduction(QDialog):
    c = sqlite3.connect('System.sqlite')

    def __init__(self):
        super(Deduction,self).__init__()
        loadUi('ui\deduction.ui',self)

        self.btnAdd.clicked.connect(self.on_AddButton_clicked)
        self.btnClear.clicked.connect(self.on_ClearButton_clicked)
        self.btnEdit.clicked.connect(self.on_EditButton_clicked)
        self.btnDelete.clicked.connect(self.on_DeleteButton_clicked)
        self.tableDeduction.clicked.connect(self.tableDeductionItem_changed)
        self.updateDeductionList()

    def updateDeductionList(self):
        cur = self.c.cursor()
        self.tableDeduction.clear()
        rows = cur.execute("Select * From Deductions")
        self.tableDeduction.setHorizontalHeaderLabels(["ID","Deduction", "Fee"])
        self.tableDeduction.setRowCount(0)
        for row,row_data in enumerate(rows):
            self.tableDeduction.insertRow(row)
            for column,column_data in enumerate(row_data):
                self.tableDeduction.setItem(row, column, QTableWidgetItem(str(column_data)))

    def tableDeductionItem_changed(self):
        cur = self.c.cursor()
        row = self.tableDeduction.currentRow()
        if row > -1:
            code = self.tableDeduction.item(row,0).text()
            rows = cur.execute('Select * From Deductions Where DeductionID = ?', (code,))
            row = rows.fetchone()
            self.txtDeductID.setText(str(row[0]))
            self.txtDeduct.setText(str(row[1]))
            self.txtFee.setText(str(row[2]))

    def on_ClearButton_clicked(self):
        self.txtDeductID.setText("")
        self.txtDeduct.setText("")
        self.txtFee.setText("")
        self.txtDeductID.setFocus()

    def on_AddButton_clicked(self):
        try:
            cur = self.c.cursor()
            id = self.txtDeductID.text()
            desc = self.txtDeduct.text()
            fee = self.txtFee.text()
            cur.execute('INSERT INTO Deductions (DeductionID,DeductionName,DeductionFee) VALUES (?,?,?)',(id,desc,float(fee),))
            self.c.commit()
            self.on_ClearButton_clicked()
            self.updateDeductionList()
        except Error as e:
            QMessagebox.about(self,"Error",str(e))

    def on_EditButton_clicked(self):
        try:
            reply = QMessageBox.question(self, "Edit", "Do you want to edit this record?", QMessageBox.Yes, QMessageBox.No)

            if reply == QMessageBox.Yes:
                cur = self.c.cursor()
                id = self.txtDeductID.text()
                desc = self.txtDeduct.text()
                fee = self.txtFee.text()

                cur.execute('UPDATE Deductions SET DeductionName = ?, DeductionFee = ? WHERE DeductionID = ?', (desc,fee,id,))
                self.c.commit()
                self.on_ClearButton_clicked()
                self.updateDeductionList()
        except Error as e:
            QMessageBox.about(self,"Error",str(e))

    def on_DeleteButton_clicked(self):
        try:
            reply = QMessageBox.question(self, "Delete", "Do you want to delete this record?", QMessageBox.Yes, QMessageBox.No)

            if reply == QMessageBox.Yes:
                cur = self.c.cursor()
                id = self.txtDeductID.text()

                cur.execute('DELETE FROM Deductions WHERE DeductionID = ?', (id,))
                self.c.commit()
                self.updateDeductionList()


        except Error as e:
            QMessageBox.about(self,"Error",str(e))

class TimeForm(QDialog):

    c = sqlite3.connect('System.sqlite')

    def __init__(self):
        super(TimeForm,self).__init__()
        loadUi('ui/timeIn.ui',self)
        self.dateActivity.setDate(QDate.currentDate())
        self.timeActivity.setTime(QTime.currentTime())
        self.tableEmployee.clicked.connect(self.tableEmployeeItem_changed)
        self.btnIn.clicked.connect(self.timeIn)
        self.btnOut.clicked.connect(self.timeOut)
        self.updateEmployeeList()

    def updateEmployeeList(self):
        try:
            cur = self.c.cursor()
            self.tableEmployee.clear()
            rows = cur.execute("Select EmployeeCode, LastName, FirstName, MiddleName, Job From Employee")
            self.tableEmployee.setHorizontalHeaderLabels(["Code", "Last Name","First Name","Middle Name","Job"])
            self.tableEmployee.setRowCount(0)
            for row,row_data in enumerate(rows):
                self.tableEmployee.insertRow(row)
                for column,column_data in enumerate(row_data):
                    self.tableEmployee.setItem(row, column, QTableWidgetItem(column_data))
        except:
            QMessagebox.about(self,"Error",str(e))

    def tableEmployeeItem_changed(self):
        cur = self.c.cursor()
        row = self.tableEmployee.currentRow()
        if row > -1:
            code = self.tableEmployee.item(row,0).text()
            rows = cur.execute('Select EmployeeCode, LastName, FirstName, MiddleName, Job From Employee WHERE EmployeeCode = ?',(code,))
            row = rows.fetchone()
            self.txtEmpCode.setText(str(row[0]))
            self.txtLName.setText(str(row[1]))
            self.txtFName.setText(str(row[2]))
            self.txtMName.setText(str(row[3]))
            self.txtJob.setText(str(row[4]))

    def timeIn(self):
        try:
            cur = self.c.cursor()
            code = self.txtEmpCode.text()
            dateTemp = self.dateActivity.date()
            date = dateTemp.toString("dd/MM/yyyy")
            timeTemp = self.timeActivity.time()
            time = timeTemp.toString(Qt.DefaultLocaleLongDate)
            status = "Time In"
            rows = cur.execute('SELECT * FROM Activity WHERE ActDate = ? and EmployeeCode = ?',(date,code))
            data = rows.fetchall()
            if len(data) == 0:
                cur.execute('INSERT INTO Activity (EmployeeCode,ActDate,ActTime,Status) VALUES (?,?,?,?)',(code,date,time,status,))
                cur.execute('INSERT INTO Attendance (EmployeeCode,AttenDate,TimeIn,TimeOut) VALUES (?,?,?,?)',(code,date,time,"-",))
                self.c.commit()
            else:
                cur.execute('UPDATE Activity Set ActTime = ? WHERE ActDate = ? and EmployeeCode = ? and Status="Time In"',(time,date,code,))
                cur.execute('UPDATE Attendance SET TimeIn = ? WHERE AttenDate = ? and EmployeeCode = ?',(time,date,code,))
                self.c.commit()
        except Error as e:
            QMessageBox.about(self,"Error",str(e))
    def timeOut(self):
        try:
            cur = self.c.cursor()
            code = self.txtEmpCode.text()
            dateTemp = self.dateActivity.date()
            date = dateTemp.toString("dd/MM/yyyy")
            timeTemp = self.timeActivity.time()
            time = timeTemp.toString(Qt.DefaultLocaleLongDate)
            status = "Time Out"
            rows = cur.execute('SELECT * FROM Activity WHERE ActDate = ? and EmployeeCode = ?',(date,code))
            data = rows.fetchall()
            if len(data) == 0:
                QMessageBox.about(self,"Error","Operation can't be completed")
            elif len(data) == 1:
                cur.execute('INSERT INTO Activity (EmployeeCode,ActDate,ActTime,Status) VALUES (?,?,?,?)',(code,date,time,status,))
                cur.execute('UPDATE Attendance SET TimeOut = ? WHERE AttenDate = ? and EmployeeCode = ?',(time,date,code,))
                self.c.commit()
            else:
                cur.execute('UPDATE Activity Set ActTime = ? WHERE ActDate = ? and EmployeeCode = ? and Status = "Time Out"',(time,date,code,))
                self.c.commit()
        except Error as e:
            QMessageBox.about(self,"Error",str(e))

class Payroll(QDialog):

    c = sqlite3.connect('System.sqlite')

    def __init__(self):
        super(Payroll,self).__init__()
        loadUi('ui\payroll.ui',self)
        self.tableEmployee.clicked.connect(self.tableEmployeeItem_changed)
        self.btnCompute.clicked.connect(self.compute)
        self.btnProceed.clicked.connect(self.proceed)
        self.updateEmployeeList()

    def updateEmployeeList(self):
        try:
            cur = self.c.cursor()
            self.tableEmployee.clear()
            rows = cur.execute("Select EmployeeCode, LastName, FirstName, MiddleName, Job From Employee")
            self.tableEmployee.setHorizontalHeaderLabels(["Code", "Last Name","First Name","Middle Name","Job"])
            self.tableEmployee.setRowCount(0)
            for row,row_data in enumerate(rows):
                self.tableEmployee.insertRow(row)
                for column,column_data in enumerate(row_data):
                    self.tableEmployee.setItem(row, column, QTableWidgetItem(column_data))
        except:
            QMessagebox.about(self,"Error",str(e))

    def tableEmployeeItem_changed(self):
        cur = self.c.cursor()
        row = self.tableEmployee.currentRow()
        if row > -1:
            code = self.tableEmployee.item(row,0).text()
            rows = cur.execute('Select EmployeeCode, LastName, FirstName, MiddleName, Job From Employee WHERE EmployeeCode = ?',(code,))
            row = rows.fetchone()
            self.txtEmpCode.setText(str(row[0]))
            self.txtLName.setText(str(row[1]))
            self.txtFName.setText(str(row[2]))
            self.txtMName.setText(str(row[3]))
            self.txtJob.setText(str(row[4]))

    def compute(self):
        cur = self.c.cursor()
        code = self.txtEmpCode.text()
        job = self.txtJob.text()
        days = self.txtDays.text()
        if days == "":
            hours=0
        else:
            hours = int(days) * 8
        jobRows = cur.execute('Select * From Job WHERE JobName = ?',(job,))
        row = jobRows.fetchone()
        rate = float(row[2])
        grossPay = rate * hours
        self.lblGross.setText(str(grossPay))
        deductionFee = 0
        deductRows = cur.execute('Select * From Deductions')
        for row in deductRows:
            deductionFee+=float(row[2])
        self.lblDeductions.setText(str(deductionFee))
        if grossPay in range(0,10001):
            tax = 0.05
        elif grossPay in range(10001,30001):
            tax = 0.1
        elif grossPay in range(30001,70001):
            tax = 0.15
        elif grossPay in range(70001,140001):
            tax = 0.20
        elif grossPay in range(140001,250001):
            tax = 0.25
        elif grossPay in range(250001,500001):
            tax = 0.3
        else:
            tax = 0.32
        taxFee = grossPay * tax
        taxFee = float(taxFee)
        self.lblTax.setText(str(taxFee))
        netPay = grossPay - (deductionFee + taxFee)
        self.lblNet.setText(str(netPay))

    def proceed(self):
        try:
            cur = self.c.cursor()
            code = self.txtEmpCode.text()
            dateTemp = QDate.currentDate()
            date = dateTemp.toString("MM/yyyy")
            netPay = self.lblNet.text()
            rows = cur.execute('SELECT * FROM Payroll WHERE PayDate = ? and EmployeeCode = ?',(date,code,))
            data = rows.fetchall()
            if len(data) == 0:
                cur.execute('INSERT INTO Payroll(PayDate,EmployeeCode,Payment) VALUES (?,?,?)',(date,code,float(netPay)))
                self.c.commit()
            else:
                cur.execute('UPDATE Payroll SET Payment=? WHERE PayDate = ? and EmployeeCode = ?',(float(netPay),date,code,))
                self.c.commit()
        except:
            QMessagebox.about(self,"Error",str(e))
        self.close()

class MonthlyReport(QDialog):

    c = sqlite3.connect('System.sqlite')

    def __init__(self):
        super(MonthlyReport,self).__init__()
        loadUi('ui\monthlyReport.ui',self)
        cur = self.c.cursor()
        dateRows = cur.execute("SELECT * FROM Payroll GROUP BY PayDate")
        for row in dateRows:
            self.cboYear.addItem(row[1])

        date = self.cboYear.currentText()
        self.tableReport.clear()
        totalPay = 0
        rows = cur.execute('SELECT Employee.EmployeeCode, Employee.LastName,Employee.FirstName,Employee.MiddleName,Employee.Job, Payment FROM Payroll INNER JOIN Employee on Payroll.EmployeeCode = Employee.EmployeeCode WHERE PayDate = ?',(date,))
        self.tableReport.setHorizontalHeaderLabels(["Code", "Last Name","First Name","Middle Name","Job","Payment"])
        self.tableReport.setRowCount(0)
        for row,row_data in enumerate(rows):
            self.tableReport.insertRow(row)
            for column,column_data in enumerate(row_data):
                self.tableReport.setItem(row, column, QTableWidgetItem(str(column_data)))

        paymentRows = cur.execute('SELECT Payment FROM Payroll')
        for row in paymentRows:
            totalPay += int(row[0])

        self.lblTotal.setText("Total : P " + str(totalPay))



class DailyAttendance(QDialog):

    c = sqlite3.connect('System.sqlite')

    def __init__(self):
        super(DailyAttendance,self).__init__()
        loadUi('ui\showAttendance.ui',self)
        self.dateEdit.setDate(QDate.currentDate())
        self.dateEdit.setCalendarPopup(True)
        attendance = QTimer(self)
        attendance.timeout.connect(self.showRecord)
        attendance.start(100)

    def showRecord(self):
        cur = self.c.cursor()
        temp=self.dateEdit.date()
        date=temp.toString("dd/MM/yyyy")
        self.tableAttendance.clear()
        rows = cur.execute('SELECT Employee.EmployeeCode, Employee.LastName,Employee.FirstName,Employee.MiddleName,Employee.Job, TimeIn,TimeOut FROM Attendance INNER JOIN Employee on Attendance.EmployeeCode = Employee.EmployeeCode WHERE AttenDate = ?',(date,))
        self.tableAttendance.setHorizontalHeaderLabels(["Code", "Last Name","First Name","Middle Name","Job","Time In","Time Out"])
        self.tableAttendance.setRowCount(0)
        for row,row_data in enumerate(rows):
            self.tableAttendance.insertRow(row)
            for column,column_data in enumerate(row_data):
                self.tableAttendance.setItem(row, column, QTableWidgetItem(str(column_data)))



app = QApplication(sys.argv)
widget = Login()
widget.show()
sys.exit(app.exec())
