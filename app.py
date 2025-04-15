from flask import Flask, request, jsonify
import time
import random

from bot.ai_bot import AIBot
from services.waha import Waha

app = Flask(__name__)

@app.route('/chatbot/webhook/', methods=['POST'])
def webhook():
    data = request.json

    print(f'EVENTO RECEBIDO: {data}')

    waha = Waha()
    ai_bot = AIBot()

    chat_id = data['payload']['from'] # Recebendo as chaves do waha
    received_message = data['payload']['body'] # Corpo da mensagem que o usuário está enviando
    is_group = '@g.us' in chat_id
    is_status = 'status@broadcast' in chat_id

    if is_group or is_status:
        return jsonify({'status': 'success', 'message': 'Mensagem ignorada'})

    waha.start_typing(chat_id=chat_id)

    response = ai_bot.invoke(question=received_message)

    waha.send_message(
        chat_id=chat_id,
        message=response
    )

    waha.stop_typing(chat_id=chat_id)

    return jsonify({'status': 'success'}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0' ,debug=True, port=5000)
