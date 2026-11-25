import json
import secrets
import string
import hashlib

from pathlib import Path


class Bank:

    DATABASE = Path(__file__).with_name("data.json")
    MAX_DEPOSIT = 10000

    # ---------------- DATABASE ----------------

    @classmethod
    def load_data(cls):

        if not cls.DATABASE.exists():
            return []

        try:
            with open(cls.DATABASE, "r", encoding="utf-8") as file:
                data = json.load(file)

            if not isinstance(data, list):
                raise ValueError("Database must contain a list")

            return data

        except (json.JSONDecodeError, OSError, ValueError) as error:
            raise RuntimeError(
                f"Unable to load database: {error}"
            ) from error

    @classmethod
    def save_data(cls, data):

        temp_file = cls.DATABASE.with_suffix(".tmp")

        try:
            with open(temp_file, "w", encoding="utf-8") as file:
                json.dump(data, file, indent=4)

            temp_file.replace(cls.DATABASE)
            return True

        except OSError as error:
            if temp_file.exists():
                temp_file.unlink()

            print(f"Database save error: {error}")
            return False

    # ---------------- PIN SECURITY ----------------

    @staticmethod
    def hash_pin(pin, salt=None):

        if salt is None:
            salt = secrets.token_hex(16)

        hashed = hashlib.pbkdf2_hmac(
            "sha256",
            pin.encode("utf-8"),
            bytes.fromhex(salt),
            200000
        )

        return salt, hashed.hex()

    @classmethod
    def verify_pin(cls, user, pin):

        if not isinstance(pin, str):
            return False

        if "pin_hash" not in user or "salt" not in user:
            return False

        _, hashed = cls.hash_pin(pin, user["salt"])

        return secrets.compare_digest(
            hashed,
            user["pin_hash"]
        )

    # ---------------- ACCOUNT NUMBER ----------------

    @classmethod
    def generate_account_number(cls):

        data = cls.load_data()

        while True:

            account_number = "".join(
                secrets.choice(string.ascii_uppercase + string.digits)
                for _ in range(10)
            )

            exists = any(
                user["accountNo."] == account_number
                for user in data
            )

            if not exists:
                return account_number

    # ---------------- AUTHENTICATION ----------------

    @classmethod
    def authenticate(cls, acc_no, pin):

        data = cls.load_data()

        for index, user in enumerate(data):

            if user["accountNo."] == acc_no:

                if cls.verify_pin(user, pin):
                    return data, index, user

                return None, None, None

        return None, None, None

    # ---------------- CREATE ACCOUNT ----------------

    @classmethod
    def create_account(cls, name, age, email, pin):

        data = cls.load_data()

        if not isinstance(name, str) or not name.strip():
            return None, "Name cannot be empty"

        if not isinstance(email, str) or not email.strip():
            return None, "Email cannot be empty"

        if isinstance(age, bool) or not isinstance(age, int):
            return None, "Age must be a valid integer"

        if age < 18:
            return None, "You must be at least 18 years old"

        if not isinstance(pin, str) or len(pin) != 4 or not pin.isdigit():
            return None, "PIN must contain exactly 4 digits"

        salt, hashed = cls.hash_pin(pin)

        user = {
            "name": name.strip(),
            "age": age,
            "email": email.strip(),
            "salt": salt,
            "pin_hash": hashed,
            "accountNo.": cls.generate_account_number(),
            "balance": 0,
            "transactions": []
        }

        data.append(user)

        if not cls.save_data(data):
            return None, "Unable to save account"

        return user, "Account created successfully"

    # ---------------- FIND USER ----------------

    @classmethod
    def find_user(cls, acc_no, pin):

        _, _, user = cls.authenticate(acc_no, pin)

        if user is None:
            return None

        # Never expose the stored PIN hash.
        return {
            key: value
            for key, value in user.items()
            if key not in ("salt", "pin_hash")
        }

    # ---------------- DEPOSIT ----------------

    @classmethod
    def deposit(cls, acc_no, pin, amount):

        data, index, user = cls.authenticate(acc_no, pin)

        if user is None:
            return False, "Invalid account number or PIN"

        if isinstance(amount, bool) or not isinstance(amount, int):
            return False, "Amount must be an integer"

        if not 0 < amount <= cls.MAX_DEPOSIT:
            return False, "Deposit must be between 1 and 10000"

        user["balance"] += amount

        user["transactions"].append({
            "type": "deposit",
            "amount": amount,
            "balance": user["balance"]
        })

        if not cls.save_data(data):
            return False, "Unable to save transaction"

        return True, "Deposit successful"

    # ---------------- WITHDRAW ----------------

    @classmethod
    def withdraw(cls, acc_no, pin, amount):

        data, index, user = cls.authenticate(acc_no, pin)

        if user is None:
            return False, "Invalid account number or PIN"

        if isinstance(amount, bool) or not isinstance(amount, int):
            return False, "Amount must be an integer"

        if amount <= 0:
            return False, "Amount must be greater than zero"

        if amount > user["balance"]:
            return False, "Insufficient balance"

        user["balance"] -= amount

        user["transactions"].append({
            "type": "withdrawal",
            "amount": amount,
            "balance": user["balance"]
        })

        if not cls.save_data(data):
            return False, "Unable to save transaction"

        return True, "Withdrawal successful"

    # ---------------- UPDATE USER ----------------

    @classmethod
    def update_user(
        cls,
        acc_no,
        pin,
        name=None,
        email=None,
        new_pin=None
    ):

        data, index, user = cls.authenticate(acc_no, pin)

        if user is None:
            return False, "Invalid account number or PIN"

        if name is not None:
            if not isinstance(name, str) or not name.strip():
                return False, "Invalid name"

            user["name"] = name.strip()

        if email is not None:
            if not isinstance(email, str) or not email.strip():
                return False, "Invalid email"

            user["email"] = email.strip()

        if new_pin is not None:

            if (
                not isinstance(new_pin, str)
                or len(new_pin) != 4
                or not new_pin.isdigit()
            ):
                return False, "PIN must contain exactly 4 digits"

            salt, hashed = cls.hash_pin(new_pin)

            user["salt"] = salt
            user["pin_hash"] = hashed

        if not cls.save_data(data):
            return False, "Unable to update account"

        return True, "User details updated successfully"

    # ---------------- TRANSACTION HISTORY ----------------

    @classmethod
    def transaction_history(cls, acc_no, pin):

        _, _, user = cls.authenticate(acc_no, pin)

        if user is None:
            return None, "Invalid account number or PIN"

        return user["transactions"], "Transaction history retrieved"

    # ---------------- DELETE USER ----------------

    @classmethod
    def delete_user(cls, acc_no, pin):

        data, index, user = cls.authenticate(acc_no, pin)

        if user is None:
            return False, "Invalid account number or PIN"

        data.pop(index)

        if not cls.save_data(data):
            return False, "Unable to delete account"

        return True, "Account deleted successfully"
