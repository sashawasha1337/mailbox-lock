import sqlite3

con = sqlite3.connect("users.db")
cur=con.cursor()


cur.execute(""" CREATE TABLE IF NOT EXISTS users(
    name TEXT PRIMARY KEY,
    pin TEXT NOT NULL,
    
    is_unlocker INTEGER DEFAULT 0
)
""")

cur.execute(""" CREATE TABLE IF NOT EXISTS admin(
    username TEXT PRIMARY KEY,
    password TEXT
)
""")

cur.execute("INSERT OR IGNORE INTO admin VALUES ('sashawasha','password')")

            
cur.execute("INSERT OR IGNORE INTO users VALUES ('issac','143',0)")
cur.execute("INSERT OR IGNORE INTO users VALUES ('jose','143',0)")
cur.execute("INSERT OR IGNORE INTO users VALUES ('ali','143',0)")

con.commit()
con.close()