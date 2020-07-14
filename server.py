import telebot
from telebot import types
import random
import sqlite3
import time
import string

bot = telebot.TeleBot('1356395096:AAHzRpEMZdjHNLDOT2xrBirbMfehCYFe2sE')
chats = {}

MY_NAME = bot.get_me().username

allsys = set()
sysadmins = {}
chats = {-1001167411877}

for id in chats:
    sysadmins[id] = set() # если оставляю пустым - падает
#sysadmins[-495950868] = {"miska924", "DENIEDBY"}

def unique_id():
    return ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(20))

class Problem:
    def __init__(self, input):
        self.id, self.state, self.from_user, self.occurence_time, self.sysadmin, self.binding_time, self.report_time, self.report, self.bot_message_id, self.chat_id = input

def supported_chat(message):
    if message.chat.id not in chats:
        if message.chat.type == "private" and message.from_user.username in allsys:
            return True
        bot.send_message(message.chat.id, "Этот чат не обслуживается");
        print(message.from_user.username + " is knocking in " + str(message.chat.id));
        return False
    return True

def query_log(function):
    def wrapper(message):
        tm = time.time()
        query_log = open("./logs/" + str(tm), "x")
        query_log.write(str(message))
        query_log.close()
        print("Query \"" + function.__name__ + "\" at ./logs/" + str(tm))
        function(message)
    return wrapper

def log(message, description):
    tm = time.time()
    query_log = open("./logs/" + str(tm), "x")
    query_log.write(str(message))
    query_log.close()
    print(description + " at ./logs/" + str(tm))

@bot.message_handler(commands = ['help','start'])
@query_log
def help_message(message):
    if not supported_chat(message):
        return
    text = MY_NAME+""" - бот, стремящийся облегчить жизнь сисадминам и взаимодействие с ними.
/problem - сообщить о проблеме.
Для владельца/администраторов:
/add_sysadmin@"""+MY_NAME+""" @user - добавить пользователя @user в список сисадминов.
/remove_sysadmin@"""+MY_NAME+""" @user - убрать пользователя @user из списка сисадминов
/list_sysadmins@"""+MY_NAME+""" - вывести всех сисадминов
Для сисадминов:
При возникновении проблемы любой сисадмин может ее принять, нажав на кнопку под соответсвующим сообщением бота.
/report id - отправить отчет по проблеме id.
/get_report id - взять отчет по проблеме id."""
    bot.send_message(message.chat.id, text)

@bot.message_handler(commands=['add_sysadmin'])
@query_log
def add_sysadmin_message(message):
    if not supported_chat(message):
        return
    status = bot.get_chat_member(message.chat.id, message.from_user.id).status
    call = message.text.strip().split()
    if len(call) < 2:
        bot.send_message(message.chat.id, "Пожалуйста, укажите никнейм пользователя.\nПример: /add_sysadmin@"+MY_NAME+" @durov")
        return
    if status == "administrator" or status == "creator":
        for i in range(1, len(call)):
            #Проверка, что пользователь $i находится в чате???
            user = call[i] if call[i][0] != "@" else call[i][1:]
            if not user:
                continue
            if user.isalnum():
                allsys.add(user)
                sysadmins[message.chat.id].add(user)
                add_sysadmin_sql(message.chat.id, user)
                print("Sysadmin " + user + " is now sysadmin")
    else:
        bot.send_message(message.chat.id, "Эту функцию могут вызвать только создатель и администраторы.")

@bot.message_handler(commands=['remove_sysadmin'])
@query_log
def remove_sysadmin_message(message):
    if not supported_chat(message):
        return

    status = bot.get_chat_member(message.chat.id, message.from_user.id).status
    call = message.text.split()
    if len(call) < 2:
        bot.send_message(message.chat.id, "Пожалуйста, укажите никнейм пользователя.\nПример: /remove_sysadmin@"+MY_NAME+" @durov")
        return
    if status == "administrator" or status == "creator":
        for i in range(1, len(call)):
            user = call[i] if call[i][0] != "@" else call[i][1:]
            if user in sysadmins[message.chat.id]:
                allsys.disicard(user)
                remove_sysadmin_sql(message.chat.id, user)
                print("Sysadmin " + user + " is not sysadmin anymore")
            sysadmins[message.chat.id].discard(user)
    else:
        bot.send_message(message.chat.id, "Эту функцию могут вызвать только создатель и администраторы.")

@bot.message_handler(commands=['list_sysadmins'])
@query_log
def list_sysadmins_message(message):
    if not supported_chat(message):
        return

    status = bot.get_chat_member(message.chat.id, message.from_user.id).status
    call = message.text.split()
    if status == "administrator" or status == "creator":
        text = ""
        for i in sysadmins[message.chat.id]:
            text += "@" + i + " "
        if not text:
            bot.send_message(message.chat.id, "В этом чате не зарегистрировано ни одного сисадмина")
            print("All sysadmins listed:\nThere is no sysadmins")
        else:
            bot.send_message(message.chat.id, text)
            print("All sysadmins listed:\n" + text)
    else:
        bot.send_message(message.chat.id, "Эту функцию могут вызвать только создатель и администраторы.")

@bot.message_handler(commands=['problem'])
@query_log
def problem_message(message):
    if not supported_chat(message):
        return
    id = unique_id()
    text = "У @" + message.from_user.username + " возникла проблема. id: " + id + "\n"
    for sa in sysadmins[message.chat.id]:
        text += "@" + sa + " ";
    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton('Заняться проблемой',callback_data=id))
    msg = bot.send_message(message.chat.id, text, reply_markup=keyboard)
    add_problem(id, time.time(), message.from_user.id, msg.message_id, message.chat.id)
    print("Problem recorded!")

@bot.callback_query_handler(func = lambda call: call.data)
@query_log
def bind_problem_query(call):
    if not supported_chat(call.message):
        return
    if call.from_user.username in sysadmins[call.message.chat.id]:
        if bind_problem(call.data, time.time(), call.from_user.id):
            problem = get_problem(call.data)
            bot.edit_message_text(call.message.text + "\nПроблему решает @" + call.from_user.username + ".",
                    chat_id = problem.chat_id,
                    message_id = problem.bot_message_id)
            print("Problem #" + str(problem.id) + " is binded by " + call.from_user.username + "/" + str(call.from_user.id))
        else:
            bot.answer_callback_query(callback_query_id = call.id, text = "Проблему уже кто-то решает.")
    else:
        bot.answer_callback_query(callback_query_id = call.id, text = "Взять проблему могут только сисадмины.")

@bot.message_handler(commands = ['report'])
@query_log
def report_message(message):
    #ignore = False
    #Обработка
    #if ignore:
    #    return
    # Хочется скипать запросы левых чуваков
    if message.chat.type != 'private':
        if not supported_chat(message):
            return
        bot.send_message(message.chat.id, "Эта функция может быть вызвана только из личной переписки со мной.")
        return
    text = message.text
    ind = 0
    id = ""
    while ind < len(text) and text[ind] != ' ':
        ind += 1
    while ind < len(text) and text[ind] == ' ':
        ind += 1
    while ind < len(text) and text[ind] != ' ':
        id += text[ind]
        ind += 1
    report = text[ind:].strip()
    if not id:
        bot.send_message(message.chat.id, "Пожалуйста, укажите id проблемы.\nЕго можно найти в соответствующем сообщении бота.\nПример: /report@"+MY_NAME+" 0D23e5A719a2cdBf5hFj")
        return
    problem = get_problem(id)
    if not problem:
        bot.send_message(message.chat.id, "Неверный id!")
        return
    if str(problem.sysadmin) != str(message.from_user.id):
        bot.send_message(message.chat.id, "Вы не можете отправлять отчет по этому кейсу")
        return
    report_problem(id, time.time(), report)
    print("Problem #" + str(id) + " got reported by user " + message.from_user.username + "/" + str(message.from_user.id))

@bot.message_handler(commands = ['get_report'])
@query_log
def get_report_message(message):
    #ignore = False
    #Обработка
    #if ignore:
    #    return
    # Хочется скипать запросы левых чуваков
    if message.chat.type != 'private':
        bot.send_message(message.chat.id, "Эта функция может быть вызвана только из личной переписки со мной.")
        return
    text = message.text
    words = text.split()
    if len(words) < 2:
        bot.send_message(message.chat.id, "Пожалуйста, укажите id проблемы.\nЕго можно найти в соответствующем сообщении бота.\nПример: /get_report@"+MY_NAME+" 0D23e5A719a2cdBf5hFj")
        return
    id = text.split()[1]
    problem = get_problem(id)
    if not problem:
        bot.send_message(message.chat.id, "Неверный id")
        return
    if str(message.from_user.id) != str(problem.sysadmin):
        bot.send_message(message.chat.id, "Извините, вы не можете запросить отчет по этому кейсу, так как кейс был взят другим сисадмином")
        return
    if problem.state != 2:
        bot.send_message(message.chat.id, "Отчет по кейсу не сдан")
        return
    bot.send_message(message.chat.id, "Пустой отчет" if not problem.report else problem.report)
    print("Problem #" + str(id) + " report is transfarred to " + message.from_user.username + "/" + str(message.from_user.id))

def add_sysadmin_sql(chat_id, username):
    with sqlite3.connect("sysadmin.db") as db_connection:
        cursor = db_connection.cursor()
        cursor.execute('''INSERT INTO sysadmins(chat_id, username)
                          VALUES(?, ?)''', (str(chat_id), str(username)))
        #for i in db_connection.execute("SELECT * FROM problems").fetchall():
        #    print(i)

def remove_sysadmin_sql(chat_id, username):
    with sqlite3.connect("sysadmin.db") as db_connection:
        cursor = db_connection.cursor()
        cursor.execute('''DELETE FROM sysadmins WHERE chat_id = ? AND username = ?''', (str(chat_id), str(username)))

def add_problem(id, time, user_id, message_id, chat_id):
    with sqlite3.connect("problem.db") as db_connection:
        cursor = db_connection.cursor()
        cursor.execute('''INSERT INTO problems(id, state, from_user, occurence_time, bot_message_id, chat_id)
                          VALUES(?, ?, ?, ?, ?, ?)''', (str(id), 0, str(user_id), str(time), str(message_id), str(chat_id)))
        #for i in db_connection.execute("SELECT * FROM problems").fetchall():
        #    print(i)

def bind_problem(id, time, user):
    with sqlite3.connect("problem.db") as db_connection:
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
    with sqlite3.connect("problem.db") as db_connection:
        cursor = db_connection.cursor()
        cursor.execute('''UPDATE problems
            SET state = 2,
                report_time = ?,
                report = ?
            WHERE id = ?''', (time, report, id))

def get_problem(id):
    with sqlite3.connect("problem.db") as db_connection:
        cursor = db_connection.cursor()
        rows = cursor.execute("SELECT * FROM problems WHERE id = ?", (id,)).fetchall()
        assert len(rows) < 2
        if len(rows) == 0:
            return None
        return Problem(rows[0])


db_connection = sqlite3.connect("problem.db")
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

db_connection_sys = sqlite3.connect("sysadmin.db")
cursor_sys = db_connection_sys.cursor()
cursor_sys.execute('''CREATE TABLE IF NOT EXISTS sysadmins
             (chat_id text,
             username text)''')
rows = cursor_sys.execute("SELECT * FROM sysadmins", ()).fetchall()
for row in rows:
    if (int(row[0]) not in sysadmins):
        sysadmins[int(row[0])] = set()
    sysadmins[int(row[0])].add(row[1])
    allsys.add(row[1])


bot.polling()
