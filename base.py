import logging
import sqlite3
import openai
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.utils import executor
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from flask import Flask, request, render_template
import os

# Настройки
TOKEN = '7430397258:AAFZ6B8VStfnscDoeDsmP7R-b5C9n0kTXhs'
openai.api_key = 'sk-xjKOINORKIDBRko4mgFjKXV8CZpQC9iyd70GuH35j8T3BlbkFJ-gSsdu7oRg__BxLObS7N-9dOjI4jw-9_HWVNdNlKsA'

# Логирование
logging.basicConfig(level=logging.INFO)

# Инициализация базы данных
conn = sqlite3.connect('lms.db', check_same_thread=False)
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT, progress INTEGER)''')
conn.commit()

# Создаем объект бота и диспетчера
bot = Bot(token=TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
dp.middleware.setup(LoggingMiddleware())

# Создаем Flask-приложение
app = Flask(__name__, template_folder='.')

# Маршрут для веб-приложения
@app.route("/")
def web():
    return render_template('index.html')


# Состояния для квиза
class QuizState(StatesGroup):
    waiting_for_answer = State()
    question_index = State()


# Вопросы квиза
questions = [
    {
        "question": "Какой язык используется для написания Telegram ботов?\n1) Python\n2) JavaScript\n3) C++",
        "correct_answer": "1"
    },
    {
        "question": "Какой фреймворк используется для создания веб-приложений на Python?\n1) React\n2) Django\n3) Laravel",
        "correct_answer": "2"
    },
    {
        "question": "Какая библиотека используется для работы с нейронными сетями в Python?\n1) NumPy\n2) TensorFlow\n3) Flask",
        "correct_answer": "2"
    }
]


# Команда /start
@dp.message_handler(Command("start"))
async def start(message: types.Message):
    user = message.from_user
    cursor.execute('INSERT OR IGNORE INTO users (id, username, progress) VALUES (?, ?, ?)', (user.id, user.username, 0))
    conn.commit()
    await message.answer(f"Привет, {user.first_name}! Добро пожаловать в нашу LMS. Готов учиться?")


# Команда для начала квиза
@dp.message_handler(Command("quiz"))
async def start_quiz(message: types.Message, state: FSMContext):
    await state.update_data(question_index=0)  # Сохраняем индекс текущего вопроса
    await message.answer(questions[0]["question"])
    await QuizState.waiting_for_answer.set()


# Обработка ответов на вопросы
@dp.message_handler(state=QuizState.waiting_for_answer)
async def handle_quiz(message: types.Message, state: FSMContext):
    data = await state.get_data()
    question_index = data.get("question_index", 0)  # Текущий вопрос

    # Проверка правильности ответа
    if message.text == questions[question_index]["correct_answer"]:
        await message.answer("Правильно!")
        cursor.execute('UPDATE users SET progress = progress + 1 WHERE id = ?', (message.from_user.id,))
        conn.commit()

        question_index += 1  # Переходим к следующему вопросу

        # Проверка, есть ли еще вопросы
        if question_index < len(questions):
            await state.update_data(question_index=question_index)
            await message.answer(questions[question_index]["question"])
        else:
            await message.answer("Поздравляю! Вы прошли весь квиз.")
            await state.finish()
    else:
        await message.answer("Неправильно. Попробуй снова.")
        await message.answer(questions[question_index]["question"])


# Команда для завершения квиза вручную
@dp.message_handler(Command("end_quiz"), state=QuizState.waiting_for_answer)
async def end_quiz(message: types.Message, state: FSMContext):
    await message.answer("Вы завершили квиз. Спасибо за участие!")
    await state.finish()


# Интеграция с GPT
@dp.message_handler(lambda message: message.text.startswith("GPT"))
async def ask_gpt(message: types.Message):
    user_input = message.text.replace("GPT", "").strip()  # Извлекаем запрос без префикса
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": user_input}],
            max_tokens=150
        )
        await message.answer(response.choices[0].message['content'].strip())
    except Exception as e:
        await message.answer("Произошла ошибка при обработке вашего запроса. Пожалуйста, попробуйте позже.")
        print(f"Error: {e}")


# Вебхук для Telegram
@app.route('/webhook', methods=['POST'])
async def webhook():
    data = await request.get_json(force=True)
    update = types.Update(**data)
    await dp.process_update(update)
    return 'ok'


# Запуск бота
if __name__ == "__main__":
    # Использование polling для разработки
    executor.start_polling(dp, skip_updates=True)
    start_webhook(
        dispatcher=dp,
        webhook_path="/webhook",
        on_startup=None,
        on_shutdown=None,
        skip_updates=True,
        host="0.0.0.0",  # Настройки для работы на сервере
        port=8443
    )
