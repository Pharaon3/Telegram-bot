from flask import Flask, render_template, request, jsonify, redirect
import json

import sqlite3 as sql

bot_temp = {}
bot_temp['menu'] = [];

temp_node = {}
temp_node['nodes'] = []
temp_node['text'] = 'temp_name'
bot_temp['menu'].append(temp_node)



app = Flask(__name__)

con = sql.connect('bot.db')
cur =  con.cursor()

@app.route('/')
def index():
    return render_template('home.html')

@app.route('/lang')
def get_lang():
    con = sql.connect('bot.db')
    cur =  con.cursor()

    cur.execute('SELECT * FROM tbl_lang where deleted = 0')

    datas = cur.fetchall()
    lang_data = []
    for lang in datas:
        data ={}
        data['id'] = lang[0]
        data['name'] = lang[1]
        lang_data.append(data) 
    return render_template('language.html', lang_data=lang_data)
    

@app.route('/lang/add', methods = ['POST', 'GET'])
def add_lang():
    if request.method == "POST":
        req_data = request.get_json()
        lang_name = req_data[0]['name']

        con = sql.connect('bot.db')
        cur =  con.cursor()
        cur.execute('INSERT into tbl_lang (lang_name, deleted) VALUES(?, 0)', (lang_name,))
        con.commit()
        cur.execute('SELECT * FROM tbl_lang ORDER BY id DESC LIMIT 1')
        last_insert = cur.fetchone()
        # print(last_insert)

        cur =  con.cursor()
        cur.execute('INSERT into tbl_visa_menu (lang_id, bot_menu) VALUES(?, ?)', (last_insert[0], json.dumps(bot_temp)))
        con.commit()

        results = {'result': 'Add language successfully',
                'insert_id': last_insert[0]}

        
    return jsonify(results)

@app.route('/lang/update', methods=['POST', 'GET'])
def update_lang():
    if request.method == 'POST':
        req_data = request.get_json()
        update_id = req_data[0]['id']
        update_lang = req_data[1]['name']
        con = sql.connect('bot.db')
        cur =  con.cursor()
        cur.execute('update tbl_lang set lang_name = ? where id = ?', (update_lang, update_id))
        con.commit()

        results = {'msg': 'Update language successfully'}

    return jsonify(results)

@app.route('/lang/delete', methods=['POST', 'GET'])
def delete_lang():
    if request.method == 'POST':
        req_data = request.get_json()
        delete_id = req_data[0]['id']
        con = sql.connect('bot.db')
        cur =  con.cursor()
        cur.execute('update tbl_lang set deleted = 1 where id = ?', (delete_id, ))
        con.commit()

        results = {'msg': 'Update language successfully'}
    return jsonify(results)
    
@app.route('/manage/visametrics')
def manage_visa():
    con = sql.connect('bot.db')
    cur =  con.cursor()

    cur.execute('SELECT * FROM tbl_lang where deleted = 0')

    datas = cur.fetchall()
    lang_data = []
    for lang in datas:
        data ={}
        data['id'] = lang[0]
        data['name'] = lang[1]
        lang_data.append(data) 
    return render_template('visametrics.html', lang_data=lang_data)

@app.route('/manage/visametrics/get', methods=['GET', 'POST'])
def get_manage_visametrics():
    if request.method == 'POST':
        
        req_data = request.get_json()
        lang_id = req_data[0]['id']
        
        con = sql.connect('bot.db')
        cur =  con.cursor()
        cur.execute('select bot_menu from tbl_visa_menu where lang_id = ?', (lang_id,))
        menu_data = cur.fetchone()        
        con.commit()

        data = json.loads(menu_data[0])
        results = {
            'data': json.dumps(data['menu'])
        }
    return jsonify(results)         

@app.route('/manage/visametrics/add', methods=['GET', 'POST'])
def add_manage_visametrics():
    if request.method == "POST":
        req_data = request.get_json()
        name = req_data[0]['name']
        description = req_data[1]['description']
        type = req_data[2]['type']
        contact = req_data[3]['contact']
        info = req_data[4]['info']
        node_id = req_data[5]['node_id']
        data_menu = json.loads(req_data[6]['data_menu'])
        lang_id = req_data[7]['lang_id']

        
        if (type == 'c'):

            add_item = {}
            add_item['nodes'] = []
            add_item['text'] = name
            add_item['contact'] = contact
            obj = {}
            obj['nodes'] = []
            obj['nodes']= data_menu

            def add_rec(obj, key, index):
                if(key == index):
                    obj['nodes'].append(add_item)
                    return 0
                idx = index
                for i in range(len(obj['nodes'])):
                    idx = add_rec(obj['nodes'][i], key, idx+1)
                    if(idx == 0): return 0
                return idx
            add_rec(obj, node_id+1, 0)
            data_menu=obj['nodes']
            update_item = {}
            update_item['menu'] = obj['nodes']
            txt = json.dumps(update_item)
            con = sql.connect('bot.db')
            cur =  con.cursor()
            cur.execute('UPDATE tbl_visa_menu SET  bot_menu= ? where lang_id= ?', (txt, lang_id))

            con.commit()

        elif (type=='i'):
            add_item = {}
            add_item['nodes'] = []
            add_item['text'] = name
            add_item['info'] = info
            obj = {}
            obj['nodes'] = []
            obj['nodes']= data_menu

            def add_rec(obj, key, index):
                if(key == index):
                    obj['nodes'].append(add_item)
                    return 0
                idx = index
                for i in range(len(obj['nodes'])):
                    idx = add_rec(obj['nodes'][i], key, idx+1)
                    if(idx == 0): return 0
                return idx
            add_rec(obj, node_id+1, 0)
            data_menu=obj['nodes']
            update_item = {}
            update_item['menu'] = obj['nodes']
            txt = json.dumps(update_item)
            con = sql.connect('bot.db')
            cur =  con.cursor()
            cur.execute('UPDATE tbl_visa_menu SET  bot_menu= ? where lang_id= ?', (txt, lang_id))

            con.commit()
        elif (type=='d'):
            add_item = {}
            add_item['nodes'] = []
            add_item['text'] = name
            add_item['description'] = description
            obj = {}
            obj['nodes'] = []
            obj['nodes']= data_menu

            def add_rec(obj, key, index):
                if(key == index):
                    obj['nodes'].append(add_item)
                    return 0
                idx = index
                for i in range(len(obj['nodes'])):
                    idx = add_rec(obj['nodes'][i], key, idx+1)
                    if(idx == 0): return 0
                return idx
            add_rec(obj, node_id+1, 0)
            data_menu=obj['nodes']
            update_item = {}
            update_item['menu'] = obj['nodes']
            txt = json.dumps(update_item)
            con = sql.connect('bot.db')
            cur =  con.cursor()
            cur.execute('UPDATE tbl_visa_menu SET  bot_menu= ? where lang_id= ?', (txt, lang_id))

            con.commit()


    results = {'data': json.dumps(data_menu)}
    return jsonify(results)

@app.route('/manage/visametrics/update', methods=['GET', 'POST'])
def update_manage_visametrics():
    if request.method == "POST":
        req_data = request.get_json()
        name = req_data[0]['name']
        description = req_data[1]['description']
        contact = req_data[2]['contact']
        info = req_data[3]['info']
        node_id = req_data[4]['node_id']
        data_menu = json.loads(req_data[5]['data_menu'])
        lang_id = req_data[6]['lang_id']
        obj = {}
        obj['nodes'] = []
        obj['nodes']= data_menu
        edit_data = {}
        if(name != ''):
            edit_data['text'] = name
        if(description != ''):
            edit_data['description'] = description
        if(contact != ''):
            edit_data['contact'] = contact
        if(info != ''):
            edit_data['info'] = info
        
        def edit_rec(obj, key, index):
            if(key == index):
                if 'text' in edit_data.keys():
                    obj_key_list=[]
                    for key_obj in obj.keys():
                        obj_key_list.append(key_obj)
                    # print(obj_key_list)
                    obj_key_list.remove('nodes')
                    for key_list in obj_key_list:
                        obj.pop(key_list)

                    obj['text'] = edit_data['text']
                    if 'description' in edit_data.keys():
                        obj['description'] = edit_data['description']
                    if 'contact' in edit_data.keys():
                        obj['contact'] = edit_data['contact']
                    if 'info' in edit_data.keys():
                        obj['info'] = edit_data['info']                    

                else:
                    obj_key_list=[]
                    for key_obj in obj.keys():
                        obj_key_list.append(key_obj)
                    # print(obj_key_list)
                    obj_key_list.remove('nodes')
                    obj_key_list.remove('text')
                    for key_list in obj_key_list:
                        obj.pop(key_list)
                    if 'description' in edit_data.keys():
                        obj['description'] = edit_data['description']
                    if 'contact' in edit_data.keys():
                        obj['contact'] = edit_data['contact']
                    if 'info' in edit_data.keys():
                        obj['info'] = edit_data['info']
                # print(obj)
                return 0
                
            idx = index
            for i in range(len(obj['nodes'])):
                idx = edit_rec(obj['nodes'][i], key, idx+1)
                if(idx == 0): return 0
            return idx
        edit_rec(obj, node_id+1, 0)
        data_menu=obj['nodes']
        update_item = {}
        update_item['menu'] = obj['nodes']
        txt = json.dumps(update_item)
        con = sql.connect('bot.db')
        cur =  con.cursor()
        cur.execute('UPDATE tbl_visa_menu SET  bot_menu= ? where lang_id= ?', (txt, lang_id))

        con.commit()
        edit_data['node_id']=node_id
    results = {'data': json.dumps(data_menu),
                'view_data': edit_data}
    return jsonify(results)


@app.route('/manage/visametrics/delete', methods=['GET', 'POST'])
def delete_manage_visametrics():
    if request.method == "POST":
        req_data = request.get_json()
        node_id = req_data[0]['node_id']
        data_menu = json.loads(req_data[1]['data_menu'])
        lang_id = req_data[2]['lang_id']
        obj = {}
        obj['nodes'] = []
        obj['nodes']= data_menu

        def delete_rec(obj, key, index):
            if(key == index):
                obj.clear()
                return 0
            idx = index
            for i in range(len(obj['nodes'])):
                idx = delete_rec(obj['nodes'][i], key, idx+1)
                if(idx == 0): return 0
            return idx
        delete_rec(obj, node_id+1, 0)
        data_menu=obj['nodes']
        data_menu = json.dumps(data_menu)
        data_menu = data_menu.replace(', {}, {', ', {')
        data_menu = data_menu.replace(', {}','')
        data_menu = data_menu.replace('{},','')
        data_menu = data_menu.replace('{}','')
        update_item = {}
        update_item['menu'] = obj['nodes']
        txt = json.dumps(update_item)
        txt = txt.replace(', {}, {',', {')
        txt = txt.replace(', {}','')
        txt = txt.replace('{},','')
        txt = txt.replace('{}','')

        # print(txt)
        con = sql.connect('bot.db')
        cur =  con.cursor()
        cur.execute('UPDATE tbl_visa_menu SET  bot_menu= ? where lang_id= ?', (txt, lang_id))

        con.commit()    
        
    results = {'data': data_menu}
    return jsonify(results)

@app.route('/manage/visametrics/view', methods = ['POST', 'GET'])
def view_manage_visametrics():
    if request.method == "POST":
        req_data = request.get_json()
        node_id = req_data[0]['node_id']
        data_menu = json.loads(req_data[1]['data_menu'])
        obj = {}
        obj['nodes'] = []
        obj['nodes']= data_menu
        view_data = {}
        def view_rec(obj, key, index):
            if(key == index):
                for key in obj.keys():
                    if(not key == 'nodes'):
                        view_data[key] = obj[key]
                return 0
            idx = index
            for i in range(len(obj['nodes'])):
                idx = view_rec(obj['nodes'][i], key, idx+1)
                if(idx == 0): return 0
            return idx
        view_rec(obj, node_id+1, 0)
        # print(view_data)     
             
    results = {'view_data': view_data}
    return jsonify(results)


if __name__ == '__main__':
    app.env = 'development'
    app.run(debug=True)
