import unicodedata

dados = [
    {
        'cpf_cnpj':'12345678912',
        'nome':'Lucas Aprigio'
    }
]

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
