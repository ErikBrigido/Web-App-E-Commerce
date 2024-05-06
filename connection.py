import cx_Oracle
from decouple import config
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# variaveis de conexão com o banco de dados Oracle
userOracle = config(
'USER_ORACLE'
)
passwordOracle = config(
'PASSWORD_ORACLE'
)
serverOracle = config(
'SERVER_ORACLE'
)
portOracle = config(
'PORT_ORACLE'
)
service_nameOracle = config(
'SERVICE_NAME_ORACLE'
)
# path do instantclient Oracle para conexão com o banco de dados Oracle
path_instantclient = Path(config('PATH_INSTANTCLIENT_Erik')).resolve()

# inicializando o cx_Oracle com o path do instantclient_19_11
cx_Oracle.init_oracle_client(lib_dir=str(path_instantclient))

string_connection_oracle = f"oracle+cx_oracle://{userOracle}:{passwordOracle}@{serverOracle}:{portOracle}/?service_name={service_nameOracle}"

class ConexaoOracleC5:
    """Conexão com o banco de dados Oracle """

    def __init__(self):
        self.__connection__string = string_connection_oracle
        self.__engine = self.__creat__engine()
        self.session = None

    def __creat__engine(self):
        """ cria a engine de conexão com o banco de dados Oracle

        Returns:

        engine: engine de conexão com o banco de dados Oracle

        """
        engine = create_engine(self.__connection__string,pool_pre_ping=True,pool_recycle=300)
        return engine

    def get_engine(self):
        """ retorna a engine de conexão com o banco de dados Oracle

        Returns:

        engine: engine de conexão com o banco de dados Oracle

        """
        return self.__engined
        
    def __enter__(self):
        """ abre a sessão com o banco de dados Oracle

        Returns:

        self: retorna a classe

        """
        session_make = sessionmaker(bind=self.__engine)

        self.session = session_make()
        return self.session

    def __exit__(self, exc_type, exc_val, exc_tb):
        """ fecha a sessão com o banco de dados Oracle

        """

        self.session.close()