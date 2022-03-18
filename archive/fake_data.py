import sqlite3
import pandas as pd


# Connect to the database
connection = sqlite3.connect("information.db")
cur = connection.cursor()


# Create the fake data, dataframe


def add_job(title, company, location, url):
    cur.execute("INSERT INTO jobs VALUES(?,?,?,?);", (title, company, location, url))
    connection.commit()
    connection.close()


"""
# Insert dataframe into Sql Database
for index, row in df.iterrows():
     add_job(row['title'], row['company'], row['location'], row['url'])
connection.commit()
connection.close()
"""