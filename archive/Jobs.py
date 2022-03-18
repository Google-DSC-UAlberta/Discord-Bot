import sqlite3

# Making the database information 
connection=sqlite3.connect("information.db")

cur=connection.cursor()


#function: delete all saved jobs from db
def rem_all():
    cur.execute("DELETE FROM jobs;")
    connection.commit()
    connection.close


# Making the table Sorted_data
# Initial Information are 
# 1) Title of Job
# 2) Which company
# 3) Location of Job
# 4) URL 

cur.execute('''CREATE TABLE if not exists jobs( Title text, Company text, Location text , URL text)''')   
connection.commit()

#display columns
data = cur.execute("SELECT * FROM jobs;")
for column in data.description:
    print(column[0])

# Currently the table is empty 
info_display=cur.fetchall()

print(info_display)

connection.close()