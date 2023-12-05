import pandas as pd
import numpy as np
from datetime import datetime
import os
import pathlib
from SQL import db_start, user_id_record_from_db, parametr_redact_from_db, Redact_redact_from_db, load_from_db, \
    datetime_fix_from_db, forward_message_from_db

from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
# from aiogram.dispatcher.filters import Command
# from filters.chat_type import ChatTypeFilter

# global table_name_db
table_name_db = 'Requests'

storage = MemoryStorage()
botMes = Bot(open(os.path.abspath('token.txt')).read())
bot = Dispatcher(botMes, storage=storage)


class Form(StatesGroup):
    name = State()
    service = State()
    problem = State()
    degree = State()
    address = State()
    timeV = State()
    timeAlt = State()



async def on_startup(table_name):
    await db_start()
    print('start')

@bot.message_handler(commands=['start'])  # Начинаем работу
async def start(message: types.message, table_name_db=table_name_db):
    # keyboard = types.ReplyKeyboardRemove()
    # if keyboard.remove_keyboard == True:
    #     await message.delete_reply_markup()
    # await message.reply('', reply_markup=keyboard)
    await user_id_record_from_db(table_name_db, message.from_user.id)
    await Form.name.set()
    await botMes.send_message(message.from_user.id, "Добрый день! \nПожалуйста, введите ваше ФИО.")

@bot.message_handler(state=Form.name)  # Обработка всех текстовых сообщений
async def name_message(message: types.Message, state: FSMContext, table_name_db=table_name_db):

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add("Iva", "MTS-Link")
    await parametr_redact_from_db(table_name_db, message.from_user.id, parametr_name='Name', parametr=message.text)
    await Form.next()
    await botMes.send_message(message.from_user.id, "Выберите сервис", reply_markup=markup)


@bot.message_handler(state=Form.service)  # Обработка всех текстовых сообщений
async def service_message(message: types.Message, state: FSMContext, table_name_db=table_name_db):
    await parametr_redact_from_db(table_name_db, message.from_user.id, 'Service', message.text)
    await Form.next()
    await botMes.send_message(message.from_user.id, "Опишите проблему")


@bot.message_handler(state=Form.problem)  # Обработка всех текстовых сообщений
async def problem_message(message: types.Message, state: FSMContext, table_name_db=table_name_db):
    await parametr_redact_from_db(table_name_db, message.from_user.id, 'Problem', message.text)
    await Form.next()
    await botMes.send_message(message.from_user.id, "Введите адрес, где произошла ошибка и номер кабинета (например: Фрунзе 57/1, каб.11)")


@bot.message_handler(state=Form.degree)  # Обработка всех текстовых сообщений
async def address_message(message: types.Message, state: FSMContext, table_name_db=table_name_db):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add("Общий", "Локальный")
    await parametr_redact_from_db(table_name_db, message.from_user.id, 'Address', message.text)
    await Form.next()
    await botMes.send_message(message.from_user.id, "Оцените степень влияния сбоя", reply_markup=markup)

@bot.message_handler(state=Form.address)  # Обработка всех текстовых сообщений
async def degree_message(message: types.Message, state: FSMContext, table_name_db=table_name_db):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add("Сейчас", "Ввести врмя вручную")
    await parametr_redact_from_db(table_name_db, message.from_user.id, 'Degree', message.text)
    await Form.next()
    await botMes.send_message(message.from_user.id, "Выберите время возникновения ошибки", reply_markup=markup)

@bot.message_handler(state=Form.timeV)
async def now_message_v(message: types.Message, state: FSMContext, table_name_db=table_name_db):
    if message.text == "Сейчас":
        await parametr_redact_from_db(table_name_db, message.from_user.id, 'timeV', message.text)
        await datetime_fix_from_db(table_name_db, message.from_user.id, str(datetime.now()))
        df = await forward_message_from_db(message.from_user.id)
        messageT = f"Запрос № {df['ID'][0]} \n" \
                  f"ФИО: {df['Name'][0]} \n" \
                  f"Сервис: {df['Service'][0]} \n" \
                  f"Проблема: {df['Problem'][0]} \n" \
                  f"Адрес: {df['Address'][0]} \n" \
                  f"Влияние: {df['Degree'][0]} \n" \
                  f"Время: {df['timeAlt'][0]}"
        await Redact_redact_from_db(table_name_db, message.from_user.id)
        await state.finish()
        await botMes.send_message(open(os.path.abspath('chat.txt')).read(), messageT)
        await botMes.send_message(message.from_user.id, "Спасибо! Информация о сбое направлена в техподдержкку. "
                                                        "\n Для повторной отправки сообщения нажмите /start")
    if message.text == "Ввести врмя вручную":
        await parametr_redact_from_db(table_name_db, message.from_user.id, 'timeV', message.text)
        await Form.next()
        await botMes.send_message(message.from_user.id, "Введите время")


@bot.message_handler(state=Form.timeAlt)
async def now_message_alt(message: types.Message, state: FSMContext, table_name_db=table_name_db):
    await parametr_redact_from_db(table_name_db, message.from_user.id, 'timeAlt', message.text)
    df = await forward_message_from_db(message.from_user.id)
    messageT = f"Запрос № {df['ID'][0]} \n" \
               f"ФИО: {df['Name'][0]} \n" \
               f"Сервис: {df['Service'][0]} \n" \
               f"Проблема: {df['Problem'][0]} \n" \
               f"Адрес: {df['Address'][0]} \n" \
               f"Влияние: {df['Degree'][0]} \n" \
               f"Время: {df['timeAlt'][0]}"
    await Redact_redact_from_db(table_name_db, message.from_user.id)
    await state.finish()
    await botMes.send_message(open(os.path.abspath('chat.txt')).read(), messageT)
    await botMes.send_message(message.from_user.id, "Спасибо! Информация о сбое направлена в техподдержкку. "
                                                    "\n Для повторной отправки сообщения нажмите /start")




if __name__ == '__main__':
    # Бесконечно запускаем бот и игнорим ошибки
    while True:
        try:
            executor.start_polling(bot, on_startup=on_startup)
        except:
            pass