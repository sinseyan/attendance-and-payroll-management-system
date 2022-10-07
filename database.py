
import sqlite3

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
