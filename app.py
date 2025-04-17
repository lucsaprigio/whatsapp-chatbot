from flask import Flask, request, jsonify

from bot.ai_bot import AIBot
from services.waha import Waha
from database.sqlite_db import SQLiteService
from utils.functions import gera_liberacao, normalize_text, get_client_data
from datetime import datetime, timedelta

app = Flask(__name__)

sqlite_service = SQLiteService(db_path='conversation_states.db')

@app.route('/chatbot/webhook/', methods=['POST'])
def webhook():
    data = request.json

    waha = Waha()
    ai_bot = AIBot()

    if data['payload']['timestamp']:
        event_time = datetime.fromtimestamp(data['payload']['timestamp'])
        current_time = datetime.now() # retorna um timestamp atual

        time_diff = current_time - event_time
        
    if time_diff > timedelta(minutes=5):
        print("Mensagem ignorada mais de 5 minutos")
        return jsonify({'status': 'ignored'})

    chat_id = data['payload']['from'] # Recebendo as chaves do waha
    received_message = data['payload']['body'] # Corpo da mensagem que o usuário está enviando
    is_group = '@g.us' in chat_id
    is_status = 'status@broadcast' in chat_id

    if is_group or is_status:
        return jsonify({'status': 'success', 'message': 'Mensagem ignorada'})
    
    waha.start_typing(chat_id=chat_id)

    current_state = sqlite_service.consulta_conversa_cliente(chat_id=chat_id)
    print(current_state)

    if current_state is None:
       response = ai_bot.invoke(
           question=received_message, 
           contexto='Pode responder o usuário como se fosse a primeira vez que ele entrou no sistema, e peça para ele digitar o CNPJ abaixo para consultar.') 
       waha.send_message(
           chat_id=chat_id,
           message=response
       )

       sqlite_service.atualizar_conversa_cliente(chat_id=chat_id, state='aguardando_cnpj', cgc_cliente='0', nome_cliente='Não identificado')
       return jsonify({'status':'success'})
    
    if current_state['state'] == 'aguardando_cnpj':
        if len(received_message) >= 11 and received_message.isdigit():
            cliente = get_client_data(cpf_cnpj=received_message)
            if cliente:
                sqlite_service.atualizar_conversa_cliente(
                        chat_id=chat_id, 
                        state='conversa_normal', 
                        cgc_cliente=cliente['cpf_cnpj'],
                        nome_cliente=cliente['nome']
                    )
                waha.send_message(
                    chat_id=chat_id,
                    message=f'Seja bem-vindo {cliente['nome']} em que posso lhe ajudar?'
            )
                
                sqlite_service.atualizar_conversa_cliente(
                    chat_id=chat_id, 
                    state='conversa_opcoes'
                )
            else:
                waha.send_message(
                    chat_id=chat_id,
                    message='Desculpe, CNPJ não cadastrado no sistema😕 \n *Tente novamente*.'
            )
        else:
            waha.send_message(
                chat_id=chat_id,
                message='CNPJ Inválido.'
            )

    if current_state['state']  == 'conversa_opcoes':
        # Manipular palavras-chave ou continuar a conversa
        if '1' in received_message:
            # Consultar duplicatas em aberto caso estiver

            waha.send_message(
                chat_id=chat_id,
                message=f'Parece que há duplicatas em aberto \n 123\n123\n123'
            )

            waha.send_message(
                chat_id=chat_id,
                message=f'Mas posso gerar um código de liberação para você. Deseja gerar o código?\n *1 - Sim*\n *2 - Não*'
            )

            sqlite_service.atualizar_conversa_cliente(chat_id, state='conversa_pendencias')
        elif '2' in received_message:
            liberacao = gera_liberacao()

            waha.send_message(
                chat_id=chat_id,
                message=f'Segue seu código de liberação 0️⃣0️ \n\n{liberacao} '
            )

            waha.send_message(
                chat_id=chat_id,
                message='Há algo mais que eu posso lhe ajudar? ☺'
            )
            sqlite_service.atualizar_conversa_cliente(chat_id, state='conversa_normal')
        elif '3' in received_message.lower():
            waha.send_message(
                chat_id=chat_id,
                message='Segue os contatos abaixo: \
                https://api.whatsapp.com/send/?phone=552731209857&text&type=phone_number&app_absent=0\n\n \
                https://api.whatsapp.com/send/?phone=552731209856&text&type=phone_number&app_absent=0'
            )
        else:
            response = ai_bot.invoke(
                question=received_message, 
                contexto='Sempre responda o cliente para colocar as opções específicas para o cliente digitar: "1 - Pendências", "2 - Código de Liberação" ou "3 - Contatos Suporte"')
            waha.send_message(
                chat_id=chat_id,
                message=response
            )

    if current_state['state'] == 'conversa_pendencias':
       if received_message == '1':
           liberacao = gera_liberacao()

           waha.send_message(
                chat_id=chat_id,
                message=f'Segue seu código de liberação 0️⃣0️ \n\n{liberacao} '
            )

           waha.send_message(
                chat_id=chat_id,
                message='Há algo mais que eu posso lhe ajudar? ☺'
            )
           sqlite_service.atualizar_conversa_cliente(chat_id, state='conversa_normal')

       if received_message == '2':
           waha.send_message(
               chat_id=chat_id,
               message='Tudo bem! Se precisar de algo mais só avisar!'
           )
           sqlite_service.atualizar_conversa_cliente(chat_id, state='conversa_normal')

    if current_state['state'] == 'conversa_normal':
        response = ai_bot.invoke(
            question=received_message, 
            contexto='Sempre responda o cliente para colocar as opções específicas para o cliente digitar: "1 - Pendências", "2 - Código de Liberação" ou "3 - Contatos Suporte"')
        waha.send_message(
            chat_id=chat_id,
            message=response
        ) 
           

    waha.stop_typing(chat_id=chat_id) 

    return jsonify({'status': 'success'}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0' ,debug=True, port=5000)
