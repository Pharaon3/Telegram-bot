import telebot
import ast
import time
from telebot import types
import json
import sqlite3 as sql
from bot_config import BOT_API_KEY


bot = telebot.TeleBot(BOT_API_KEY)

languageList = []

con = sql.connect('bot.db')
cur =  con.cursor()

cur.execute('SELECT * FROM tbl_lang where deleted = 0')

datas = cur.fetchall()
for lang_item in datas:
    item = {}
    item['id'] = lang_item[0]
    item['lang_name'] = lang_item[1]
    languageList.append(item)    

cur =  con.cursor()

cur.execute('SELECT lang_id, bot_menu FROM tbl_visa_menu ')

datas = cur.fetchall()
menu = {}
menu_list = {}
for data in datas:

    menu_list[str(data[0])] = json.loads(data[1])['menu'][0]

def detect_object(obj, key):
    if(len(key)==0):
        return obj
    key_pop = key.pop(0) 
    # print(key)
    return detect_object(obj['nodes'][key_pop], key)  

def makeKeyboard_language():
    markup = types.InlineKeyboardMarkup()
    for lang in languageList:            
        markup.add(types.InlineKeyboardButton(text=lang['lang_name'],
                                              callback_data="{'lang': " +str(lang['id'])+ "}"))

    return markup

def makeKeyboard(obj, key):
    markup = types.InlineKeyboardMarkup()
    index_back = key.copy()
    if(not len(index_back) == 0):
        index_back.pop()
        markup.add(types.InlineKeyboardButton(text='<-- Back',
                                                callback_data="{'index': " +str(index_back)+ "}"))
    for i in range(len(obj['nodes'])):
        index = key.copy()
        index.append(i)
        menu_title = obj['nodes'][i]['text']
        markup.add(types.InlineKeyboardButton(text=menu_title,
                                              callback_data="{'index': " +str(index)+ "}"))

    return markup


@bot.message_handler(commands=['start', 'restart'])
def handle_command_adminwindow(message):
    bot.send_message(chat_id=message.chat.id,
                    text='Choose your language',
                    reply_markup=makeKeyboard_language(),
                    parse_mode='HTML')

@bot.callback_query_handler(func=lambda call: True)
def handle_query(call):
    if (call.data.startswith("{'lang'")):
        print(f"call.data : {call.data} , type : {type(call.data)}")
        print(f"ast.literal_eval(call.data) : {ast.literal_eval(call.data)} , type : {type(ast.literal_eval(call.data))}")
        call_l_data = ast.literal_eval(call.data)
        lang = call_l_data['lang']
        # print(lang, type(lang))
        global menu
        menu = menu_list[str(lang)]
        bot.send_message(chat_id=call.message.chat.id,
                text=menu['text'],
                reply_markup=makeKeyboard(menu, []),
                parse_mode='HTML')   

    if (call.data.startswith("{'index'")):
        # print(f"call.data : {call.data} , type : {type(call.data)}")
        # print(f"ast.literal_eval(call.data) : {ast.literal_eval(call.data)} , type : {type(ast.literal_eval(call.data))}")
        call_data = ast.literal_eval(call.data)
        key = call_data['index']
        key_obj = key.copy()
        obj = detect_object(menu, key_obj)
        
        
        if(not len(obj['nodes'])==0):
            if(len(key)== 0):
                bot.send_message(chat_id=call.message.chat.id,
                        text=obj['text'],
                        reply_markup=makeKeyboard(obj, key),
                        parse_mode='HTML')
            else:
                bot.send_message(chat_id=call.message.chat.id,
                        text=obj['description'],
                        reply_markup=makeKeyboard(obj, key),
                        parse_mode='HTML')
        else:
            if 'info' in obj.keys():
                markup_url = types.InlineKeyboardMarkup()
                markup_url.add(types.InlineKeyboardButton(text = obj['text'], url= obj['info']))
                bot.send_message(chat_id=call.message.chat.id,
                        text = 'info',
                        reply_markup=markup_url,
                        parse_mode='HTML')             
            elif 'contact' in obj.keys():
                bot.send_message(chat_id=call.message.chat.id,
                        text= "Please contact us to link: \n"+obj['contact'],
                        parse_mode='HTML')
            elif 'description' in obj.keys():
                bot.send_message(chat_id=call.message.chat.id,
                        text= obj['description'],
                        parse_mode='HTML')    


while True:
    try:        
        bot.polling(none_stop=True, interval=0, timeout=0)
    except:
        time.sleep(10)
