from datetime import datetime
import telebot
from telebot import types
import random

bot = telebot.TeleBot('1140733846:AAHW8980Rv0ZF4BweijW16XHQctcpqRLyu0')
sysadmins = { "O442A4O3", "miska924" }
problems = {}

class Problem:
    state=0
    active_sa=None
    from_user=None
    occurence_time=None
    binding_time=None
    sysadmin=None
    report_time=None
    report=None
    bot_message_id=None
    chat_id=None
    
    def __init__(self, occurence_time, from_user, bot_message_id, chat_id):
        self.occurence_time = occurence_time
        self.from_user = from_user
        self.bot_message_id = bot_message_id
        self.chat_id = chat_id

    def bind(self, time, sysadmin):
        if self.state != 0:
            return
        self.state = 1
        self.sysadmin = sysadmin
        self.binding_time = time

    def report(self, time, report):
        if self.state != 1:
            return
        self.state = 2
        self.report_time = time
        self.report = report

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
    add_problem(id, datetime.utcnow(), message.from_user.username, msg.message_id, message.chat.id)

@bot.callback_query_handler(func=lambda call: call.data)
def bind_problem_query(call):
    print(call)
    if call.message.chat.type != 'group' and call.message.chat.type != 'supergroup':
        bot.send_message(message.chat.id, "Эта функция может быть вызвана только из группы.")
        return
    if call.from_user.username in sysadmins:
        if bind_problem(call.data, datetime.utcnow(), call.from_user.id):
            bot.edit_message_text(call.message.text + "\nПроблему решает @" + call.from_user.username + ".", 
                    chat_id=problems[call.data].chat_id, 
                    message_id=problems[call.data].bot_message_id)
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
    if id not in problems:
        bot.send_message(message.chat.id, "Неверный id")
        return
    if problems[id].sysadmin != message.from_user.id:
        bot.send_message(message.chat.id, "Извините, вы не можете отправлять отчет по этому кейсу, так как кейс был взят другим сисадмином")
        print(message.from_user.id, problems[id].sysadmin)
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
    if id not in problems:
        bot.send_message(message.chat.id, "Неверный id")
        return
    if message.from_user.id != problems[id].sysadmin:
        bot.send_message(message.chat.id, "Извините, вы не можете запросить отчет по этому кейсу, так как кейс был взят другим сисадмином")
        return
    if problems[id].state != 2:
        bot.send_message(message.chat.id, "Отчет по кейсу не сдан")
        return
    bot.send_message(message.chat.id, get_report(id))

def add_problem(id, time, username, message_id, chat_id):
    problems[id]=Problem(time, username, message_id, chat_id)

def bind_problem(id, time, user):
    if problems[id].state != 0:
        return False
    problems[id].bind(time, user)
    return True

def report_problem(id, time, report):
    problems[id].report(time, report)

def get_report(id):
    return problems[id].report

bot.polling()
