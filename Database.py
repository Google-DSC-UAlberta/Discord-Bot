import psycopg2
import sqlite3
import os
from encryption import Encryption
from dotenv import load_dotenv

load_dotenv()

IS_PRODUCTION = os.getenv("MODE") == "production"

class Singleton():
    _instance = None

    # Making the class Singleton
    # make sure there is only one instance of the class
    def __new__(cls, *args, **kwargs):
        if Singleton._instance is None:
            Singleton._instance = object.__new__(cls, *args, **kwargs)
        return Singleton._instance

# The Database class that connects to the sqlite database
# Any database access and update should be done through this class
class Database(Singleton):
    # Constructor
    def __init__(self):
        if IS_PRODUCTION:
            try:
                self.connection = psycopg2.connect(os.getenv("DATABASE_URL"))
            except:
                raise Exception("Cannot connect to Postgres database")
        else:
            self.connection = sqlite3.connect("information.db")
        self.cursor = self.connection.cursor()
        self.encryption = Encryption()

    # Destructor
    def __del__(self):
        self.connection.close()

    def execute(self, query, args):
        """
        Execute a query, handling syntax conversion from sqlite to postgres
        This expects the query to use the '?' syntax for placeholder
        Args:
            query: the query to execute
            args: the arguments to the query
        """
        if IS_PRODUCTION:
            query = query.replace("?", "%s")
        self.cursor.execute(query, args)

    def create_tables(self):
        """
        Create the tables for the database
        """
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id TEXT PRIMARY KEY,
            notify_interval INT
        );''')

        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS jobs ( 
            title TEXT, 
            company TEXT, 
            location TEXT, 
            url TEXT,
            Date TEXT,
            PRIMARY KEY (title, company, location)
        );''')
        
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_job (
            job_name CHAR(40),  
            user_id TEXT ,   
            FOREIGN KEY (user_id)
            REFERENCES users(user_id)
            ON DELETE CASCADE
        );''')
        
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_location (
            location CHAR(40),
            user_id TEXT ,
            FOREIGN KEY (user_id)
            REFERENCES users(user_id)
            ON DELETE CASCADE
        );''')

        self.connection.commit()

    def print_tables(self):
        """
        Printing all the current tables
        """
        if IS_PRODUCTION:
            self.cursor.execute("""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema='public'
                AND table_type='BASE TABLE';
            """)
        else:
            self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        info_display = self.cursor.fetchall()
        print(info_display)

    def check_if_user_exist(self, user_id):
        """
        Check if the user's id is already in the database
        Args:
            user_id: the user's Discord id
        Returns: 
            True if the user is in the database, False otherwise
        """
        user_id = self.encryption.encrypt(user_id)
        self.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
        result = self.cursor.fetchall()
        return len(result) > 0
    
    def get_location(self, user_id):
        """
        Checks for the location of the user
        Args:
            user_id: the user's Discord id
        Returns: 
            The location 
        """
        user_id = self.encryption.encrypt(user_id)
        self.execute("SELECT location FROM user_location WHERE user_id=?", (user_id,))
        result = self.cursor.fetchall()
        
        return result
    
    def add_user(self, user_id, notify_interval, keywords, locations):
        """
        Add a user to the database
        Args:
            user_id: the user's Discord id
            notify_interval: the user's notification interval
            keywords: the user's job keyword(s)
            locations: the user's preferred job location(s)
        """
        user_id = self.encryption.encrypt(user_id)
        self.execute("INSERT INTO users VALUES (?, ?)", (user_id, notify_interval))
        
        for keyword in keywords:
            self.execute("INSERT INTO user_job VALUES (?, ?)", (keyword, user_id))
        for location in locations:
            self.execute("INSERT INTO user_location VALUES (?, ?)", (location, user_id))
        
        self.connection.commit()
    
    def delete_user(self, user_id):
        """
        Delete a user from the database
        Args:
            user_id: the user's Discord id
        """
        user_id = self.encryption.encrypt(user_id)
        self.execute("DELETE FROM users WHERE user_id=?", (user_id,))
        self.connection.commit()

    def get_keywords_and_location(self, user_id):
        """
        Retrieve the job search keywords and location from the user_job table and user_location table
        Args:
            user_id: the user's Disccord id
        Returns:
            A dictionary with two keys: job_keywords and location. Each key's value is a list.
        """
        result = {"job_keywords": [], "location": []}
        user_id = self.encryption.encrypt(user_id)

        self.execute("SELECT location FROM user_location WHERE user_id = ?", (user_id,))
        locations_info = self.cursor.fetchall()
        for location_info in locations_info:
            result["location"].append(location_info[0].strip())
        
        self.execute("SELECT job_name FROM user_job WHERE user_id = ?", (user_id,))
        job_keywords_info = self.cursor.fetchall()
        for job_keyword_info in job_keywords_info:
            result["job_keywords"].append(job_keyword_info[0].strip())
        
        return result
        
    def add_job(self, title, company, location, url, date):
        """
        Add a job to the database 
        Args:
            title: the job's title
            company: the job's company
            location: the job's location
            url: the job's url
        """
        # For postgres, the syntax for INSERT IGNORE INTO is slightly different
        if IS_PRODUCTION:
            self.cursor.execute("""
                INSERT INTO jobs(title, company, location, url, Date)
                VALUES(%s,%s,%s,%s,%s) 
                ON CONFLICT(title, company, location) DO NOTHING;
            """, (title, company, location, url, date))
        else:
            self.cursor.execute("INSERT OR IGNORE INTO jobs VALUES(?,?,?,?,?);", (title, company, location, url, date))
        self.connection.commit()

    def get_jobs(self, job_keywords, locations, pg_num):
        """
        Retrieve the jobs from the database
        Args:
            job_keywords: the job keywords
            location: the location
        Returns:
            A list of jobs
        """
        jobs = []
        for job_keyword in job_keywords:
            if len(locations) > 0:
                # TODO: using for with multiple locations can return a maximum of 10*len(locations) jobs per page
                # use a better way to handle the pagination
                for location in locations:
                    self.execute("""
                        SELECT * FROM jobs 
                        WHERE LOWER(title) LIKE ? AND LOWER(location) LIKE ? 
                        ORDER BY date DESC 
                        LIMIT 10 
                        OFFSET ?
                    """, ("%" + job_keyword.lower().split("_")[0] + "%", "%" + location.lower() + "%", pg_num*10))
                    result = self.cursor.fetchall()
                    for job in result:
                        jobs.append(job)
            
            else:
                self.execute("""
                    SELECT * FROM jobs 
                    WHERE LOWER(title) LIKE ?
                    ORDER BY date DESC 
                    LIMIT 10 
                    OFFSET ?
                """, ("%" + job_keyword.lower().split("_")[0] + "%", pg_num*10))
                result = self.cursor.fetchall()
                for job in result:
                    jobs.append(job)
        
        # TODO: use a better way to handle the pagination
        if len(jobs) > 10:
            jobs = jobs[0:10]
        return jobs

    def edit_user(self, user_id, keywords, locations, notify_interval):
        user_id = self.encryption.encrypt(user_id)
        if (len(keywords) != 0):
            #keywords not empty
            self.execute("DELETE FROM user_job WHERE user_id = ?", (user_id,))
            for keyword in keywords:
                self.execute("INSERT INTO user_job VALUES (?, ?)", (keyword, user_id))
            self.connection.commit()

        if (len(locations) != 0):
            #locations not empty
            self.execute("DELETE FROM user_location WHERE user_id = ?", (user_id,))
            for location in locations:
                self.execute("INSERT INTO user_location VALUES (?, ?)", (location, user_id))
            self.connection.commit()
        if notify_interval > 0:
            self.execute("UPDATE users SET notify_interval = ? WHERE user_id = ?", (notify_interval, user_id))
            self.connection.commit()
            
    def get_notify_interval(self, user_id):
        """
        Retrieve the notify interval of the user
        Args:
            user_id: the user's Discord id
        Returns: 
            An integer containing the notify interval (in minutes) 
        """
        user_id = self.encryption.encrypt(user_id)
        self.execute("SELECT notify_interval FROM users WHERE user_id=?", (user_id,))
        result = self.cursor.fetchone()[0]
        
        return result

    def delete_jobs(self):
        """
        Delete all jobs from the database
        """
        self.cursor.execute("DELETE FROM jobs")
        self.connection.commit()

    def delete_old_jobs(self):
        """
        Delete old jobs from the database
        """
        self.cursor.execute("DELETE FROM jobs WHERE Date < date('now','-180 day')")
        self.connection.commit()
    

if __name__ == "__main__":
    # a simple test on the Singleton pattern
    # there should be the only instance of the Database class
    # so the two instances created should be the same
    db = Database()
    test_db = Database()
    assert db is test_db

    if IS_PRODUCTION:
        print("database is in production mode")
    else:
        print("database is in development mode")
    db.create_tables()
    db.print_tables()
    
    # Testing
    #print(len(db.get_jobs(["software_engineer"], [])))
    #print(len(db.get_jobs(["software"], [])))



