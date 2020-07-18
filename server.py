import datetime
import telebot
from telebot import types
import time
import os
from db import *
from logs import *
from utils import *
from problem import *
from user import User

bot = telebot.TeleBot('1356395096:AAHzRpEMZdjHNLDOT2xrBirbMfehCYFe2sE')
MY_NAME = bot.get_me().username

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

@bot.message_handler(commands=['help','start'])
@query_handler
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
@query_handler
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
@query_handler
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
@query_handler
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
@query_handler
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
@callback_handler
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
@query_handler
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
@query_handler
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
@query_handler
def get_time_period_report_message(message):
    if not supported_chat(message, private_allowed=True):
        return
    INCORRECT_FORMAT_MESSAGE = "Неверный формат запроса!\nПример: /get_time_period_report 5.7.2020 15.7.2020 - запрос всех отчетов с 5 июля 2020 года по 15 июля 2020 года"
    text = message.text
    words = text.split()
    if len(words) != 3:
        bot.send_message(message.chat.id, INCORRECT_FORMAT_MESSAGE)
        return
    date1 = words[1].split('.')
    date2 = words[2].split('.')
    if len(date1) != 3 or len(date2) != 3:
        bot.send_message(message.chat.id, INCORRECT_FORMAT_MESSAGE)
        print("lol")
        return
    try:
        date1 = datetime.datetime(int(date1[2]), int(date1[1]), int(date1[0]))
        date2 = datetime.datetime(int(date2[2]), int(date2[1]), int(date2[0]))
    except:
        bot.send_message(message.chat.id, INCORRECT_FORMAT_MESSAGE)
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
    report = "Отчет о работе с {:02d}.{:02d}.{:04d} по {:02d}.{:02d}.{:04d}\n\n".format(date1.day, date1.month, date1.year, date2.day, date2.month, date2.year)
    i = 1
    for problem in problems:
        occurence_time = datetime.datetime.fromtimestamp(float(problem.occurence_time))
        binding_time = datetime.datetime.fromtimestamp(float(problem.binding_time))
        report_time = datetime.datetime.fromtimestamp(float(problem.report_time))
        format_string = "{:02d}.{:02d}.{:04d} {:02d}:{:02d}:{:02d}"
        occurence_time = format_string.format(occurence_time.day, occurence_time.month, occurence_time.year, occurence_time.hour, occurence_time.minute, occurence_time.second)
        binding_time = format_string.format(binding_time.day, binding_time.month, binding_time.year, binding_time.hour, binding_time.minute, binding_time.second)
        report_time = format_string.format(report_time.day, report_time.month, report_time.year, report_time.hour, report_time.minute, report_time.second)
        user = users[problem.from_user].last_name + " " + users[problem.from_user].first_name
        problem_report = "{})\nСотрудник: {}\nВремя возникновения: {}\nВремя принятия: {}\nВремя сдачи отчета: {}\nОтчет:\n{}\n\n".format(i, user, occurence_time, binding_time, report_time, problem.report)
        report += problem_report
        i += 1
    report_file.write(report)
    report_file.close()
    report_file = open("./report_file.txt", "r")
    bot.send_document(message.chat.id, report_file)
    report_file.close()

init()
bot.polling()
