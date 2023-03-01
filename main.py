from flask import Flask, jsonify, request
import sqlite3
import db
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


app = Flask(__name__)


def create_connection():
  conn = None
  try:
    conn = sqlite3.connect(DATABASE)
  except Error as e:
    print(e)

  return conn


def close_connection(conn):
  if conn:
    conn.close()


def send_email(item_list, owner_email):
  # Create the message object
  msg = MIMEMultipart()
  msg['From'] = 'noreply@yourdomain.com'
  msg['To'] = owner_email
  msg['Subject'] = 'Order Details'

  # Create the message body
  message = 'Order Details:\n'
  for item, quantity in item_list.items():
    message += f'{item}: {quantity}\n'
  body = MIMEText(message)
  msg.attach(body)

  # Send the email
  with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
    smtp.starttls()
    smtp.login('your_email@gmail.com', 'your_password')
    smtp.send_message(msg)


app = Flask(__name__, template_folder='templates')


@app.route('/items', methods=['POST'])
def create_item():
  if not request.json:
    return make_response(jsonify({'error': 'The request must be JSON format'}),
                         400)

  name = request.json.get('name', '')
  price = request.json.get('price', '')
  description = request.json.get('description', '')
  image_url = request.json.get('image_url', '')

  if name == '':
    return make_response(jsonify({'error': 'Name is required'}), 400)
  if price == '':
    return make_response(jsonify({'error': 'Price is required'}), 400)

  try:
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute(
      "INSERT INTO items (name, description, price, image_url) VALUES (?, ?, ?, ?)",
      (name, description, price, image_url))
    new_id = cursor.lastrowid
    conn.commit()
    close_connection(conn)
  except Error as e:
    print(e)
    close_connection(conn)
    return make_response(jsonify({'error': 'Could not create item'}), 500)

  created_item = {
    'id': new_id,
    'name': name,
    'description': description,
    'price': price,
    'image_url': image_url
  }

  return jsonify(created_item), 201


@app.route('/items', methods=['GET'])
def get_all_items():
  conn = create_connection()
  cursor = conn.cursor()
  cursor.execute("SELECT * FROM items")
  items = cursor.fetchall()
  close_connection(conn)
  item_list = []
  for item in items:
    item_dict = {}
    item_dict['id'] = item[0]
    item_dict['name'] = item[1]
    item_dict['description'] = item[2]
    item_dict['price'] = item[3]
    item_dict['image_url'] = item[4]
    item_list.append(item_dict)
  return jsonify(item_list)


@app.route('/items/<int:item_id>', methods=['GET'])
def get_item(item_id):
  conn = create_connection()
  cursor = conn.cursor()
  cursor.execute("SELECT * FROM items WHERE id=?", (item_id, ))
  item = cursor.fetchone()
  close_connection(conn)
  if item:
    item_dict = {}
    item_dict['id'] = item[0]
    item_dict['name'] = item[1]
    item_dict['description'] = item[2]
    item_dict['price'] = item[3]
    item_dict['image_url'] = item[4]
    return jsonify(item_dict)
  else:
    return make_response(jsonify({'error': 'Item not found'}), 404)



@app.route('/items/<int:item_id>', methods=['PUT'])
def update_item(item_id):
    if not request.json:
        return make_response(jsonify({'error': 'The request must be JSON format'}), 400)

    name = request.json.get('name', '')
    price = request.json.get('price', '')
    description = request.json.get('description', '')
    image_url = request.json.get('image_url', '')

    if name == '':
        return make_response(jsonify({'error': 'Name is required'}), 400)
    if price == '':
        return make_response(jsonify({'error': 'Price is required'}), 400)

    try:
        conn = create_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM items WHERE id=?", (item_id,))
        item = cursor.fetchone()
        if not item:
            close_connection(conn)
            return make_response(jsonify({'error': 'Item not found'}), 404)

        cursor.execute("UPDATE items SET name=?, description=?, price=?, image_url=? WHERE id=?",
                       (name, description, price, image_url, item_id))
        conn.commit()
        close_connection(conn)
    except Error as e:
        print(e)
        close_connection(conn)
        return make_response(jsonify({'error': 'Could not update item'}), 500)

    updated_item = {'id': item_id, 'name': name, 'description': description, 'price': price, 'image_url': image_url}

    return jsonify(updated_item)


@app.route('/items/<int:item_id>', methods=['DELETE'])
def delete_item(item_id):
    conn = create_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("DELETE FROM items WHERE id=?", (item_id, ))
        if cursor.rowcount == 0:
            raise ValueError('Item not found')
    except Error as e:
        print(e)
        close_connection(conn)
        return make_response(jsonify({'error': 'Could not delete item'}), 500)

    conn.commit()
    close_connection(conn)
    return jsonify({'message': 'Item deleted successfully!'})


@app.route('/order', methods=['POST'])
def send_order():
  item_list = request.json['items']
  owner_email = request.json['email']
  send_email(item_list, owner_email)
  return 'Order details sent to owner'


if __name__ == '__main__':
  app.run(host='0.0.0.0', port='8080', debug=True)
