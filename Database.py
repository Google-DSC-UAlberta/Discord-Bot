import sqlite3

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
        self.connection = sqlite3.connect("information.db")
        self.cursor = self.connection.cursor()

    # Destructor
    def __del__(self):
        self.connection.close()

    def create_tables(self):
        """
        Create the tables for the database
        """
        self.cursor.executescript('''
        CREATE TABLE IF NOT EXISTS users (
            user_id CHAR(40) PRIMARY KEY,
            notify_interval INT,
            job_key CHAR(40),
            location CHAR(50)
        );

        CREATE TABLE IF NOT EXISTS jobs ( 
            title TEXT, 
            company TEXT, 
            location TEXT, 
            url TEXT
        );
        
        CREATE TABLE IF NOT EXISTS user_job (
            job_name CHAR(40),  
            user_id CHAR(40) ,   
            FOREIGN KEY (user_id)
            REFERENCES users(user_id)
        );
        
        CREATE TABLE IF NOT EXISTS user_location (
            location CHAR(40),
            user_id CHAR(40) ,
            FOREIGN KEY (user_id)
            REFERENCES users(user_id)
        );
        
        
        
        
        ''')

        self.connection.commit()

    def print_tables(self):
        """
        Printing all the current tables
        """
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
        self.cursor.execute("SELECT * FROM users WHERE user_id=:uid", {"uid": user_id})
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
        
        self.cursor.execute("SELECT location FROM users WHERE user_id=:uid", {"uid": user_id})
        result = self.cursor.fetchall()
        
        return result
    
    def add_user(self, user_id, notify_interval, job_key, location):
        """
        Add a user to the database
        Args:
            user_id: the user's Discord id
            notify_interval: the user's notification interval
            job_key: the user's job keyword
            location: the user's location
        """
        self.cursor.execute("INSERT INTO users VALUES (:uid, :ni, :jk, :l)", {"uid": user_id, "ni": notify_interval, "jk": job_key, "l": location})
        self.cursor.execute("INSERT INTO user_job VALUES (:jk, :uid)", {"jk": job_key,"uid": user_id})
        elf.cursor.execute("INSERT INTO user_location VALUES (:l, :uid)", {"l": location,"uid": user_id})
        
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
        
        self.cursor.execute("SELECT location FROM user_location WHERE user_id = :uid", {"uid": user_id})
        locations_info = self.cursor.fetchall()
        for location_info in locations_info:
            result["location"].append(location_info[0])
        
        self.cursor.execute("SELECT job_name FROM user_job WHERE user_id = :uid", {"uid": user_id})
        job_keywords_info = self.cursor.fetchall()
        for job_keyword_info in job_keywords_info:
            result["job_keywords"].append(job_keyword_info[0])
        
        return result

if __name__ == "__main__":
    # a simple test on the Singleton pattern
    # there should be the only instance of the Database class
    # so the two instances created should be the same
    db = Database()
    test_db = Database()
    assert db is test_db

    db.create_tables()
    db.print_tables()



