from db import add_user
import time

def query_log(message):
    tm = time.time()
    query_log = open("./logs/" + str(tm), "x")
    query_log.write(str(message))
    query_log.close()

def callback_log(message):
    tm = time.time()
    query_log = open("./logs/" + str(tm), "x")
    query_log.write(str(message))
    query_log.close()
    print("Callback \"" + function.__name__ + "\" in chat " + str(message.message.chat.id) + " from " + str(message.from_user.id) + " is at ./logs/" + str(tm))

def query_handler(function):
    def wrapper(message):
        user = message.from_user
        add_user(str(user.id), user.username, user.first_name, user.last_name)
        query_log(message)
        function(message)
    return wrapper

def callback_handler(function):
    def wrapper(message):
        user = message.from_user
        add_user(user.id, user.username, user.first_name, user.last_name)
        callback_handler(message)
        function(message)
    return wrapper

def log(message, description):
    tm = time.time()
    query_log = open("./logs/" + str(tm), "x")
    query_log.write(str(message))
    query_log.close()
    print(description + " at ./logs/" + str(tm))
