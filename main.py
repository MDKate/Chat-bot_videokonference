# Импорт библиотек
import pandas as pd
import numpy as np
from datetime import datetime
import os
import pathlib
import sqlite3 as sq
from SQL import db_start, user_id_record_from_db, parametr_redact_from_db, Redact_redact_from_db, load_from_db, \
    datetime_fix_from_db, forward_message_from_db, del_row_from_db, load_from_VKS_db, serch_request_from_db

from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage


# Имя таблицы в БД
table_name_db = 'Requests'
#Подключаемся к боту
storage = MemoryStorage()
botMes = Bot(open(os.path.abspath('token.txt')).read())
bot = Dispatcher(botMes, storage=storage)

#Формируем список состояний
class Form(StatesGroup):
    name = State()
    service = State()
    problem = State()
    address_building = State()
    address = State()
    address_other = State()
    degree = State()
    timeV = State()
    timeAlt = State()

class Doc(StatesGroup):
    file = State()

class Req(StatesGroup):
    search = State()

#Текст сообщения
start_message = 'Если чаб-бот завис или вы передумали, то нажмите кнопку "Выйти"' \
                '\n Для повторной отправки сообщения нажмите /start'


#Создание БД
async def on_startup(table_name):
    await db_start()
    print('start')



@bot.message_handler(commands=['start'])  # Начинаем работу
async def start(message: types.message, table_name_db=table_name_db):
    await del_row_from_db(table_name_db, message.from_user.id)
    #Добавляем пользователя в БД
    await user_id_record_from_db(table_name_db, message.from_user.id)
    # Формируем кнопки
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add("Выйти")
    #Переходим в следующее состояние
    await Form.name.set()
    #Отправляем сообщение
    await botMes.send_message(message.from_user.id, "Добрый день! \nПожалуйста, введите ваше ФИО.", reply_markup=markup)

@bot.message_handler(state=Form.name)  # Получаем имя
async def name_message(message: types.Message, state: FSMContext, table_name_db=table_name_db, start_message=start_message):
    # проверяем, хочет ли пользователь сбросить состояние
    if message.text == "Выйти":
        # Удаляем пустые записи в БД
        await del_row_from_db(table_name_db, message.from_user.id)
        await state.finish()
        await botMes.send_message(message.from_user.id, start_message)
    else:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        markup.add("Iva", "MTS-Link")
        markup.add("Выйти")
        # Вносим имя
        await parametr_redact_from_db(table_name_db, message.from_user.id, parametr_name='Name', parametr=message.text)
        await Form.next()
        await botMes.send_message(message.from_user.id, "Выберите сервис", reply_markup=markup)


@bot.message_handler(state=Form.service)  # Выбор сервиса
async def service_message(message: types.Message, state: FSMContext, table_name_db=table_name_db):
    if message.text == "Выйти":
        await del_row_from_db(table_name_db, message.from_user.id)
        await state.finish()
        await botMes.send_message(message.from_user.id, start_message)
    else:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        if message.text == "Iva" or message.text == "MTS-Link":
            # Вносим название сервиса
            markup.add("Выйти")
            await parametr_redact_from_db(table_name_db, message.from_user.id, 'Service', message.text)
            await Form.next()
            await botMes.send_message(message.from_user.id, "Опишите проблему", reply_markup=markup)
        else:
            markup.add("Iva", "MTS-Link")
            markup.add("Выйти")
            await Form.service.set()
            await botMes.send_message(message.from_user.id, "Пожалуйста, воспользуйтесь кнопками!", reply_markup=markup)


@bot.message_handler(state=Form.problem)  # Получаем описание проблемы
async def problem_message(message: types.Message, state: FSMContext, table_name_db=table_name_db):
    if message.text == "Выйти":
        await del_row_from_db(table_name_db, message.from_user.id)
        await state.finish()
        await botMes.send_message(message.from_user.id, start_message)
    else:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        #Записываем в БД описание проблемы
        await parametr_redact_from_db(table_name_db, message.from_user.id, 'Problem', message.text)
        await Form.address_building.set()
        #Получаем список зданий и генерим соответственно кнопки
        df = await load_from_VKS_db()
        df = df['Адрес'].unique()
        for i in range(0, len(df)):
            markup.add(df[i])
        markup.add("Выйти")
        await botMes.send_message(message.from_user.id,
                                  "Выберите здание, в котором наблюдается ошибка",
                                  reply_markup=markup)

@bot.message_handler(state=Form.address_building)  # Получаем описание проблемы
async def problem_message(message: types.Message, state: FSMContext, table_name_db=table_name_db):
    if message.text == "Выйти":
        await del_row_from_db(table_name_db, message.from_user.id)
        await state.finish()
        await botMes.send_message(message.from_user.id, start_message)
    else:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        #Записываем в БД описание проблемы
        await parametr_redact_from_db(table_name_db, message.from_user.id, 'Address', message.text)
        await Form.address.set()
        #Генерим помещения по адресам, перезаписываем адрес
        df = await load_from_VKS_db()
        mes = await forward_message_from_db(message.from_user.id)
        df = df[df['Адрес'] == mes['Address'][0]]
        df = df['Помещение'].unique()
        for i in range(0, len(df)):
            markup.add(df[i])
        markup.add("Другое помещение", "Выйти")
        await botMes.send_message(message.from_user.id,
                                  "Выберите помещение, в котором наблюдается ошибка",
                                  reply_markup=markup)


@bot.message_handler(state=Form.address)  # Записываем адрес
async def address_message(message: types.Message, state: FSMContext, table_name_db=table_name_db):
    if message.text == "Выйти":
        await del_row_from_db(table_name_db, message.from_user.id)
        await state.finish()
        await botMes.send_message(message.from_user.id, start_message)
    else:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        markup.add("Общий", "Локальный")
        markup.add("Выйти")
        # Вносим адрес в БД
        mes = await forward_message_from_db(message.from_user.id)
        if message.text != "Другое помещение":
            # Перезаписываем адрес
            mes = mes['Address'][0] + ', ' + message.text
            await parametr_redact_from_db(table_name_db, message.from_user.id, 'Address', mes)
            await Form.degree.set()
            await botMes.send_message(message.from_user.id, "Оцените степень влияния сбоя", reply_markup=markup)
        else:
            await Form.address_other.set()
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
            markup.add("Выйти")
            await botMes.send_message(message.from_user.id, "Введите другой номер помещения", reply_markup=markup)

@bot.message_handler(state=Form.address_other)  # Записываем адрес
async def address_message(message: types.Message, state: FSMContext, table_name_db=table_name_db):
    if message.text == "Выйти":
        await del_row_from_db(table_name_db, message.from_user.id)
        await state.finish()
        await botMes.send_message(message.from_user.id, start_message)
    else:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        markup.add("Общий", "Локальный")
        markup.add("Выйти")
        # Вносим адрес в БД
        mes = await forward_message_from_db(message.from_user.id)
        mes = mes['Address'][0] + ', ' + message.text
        await parametr_redact_from_db(table_name_db, message.from_user.id, 'Address', mes)
        await Form.degree.set()
        await botMes.send_message(message.from_user.id, "Оцените степень влияния сбоя", reply_markup=markup)

@bot.message_handler(state=Form.degree)  # Записываем степень охвата
async def degree_message(message: types.Message, state: FSMContext, table_name_db=table_name_db):
    if message.text == "Выйти":
        await del_row_from_db(table_name_db, message.from_user.id)
        await state.finish()
        await botMes.send_message(message.from_user.id, start_message)
    else:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        if message.text == "Общий" or message.text == "Локальный":
            markup.add("Сейчас", "Ввести время вручную")
            markup.add("Выйти")
            # Вносим в БД Степень охвата
            await parametr_redact_from_db(table_name_db, message.from_user.id, 'Degree', message.text)
            await Form.next()
            await botMes.send_message(message.from_user.id, "Выберите время возникновения ошибки", reply_markup=markup)
        else:
            markup.add("Общий", "Локальный")
            markup.add("Выйти")
            await Form.degree.set()
            await botMes.send_message(message.from_user.id, "Пожалуйста, воспользуйтесь кнопками!", reply_markup=markup)

@bot.message_handler(state=Form.timeV) # Выбираем тип времени
async def now_message_v(message: types.Message, state: FSMContext, table_name_db=table_name_db, start_message=start_message):
    if message.text == "Выйти":
        await del_row_from_db(table_name_db, message.from_user.id)
        await state.finish()
        await botMes.send_message(message.from_user.id, start_message)
    else:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        markup.add("Выйти")
        if message.text == "Сейчас": # Если нужно фиксировать текущее время
            #Вносим информацию в БД
            await parametr_redact_from_db(table_name_db, message.from_user.id, 'timeV', message.text)
            #Пересылаем сообщение в чат сопровождения
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
            await botMes.send_message(message.from_user.id, "Спасибо! Информация о сбое направлена в техподдержкку. ",
                                      reply_markup=markup)
            await botMes.send_message(message.from_user.id, start_message)
        elif message.text == "Ввести время вручную": # Если нужно внести время вручную
            # Вносим информацию в БД
            await parametr_redact_from_db(table_name_db, message.from_user.id, 'timeV', message.text)
            await Form.next()
            await botMes.send_message(message.from_user.id, "Введите время", reply_markup=markup)
        else: # Если пользователь ввел непредусмотренное сообщение
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
            markup.add("Сейчас", "Ввести время вручную")
            markup.add("Выйти")
            # Откатиться обратно
            await state.set_state(Form.timeV)
            await botMes.send_message(message.from_user.id, "Пожалуйста, воспользуйтесь кнопками", reply_markup=markup)



@bot.message_handler(state=Form.timeAlt) #Вносим время вручную
async def now_message_alt(message: types.Message, state: FSMContext, table_name_db=table_name_db, start_message=start_message):
    if message.text == "Выйти":
        await del_row_from_db(table_name_db, message.from_user.id)
        await state.finish()
        await botMes.send_message(message.from_user.id, start_message)
    else:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        markup.add("Выйти")
        # Вносим информацию в БД
        await parametr_redact_from_db(table_name_db, message.from_user.id, 'timeAlt', message.text)
        #Пересылаем сообщение в чат сопровождения
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
        await botMes.send_message(message.from_user.id, "Спасибо! Информация о сбое направлена в техподдержкку. ",
                                  reply_markup=markup)
        await botMes.send_message(message.from_user.id, start_message)

@bot.message_handler(commands=['help'])  # Помощь
async def start(message: types.message):
    #Отправляем сообщение
    await botMes.send_message(message.from_user.id, "Справочник команд администратора:\n"
                                                    "/update_vks - обновить в базе таблицу vks\n"
                                                    "/dload_filt_vks - получить информацию о vks по фильтру")

@bot.message_handler(commands=['update_vks'])  # обновить в базе таблицу vks
async def start(message: types.message, table_name_db=table_name_db):
    await Doc.file.set()
    #Отправляем сообщение
    await botMes.send_message(message.from_user.id, "Отправьте в чат файл. Названя столбцов не должны меняться. "
                                                    "Не должно быть лишних пометок.")

@bot.message_handler(content_types=types.ContentType.DOCUMENT, state=Doc.file)  # Обрабатываем документ
async def doc_message(message: types.Message, state: FSMContext, table_name_db=table_name_db):
    document = message.document
    if ".xlsx" in document.file_name:
        docName = document.file_name.partition('.')[0]
        try:
            os.remove(os.path.abspath(docName + '.xlsx'))
        except:
            pass
        await document.download(destination_file=f'{document.file_name}')
        table_replace = pd.read_excel(os.path.abspath(document.file_name))
        table_replace.to_sql(docName, sq.connect('videoconf.db'), if_exists='replace', index=False)
        await state.finish()
        await botMes.send_message(message.from_user.id, "Таблица обновлена!")
    else:
        await Doc.file.set()
        await botMes.send_message(message.from_user.id, "Отправьте файл в формате xlsx!")

@bot.message_handler(commands=['dload_filt_vks'])  # получить информацию о vks по фильтру
async def start(message: types.message, table_name_db=table_name_db):
    await Req.search.set()
    await botMes.send_message(message.from_user.id, "Введите номер запроса, по которому нужна информация")

@bot.message_handler(state=Req.search)  # Генерим подробное описание
async def doc_message(message: types.Message, state: FSMContext, table_name_db=table_name_db):
    df = await serch_request_from_db(str(message.text))
    s = df['Address'][0]
    sep = ', '
    s = [x+sep for x in s.split(sep)]
    s = [x[:-2] for x in s]
    df = await load_from_VKS_db()
    df = df[df['Адрес'] == s[0]]
    print(len(s))
    df = df[df['Помещение'] == s[1]]
    if df.empty == True:
        await botMes.send_message(message.from_user.id, "Данных по такому адресу нет в таблице VKS!")
    else:
        for i in range(0, df.shape[1]):
            await botMes.send_message(message.from_user.id, f"{df.columns[i]} {df[df.columns[i]].values[0]}")
    await state.finish()


if __name__ == '__main__':
    # Бесконечно запускаем бот и игнорим ошибки
    while True:
        try:
            executor.start_polling(bot, on_startup=on_startup, timeout=2)
        except:
            pass