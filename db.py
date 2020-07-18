import sqlite3
from user import User
from problem import Problem

allsys = dict()
users = dict()
sysadmins = {}
chats = { -1001167411877 }

def init():
    #sysadmins[-495950868] = {"miska924", "DENIEDBY"}
    db_connection = sqlite3.connect("syshelper.db")
    cursor = db_connection.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS problems
                 (id text,
                 state integer,
                 from_user text,
                 occurence_time text,
                 sysadmin text,
                 binding_time text,
                 report_time text,
                 report text,
                 bot_message_id text,
                 chat_id text)''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS sysadmins
                 (chat_id text,
                 username text)''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS users
                 (user_id text,
                 username text,
                 first_name text,
                 last_name text)''')

    for id in chats:
        sysadmins[id] = set()
    rows = cursor.execute("SELECT * FROM sysadmins", ()).fetchall()
    for row in rows:
        if (int(row[0]) not in sysadmins):
            sysadmins[int(row[0])] = set()
        sysadmins[int(row[0])].add(row[1])
        if not row[1] in allsys:
            allsys[row[1]] = 0
        allsys[row[1]] += 1

    rows = cursor.execute("SELECT * FROM users", ()).fetchall()
    for row in rows:
        users[row[0]] = User(row)

def add_sysadmin(chat_id, username):
    username = username.lower()
    with sqlite3.connect("syshelper.db") as db_connection:
        cursor = db_connection.cursor()
        cursor.execute('''INSERT INTO sysadmins(chat_id, username)
                          VALUES(?, ?)''', (str(chat_id), str(username)))

def remove_sysadmin(chat_id, username):
    username = username.lower()
    with sqlite3.connect("syshelper.db") as db_connection:
        cursor = db_connection.cursor()
        cursor.execute('''DELETE FROM sysadmins WHERE chat_id = ? AND username = ?''', (str(chat_id), str(username)))

def add_problem(id, time, user_id, message_id, chat_id):
    with sqlite3.connect("syshelper.db") as db_connection:
        cursor = db_connection.cursor()
        cursor.execute('''INSERT INTO problems(id, state, from_user, occurence_time, bot_message_id, chat_id)
                          VALUES(?, ?, ?, ?, ?, ?)''', (str(id), 0, str(user_id), str(time), str(message_id), str(chat_id)))

def bind_problem(id, time, user):
    with sqlite3.connect("syshelper.db") as db_connection:
        cursor = db_connection.cursor()
        rows = cursor.execute('''SELECT state FROM problems WHERE id = ?''', (id,)).fetchall()
        if len(rows) == 0:
            return False
        if rows[0][0] != 0:
            return False
        cursor.execute('''UPDATE problems
            SET state = 1,
                binding_time = ? ,
                sysadmin = ?
            WHERE id = ?''', (time, user, id))
        return True

def report_problem(id, time, report):
    with sqlite3.connect("syshelper.db") as db_connection:
        cursor = db_connection.cursor()
        cursor.execute('''UPDATE problems
            SET state = 2,
                report_time = ?,
                report = ?
            WHERE id = ?''', (time, report, id))

def get_problem(id):
    with sqlite3.connect("syshelper.db") as db_connection:
        cursor = db_connection.cursor()
        rows = cursor.execute("SELECT * FROM problems WHERE id = ?", (id,)).fetchall()
        assert len(rows) < 2
        if len(rows) == 0:
            return None
        return Problem(rows[0])

def get_time_period_report(user, from_time, till_time):
    with sqlite3.connect("syshelper.db") as db_connection:
        cursor = db_connection.cursor()
        rows = cursor.execute("SELECT * FROM problems WHERE sysadmin = ? AND state = 2 AND occurence_time BETWEEN ? AND ?", (user, from_time, till_time)).fetchall()
        return map(lambda i: Problem(i), rows)

def add_user(user_id, username, first_name, last_name):
    username = username.lower()
    with sqlite3.connect("syshelper.db") as db_connection:
        cursor  = db_connection.cursor()
        if cursor.execute("SELECT EXISTS(SELECT * FROM users WHERE user_id = ?)", (user_id,)).fetchone():
            cursor.execute('''UPDATE
                                users
                              SET
                                username = ?,
                                first_name = ?,
                                last_name = ?
                              WHERE
                                user_id = ?''', (username, first_name, last_name, user_id))
        else:
            cursor.execute('''INSERT INTO
                                users(user_id, username, first_name, last_name)
                              VALUES(?, ?, ?, ?)''', (user_id, username, first_name, last_name))
    users[user_id] = User((user_id, username, first_name, last_name))
