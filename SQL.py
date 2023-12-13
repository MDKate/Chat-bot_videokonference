import os.path
import sqlite3 as sq
import pandas as pd

async def db_start(): #Создание БД
    global db, cur
    db = sq.connect('videoconf.db')
    cur = db.cursor()
    table_name = 'Requests'
    # sheet_name = "RequestsVC"
    cur.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'")
    result = cur.fetchone()
    if result is None:
        data = pd.DataFrame([{'ID': '', 'Redact': '', 'User_id': '', 'Name': '', 'Service': '', 'Problem': '',
                                        'Degree': '', 'Address': '', 'timeV': '', 'timeAlt': ''}])
        # print(data)
        data.to_sql(table_name, sq.connect('videoconf.db'), index=False)
    db.commit()


async def user_id_record_from_db(table_name_db, user_id): #Записываем параметр user_id
    df = pd.read_sql(f"SELECT * FROM Requests", sq.connect('videoconf.db'))
    max_z = 0
    if df['ID'][0] != "":
        max_z = int(max((df['ID'].values).astype(int))+1)
        sql_update_query = f"""INSERT INTO {table_name_db}(ID, Redact, User_id, Name, Service, Problem, Degree, Address, timeV, timeAlt) 
                                VALUES ('', '', '', '', '', '', '', '', '', '')"""
        cur.execute(sql_update_query)
    sql_update_query = f"""Update {table_name_db} as A  set User_id = {user_id} where User_id = "" """
    cur.execute(sql_update_query)
    sql_update_query = f"""Update {table_name_db} as A  set ID = {max_z} where ID = "" """
    cur.execute(sql_update_query)
    sql_update_query = f"""Update {table_name_db} as A  set Redact = 1 where Redact = "" """
    cur.execute(sql_update_query)
    db.commit()

async def parametr_redact_from_db(table_name_db, user_id, parametr_name, parametr): #Редактируем таблицу
    sql_update_query = f"""Update {table_name_db} as A  set {parametr_name} = "{parametr}"
        where User_id = {user_id} and Redact = 1"""
    cur.execute(sql_update_query)
    db.commit()

async def Redact_redact_from_db(table_name_db, user_id): #Меняем статус запроса
    sql_update_query = f"""Update {table_name_db} as A  set Redact = 0
        where User_id = {user_id} and Redact = 1"""
    cur.execute(sql_update_query)
    db.commit()

async def datetime_fix_from_db(table_name_db, user_id, datetime_fix): #Записываем текущие дату и время
    sql_update_query = f"""Update {table_name_db} as A  set timeAlt = '{datetime_fix}'
        where User_id = {user_id} and Redact = 1"""
    cur.execute(sql_update_query)
    db.commit()

async def del_row_from_db(table_name, user_id): #Удаляем первую пустую строку
    sql_update_query = f"""DELETE  FROM {table_name} where User_id = {user_id} and Redact = 1"""
    cur.execute(sql_update_query)
    db.commit()

async def load_from_db(): #Получаем информацию из таблицы Requests
    df = pd.read_sql(f"SELECT * FROM Requests", sq.connect('videoconf.db'))
    return df

async def load_from_VKS_db(): #Получаем информацию из таблицы VKS
    df = pd.read_sql(f"SELECT * FROM VKS", sq.connect('videoconf.db'))
    return df

async def forward_message_from_db(user_id):
    df = pd.read_sql(f"SELECT * FROM Requests where User_id = {user_id} and Redact = 1 ", sq.connect('videoconf.db'))
    return df

async def serch_request_from_db(ID):
    df = pd.read_sql(f"SELECT * FROM Requests where ID = {ID} ", sq.connect('videoconf.db'))
    return df


# async def user_id_from_db(table_name_db, user_id, user_phone): #Вносим номер телефона участника
#     sql_update_query = f"""Update {table_name_db} as A  set user_ID = {user_id}
#         where A.ID = (
#             select ID
#             from ID
#             where user_phone = {user_phone})"""
#     cur.execute(sql_update_query)
#     db.commit()

# async def help_from_db(table_name_db, help_request, user_id): #Вносим чат-айди
#     sql_update_query = f"""Update {table_name_db} as A set help_request = {help_request}
#     where  user_ID = {user_id}"""
#     cur.execute(sql_update_query)
#     db.commit()

# async def table_help_insert_from_db(user_id, text_message): #Создаем пометку о необходимости помощи
#     # cur.execute(f"SELECT MAX(ID_help) FROM Help")
#     # result = cur.fetchone()
#     # hID = result[0] if not result[0] is None else 0
#     df = pd.read_sql(f"SELECT * FROM help",
#                      sq.connect('appointment.db'))
#     hID = len(df) if not len(df) is None else 0
#     text_message = text_message.replace("'", "*")
#     text_message = text_message.replace('"', "*")
#     sql_update_query = f"""INSERT INTO Help(ID_help, user_ID, text_message)
#                             VALUES ({int(hID)+1}, {user_id}, '{text_message}')"""
#     cur.execute(sql_update_query)
#     db.commit()
#     return hID if int(hID) > 0 else 0


# async def user_id_search_from_db(table_name_db, user_phone): #Поиск пользователя в БД
#     # cursor = db.cursor()
#     cur.execute(f"SELECT user_name "
#                 f"FROM {table_name_db} JOIN ID ON {table_name_db}.ID = ID.ID "
#                 f"WHERE user_phone = {user_phone}")
#     result = cur.fetchone()
#     # await result[0]
#     return result[0] if result else None



# async def search_from_db(parametr, table_name_db, user_ID): #Поиск любого параметра по таблице CBAppointment
#     # cursor = db.cursor()
#     cur.execute(f"SELECT {parametr} "
#                 f"FROM {table_name_db} "
#                 f"WHERE user_ID = {user_ID} ")
#     result = cur.fetchone()
#     # print(cur.execute)
#     # await result[0]
#     return result[0] if result else None


