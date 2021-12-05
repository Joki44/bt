import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from config import TOKEN
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from config import TOKEN, HOST, USER, PASSWORD, DB_NAME
import pymysql


logging.basicConfig(level=logging.INFO)
bot = Bot(token=TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
dp.middleware.setup(LoggingMiddleware())
loop = asyncio.get_event_loop()


games = {}
publickGames = []

try:
    
    connection = pymysql.connect(
        host=HOST,
        port=3306,
        user=USER,
        passwd=PASSWORD,
        database=DB_NAME,
        cursorclass=pymysql.cursors.DictCursor
    )

    
    try:
        with connection.cursor() as cursor:
            create = "CREATE TABLE users (id int AUTO_INCREMENT, tele_id int, tele_name varchar(32), cash int, chips int, wins_day_value int, wins_week_value int, wins_all_time int, in_game boolean, table_id varchar(32), PRIMARY KEY (id));"
            cursor.execute(create)
    except Exception as ex:
        print(ex)
    
    
    
    try:
        with connection.cursor() as cursor:
            create = "CREATE TABLE payments (id int AUTO_INCREMENT, tele_id int, chips boolean, value int, order_id int, PRIMARY KEY (id));"
            cursor.execute(create)
    except Exception as ex:
        print(ex)
        
        
    try:
        with connection.cursor() as cursor:
            create = "CREATE TABLE friends (id int AUTO_INCREMENT, first_friend int, second_friend int, PRIMARY KEY (id));"
            cursor.execute(create)
    except Exception as ex:
        print(ex)
    
    
    
except Exception as ex:
    print("Проблема подключения к бд")
    print(ex)