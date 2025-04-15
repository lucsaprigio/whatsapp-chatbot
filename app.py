from flask import Flask, request, jsonify
import unicodedata

from bot.ai_bot import AIBot
from services.waha import Waha

app = Flask(__name__)

dados = [
    {
        'cpf_cnpj':'12016936754',
        'nome':'Lucas Aprigio'
    }
]
conversation_states = []

def normalize_text(text):
    """Remove acentos e caracteres especiais de uma string."""
    return ''.join(
        c for c in unicodedata.normalize('NFD', text)
        if unicodedata.category(c) != 'Mn'
    ).lower()

def gera_liberacao():
    return '1.2.3.4.5.6.7.8.9.0'

def get_boletos():
    return 'Boletos'

def get_client_data(cpf_cnpj):
    for cliente in dados:
        if cliente['cpf_cnpj'] == cpf_cnpj:
            return cliente
    return None

def get_conversation_state(chat_id):
    """Obtém o estado da conversa para um chat_id específico."""
    for conversation in conversation_states:
        if conversation['chat_id'] == chat_id:
            return conversation['state']
    return None

def update_conversation_state(chat_id, state):
    """Atualiza ou cria o estado da conversa para um chat_id específico."""
    for conversation in conversation_states:
        if conversation['chat_id'] == chat_id:
            conversation['state'] = state
            return
    # Se não existir, cria uma nova entrada
    conversation_states.append({'chat_id': chat_id, 'state': state})


@app.route('/chatbot/webhook/', methods=['POST'])
def webhook():
    data = request.json

    waha = Waha()
    ai_bot = AIBot()

    chat_id = data['payload']['from'] # Recebendo as chaves do waha
    received_message = data['payload']['body'] # Corpo da mensagem que o usuário está enviando
    is_group = '@g.us' in chat_id
    is_status = 'status@broadcast' in chat_id

    if is_group or is_status:
        return jsonify({'status': 'success', 'message': 'Mensagem ignorada'})
    
    waha.start_typing(chat_id=chat_id)

    current_state = get_conversation_state(chat_id=chat_id)

    if current_state is None:
       response = ai_bot.invoke(
           question=received_message, 
           contexto='Pode responder o usuário como se fosse a primeira vez que ele entrou no sistema, e peça para ele digitar o CNPJ abaixo para cadastrar') 
       waha.send_message(
           chat_id=chat_id,
           message=response
       )
       update_conversation_state(chat_id=chat_id, state='aguardando_cnpj')
       return jsonify({'status':'success'})
    
    if current_state == 'aguardando_cnpj':
        if len(received_message) >= 11 and received_message.isdigit():
            cliente = get_client_data(cpf_cnpj=received_message)

            if cliente:
                waha.send_message(
                    chat_id=chat_id,
                    message=f'Seja bem-vindo {cliente['nome']} em que posso lhe ajudar?'
            )
                update_conversation_state(chat_id=chat_id, state='conversa_normal')
            else:
                waha.send_message(
                    chat_id=chat_id,
                    message='Desculpe, CNPJ não cadastrado na empresa.'
            )
        else:
            waha.send_message(
                chat_id=chat_id,
                message='CNPJ Inválido.'
            )

            
    if current_state == 'conversa_normal':
        # Manipular palavras-chave ou continuar a conversa
        if 'boletos' in received_message.lower():
            waha.send_message(
                chat_id=chat_id,
                message='Parece que há parcelas atrasadas no seu CNPJ! Deseja fazer download da última duplicata?'
            )
        elif 'codigo de liberaçao' in normalize_text(received_message):
            liberacao = gera_liberacao()

            waha.send_message(
                chat_id=chat_id,
                message=f'Segue seu código de liberação\n\n{liberacao}'
            )

            response = ai_bot.invoke(
                    question=received_message, 
                    contexto='Só pergunte o em que pode ajudar mais.'
            ) 
            waha.send_message(
                chat_id=chat_id,
                message=response
            )
        elif 'suporte' in received_message.lower():
            waha.send_message(
                chat_id=chat_id,
                message='Segue os contatos abaixo: \
                https://api.whatsapp.com/send/?phone=552731209857&text&type=phone_number&app_absent=0\n\n \
                https://api.whatsapp.com/send/?phone=552731209856&text&type=phone_number&app_absent=0'
            )
        else:
            response = ai_bot.invoke(
                question=received_message, 
                contexto='Sempre responda o cliente para colocar as opções específicas para o cliente digitar: "Código de liberação", "Boletos" ou "Suporte"')
            waha.send_message(
                chat_id=chat_id,
                message=response
            )

    waha.stop_typing(chat_id=chat_id)

    return jsonify({'status': 'success'}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0' ,debug=True, port=5000)
