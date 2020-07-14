from datetime import datetime
import telebot
from telebot import types
import random
import sqlite3

bot = telebot.TeleBot('1140733846:AAHW8980Rv0ZF4BweijW16XHQctcpqRLyu0')
sysadmins = { "O442A4O3", "miska924" }

class Problem:
    def __init__(self, input):
        self.id, self.state, self.from_user, self.occurence_time, self.sysadmin, self.report_time, self.report, self.bot_message_id, self.chat_id = input
        

@bot.message_handler(commands=['help'])
def start_message(message):
    text = """SysadminHelpBot - бот, стремящийся облегчить жизнь сисадминам и взаимодействие с ними.
/add_sysadmin@SysadminHelpBot @user - добавить пользователя @user в список сисадминов.
/remove_sysadmin@SysadminHelpBot @user - убрать пользователя @user из списка сисадминов
/list_sysadmins@SysadminHelpBot - вывести всех сисадминов"""
    bot.send_message(message.chat.id, text)

@bot.message_handler(commands=['add_sysadmin'])
def add_sysadmin_message(message):
    if message.chat.type != 'group' and message.chat.type != 'supergroup':
        bot.send_message(message.chat.id, "Эта функция может быть вызвана только из группы.")
        return
    status = bot.get_chat_member(message.chat.id, message.from_user.id).status
    call = message.text.split()
    if len(call) < 2:
        bot.send_message(message.chat.id, "Пожалуйста, укажите никнейм пользователя.\nПример: /add_sysadmin@SysadminHelpBot @durov")
        return
    if status == "administrator" or status == "creator":
        for i in range(1, len(call)):
            #Проверка, что пользователь $i находится в чате???
            user = call[i] if call[i][0] != "@" else call[i][1:]
            if not user:
                continue
            if user.isalnum():
                sysadmins.add(user)
    else:
        bot.send_messge(message.chat.id, "Эту функцию могут вызвать только создатель и администраторы.")

@bot.message_handler(commands=['remove_sysadmin'])
def remove_sysadmin_message(message):
    if message.chat.type != 'group' and message.chat.type != 'supergroup':
        bot.send_message(message.chat.id, "Эта функция может быть вызвана только из группы.")
        return
    status = bot.get_chat_member(message.chat.id, message.from_user.id).status
    call = message.text.split()
    if len(call) < 2:
        bot.send_message(message.chat.id, "Пожалуйста, укажите никнейм пользователя.\nПример: /remove_sysadmin@SysadminHelpBot @durov")
        return
    if status == "administrator" or status == "creator":
        for i in range(1, len(call)):
            user = call[i] if call[i][0] != "@" else call[i][1:]
            sysadmins.discard(user)
    else:
        bot.send_messge(message.chat.id, "Эту функцию могут вызвать только создатель и администраторы.")

@bot.message_handler(commands=['list_sysadmins'])
def list_sysadmins_message(message):
    print(message)
    if message.chat.type != 'group' and message.chat.type != 'supergroup':
        bot.send_message(message.chat.id, "Эта функция может быть вызвана только из группы.")
        return
    status = bot.get_chat_member(message.chat.id, message.from_user.id).status
    call = message.text.split()
    if status == "administrator" or status == "creator":
        text = ""
        for i in sysadmins:
            text += "@" + i + " "
        bot.send_message(message.chat.id, text)
    else:
        bot.send_messge(message.chat.id, "Эту функцию могут вызвать только создатель и администраторы.")

@bot.message_handler(commands=['problem'])
def problem_message(message):
    print(message)
    if message.chat.type != 'group' and message.chat.type != 'supergroup':
        bot.send_message(message.chat.id, "Эта функция может быть вызвана только из группы.")
        return
    
    id = "{:09d}".format(random.randrange(10**9))
    text = "У @" + message.from_user.username + " возникла проблема. id: " + id + ".\n"
    for sa in sysadmins:
        text += "@" + sa + " ";
    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton('Заняться проблемой',callback_data=id))
    msg = bot.send_message(message.chat.id, text, reply_markup=keyboard)
    add_problem(id, datetime.utcnow(), message.from_user.id, msg.message_id, message.chat.id)

@bot.callback_query_handler(func=lambda call: call.data)
def bind_problem_query(call):
    print(call)
    if call.message.chat.type != 'group' and call.message.chat.type != 'supergroup':
        bot.send_message(message.chat.id, "Эта функция может быть вызвана только из группы.")
        return
    if call.from_user.username in sysadmins:
        if bind_problem(call.data, datetime.utcnow(), call.from_user.id):
            problem = get_problem(call.data)
            bot.edit_message_text(call.message.text + "\nПроблему решает @" + call.from_user.username + ".", 
                    chat_id=problem.chat_id, 
                    message_id=problem.bot_message_id)
        else:
            bot.answer_callback_query(callback_query_id=call.id, text="Проблему уже кто-то решает.")
    else:
        bot.answer_callback_query(callback_query_id=call.id, text="Взять проблему могут только сисадмины.")

@bot.message_handler(commands=['report'])
def report_message(message):
    if message.chat.type != 'private':
        bot.send_message(message.chat.id, "Эта функция может быть вызвана только из личной переписки со мной.")
        return
    print(message)
    text = message.text
    ind=0
    id = ""
    while ind < len(text) and text[ind] != ' ':
        ind += 1
    while ind < len(text) and text[ind] == ' ':
        ind += 1
    while ind < len(text) and text[ind].isdigit():
        id += text[ind]
        ind += 1
    while ind < len(text) and text[ind] == ' ':
        ind += 1
    report = text[ind:]
    if not id:
        bot.send_message(message.chat.id, "Пожалуйста, укажите id проблемы; его можно найти в соответствующем сообщении бота.\nПример: /get_report@SysadminHelpBot 123456789")
        return
    problem = get_problem(id)
    if not problem:
        print("Неверный id")
        return
    if str(problem.sysadmin) != str(message.from_user.id):
        bot.send_message(message.chat.id, "Извините, вы не можете отправлять отчет по этому кейсу, так как кейс был взят другим сисадмином")
        print(message.from_user.id, problem.sysadmin)
        return
    report_problem(id, datetime.utcnow(), report)

@bot.message_handler(commands=['get_report'])
def get_report_message(message):
    if message.chat.type != 'private':
        bot.send_message(message.chat.id, "Эта функция может быть вызвана только из личной переписки со мной.")
        return
    print(message)
    text = message.text
    words = text.split()
    if len(words) < 2:
        bot.send_message(message.chat.id, "Пожалуйста, укажите id проблемы; его можно найти в соответствующем сообщении бота.\nПример: /get_report@SysadminHelpBot 123456789")
        return
    id = text.split()[1]
    if not id.isdigit():
        bot.send_message(message.chat.id, "Пожалуйста, укажите id проблемы; его можно найти в соответствующем сообщении бота.\nПример: /get_report@SysadminHelpBot 123456789")
        return
    problem = get_problem(id)
    if not problem:
        bot.send_message(message.chat.id, "Неверный id")
        return
    if str(message.from_user.id) != str(problem.sysadmin):
        bot.send_message(message.chat.id, "Извините, вы не можете запросить отчет по этому кейсу, так как кейс был взят другим сисадмином")
        print(message.from_user.id, problem.sysadmin)
        return
    if problem.state != 2:
        bot.send_message(message.chat.id, "Отчет по кейсу не сдан")
        return
    bot.send_message(message.chat.id, "Пустой отчет" if not problem.report else problem.report)

def add_problem(id, time, user_id, message_id, chat_id):
    with sqlite3.connect("sysadmin.db") as db_connection:
        cursor = db_connection.cursor()
        cursor.execute('''INSERT INTO problems(id, state, from_user, occurence_time, bot_message_id, chat_id) 
                          VALUES(?, ?, ?, ?, ?, ?)''', (str(id), 0, str(user_id), str(time), str(message_id), str(chat_id)))
        for i in db_connection.execute("SELECT * FROM problems").fetchall():
            print(i)

def bind_problem(id, time, user):
    with sqlite3.connect("sysadmin.db") as db_connection:
        cursor = db_connection.cursor()
        rows = cursor.execute('''SELECT state FROM problems WHERE id = ?''', (id,)).fetchall()
        if len(rows) == 0:
            return False
        if rows[0][0] != 0:
            return False
        cursor.execute('''UPDATE problems
            SET state = 1,
                occurence_time = ? ,
                sysadmin = ?
            WHERE id = ?''', (time, user, id))
        return True

def report_problem(id, time, report):
    with sqlite3.connect("sysadmin.db") as db_connection:
        cursor = db_connection.cursor()
        cursor.execute('''UPDATE problems
            SET state = 2,
                report_time = ?,
                report = ?
            WHERE id = ?''', (time, report, id))

def get_problem(id):
    with sqlite3.connect("sysadmin.db") as db_connection:
        cursor = db_connection.cursor()
        rows = cursor.execute("SELECT * FROM problems WHERE id = ?", (id,)).fetchall()
        assert len(rows) < 2
        if len(rows) == 0:
            return None
        return Problem(rows[0])


db_connection = sqlite3.connect("sysadmin.db")
cursor = db_connection.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS problems
             (id text, 
             state integer,
             from_user text, 
             occurence_time text, 
             sysadmin text, 
             report_time text, 
             report text, 
             bot_message_id text, 
             chat_id text)''')
bot.polling()
