from flask import Flask, make_response, jsonify, request
import sqlite3
import json
from flask import g

app = Flask(__name__)
DATABASE = "/Users/liyanan/WorkSpace/Innovation/untitled/li.yanan"


# 获取数据库
def get_db():
    db = getattr(g, '_database_', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db


# 查询
def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv


# 增加数据
def add_db(add_sql, args=()):
    db = get_db()
    cur = db.cursor()
    cur.execute(add_sql, args)
    db.commit()
    return "true"


# 删除数据
def delete_db(delete_query, args=()):
    db = get_db()
    cur = db.cursor()
    cur.execute(delete_query, args)
    db.commit()
    return "true"


# 更新数据
def update_db(update_sql, args=()):
    db = get_db()
    cur = db.cursor()
    cur.execute(update_sql, args)
    db.commit()
    return "true"


# 数据库关闭
@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database_', None)
    if db is not None:
        db.close()


# 错误404处理
@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


# 1.登录验证
@app.route("/KH/v1/login", methods=['POST'])
def login():
    data = {
        'username': '',  # android端发送请求时所获取的数据
        "description": "登录失败",  # 用于toast显示的消息内容
        "flag": "fail",  # if/else判断的条件
    }
    username = request.form['username']
    password = request.form['password']
    if query_db("SELECT username FROM user WHERE username=?AND password=?",
                args=(username, password)):
        data['username'] = username
        data['description'] = '登录成功'
        data['flag'] = 'success'
    else:
        pass
    return_data = jsonify(data)
    print("接收到一个'登录请求")
    return return_data


# 2.注册验证
@app.route("/KH/v1/register", methods=['POST'])
def register():
    data = {
        "description": "注册失败",
        "flag": "fail",
    }
    username = request.form['username']
    password = request.form['password']
    if add_db("INSERT INTO user('username','password') VALUES (?,?)",
              args=(username, password)):
        data['description'] = '登录成功'
        data['flag'] = 'success'
    else:
        pass
    return_data = jsonify(data)
    print("接收到一个注册请求")
    return return_data


# 3.提交我要用伞请求
@app.route("/KH/v1/submit_um", methods=['POST'])
def submit_um():
    # INSERT INTO needum('mylocation','destination','type','username') VALUES (?,?,?,?)
    data = {
        'flag': 0,
        'description': '请求失败,请重试'
    }
    mylocation = request.form['mylocation']
    destination = request.form['destination']
    type = request.form['type']
    username = request.form['username']
    if add_db("INSERT INTO needum('mylocation','destination','type','username') VALUES (?,?,?,?)",
              args=(mylocation, destination, type, username)):
        data['flag'] = 1
        data['description'] = '请求成功'

    return_data = jsonify(data)
    print("接收到一个'我要打伞'请求，来自用户：", username)
    return return_data


# 4.取消我要用伞的请求
@app.route("/KH/v1/delete_um", methods=['POST'])
def delete_um():
    # DELETE FROM needum WHERE username = ?
    data = {
        'flag': 0,
        'description': '网络错误，取消失败'
    }
    username = request.form['username']
    if delete_db("DELETE FROM needum WHERE username = ?", args=(username,)):
        data['flag'] = 1
        data['description'] = '取消成功'
    return_data = jsonify(data)
    print("接收到一个取消'我要打伞'请求，来自用户：", username)
    return return_data


# 5.提交我有伞请求
@app.route("/KH/v1/submit_haveum", methods=['POST'])
def submit_haveum():
    # INSERT INTO haveum('mylocation','destination','type','username') VALUES (?,?,?,?)
    data = {
        'flag': 0,
        'description': '请求失败,请重试'
    }
    mylocation = request.form['mylocation']
    destination = request.form['destination']
    type = request.form['type']
    username = request.form['username']
    if add_db("INSERT INTO haveum('mylocation','destination','type','username') VALUES (?,?,?,?)",
              args=(mylocation, destination, type, username)):
        data['flag'] = 1
        data['description'] = '请求成功'

    return_data = jsonify(data)
    print("接收到一个'我有伞'请求，来自用户：", username)
    return return_data


# 6.取消我有伞的请求
@app.route("/KH/v1/delete_haveum", methods=['POST'])
def delete_haveum():
    # DELETE FROM haveum WHERE username = ?
    data = {
        'flag': 0,
        'description': '网络错误，取消失败'
    }
    username = request.form['username']
    if delete_db("DELETE FROM haveum WHERE username = ?", args=(username,)):
        data['flag'] = 1
        data['description'] = '取消成功'
    return_data = jsonify(data)
    print("接收到一个取消'我有伞'请求，来自用户：", username)
    return return_data


# 7.修改个人信息(用户名)
@app.route("/KH/v1/update", methods=['POST'])
def update():
    # UPDATE user SET password = 'stph12' WHERE username = 'stph'
    data = {
        'password': '',
        'flag': 0,
        'description': '网络错误，请重试'
    }
    username = request.form['username']
    password = request.form['password']
    if update_db("UPDATE user SET password = ? WHERE username = ?",
                 args=(password, username,)):
        data['flag'] = 1
        data['description'] = '修改成功'
        data['password'] = password
    return_data = jsonify(data)
    print("接收到一个'修改个人密码'请求，来自用户：", username)
    return return_data


# 8.显示订单列表
@app.route("/KH/v1/order_list", methods=['POST'])
def order_list():
    data = {
        'orders': [],
        'flag': 0,
        'description': '暂无订单'
    }

    username = request.form['username']
    result = query_db("SELECT username ,datetime,type FROM orders,user WHERE user.user_id=orders.user2_id AND"
                      "(SELECT user.user_id FROM user WHERE user.username=?)=orders.user_id", args=(username,))
    if result:
        # 定义一个空的订单列表
        # 将查询结果一一放进列表中
        for item in result:
            listitem = {
                "username2": "",
                "datetime": "",
                "type": ""
            }
            listitem['username2'] = item[0]
            listitem['datetime'] = item[1]
            listitem['type'] = item[2]

            data['orders'].append(listitem)

        data['flag'] = 1
        data['description'] = '请看订单！'
    print("接收到一个'查看个人订单'请求，来自用户：", username)
    return_data = jsonify(data)
    return return_data

#9.打伞请求获取有伞队列
@app.route("/KH/v1/get_um", methods=["POST"])
def get_um():
    #SELECT mylocation,destination,username FROM haveum
    data = {
        'haveum_list': [],
        "flag": "1",
    }
    username = request.form['username']
    result = query_db("SELECT mylocation,destination,username FROM haveum")
    if result:
        for item in result:
            list = {
                'mylocation':'',
                'destination':'',
                'username':''
            }
            list['mylocation']=item[0]
            list['destination']=item[1]
            list['username']=item[2]
            data['haveum_list'].append(list)
        data['flag'] = 1
    print("接收到一个'打伞请求获取有伞队列'请求，来自用户：",username)
    return_data = jsonify(data)
    return jsonify(data)

#10.接受建立连接消息
@app.route("/KH/v1/connect",methods=["POST"])
def connect():
    data = {
        "flag": "0",
    }
    username = request.form['username']
    if 1:
        data['flag'] = 1
    print("接收到一个'建立连接的'请求，来自用户：", username)
    return_data = jsonify(data)
    return return_data

#11.取消一次建立连接
@app.route("/KH/v1/delete_connect", methods=['POST'])
def delete_connect():
    # DELETE FROM needum WHERE username = ?
    data = {
        'flag': 0,
        'description': '网络错误，取消失败'
    }
    username = request.form['username']
    if 1:
        data['flag'] = 1
        data['description'] = '取消成功'
    return_data = jsonify(data)
    print("接收到一个取消'我要打伞'请求，来自用户：", username)
    return return_data

#12.结束行程
@app.route("/KH/v1/over", methods=['POST'])
def over():
    # DELETE FROM needum WHERE username = ?
    data = {
        'flag': 0,
        'description': '网络错误，取消失败'
    }
    username = request.form['username']
    if 1:
        data['flag'] = 1
        data['description'] = '取消成功'
    return_data = jsonify(data)
    print("接收到一个'结束行程'请求，来自用户：", username)
    return return_data


@app.route('/')
def hello_world():
    return "nn"


if __name__ == '__main__':
    app.run(host='0.0.0.0')
