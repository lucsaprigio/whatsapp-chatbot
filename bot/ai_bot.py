import os

from decouple import config

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_groq import ChatGroq

os.environ['GROQ_API_KEY'] = config('GROQ_API_KEY')

class AIBot:
    def __init__(self):
        self.__chat = ChatGroq(model='llama-3.3-70b-versatile')
    
    def invoke(self, question):
        prompt = PromptTemplate(
            input_variables=['texto'],
            template=''' 
                Você é um agente, que só responde com gentileza que eu não estou disponível, e precisa enviar mensagem para o contato
                Rômulo - https://api.whatsapp.com/send/?phone=552731209857&text&type=phone_number&app_absent=0

                Alex - https://api.whatsapp.com/send/?phone=552731209856&text&type=phone_number&app_absent=0
                <texto>
                {texto}
                </texto>
            '''
        )
        # Cadeia de funções que encadeia uma atrás da outra
        chain = prompt | self.__chat | StrOutputParser() # prompt  deve ser enviado para o | chat | que deve ser enviado para o InputParser

        response = chain.invoke({
            'texto':question
        })
        return response