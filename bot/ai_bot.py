import os

from decouple import config

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_groq import ChatGroq

os.environ['GROQ_API_KEY'] = config('GROQ_API_KEY')

class AIBot:
    def __init__(self):
        self.__chat = ChatGroq(model='gemma2-9b-it')
    
    def invoke(self, question, contexto):
        prompt = PromptTemplate(
            input_variables=['texto', 'contexto'],
            template=''' 
                Você é um Agente virtual da empresa "Speed Automac".
                A Speed automac, é uma empresa de ERP.
                Sempre mande emoticons quando puder.
                {contexto}
                <texto>
                {texto}
                </texto>
            '''
        )
        # Cadeia de funções que encadeia uma atrás da outra
        chain = prompt | self.__chat | StrOutputParser() # prompt  deve ser enviado para o | chat | que deve ser enviado para o InputParser

        response = chain.invoke({
            'texto':question,
            'contexto':contexto
        })
        return response