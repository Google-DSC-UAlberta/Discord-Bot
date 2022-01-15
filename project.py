import sqlite3

# Making the database information 
connection=sqlite3.connect("information.db")

cur=connection.cursor()

# Making the table Sorted_data
# Initial Information are 
# 1) Keyword ( for keyword search)
# 2) Type (type of job)
# 3) Update (how often would database stores information)

cur.execute('''CREATE TABLE if not exists sorted_data ( key_word text, type text, often_update INTEGER)''')   

# Currently the table is empty 

info_display=cur.fetchall()

print(info_display)