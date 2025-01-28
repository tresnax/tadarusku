import sqlite3


def db_connection():
    conn = sqlite3.connect('db/tadarusku_bot.db')

    return conn

#==================================================================================================

def add_user(userid: str, register_date: str, notif: bool) -> None:
    conn = db_connection()
    cursor = conn.cursor()

    cursor.execute('''INSERT INTO users (userid, register_date, notif) 
                   VALUES (?, ?, ?)''', (userid, register_date, notif, )
                   )

    conn.commit()
    conn.close()


def get_user_notif() -> list:
    conn = db_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT userid FROM users WHERE notif = 1')
    users = cursor.fetchall()

    conn.close()
    return users


def del_notif(userid: str) -> None:
    conn = db_connection()
    cursor = conn.cursor()

    cursor.execute('UPDATE users SET notif = 0 WHERE userid = ?', (userid, ))

    conn.commit()
    conn.close()

#==================================================================================================

def get_tadarus(userid: str) -> dict:
    conn = db_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM tadarus WHERE userid = ?', (userid, ))
    stats = cursor.fetchone()

    conn.close()

    if stats:
        return {
            'userid': stats[1],
            'runtutan': stats[2],
            'rn_date': stats[3],
            'start_date': stats[4]
        }
    else:
        return {}


def new_tadarus(userid: str, runtutan: int, rn_date: str) -> None:
    conn = db_connection()
    cursor = conn.cursor()

    cursor.execute('''INSERT INTO tadarus (userid, runtutan, start_date) 
                   VALUES (?, ?, ?)''', (userid, runtutan, rn_date,)
                   )

    cursor.execute('''INSERT INTO tadarus_stats (userid, runtutan)
                     VALUES (?, ?)''', (userid, runtutan,)
                     )

    conn.commit()
    conn.close()


def update_tadarus(userid: str, rn_date: str) -> None:
    conn = db_connection()
    cursor = conn.cursor()

    cursor.execute('''UPDATE tadarus SET runtutan = runtutan + 1 , rn_date = ? WHERE userid = ?''', (rn_date, userid,))
    
    conn.commit()
    conn.close()


def renew_tadarus(userid: str, runtutan: int, rn_date: str) -> None:
    conn = db_connection()
    cursor = conn.cursor()

    cursor.execute('''UPDATE tadarus SET runtutan = ?, rn_date = ? WHERE userid = ?''', (runtutan, rn_date, userid))

    conn.commit()
    conn.close()

#==================================================================================================

def get_stats(userid: str) -> dict:
    conn = db_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM tadarus_stats WHERE userid = ?', (userid, ))
    stats = cursor.fetchone()

    conn.close()

    if stats:
        return {
            'userid': stats[1],
            'runtutan': stats[2],
            'start_date': stats[3],
            'last_date': stats[4]
        }
    else:
        return {}

        
def save_stats(userid: str, last_date: str) -> None:
    conn = db_connection()
    cursor = conn.cursor()

    cursor.execute('''UPDATE tadarus_stats 
                      SET runtutan = (SELECT runtutan FROM tadarus WHERE userid = ?), 
                          start_date = (SELECT start_date FROM tadarus WHERE userid = ?),
                          last_date = ?
                      WHERE userid = ?''', (userid, userid, userid, last_date))

    conn.commit()
    conn.close()


def reset_stats(userid: str) -> None:
    conn = db_connection()
    cursor = conn.cursor()

    cursor.execute('''UPDATE tadarus_stats 
                      SET runtutan = 0, start_date = NULL, last_date = NULL
                      WHERE userid = ?''', (userid, ))

    cursor.execute('''UPDATE tadarus 
                        SET runtutan = 0, rn_date = NULL
                        WHERE userid = ?''', (userid, ))
    conn.commit()
    conn.close()