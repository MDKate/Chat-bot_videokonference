import pandas as pd
import numpy as np
import datetime
import os
import pathlib


from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from magic_filter import F



storage = MemoryStorage()
botMes = Bot(open(os.path.abspath('token.txt')).read())
bot = Dispatcher(botMes, storage=storage)


class Form(StatesGroup):
    name = State()
    service = State()
    problem = State()
    address = State()
    timeV = State()


async def on_startup(_):
    #await db_start()
    print(1)

@bot.message_handler(commands=['start'])  # Начинаем работу
async def start(message: types.message):
    await Form.name.set()
    await botMes.send_message(message.from_user.id, "Добрый день! \nПожалуйста, введите ваше ФИО.")

@bot.message_handler(state=Form.name)  # Обработка всех текстовых сообщений
async def name_message(message: types.Message, state: FSMContext):

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    markup.add("Iva", "MTS-Link")

    await Form.next()
    await botMes.send_message(message.from_user.id, "Выберите сервис", reply_markup=markup)


@bot.message_handler(state=Form.service)  # Обработка всех текстовых сообщений
async def service_message(message: types.Message, state: FSMContext):
    await Form.next()
    await botMes.send_message(message.from_user.id, "Опишите проблему")


@bot.message_handler(state=Form.problem)  # Обработка всех текстовых сообщений
async def problem_message(message: types.Message, state: FSMContext):
    await Form.next()
    await botMes.send_message(message.from_user.id, "Введите адрес, где произошла ошибка и номер кабинета (например: Фрунзе 57/1, каб.11")


@bot.message_handler(state=Form.address)  # Обработка всех текстовых сообщений
async def address_message(message: types.Message, state: FSMContext):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    markup.add("Сейчас", "Ввести врмя вручную")

    await Form.next()
    await botMes.send_message(message.from_user.id, "Выберите время возникновения ошибки", reply_markup=markup)

@bot.message_handler(F.from_user.as_("Сейчас"))
async def now_message(message: types.Message, state: FSMContext):

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    markup.add("Общий", "Локальный")
    print(54634)
    await Form.next()
    await botMes.send_message(message.from_user.id, "Определите степень влияния сбоя", reply_markup=markup)


@bot.message_handler(F.text.lower() == "Ввести врмя вручную")
async def time_message(message: types.Message, state: FSMContext):
    print("fdghjkl")
    await Form.next()
    await botMes.send_message(message.from_user.id, "Введите время")


if __name__ == '__main__':
    # Бесконечно запускаем бот и игнорим ошибки
    while True:
        try:
            executor.start_polling(bot, on_startup=on_startup)
        except:
            pass