import sqlite3
import pandas as pd


# Making the database information 
connection=sqlite3.connect("information.db")

cur=connection.cursor()

# Making the table USER
# 1) USERNAME 
# 2) PASSWORD (encrypted)
# 3) NOTIF_INTERVAL
# 4) JOB_KEY

#cur.execute('''CREATE TABLE if not exists sorted_data ( key_word text, type text, often_update INTEGER)''')   
cur.execute('''DROP TABLE IF EXISTS USER''')   

#Creating User table
u_table = '''CREATE TABLE USER(
    USERNAME CHAR(40) PRIMARY KEY,
    PASSWORD CHAR(40),  
    NOTIF_INTERVAL INT,
    JOB_KEY CHAR(40)
);'''

#password and job keywords is char for now at least because idk what they should be
cur.execute(u_table)
connection.commit()

#printing the columns
data = cur.execute("SELECT * FROM USER;")
for column in data.description:
    print(column[0])

#printing all the current tables
cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
# Currently the table is empty 
info_display=cur.fetchall()
print(info_display)

connection.close()