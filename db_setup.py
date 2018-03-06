import sqlite3

# Create Tables
conn = sqlite3.connect('db')
c = conn.cursor()

c.execute('''
    CREATE TABLE IF NOT EXISTS old_sessions (
    id INTEGER PRIMARY KEY,
    machine text,
    user text,
    starttime DATETIME,
    endtime DATETIME
    );

''')

c.execute('''
    CREATE TABLE IF NOT EXISTS current_sessions (
    id INTEGER PRIMARY KEY,
    machine TEXT,
    user TEXT,
    starttime DATETIME
    );
''')


conn.commit()
conn.close()
