
from collections import UserDict

def parse_input(user_input):  #збирає введений користувачем рядок на команду та аргументи.
    cmd, *args = user_input.split()  # Розділяємо введений рядок на список слів (перше слово — команда, решта — аргументи)
    cmd = cmd.strip().lower()  # Видаляємо зайві пробіли та переводимо команду в нижній регістр
    return cmd, *args  # Повертаємо команду та її аргументи

# Декоратор для обробки помилок введення
def input_error(func):
    # Внутрішня функція-обгортка, яка додає обробку помилок
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)  # Викликаємо оригінальну функцію
        except ValueError:  # Якщо виникла помилка ValueError (наприклад, недостатньо аргументів)
            return "Give me name and phone please."  # Повертаємо повідомлення про помилку
        except IndexError:
            return "Enter the argument for the command." # Повертаємо повідомлення про помилку
        except KeyError:
            return "Error: Contact not found." # Повертаємо повідомлення про помилку

    return inner  # Повертаємо обгортку, яка буде використовуватися замість оригінальної функції


@input_error
def add_contact(args, contacts): # Додає новий контакт у словник contacts
    name, phone = args  # Отримуємо два аргументи: ім'я та телефон
    contacts[name] = phone  # Додаємо контакт у словник
    return "Contact added."  # Повертаємо підтвердження


@input_error
def change_contact(args, contacts): #Оновлює номер телефону для існуючого контакту
    name, phone = args  # Отримуємо ім'я та новий телефон
    if name in contacts:  # Якщо контакт існує у словнику
        contacts[name] = phone  # Оновлюємо номер
        return "Contact updated."  # Підтвердження
    else:
        return "Error: Contact not found"  # Якщо контакту немає, повертаємо помилку

@input_error
def show_phone(args, contacts):  #Повертає номер телефону за ім’ям.
    name = args[0]  # Отримуємо лише ім'я
    if name in contacts: # Перевіряємо, чи є ім'я у словнику
        return f"{contacts[name]}"  # Повертаємо номер телефону
    else:
        return "Error: Contact not found"  # Якщо контакту немає, повертаємо помилку


@input_error
def show_all(contacts):  #Виводить список усіх контактів
    if contacts:  # Перевіряємо, чи є контакти у словнику
        return "\n".join([f"{name}: {phone}" for name, phone in contacts.items()])  # Форматуємо список
    else:
        return "Contact list is empty."  # Якщо контактів немає


#Головний цикл бота, що очікує команди від користувача
def main():
    contacts = {}  # Порожній словник для збереження контактів
    print("Welcome to the assistant bot!")  # Вітання
    
    while True:
        user_input = input("Enter a command: ")  # Запитуємо команду у користувача
        command, *args = parse_input(user_input)  # Розбираємо команду та аргументи

        if command in ["close", "exit"]:  # Якщо команда "close" або "exit" → вихід
            print("Good bye!")
            break
        elif command == "hello":  # Відповідь на "hello"
            print("How can I help you?")
        elif command == "add":  # Додати контакт
            print(add_contact(args, contacts))
        elif command == "change":  # Змінити контакт
            print(change_contact(args, contacts))
        elif command == "phone":  # Показати номер контакту
            print(show_phone(args, contacts))
        elif command == "all":  # Показати всі контакти
            print(show_all(contacts))
        else:
            print("Invalid command.")  # Якщо команда невідома


if __name__ == "__main__":  #запуститься тільки якщо її виконати напряму, а не імпортувати як модуль.
    main()


    

class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)


class Name(Field):
    # реалізація класу
    def __init__(self, value):
        if not value.strip():
            raise ValueError("Name cannot be empty.")
        super().__init__(value)  # type: ignore


class Phone(Field):
    def __init__(self, value):
        if not value.isdigit() or len(value) != 10:
            raise ValueError("Phone number must be exactly 10 digits.")
        super().__init__(value)  # type: ignore


class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []

    # реалізація класу

    def add_phone(self, phone_number):
        self.phones.append(Phone(phone_number))

    def remove_phone(self, phone_number):
        phone_obj = self.find_phone(phone_number)
        if phone_obj:
            self.phones.remove(phone_obj)
        else:
            raise ValueError("Phone number not found.")


    def edit_phone(self, old_phone, new_phone):
        if self.find_phone(old_phone):
            self.add_phone(new_phone)
            self.remove_phone(old_phone)
        else:
            raise ValueError("Old phone number not found.")

    def find_phone(self, phone_number):
        for phone in self.phones:
            if phone.value == phone_number:
                return phone
        return None

    def __str__(self):
        return f"Contact name: {self.name.value}, phones: {'; '.join(p.value for p in self.phones)}"


class AddressBook(UserDict):

    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(name)

    def delete(self, name):
        if name in self.data:
            del self.data[name]

    def __str__(self):
        return "\n".join(str(record) for record in self.data.values())


book = AddressBook()

john_record = Record("John")
john_record.add_phone("1234567890")
john_record.add_phone("5555555555")
book.add_record(john_record)

jane_record = Record("Jane")
jane_record.add_phone("9876543210")
book.add_record(jane_record)

print(book)

john = book.find("John")
john.edit_phone("1234567890", "1112223333")
john.remove_phone("5555555555")
print(john)

found_phone = john.find_phone("5555555555")
print(f"{john.name}: {found_phone}")

book.delete("Jane")
print(book)




