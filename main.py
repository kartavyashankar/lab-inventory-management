from Menu import Menu
from client.DBClient import DBClient

if __name__ == '__main__':
    db_client = DBClient()
    menu = Menu(db_client)
    menu.main_menu()
