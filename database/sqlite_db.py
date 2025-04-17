import sqlite3

class SQLiteService:
    def __init__(self, db_path):
        self.connection = sqlite3.connect(db_path, check_same_thread=False)
        self.cursor = self.connection.cursor()
        self.create_table()

    def create_table(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS conversation_states (
                chat_id TEXT PRIMARY KEY,
                cgc_cliente TEXT,
                nome_cliente TEXT,
                state TEXT
            )
        ''')
        self.connection.commit()

    def consulta_conversa_cliente(self, chat_id):
        # Configura o row_factory da conexão para retornar um objeto
        self.connection.row_factory = sqlite3.Row
        self.cursor = self.connection.cursor()

        self.cursor.execute('SELECT * FROM conversation_states WHERE chat_id = ?', (chat_id,))

        result = self.cursor.fetchone()

        return dict(result) if result else None
    
    def atualizar_conversa_cliente(self, chat_id, state, cgc_cliente=None, nome_cliente=None):
        self.cursor.execute('''
            INSERT INTO conversation_states(chat_id, state, cgc_cliente, nome_cliente)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(chat_id) DO UPDATE SET 
            state = excluded.state, 
            cgc_cliente = COALESCE(excluded.cgc_cliente, cgc_cliente), 
            nome_cliente = COALESCE(excluded.nome_cliente, nome_cliente)

        ''', (chat_id, state, cgc_cliente, nome_cliente))
        self.connection.commit()
    
    def close(self):
        self.cursor.close()
        self.connection.close()


SQLiteService('conversation_states.db').atualizar_conversa_cliente('123', 'casd', '123456789123', 'Lucao')