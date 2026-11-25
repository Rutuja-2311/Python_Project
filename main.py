import json
import secrets
import string
import hashlib
import getpass

from pathlib import Path


class Bank:

    DATABASE = Path(__file__).with_name("data.json")
    MAX_DEPOSIT = 10000

    def __init__(self):
        self.data = self.load_data()

    # ---------------- DATABASE HANDLING ----------------

    def load_data(self):
        if not self.DATABASE.exists():
            return []

        try:
            with open(self.DATABASE, "r", encoding="utf-8") as file:
                data = json.load(file)

            if not isinstance(data, list):
                raise ValueError("Invalid database format")

            return data

        except (json.JSONDecodeError, OSError, ValueError) as error:
            print(f"Database error: {error}")
            return []

    def save_data(self):
        try:
            temp_file = self.DATABASE.with_suffix(".tmp")

            with open(temp_file, "w", encoding="utf-8") as file:
                json.dump(self.data, file, indent=4)

            temp_file.replace(self.DATABASE)

        except OSError as error:
            print(f"Unable to save data: {error}")

    # ---------------- INPUT VALIDATION ----------------

    @staticmethod
    def get_integer(message, minimum=None, maximum=None):

        while True:
            try:
                value = int(input(message))

                if minimum is not None and value < minimum:
                    print(f"Value must be at least {minimum}")
                    continue

                if maximum is not None and value > maximum:
                    print(f"Value cannot exceed {maximum}")
                    continue

                return value

            except ValueError:
                print("Please enter a valid number.")

    @staticmethod
    def get_pin(message="Enter your 4-digit PIN: "):

        while True:
            pin = getpass.getpass(message)

            if len(pin) == 4 and pin.isdigit():
                return pin

            print("PIN must contain exactly 4 digits.")

    # ---------------- PIN SECURITY ----------------

    @staticmethod
    def hash_pin(pin, salt=None):

        if salt is None:
            salt = secrets.token_hex(16)

        hashed = hashlib.pbkdf2_hmac(
            "sha256",
            pin.encode(),
            bytes.fromhex(salt),
            200000
        )

        return salt, hashed.hex()

    # ---------------- ACCOUNT GENERATION ----------------

    def generate_account_number(self):

        while True:
            account_number = "".join(
                secrets.choice(string.digits)
                for _ in range(10)
            )

            if not any(
                user["accountNo."] == account_number
                for user in self.data
            ):
                return account_number

    # ---------------- AUTHENTICATION ----------------

    def authenticate(self):

        account_number = input("Enter account number: ").strip()
        pin = getpass.getpass("Enter your PIN: ")

        user = next(
            (
                user for user in self.data
                if user["accountNo."] == account_number
            ),
            None
        )

        if user is None:
            print("Account not found.")
            return None

        # Support accounts created by your original program.
        if "pin" in user:
            if str(user["pin"]) != pin:
                print("Incorrect PIN.")
                return None

            salt, hashed = self.hash_pin(pin)
            user["salt"] = salt
            user["pin_hash"] = hashed
            del user["pin"]
            self.save_data()

            return user

        salt = user["salt"]
        _, hashed = self.hash_pin(pin, salt)

        if not secrets.compare_digest(hashed, user["pin_hash"]):
            print("Incorrect PIN.")
            return None

        return user

    # ---------------- CREATE ACCOUNT ----------------

    def create_account(self):

        print("\n--- CREATE ACCOUNT ---")

        name = input("Enter your name: ").strip()
        age = self.get_integer("Enter your age: ", 1)

        email = input("Enter your email: ").strip()

        if not name or not email:
            print("Name and email cannot be empty.")
            return

        if age < 18:
            print("Sorry, you must be at least 18.")
            return

        pin = self.get_pin()

        salt, hashed = self.hash_pin(pin)

        account = {
            "name": name,
            "age": age,
            "email": email,
            "salt": salt,
            "pin_hash": hashed,
            "accountNo.": self.generate_account_number(),
            "balance": 0
        }

        self.data.append(account)
        self.save_data()

        print("\nAccount created successfully!")
        print(f"Account holder: {name}")
        print(f"Account number: {account['accountNo.']}")
        print("Initial balance: 0")

        print("\nPlease save your account number.")

    # ---------------- DEPOSIT MONEY ----------------

    def deposit_money(self):

        print("\n--- DEPOSIT MONEY ---")

        user = self.authenticate()

        if user is None:
            return

        amount = self.get_integer(
            "Enter deposit amount: ",
            minimum=1,
            maximum=self.MAX_DEPOSIT
        )

        user["balance"] += amount

        self.save_data()

        print(f"Successfully deposited {amount}.")
        print(f"Available balance: {user['balance']}")

    # ---------------- WITHDRAW MONEY ----------------

    def withdraw_money(self):

        print("\n--- WITHDRAW MONEY ---")

        user = self.authenticate()

        if user is None:
            return

        amount = self.get_integer(
            "Enter withdrawal amount: ",
            minimum=1
        )

        if amount > user["balance"]:
            print("Insufficient balance.")
            return

        user["balance"] -= amount

        self.save_data()

        print(f"Successfully withdrawn {amount}.")
        print(f"Remaining balance: {user['balance']}")

    # ---------------- SHOW ACCOUNT DETAILS ----------------

    def show_details(self):

        print("\n--- ACCOUNT DETAILS ---")

        user = self.authenticate()

        if user is None:
            return

        print("\nYour account information:")

        print(f"Name: {user['name']}")
        print(f"Age: {user['age']}")
        print(f"Email: {user['email']}")
        print(f"Account Number: {user['accountNo.']}")
        print(f"Balance: {user['balance']}")

    # ---------------- UPDATE ACCOUNT DETAILS ----------------

    def update_details(self):

        print("\n--- UPDATE ACCOUNT DETAILS ---")

        user = self.authenticate()

        if user is None:
            return

        print("\nLeave a field empty to keep its current value.")

        name = input("Enter new name: ").strip()
        email = input("Enter new email: ").strip()

        if name:
            user["name"] = name

        if email:
            user["email"] = email

        change_pin = input("Do you want to change your PIN? (y/n): ")

        if change_pin.lower() == "y":

            new_pin = self.get_pin("Enter your new PIN: ")

            salt, hashed = self.hash_pin(new_pin)

            user["salt"] = salt
            user["pin_hash"] = hashed

        self.save_data()

        print("Account details updated successfully!")

    # ---------------- DELETE ACCOUNT ----------------

    def delete_account(self):

        print("\n--- DELETE ACCOUNT ---")

        user = self.authenticate()

        if user is None:
            return

        confirmation = input(
            "Are you sure you want to delete your account? (y/n): "
        )

        if confirmation.lower() != "y":
            print("Account deletion cancelled.")
            return

        self.data.remove(user)
        self.save_data()

        print("Account deleted successfully!")


# ---------------- MAIN MENU ----------------

def main():

    bank = Bank()

    while True:

        print("\n========== BANK MANAGEMENT SYSTEM ==========")

        print("1. Create an account")
        print("2. Deposit money")
        print("3. Withdraw money")
        print("4. Show account details")
        print("5. Update account details")
        print("6. Delete account")
        print("7. Exit")

        choice = input("\nEnter your choice: ").strip()

        if choice == "1":
            bank.create_account()

        elif choice == "2":
            bank.deposit_money()

        elif choice == "3":
            bank.withdraw_money()

        elif choice == "4":
            bank.show_details()

        elif choice == "5":
            bank.update_details()

        elif choice == "6":
            bank.delete_account()

        elif choice == "7":
            print("Thank you for using our banking system!")
            break

        else:
            print("Invalid choice. Please select 1-7.")


if __name__ == "__main__":
    main()
