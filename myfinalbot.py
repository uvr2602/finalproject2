import json
import os
import telebot
from telebot import types
from myfinallocations import locations_data

BOT_TOKEN = input("Введите токен для своего бота: ")
TOKEN = 'token'
bot = telebot.TeleBot(TOKEN)

def load_user_data():
    try:
        with open("user_data.json", "r") as file:
            return json.load(file)
    except:
        return {}

def save_user_data(user_data):
    with open("user_data.json", "w") as file:
        json.dump(user_data, file)

# Структура для хранения данных пользователя
if os.path.exists("user_data.json"):
    user_data = load_user_data() # загрузка всего джейсон файла (всех пользователей) в user_data, если такой файл существует
else:
    user_data = {}

@bot.message_handler(commands=["start"])
def start_quest(message):
    global user_data
    if str(message.chat.id) in user_data and user_data[str(message.chat.id)]['location'] not in ['find_path', 'approach_waterfall', 'explore_cave', 'talk_to_villagers']:
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        markup.add("Начало")
        markup.add("Продолжить")

        bot.send_message(message.chat.id, "Хотите продолжить с последней локации или начать заново?", reply_markup=markup)
    else:
        user_data[str(message.chat.id)] = {"location": "start"} #  в данный момент каждый раз локация сбрасывается на старт
        send_location(str(message.chat.id))

# Функция отправки локации с вариантами пути
def send_location(chat_id):
    current_location = user_data[str(chat_id)]["location"] # считываем текущую локацию пользователя из джейсона
    location_data = locations_data[current_location] # словарь конкретной локации пользователя из словаря с локациями
    description = location_data["description"] # описание локации
    options = location_data["options"] # варианты выбора пользователя следующей локации (словарь)
    picture_path = location_data["pucture"] #  путь к картинке

    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    for option_text in options: # option_text - ключ в словаре вариантов выбора
        markup.add(option_text)

    with open(picture_path, "rb") as photo:
        bot.send_photo(chat_id, photo) # bot.send_photo(chat_id, photo_url)
    bot.send_message(chat_id, description, reply_markup=markup)

# Обработчик получения ответа пользователя
@bot.message_handler(func=lambda message: True)
def handle_answer(message):
    global user_data
    chat_id = message.chat.id
    if str(chat_id) not in user_data:
        bot.send_message(chat_id, "Пожалуйста, начните анкету с помощью команды /start")
        return

    if message.text == 'Начало':
        user_data[str(chat_id)]["location"] = "start"
        send_location(str(chat_id))
    elif message.text == 'Продолжить':
        current_location = user_data[str(chat_id)]["location"]
        send_location(str(chat_id))

    current_location = user_data[str(chat_id)]["location"]
    options = locations_data[current_location]["options"]
    if message.text not in options:
        bot.send_message(chat_id, "Пожалуйста, выберите один из предложенных вариантов.")
        return

    user_data[str(chat_id)]["location"] = options[message.text] # присваивается выбор пользователя из словаря options в джейсон в текущую локацию пользователя
    send_location(str(chat_id))

    save_user_data(user_data)

# Запуск бота
bot.polling(non_stop=True)