import time

from pandas import DataFrame

from client.DBClient import DBClient
from exceptions.Exceptions import UnauthorizedUserException, NotFoundException, ForbiddenOperationException
from model.Apparatus import Apparatus
from model.Lab import Lab
from model.User import User
from service.ApparatusService import ApparatusService
from service.LabService import LabService
from service.UserService import UserService
from utils import clear_screen, get_user_permission_for_lab


class Menu:
    def __init__(self, db_client: DBClient):
        self.user_service = UserService(db_client)
        self.lab_service = LabService(db_client)
        self.apparatus_service = ApparatusService(db_client)
        self.current_user = User()

    def main_menu(self):
        while True:
            clear_screen()
            print("Press 1 to create account.\nPress 2 to login to an existing account.\nPress anything else to quit the application.")
            choice = input("\nEnter your choice: ")
            if choice == "1":
                self.add_user_menu()
            elif choice == "2":
                self.login_menu()
            else:
                return

    def login_menu(self):
        while True:
            clear_screen()
            print("Please login to the inventory management system\n")
            username = input("Username: ")
            password = input("Password: ")

            try:
                user: User = self.user_service.login(username, password)
            except UnauthorizedUserException:
                print("Invalid Credentials. Please try again...")
                time.sleep(4)
                continue

            self.current_user = user
            self.user_menu()

    def user_menu(self):
        while True:
            clear_screen()
            print("Welcome, " + self.current_user.username + ". Please wait while we gather your data.")
            if self.current_user.org_admin:
                labs = self.lab_service.get_all_labs(self.current_user)
            else:
                labs = []
                for lab_id in self.current_user.access.keys():
                    if self.current_user.access[lab_id]["user"] == "none" and self.current_user.access[lab_id]["apparatus"] == "none":
                        continue
                    labs.append(self.lab_service.get_lab_by_id(self.current_user, lab_id))
            option_low_limit: int = 1
            option_high_limit: int = len(labs)

            for i in range(len(labs)):
                print("Press " + str(i + 1) + " to select " + labs[i].name + "(id=" + str(labs[i].tiny_id) + ").")

            add_user_option = len(labs) + 1
            remove_user_option = len(labs) + 2
            list_all_users_option = len(labs) + 3
            download_user_data_option = len(labs) + 4
            add_lab_option = len(labs) + 5
            edit_lab_option = len(labs) + 6
            remove_lab_option = len(labs) + 7
            list_all_labs_option = len(labs) + 8
            download_lab_data_option = len(labs) + 9

            if self.current_user.org_admin:
                print("Press " + str(add_user_option) + " to add new users.")
                print("Press " + str(remove_user_option) + " to remove user.")
                print("Press " + str(list_all_users_option) + " to list all users.")
                print("Press " + str(download_user_data_option) + " to download user data in csv file.")
                print("Press " + str(add_lab_option) + " to add new labs.")
                print("Press " + str(edit_lab_option) + " to edit lab's name.")
                print("Press " + str(remove_lab_option) + " to remove labs. Beware, this operation will also remove related apparatus data.")
                print("Press " + str(list_all_labs_option) + " to list all labs.")
                print("Press " + str(download_lab_data_option) + " to download lab data in csv file.")
                option_high_limit = option_high_limit + 9

            print("Press " + str(
                option_high_limit + 1) + " to logout.")
            option_high_limit = option_high_limit + 1

            choice: int = int(input("\nEnter your choice: "))

            if choice < option_low_limit or choice > option_high_limit:
                print("Invalid choice. Please try again...")
                time.sleep(4)
                continue

            if choice <= len(labs):
                self.lab_menu(labs[choice - 1])

            if choice == option_high_limit:
                print("Logging out...")
                time.sleep(4)
                return

            if choice == add_user_option:
                self.add_user_menu()
            elif choice == remove_user_option:
                self.remove_user_menu()
            elif choice == list_all_users_option:
                self.list_all_users_menu()
            elif choice == download_user_data_option:
                self.download_user_data_menu()
            elif choice == add_lab_option:
                self.add_lab_menu()
            elif choice == edit_lab_option:
                self.edit_lab_menu()
            elif choice == remove_lab_option:
                self.remove_lab_menu()
            elif choice == list_all_labs_option:
                self.list_all_labs_menu()
            elif choice == download_lab_data_option:
                self.download_lab_data_menu()

    def lab_menu(self, current_lab: Lab):
        while True:
            clear_screen()
            print("Manage " + current_lab.name + "\n")
            print("Press 1 list all apparatus data.")
            print("Press 2 to download all apparatus data.")
            action_map = {
                1: self.list_all_apparatus_menu,
                2: self.download_apparatus_data_menu,
            }
            option_low_limit = 1
            option_high_limit = 2
            if self.current_user.org_admin or self.current_user.access[str(current_lab.tiny_id)]["apparatus"] == "write":
                option_high_limit = option_high_limit + 1
                print("Press " + str(option_high_limit) + " to add apparatus data.")
                action_map[option_high_limit] = self.add_apparatus_menu

                option_high_limit = option_high_limit + 1
                print("Press " + str(option_high_limit) + " to update apparatus data.")
                action_map[option_high_limit] = self.edit_apparatus_menu

                option_high_limit = option_high_limit + 1
                print("Press " + str(option_high_limit) + " to delete apparatus data.")
                action_map[option_high_limit] = self.delete_apparatus_menu

            if self.current_user.org_admin or self.current_user.access[str(current_lab.tiny_id)]["user"] == "write":
                option_high_limit = option_high_limit + 1
                print("Press " + str(option_high_limit) + " to edit user access to lab.")
                action_map[option_high_limit] = self.update_user_lab_access_menu

            option_high_limit = option_high_limit + 1
            print("Press " + str(option_high_limit) + " to return to previous menu.")

            choice = int(input("\nPlease enter your choice: "))

            if choice == option_high_limit:
                return
            if choice < option_low_limit or choice > option_high_limit:
                print("Invalid choice. Please try again...")
                time.sleep(4)
                continue
            action_map[choice](current_lab)

    def list_all_apparatus_menu(self, current_lab: Lab):
        clear_screen()
        print("Loading apparatus data...\n")
        try:
            apparatus_df: DataFrame = self.apparatus_service.list_all_apparatus(self.current_user, current_lab.tiny_id)
            clear_screen()
            print(apparatus_df)
        except ForbiddenOperationException:
            print("You are not allowed to list apparatus...")
            time.sleep(4)
            return

        input("\nEnter anything to return to previous menu")
        return

    def download_apparatus_data_menu(self, current_lab: Lab):
        clear_screen()
        print("Downloading apparatus data...\n")
        try:
            filename: str = self.apparatus_service.export_all_apparatus_data(self.current_user, current_lab.tiny_id)
            clear_screen()
            print("Data downloaded to " + str(filename))
        except ForbiddenOperationException:
            print("You are not allowed to download apparatus data...")
            time.sleep(4)
            return

        input("\nEnter anything to return to previous menu")
        return

    def add_apparatus_menu(self, current_lab: Lab):
        while True:
            clear_screen()
            apparatus = Apparatus()
            apparatus.lab_id = current_lab.tiny_id
            apparatus.name = input("Enter apparatus name: ")
            apparatus.year_of_purchase = int(input("Enter year of purchase: "))
            apparatus.working_condition = input("Enter apparatus working condition: ")
            try:
                self.apparatus_service.add_apparatus(self.current_user, apparatus)
                print("Apparatus Data successfully added.")
            except ForbiddenOperationException:
                print("You are not allowed to add apparatus...")
                time.sleep(4)
                return

            print("\nPress 1 to add another apparatus.")
            print("Press any other key to go back to previous menu.")
            choice = input("\nEnter your choice: ")
            if choice == "1":
                continue
            else:
                return

    def edit_apparatus_menu(self, current_lab: Lab):
        while True:
            clear_screen()
            apparatus_id: int = int(input("Enter the id of the apparatus to be edited."))
            try:
                apparatus: Apparatus = self.apparatus_service.get_apparatus(self.current_user, current_lab.tiny_id, apparatus_id)
                apparatus.name = input("Enter apparatus name (current=" + apparatus.name + "): ")
                apparatus.year_of_purchase = int(input("Enter apparatus year of purchase (current=" + str(apparatus.year_of_purchase) +"): "))
                apparatus.working_condition = input("Enter working condition (current=" + apparatus.working_condition + "): ")
                self.apparatus_service.update_apparatus(self.current_user, apparatus)
            except NotFoundException:
                print("Apparatus with id " + str(apparatus_id) + " not found.")
            except ForbiddenOperationException:
                print("You are not allowed to edit apparatus data.")
                time.sleep(4)
                return
            print("\nPress 1 to update another apparatus.")
            print("Press any other key to go back to previous menu.")
            choice = input("\nEnter your choice: ")
            if choice == "1":
                continue
            else:
                return

    def delete_apparatus_menu(self, current_lab: Lab):
        while True:
            clear_screen()
            apparatus_id: int = int(input("Enter the id of the apparatus to be edited."))
            try:
                self.apparatus_service.remove_apparatus(self.current_user, current_lab.tiny_id, apparatus_id)
            except ForbiddenOperationException:
                print("You are not allowed to delete apparatus data.")
                time.sleep(4)
                return
            print("\nPress 1 to delete another apparatus.")
            print("Press any other key to go back to previous menu.")
            choice = input("\nEnter your choice: ")
            if choice == "1":
                continue
            else:
                return

    def update_user_lab_access_menu(self, current_lab: Lab):
        while True:
            clear_screen()
            username = input("Enter username of the user whose access needs to be changed: ")
            try:
                user: User = self.user_service.get_user_by_username(username)
                access_dict = get_user_permission_for_lab(user, current_lab.tiny_id)
                user_data_access_level = access_dict["user"]
                apparatus_data_access_level = access_dict["apparatus"]
                print("\nNote: The allowed values for access level are: 'read', 'write' and 'none'. Default value is 'none'.")
                user_data_access_level = input("\nEnter user's user-data access level (current=" + user_data_access_level + "): ")
                apparatus_data_access_level = input("Enter user's apparatus-data access level (current=" + apparatus_data_access_level + "): ")

                if user_data_access_level != "read" and user_data_access_level != "write":
                    user_data_access_level = "none"

                if apparatus_data_access_level != "read" and apparatus_data_access_level != "write":
                    apparatus_data_access_level = "none"

                access_dict = {
                    "user": user_data_access_level,
                    "apparatus": apparatus_data_access_level
                }
                self.user_service.update_user_lab_access(self.current_user, current_lab.tiny_id, username, access_dict)
                print("Access updated successfully!")
            except NotFoundException:
                print("User with username " + username + " does not exist.")
            except ForbiddenOperationException:
                print("You are not allowed to modify user access levels...")
                time.sleep(4)
                return
            print("\nPress 1 to modify lab access for another user.")
            print("Press any other key to go back to previous menu.")
            choice = input("\nEnter your choice: ")
            if choice == "1":
                continue
            else:
                return

    def add_user_menu(self):
        while True:
            clear_screen()
            user: User = User()
            user.username = input("Enter user's username: ")
            user.full_name = input("Enter user's full name: ")
            user.mobile_number = input("Enter user's mobile number: ")
            user.unique_school_code = input("Enter user's unique school code: ")
            password: str = input("Enter user's account password: ")

            if self.current_user.org_admin:
                choice = input(
                    "Make this user org-admin (org-admin is the highest level of authority in the application) (y/N)? ")
                if choice == 'y':
                    user.org_admin = True

            print("Please confirm user data: ")
            print(user.to_displayable_dict())
            print("password: " + password)
            choice = input("\nConfirm (y/N)? ")
            if choice == 'y':
                self.user_service.add_user(user, password)
                print("User created successfully!")
            else:
                print("User creation aborted...")

            if self.current_user.org_admin:
                print("\nPress 1 to add another user.")
                print("Press any other key to go back to previous menu.")
                choice = input("\nEnter your choice: ")
                if choice == "1":
                    continue
                else:
                    return

            time.sleep(4)
            return

    def remove_user_menu(self):
        while True:
            clear_screen()
            username = input("Please enter the username of the user to be deleted: ")
            if username == self.current_user.username:
                print("You cannot delete your own account...")
                time.sleep(4)
                continue
            try:
                self.user_service.remove_user(self.current_user, username)
                print("User deleted successfully!")
            except NotFoundException:
                print("User with username not found!")
            except ForbiddenOperationException:
                print("You are not allowed to delete users...")
                time.sleep(4)
                return

            print("\nPress 1 to delete another user.")
            print("Press any other key to go back to previous menu.")
            choice = input("\nEnter your choice: ")
            if choice == "1":
                continue
            else:
                return

    def list_all_users_menu(self):
        clear_screen()
        print("Loading user data...\n")
        try:
            user_df: DataFrame = self.user_service.list_all_user_data(self.current_user)
            clear_screen()
            print(user_df)
        except ForbiddenOperationException:
            print("You are not allowed to list users...")
            time.sleep(4)
            return

        input("\nEnter anything to return to previous menu")
        return

    def download_user_data_menu(self):
        clear_screen()
        print("Downloading user data...\n")
        try:
            filename: str = self.user_service.export_all_user_data(self.current_user)
            clear_screen()
            print("Data downloaded to " + str(filename))
        except ForbiddenOperationException:
            print("You are not allowed to download user data...")
            time.sleep(4)
            return

        input("\nEnter anything to return to previous menu")
        return

    def add_lab_menu(self):
        while True:
            clear_screen()
            lab: Lab = Lab()
            lab.name = input("Enter lab name: ")
            try:
                self.lab_service.add_lab(self.current_user, lab)
                print("Lab added successfully!")
            except ForbiddenOperationException:
                print("You are not allowed to add labs...")
                time.sleep(4)
                return

            print("\nPress 1 to add another lab.")
            print("Press any other key to go back to previous menu.")
            choice = input("\nEnter your choice: ")
            if choice == "1":
                continue
            else:
                return

    def edit_lab_menu(self):
        while True:
            clear_screen()
            lab_id = int(input("Enter the id of the lab to be edited: "))
            try:
                lab: Lab = self.lab_service.get_lab_by_id(self.current_user, lab_id)
                lab.name = input("Enter new name for the lab (current=" + lab.name + "): ")
                self.lab_service.update_lab(self.current_user, lab)
            except NotFoundException:
                print("No lab with id: " + str(lab_id) + " found!")
            except ForbiddenOperationException:
                print("You are not allowed to edit labs...")
                time.sleep(4)
                return
            print("\nPress 1 to add another lab.")
            print("Press any other key to go back to previous menu.")
            choice = input("\nEnter your choice: ")
            if choice == "1":
                continue
            else:
                return

    def remove_lab_menu(self):
        while True:
            clear_screen()
            lab_id = int(input("Enter the id of the lab to be deleted: "))
            choice = input("This will also delete related apparatus data. Confirm (y/N)? ")
            if choice == 'y':
                try:
                    self.lab_service.remove_lab(self.current_user, lab_id)
                    print("Lab deleted successfully!")
                except ForbiddenOperationException:
                    print("You are not allowed to delete labs...")
                    time.sleep(4)
                    return

            print("\nPress 1 to delete another lab.")
            print("Press any other key to go back to previous menu.")
            choice = input("\nEnter your choice: ")
            if choice == "1":
                continue
            else:
                return

    def list_all_labs_menu(self):
        clear_screen()
        print("Loading lab data...\n")
        try:
            labs_df: DataFrame = self.lab_service.list_all_lab_data(self.current_user)
            clear_screen()
            print(labs_df)
        except ForbiddenOperationException:
            print("You are not allowed to list labs...")
            time.sleep(4)
            return

        input("\nEnter anything to return to previous menu")
        return

    def download_lab_data_menu(self):
        clear_screen()
        print("Downloading lab data...\n")
        try:
            filename: str = self.lab_service.export_all_lab_data(self.current_user)
            clear_screen()
            print("Data downloaded to " + str(filename))
        except ForbiddenOperationException:
            print("You are not allowed to download lab data...")
            time.sleep(4)
            return

        input("\nEnter anything to return to previous menu")
        return


