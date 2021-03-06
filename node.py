from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

#Наши файлы
from wallet import Wallet
from blockchain import Blockchain

#Конструктор (обязательный для Flask)
app = Flask(__name__)
CORS(app)

#Главная страница с переходом на node.html
@app.route('/', methods=['GET'])
def get_node_ui():
    return send_from_directory('ui', 'node.html')


@app.route('/network', methods=['GET'])
def get_network_ui():
    return send_from_directory('ui', 'network.html')

#Создание профиля
@app.route('/wallet', methods=['POST'])
def create_keys():
    #Создание ключей
    wallet.create_keys()
    #Сохранение ключей
    if wallet.save_keys():
        #Видимая переменная
        global blockchain
        blockchain = Blockchain(wallet.public_key, port)
        response = {
            'public_key': wallet.public_key,
            'private_key': wallet.private_key,
            'funds': blockchain.get_balance()
        }
        return jsonify(response), 201
    else:
        response = {
            'message': 'Сохранение ключей не удалось.'
        }
        return jsonify(response), 500

#Загрузает ключи
@app.route('/wallet', methods=['GET'])
def load_keys():
    #Провервка на существование/загрузку ключей
    if wallet.load_keys():

        global blockchain
        blockchain = Blockchain(wallet.public_key, port)
        response = {
            'public_key': wallet.public_key,
            'private_key': wallet.private_key,
            'funds': blockchain.get_balance()
        }
        return jsonify(response), 201
    else:
        response = {
            'message': 'Загрузка ключей не удалась.'
        }
        return jsonify(response), 500

#Показ баланса
@app.route('/balance', methods=['GET'])
def get_balance():
    balance = blockchain.get_balance()
    if balance != None:
        response = {
            'message': 'Показ баланса прошел успешно.',
            'funds': balance
        }
        return jsonify(response), 200
    else:
        response = {
            'messsage': 'Загрузка баланса не удалась.',
            'wallet_set_up': wallet.public_key != None
        }
        return jsonify(response), 500


@app.route('/broadcast-transaction', methods=['POST'])
def broadcast_transaction():
    values = request.get_json()
    if not values:
        response = {'message': 'Данных не найденно.'}
        return jsonify(response), 400
    required = ['sender', 'recipient', 'amount', 'signature']
    if not all(key in values for key in required):
        response = {'message': 'Данные потерянны.'}
        return jsonify(response), 400
    success = blockchain.add_transaction(
        values['recipient'], values['sender'], values['signature'], values['amount'], is_receiving=True)
    if success:
        response = {
            'message': 'Успешно добавлена транзакция.',
            'transaction': {
                'sender': values['sender'],
                'recipient': values['recipient'],
                'amount': values['amount'],
                'signature': values['signature']
            }
        }
        return jsonify(response), 201
    else:
        response = {
            'message': 'Создание транзакций не удалось.'
        }
        return jsonify(response), 500


@app.route('/broadcast-block', methods=['POST'])
def broadcast_block():
    values = request.get_json()
    if not values:
        response = {'message': 'Данных не найденно.'}
        return jsonify(response), 400
    if 'block' not in values:
        response = {'message': 'Данные потерянны.'}
        return jsonify(response), 400
    block = values['block']
    if block['index'] == blockchain.chain[-1].index + 1:
        if blockchain.add_block(block):
            response = {'message': 'Блок добавлен'}
            return jsonify(response), 201
        else:
            response = {'message': 'Блок недействительный.'}
            return jsonify(response), 409
    elif block['index'] > blockchain.chain[-1].index:
        response = {'message': 'Блокчейн, кажется, отличается от локального блокчейна.'}
        blockchain.resolve_conflicts = True
        return jsonify(response), 200
    else:
        response = {'message': 'Блокчейн меньше оригинального, блок не добавлен'}
        return jsonify(response), 409


@app.route('/transaction', methods=['POST'])
def add_transaction():

    if wallet.public_key == None:
        response = {
            'message': 'Профиль не создан.'
        }
        return jsonify(response), 400
    values = request.get_json()
    if not values:
        response = {
            'message': 'Данных(JSON) не найдено.'
        }
        return jsonify(response), 400
    #Проверяем, существуют ли все эти два поля
    required_fields = ['recipient', 'amount']
    #Если нет, то пишем ошибку
    if not all(field in values for field in required_fields):
        response = {
            'message': 'Запрашиваемые данные потерянны.'
        }
        return jsonify(response), 400
    recipient = values['recipient']
    amount = values['amount']
    #Подписывает под транзакцию
    signature = wallet.sign_transaction(wallet.public_key, recipient, amount)

    success = blockchain.add_transaction(
        recipient, wallet.public_key, signature, amount)
    if success:
        response = {
            'message': 'Успешно добавленная транзакция.',
            'transaction': {
                'sender': wallet.public_key,
                'recipient': recipient,
                'amount': amount,
                'signature': signature
            },
            'funds': blockchain.get_balance()
        }
        return jsonify(response), 201
    else:
        response = {
            'message': 'Ошибка в отправке транзакции.'
        }
        return jsonify(response), 500


@app.route('/mine', methods=['POST'])
def mine():
    if blockchain.resolve_conflicts:
        response = {'message': 'Блок не был добавлен, сначала решите конфликт!'}
        return jsonify(response), 409
    block = blockchain.mine_block()
    #Если у нас есть профиль/wallet
    if block != None:
        #Конвертация блока в дикт
        dict_block = block.__dict__.copy()
        dict_block['transactions'] = [
            tx.__dict__ for tx in dict_block['transactions']]
        response = {
            'message': 'Блок создан успешно.',
            'block': dict_block,
            'funds': blockchain.get_balance()
        }
        return jsonify(response), 201

    else:
        response = {
            'message': 'Добавление блока не удалось.',
            'wallet_set_up': wallet.public_key != None
        }
        return jsonify(response), 500


@app.route('/resolve-conflicts', methods=['POST'])
def resolve_conflicts():
    replaced = blockchain.resolve()
    if replaced:
        response = {'message': 'Цепь была заменена!'}
    else:
        response = {'message': 'Локальная цепь сохранена!'}
    return jsonify(response), 200

#Показ всех транзакций
@app.route('/transactions', methods=['GET'])
def get_open_transaction():
    transactions = blockchain.get_open_transactions()
    dict_transactions = [tx.__dict__ for tx in transactions]
    return jsonify(dict_transactions), 200


@app.route('/chain', methods=['GET'])
def get_chain():
    chain_snapshot = blockchain.chain
    dict_chain = [block.__dict__.copy() for block in chain_snapshot]
    for dict_block in dict_chain:
        dict_block['transactions'] = [
            tx.__dict__ for tx in dict_block['transactions']]
    return jsonify(dict_chain), 200


@app.route('/node', methods=['POST'])
def add_node():
    values = request.get_json()
    if not values:
        response = {
            'message': 'Данных нет.'
        }
        return jsonify(response), 400
    if 'node' not in values:
        response = {
            'message': 'Данные узла не найденны.'
        }
        return jsonify(response), 400
    node = values['node']
    blockchain.add_peer_node(node)
    response = {
        'message'  : 'Узлы добавленны успешно.',
        'all_nodes': blockchain.get_peer_nodes()
    }
    return jsonify(response), 201

#Удаление узла 
@app.route('/node/<node_url>', methods=['DELETE'])
def remove_node(node_url):
    if node_url == '' or node_url == None:
        response = {
            'message': 'Узлы не найдены.'
        }
        return jsonify(response), 400
    blockchain.remove_peer_node(node_url)
    response = {
        'message': 'Узел удален',
        'all_nodes': blockchain.get_peer_nodes()
    }
    return jsonify(response), 200

#Все узлы 
@app.route('/nodes', methods=['GET'])
def get_nodes():
    nodes = blockchain.get_peer_nodes()
    response = {
        'all_nodes': nodes
    }
    return jsonify(response), 200

### Запуск 
### python3 node.py -p номер_порта

if __name__ == '__main__':
    from argparse import ArgumentParser
    parser = ArgumentParser()
    #################################№№№№№№№№№№№№№№ ПОРТ
    parser.add_argument('-p', '--port', type=int, default=5005)
    args = parser.parse_args()
    port = args.port
    wallet = Wallet(port)
    blockchain = Blockchain(wallet.public_key, port)
    app.run(host='0.0.0.0', port=port)
