import telebot
from telebot import types

bot = telebot.TeleBot('1140733846:AAHW8980Rv0ZF4BweijW16XHQctcpqRLyu0')
sysadmins = []
problems = []

class Problem:
    state=0
    active_sa=None
    from_user
    occurence_time
    problem_taken_time
    finish_time
    report=None
    
    def __init__(self, occurence_time, from_user):
        self.occurence_time = occurence_time
        self.from_user = from_user

    def problem_taken(self, time, sa):
        if self.state != 0:
            return
        self.state = 1
        self.active_sa = sa
        self.occurence_time = time

    def finish(self, time):
        if self.state != 1:
            return
        self.state = 2
        self.finish_time = time

    def submit_report(self, report):
        if self.state != 2:
            return
        self.report = report



@bot.message_handler(commands=['start'])
def start_message(message):
    print(message)
    bot.send_message(message.chat.id, '/start: TODO')

@bot.message_handler(commands=['add_sysadmin'])
def add_sysadmin_message(message):
    #TODO
    pass

@bot.message_handler(commands=['remove_sysadmin'])
def remove_sysadmin_message(message):
    #TODO
    pass

@bot.message_handler(commands=['list_sysadmin'])
def list_sysadmin_message(message):
    #TODO
    pass

@bot.message_handler(commands=['problem'])
def problem_message(message):
    print(message)
    if message.chat.type != 'group' and message.chat.type != 'supergroup':
        bot.send_message(message.chat.id, "Извините, эта функция может быть вызвана только из группы.")
        return

    #Убрать несуществующих сисадминов
    '''
    if not sysadmins:
        bot.send_message(message.chat.id, "В чате нет сисадминов. Чтобы присвоить такую должность, администратор чата должен добавить сисадмина командой /add_sysadmin @[никнейм сисадмина]")
        return
    '''
    
    text = "У @" + message.from_user.username + " возникла проблема. id проблемы: " + str(len(problems)) + "\n"
    problems.append(
    for sa in sysadmins:
        text += "@" + sa;
    keyboard = telebot.types.InlineKeyboardMarkup()
    ui = types.InlineKeyboardButton('Заняться проблемой',url='https://google.com')
    keyboard.add(ui)
    bot.send_message(message.chat.id, text, reply_markup=keyboard)
        

bot.polling()
