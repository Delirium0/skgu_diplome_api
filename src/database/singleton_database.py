from src.database.sqlalchemy_intefrace import SQLAlchemyDatabase


class DatabaseSingleton:
    _instance = None

    # если честно я не понимаю почему эта часть кода необходима
    @staticmethod
    def get_instance(db_url: str):
        if DatabaseSingleton._instance is None:
            DatabaseSingleton._instance = SQLAlchemyDatabase(db_url)
        return DatabaseSingleton._instance
