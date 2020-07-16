import datetime
import telebot
from telebot import types
import time
import random
import sqlite3
import string
import os

bot = telebot.TeleBot('1356395096:AAHzRpEMZdjHNLDOT2xrBirbMfehCYFe2sE')
MY_NAME = bot.get_me().username

allsys = dict()
sysadmins = {}
chats = { -1001167411877 }

for id in chats:
    sysadmins[id] = set()
#sysadmins[-495950868] = {"miska924", "DENIEDBY"}

def unique_id():
    return ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(20))

class Problem:
    def __init__(self, input):
        self.id, self.state, self.from_user, self.occurence_time, self.sysadmin, self.binding_time, self.report_time, self.report, self.bot_message_id, self.chat_id = input

def supported_chat(message, group_allowed=False, private_allowed=False):
    if message.chat.type == "group" or message.chat.type == "supergroup":
        if not group_allowed:
            bot.send_message(message.chat.id, "Эта функция может быть вызвана только из личной переписки со мной")
            return False
        if message.chat.id not in chats:
            bot.send_message(message.chat.id, "Этот чат не обслуживается")
            return False
        return True
    else:
        if not private_allowed:
            bot.send_message(message.chat.id, "Эта функция может быть вызвана только из чата")
            return False
        if message.from_user.username not in allsys:
            return False
        return True

def query_log(function):
    def wrapper(message):
        tm = time.time()
        query_log = open("./logs/" + str(tm), "x")
        query_log.write(str(message))
        query_log.close()
        print("Query \"" + function.__name__ + "\" in chat " + str(message.chat.id) + " from " + str(message.from_user.id) + " is at ./logs/" + str(tm))
        function(message)
    return wrapper

def callback_log(function):
    def wrapper(message):
        tm = time.time()
        query_log = open("./logs/" + str(tm), "x")
        query_log.write(str(message))
        query_log.close()
        chat_id = message.message.chat.id
        print("Callback \"" + function.__name__ + "\" in chat " + str(message.message.chat.id) + " from " + str(message.from_user.id) + " is at ./logs/" + str(tm))
        function(message)
    return wrapper

def log(message, description):
    tm = time.time()
    query_log = open("./logs/" + str(tm), "x")
    query_log.write(str(message))
    query_log.close()
    print(description + " at ./logs/" + str(tm))

@bot.message_handler(commands=['help','start'])
@query_log
def help_message(message):
    if not supported_chat(message, group_allowed=True, private_allowed=True):
        return
    text = """Сисхелпер - бот, стремящийся облегчить жизнь сисадминам и взаимодействие с ними.
/problem - сообщить о проблеме.
Для владельца/администраторов:
/add_sysadmin@"""+MY_NAME+""" @user - добавить пользователя @user в список сисадминов.
/remove_sysadmin@"""+MY_NAME+""" @user - убрать пользователя @user из списка сисадминов
/list_sysadmins@"""+MY_NAME+""" - список всех сисадминов
Для сисадминов:
При возникновении проблемы любой сисадмин может ее принять, нажав на кнопку под соответсвующим сообщением бота.
/report id - отправить отчет по проблеме id.
/get_report id - взять отчет по проблеме id."""
    bot.send_message(message.chat.id, text)

@bot.message_handler(commands=['add_sysadmin'])
@query_log
def add_sysadmin_message(message):
    if not supported_chat(message, group_allowed=True):
        return
    status = bot.get_chat_member(message.chat.id, message.from_user.id).status
    call = message.text.split()
    if len(call) < 2:
        bot.send_message(message.chat.id, "Пожалуйста, укажите никнейм пользователя.\nПример: /add_sysadmin@"+MY_NAME+" @durov")
        return
    if status == "administrator" or status == "creator":
        text = ""
        for i in range(1, len(call)):
            #Проверка, что пользователь $i находится в чате???
            user = call[i] if call[i][0] != "@" else call[i][1:]
            if user not in sysadmins[message.chat.id]:
                if not user:
                    continue
                if user.isalnum():
                    if user not in allsys:
                        allsys[user] = 0
                    allsys[user] += 1
                    sysadmins[message.chat.id].add(user)
                    add_sysadmin(message.chat.id, user)
                    print("Sysadmin " + user + " is now sysadmin")
            else:
                text += user + " уже является сисадмином этого чата\n"
        if text:
            bot.send_message(message.chat.id, text)
    else:
        bot.send_message(message.chat.id, "Эту функцию могут вызвать только создатель и администраторы.")

@bot.message_handler(commands=['remove_sysadmin'])
@query_log
def remove_sysadmin_message(message):
    if not supported_chat(message, group_allowed=True):
        return

    status = bot.get_chat_member(message.chat.id, message.from_user.id).status
    call = message.text.split()
    if len(call) < 2:
        bot.send_message(message.chat.id, "Пожалуйста, укажите никнейм пользователя.\nПример: /remove_sysadmin@"+MY_NAME+" @durov")
        return
    if status == "administrator" or status == "creator":
        text = ""
        for i in range(1, len(call)):
            user = call[i] if call[i][0] != "@" else call[i][1:]
            if user in sysadmins[message.chat.id]:
                allsys[user] -= 1
                if allsys[user] == 0:
                    allsys.pop(user)
                remove_sysadmin(message.chat.id, user)
                print("Sysadmin " + user + " is not sysadmin anymore")
                sysadmins[message.chat.id].discard(user)
            else:
                text += user + " не является сисадмином этого чата\n"
        if text:
            bot.send_message(message.chat.id, text)
    else:
        bot.send_message(message.chat.id, "Эту функцию могут вызвать только создатель и администраторы.")

@bot.message_handler(commands=['list_sysadmins'])
@query_log
def list_sysadmins_message(message):
    if not supported_chat(message, group_allowed=True):
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
    if not supported_chat(message, group_allowed=True):
        return
    id = unique_id()
    text = "У @" + message.from_user.username + " возникла проблема. id: " + id + "\n"
    for sa in sysadmins[message.chat.id]:
        text += "@" + sa + " "
    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton('Заняться проблемой',callback_data=id))
    msg = bot.send_message(message.chat.id, text, reply_markup=keyboard)
    add_problem(id, time.time(), message.from_user.id, msg.message_id, message.chat.id)
    print("Problem recorded!")

@bot.callback_query_handler(func = lambda call: call.data)
@callback_log
def bind_problem_query(call):
    if call.from_user.username in sysadmins[call.message.chat.id]:
        if bind_problem(call.data, time.time(), call.from_user.id):
            problem = get_problem(call.data)
            bot.edit_message_text(call.message.text + "\nПроблему решает @" + call.from_user.username + ".",
                    chat_id=problem.chat_id,
                    message_id=problem.bot_message_id)
            print("Problem " + str(problem.id) + " is binded by " + call.from_user.username + "/" + str(call.from_user.id))
        else:
            bot.answer_callback_query(callback_query_id=call.id, text="Проблему уже кто-то решает.")
    else:
        bot.answer_callback_query(callback_query_id=call.id, text="Взять проблему могут только сисадмины.")

@bot.message_handler(commands=['report'])
@query_log
def report_message(message):
    if not supported_chat(message, private_allowed=True):
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
        bot.send_message(message.chat.id, "Пожалуйста, укажите id проблемы.\nЕго можно найти в соответствующем сообщении бота.\nПример: /report@" + MY_NAME + " 0D23e5A719a2cdBf5hFj")
        return
    problem = get_problem(id)
    if not problem:
        bot.send_message(message.chat.id, "Неверный id!")
        return
    if str(problem.sysadmin) != str(message.from_user.id):
        bot.send_message(message.chat.id, "Вы не можете отправлять отчет по этому кейсу")
        return
    report_problem(id, time.time(), report)
    print("Problem " + str(id) + " got reported by user " + message.from_user.username + "/" + str(message.from_user.id))

@bot.message_handler(commands=['get_report'])
@query_log
def get_report_message(message):
    if not supported_chat(message, private_allowed=True):
        return
    text = message.text
    words = text.split()
    if len(words) < 2:
        bot.send_message(message.chat.id, "Пожалуйста, укажите id проблемы.\nЕго можно найти в соответствующем сообщении бота.\nПример: /get_report@" + MY_NAME + " 0D23e5A719a2cdBf5hFj")
        return
    id = text.split()[1]
    problem = get_problem(id)
    if not problem:
        bot.send_message(message.chat.id, "Неверный id")
        return
    if str(message.from_user.id) != str(problem.sysadmin):
        bot.send_message(message.chat.id, "Вы не можете запросить отчет по этому кейсу, так как кейс был взят другим сисадмином")
        return
    if problem.state != 2:
        bot.send_message(message.chat.id, "Отчет по кейсу не сдан")
        return
    bot.send_message(message.chat.id, "Пустой отчет" if not problem.report else problem.report)
    print("Problem " + str(id) + " report is transfarred to " + message.from_user.username + "/" + str(message.from_user.id))

@bot.message_handler(commands=['get_time_period_report'])
@query_log
def get_time_period_report_message(message):
    if not supported_chat(message, private_allowed=True):
        return
    text = message.text
    words = text.split()
    if len(words) != 3:
        bot.send_message(message.chat.id, "Неверный формат запроса!\nПример: /get_time_period_report 5.7.2020 15.7.2020 - запрос всех отчетов с 5 июля 2020 года по 15 июля 2020 года")
        return
    date1 = words[1].split('.')
    date2 = words[2].split('.')
    if len(date1) != 3 or len(date2) != 3:
        bot.send_message(message.chat.id, "Неверный формат запроса!\nПример: /get_time_period_report 5.7.2020 15.7.2020 - запрос всех отчетов с 5 июля 2020 года по 15 июля 2020 года")
        print("lol")
        return
    try:
        date1 = datetime.datetime(int(date1[2]), int(date1[1]), int(date1[0]))
        date2 = datetime.datetime(int(date2[2]), int(date2[1]), int(date2[0]))
    except:
        bot.send_message(message.chat.id, "Неверный формат запроса!\nПример: /get_time_period_report 5.7.2020 15.7.2020 - запрос всех отчетов с 5 июля 2020 года по 15 июля 2020 года")
        return
    #Костыльный способ
    problems = get_time_period_report(message.from_user.id, (date1 - datetime.datetime(1969, 12, 31, 19)).total_seconds(), (date2 - datetime.datetime(1969, 12, 30, 19)).total_seconds())
    report_file = None
    try:
        if os.path.exists("./report_file.txt"):
            report_file = open("./report_file.txt", "w")
        else:
            report_file = open("./report_file.txt", "x")
    except:
        bot.send_message(message.chat.id, "SOS! Что-то пошло не так!")
        print("I couldn't open file!")
        return
    report = "Отчет о работе с " + str(date1.day) + "." + str(date1.month) + "." + str(date1.year) + " года по " + str(date2.day) + "." + str(date2.month) + "." + str(date2.year) + " года \n"
    i = 1
    for problem in problems:
        occurence_time = datetime.datetime.fromtimestamp(float(problem.occurence_time))
        binding_time = datetime.datetime.fromtimestamp(float(problem.binding_time))
        report_time = datetime.datetime.fromtimestamp(float(problem.report_time))
        format_string = "{}.{}.{} {}:{}:{}"
        occurence_time = format_string.format(occurence_time.day, occurence_time.month, occurence_time.year, occurence_time.hour, occurence_time.minute, occurence_time.second)
        binding_time = format_string.format(binding_time.day, binding_time.month, binding_time.year, binding_time.hour, binding_time.minute, binding_time.second)
        report_time = format_string.format(report_time.day, report_time.month, report_time.year, report_time.hour, report_time.minute, report_time.second)
        problem_report = "{}) Сотрудник: {}\nВремя возникновения: {}\nВремя принятия: {}\nОтчет:\n{}\n".format(i, occurence_time, binding_time, report_time, problem.report)
        report += problem_report
        i += 1
    report_file.write(report)
    report_file.close()
    report_file = open("./report_file.txt", "r")
    bot.send_document(message.chat.id, report_file)
    report_file.close()

def add_sysadmin(chat_id, username):
    with sqlite3.connect("sysadmin.db") as db_connection:
        cursor = db_connection.cursor()
        cursor.execute('''INSERT INTO sysadmins(chat_id, username)
                          VALUES(?, ?)''', (str(chat_id), str(username)))

def remove_sysadmin(chat_id, username):
    with sqlite3.connect("sysadmin.db") as db_connection:
        cursor = db_connection.cursor()
        cursor.execute('''DELETE FROM sysadmins WHERE chat_id = ? AND username = ?''', (str(chat_id), str(username)))

def add_problem(id, time, user_id, message_id, chat_id):
    with sqlite3.connect("problem.db") as db_connection:
        cursor = db_connection.cursor()
        cursor.execute('''INSERT INTO problems(id, state, from_user, occurence_time, bot_message_id, chat_id)
                          VALUES(?, ?, ?, ?, ?, ?)''', (str(id), 0, str(user_id), str(time), str(message_id), str(chat_id)))

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

def get_time_period_report(user, from_time, till_time):
    with sqlite3.connect("problem.db") as db_connection:
        cursor = db_connection.cursor()
        rows = cursor.execute("SELECT * FROM problems WHERE sysadmin = ? AND state = 2 AND occurence_time BETWEEN ? AND ?", (user, from_time, till_time)).fetchall()
        return map(lambda i: Problem(i), rows)

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
    if not row[1] in allsys:
        allsys[row[1]] = 0
    allsys[row[1]] += 1


bot.polling()
