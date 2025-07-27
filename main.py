import telebot
import requests
import random
from telebot import types
from dictionaries import idinah_list, hello_list


TELEGRAM_TOKEN = '7266703224:AAHLwpIqBE-Rd9NVkSmD-bSD0IR6clmdSOQ'
API_KEY = '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'
API_URL = 'https://openrouter.ai/api/v1/chat/completions'
MODEL = "mistralai/mistral-7b-instruct"

mtvzg_bot = telebot.TeleBot(TELEGRAM_TOKEN)


@mtvzg_bot.message_handler(commands=['start'])
def start_message(message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
    buttons = ["Привет", "Помощь", "Что ты умеешь?", "Вопрос"]
    keyboard.add(*[types.KeyboardButton(btn) for btn in buttons])
    mtvzg_bot.send_chat_action(message.chat.id, 'typing')

    random_greeting = random.choice(hello_list)
    mtvzg_bot.send_message(
        message.chat.id,
        f'{random_greeting}, {message.from_user.first_name}! Нажми /start, чтобы начать.',
        reply_markup=keyboard
    )


@mtvzg_bot.message_handler(commands=['ask'])
def ask_handler(message):
    msg = mtvzg_bot.send_message(message.chat.id, "Напиши свой вопрос:")
    mtvzg_bot.register_next_step_handler(msg, ask_gpt)


def ask_gpt(message):
    user_question = message.text

    mtvzg_bot.send_chat_action(message.chat.id, 'typing')

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://t.me/mtvzgSupportBot",  # ОБЯЗАТЕЛЬНО, иначе может быть ошибка
        "X-Title": "TelegramBot"
    }

    payload = {
        "model": MODEL,
        "messages": [{"role": "user", "content": user_question}],
        "temperature": 0.7
    }

    try:
        response = requests.post(API_URL, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()
        reply = data["choices"][0]["message"]["content"]
    except Exception as e:
        reply = f"Ошибка при запросе к GPT: {e}"

    mtvzg_bot.send_message(message.chat.id, reply)


@mtvzg_bot.message_handler(func=lambda msg: True)
def check_input_messages(message):
    mtvzg_bot.send_chat_action(message.chat.id, 'typing')
    text = message.text.lower()

    if text in idinah_list:
        mtvzg_bot.reply_to(message, 'Ты иди нахуй!')
    elif text in hello_list:
        mtvzg_bot.reply_to(message, random.choice(hello_list))
    elif message.text == "Помощь":
        mtvzg_bot.reply_to(message, "Я могу помочь с разными вопросами! Напиши, что нужно.")
    elif message.text == "Что ты умеешь?":
        mtvzg_bot.reply_to(message,
                           "Я могу:\n1. Поздороваться\n2. Ответить на команды\n3. Похамить, если что 😜\n4. Ответить на вопросы через /ask")
    elif message.text == "Вопрос":
        ask_handler(message)
    else:
        mtvzg_bot.reply_to(message, "Не понял. Попробуй /ask или нажми /start.")


print("Бот запущен!")
mtvzg_bot.polling(none_stop=True)

