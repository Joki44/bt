from flask import Flask, jsonify, request
import pymysql

app = Flask(__name__)

test = [1, 2]

connection = pymysql.connect(
    host="localhost",
    port=3306,
    user="user",
    passwd="passwd",
    database="database",
    cursorclass=pymysql.cursors.DictCursor
) 


@app.route('/test', methods=['GET'])
def get_list():
    data = request.args
    with connection.cursor() as cursor:
        order_request = f"SELECT * FROM payment WHERE order_id= {data['MERCHANT_ORDER_ID']};"
        cursor.execute(order_request)
        order = cursor.fetchone()
        if order['chips'] == 1:
            xz = f"UPDATE users SET chips = (chips + {order['value']}) WHERE tele_id = {order['tele_id']};"
            
        if order['chips'] == 0:
            xz = f"UPDATE users SET cash = (cash + {order['value']}) WHERE tele_id = {order['tele_id']};"
            
        cursor.execute(xz)
    
    return "YES"
    
    

if __name__ == "__main__":
    from waitress import serve
    serve(app, host="0.0.0.0", port=8080)