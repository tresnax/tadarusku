import sqlite3

def create_database():
    conn = sqlite3.connect('db/tadarusku_bot.db')
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    userid TEXT NOT NULL UNIQUE,
                    register_date DATE NOT NULL,
                    notif BOOLEAN NOT NULL)
                    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS tadarus (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    userid TEXT NOT NULL,
                    runtutan INTEGER NOT NULL,
                    rn_date DATE,
                    start_date DATE)
                    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS tadarus_stats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    userid TEXT NOT NULL,
                    runtutan INTEGER NOT NULL,
                    start_date DATE,
                    last_date DATE)
                    ''')
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    create_database()