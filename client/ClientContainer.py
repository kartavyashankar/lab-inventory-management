from dependency_injector import containers, providers

from client.DBClient import DBClient


class ClientContainer(containers.DeclarativeContainer):
    db_client = providers.Singleton(DBClient)
