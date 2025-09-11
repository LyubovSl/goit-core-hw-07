
from collections import UserDict
from datetime import datetime, timedelta

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

class Birthday(Field):  # Клас для зберігання дня народження
    def __init__(self, value):  # Перевірка та конвертація дати
        try:
            datetime.strptime(value, "%d.%m.%Y")  # Конвертація рядка у дату
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")
        super().__init__(value)  # Виклик конструктора базового класу

class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

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

    def add_birthday(self, birthday_str):  # Додавання дня народження
        self.birthday = Birthday(birthday_str)        

    def __str__(self):
        phones_str = "; ".join(p.value for p in self.phones) if self.phones else "No phones"
        birthday_str = self.birthday.value if self.birthday else "No birthday"
        return f"Contact name: {self.name.value}, phones: {phones_str}, birthday: {birthday_str}"

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

    def get_upcoming_birthdays(self):  # Список ДН на 7 днів вперед
        today = datetime.today().date()
        upcoming = []
        for record in self.data.values():
            if record.birthday:
                bday_date = datetime.strptime(record.birthday.value, "%d.%m.%Y").date()
                bday_this_year = bday_date.replace(year=today.year)
                if bday_this_year < today:
                    bday_this_year = bday_this_year.replace(year=today.year + 1)
                days_diff = (bday_this_year - today).days
                if 0 <= days_diff <= 7:
                    congratulate_date = bday_this_year
                    if congratulate_date.weekday() >= 5:  # Якщо вихідний → перенос на понеділок
                        congratulate_date += timedelta(days=(7 - congratulate_date.weekday()))
                    upcoming.append({
                        "name": record.name.value,
                        "birthday": congratulate_date.strftime("%d.%m.%Y")
                    })
        return upcoming




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
        except AttributeError:
            return "Error: Contact not found."
    return inner  # Повертаємо обгортку, яка буде використовуватися замість оригінальної функції


@input_error
def add_contact(args, book: AddressBook): # Додає новий контакт у словник contacts
    name, phone, *_ = args
    record = book.find(name)
    message = "Contact updated."
    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Contact added."
    record.add_phone(phone)
    return message

@input_error
def change_contact(args, book: AddressBook): #Оновлює номер телефону для існуючого контакту
    name, old_phone, new_phone = args
    record = book.find(name)
    record.edit_phone(old_phone, new_phone)
    return "Phone updated."

@input_error
def show_phone(args, book: AddressBook):  #Повертає номер телефону за ім’ям.
    name = args[0]  
    record = book.find(name)
    return "; ".join(phone.value for phone in record.phones)

@input_error
def show_all(book: AddressBook):  #Виводить список усіх контактів
    if book:  # Перевіряємо, чи є контакти у словнику
        return "\n".join(str(record) for record in book.values())  # Форматуємо список
    else:
        return "Contact list is empty."  # Якщо контактів немає

@input_error
def add_birthday(args, book: AddressBook):
    name, birthday_str = args
    record = book.find(name)
    record.add_birthday(birthday_str)
    return f"Birthday added for {name}."
    
@input_error
def show_birthday(args, book: AddressBook):
    name = args[0]
    record = book.find(name)
    return f"{name}'s birthday is {record.birthday.value}"

@input_error
def birthdays(args, book: AddressBook):
    upcoming = book.get_upcoming_birthdays()
    if not upcoming:
        return "No upcoming birthdays."
    return "\n".join(f"{item['name']} -> {item['birthday']}" for item in upcoming)

def parse_input(user_input):  #збирає введений користувачем рядок на команду та аргументи.
    if not user_input.strip():   # порожній рядок
        return "", []
    cmd, *args = user_input.split()  # Розділяємо введений рядок на список слів (перше слово — команда, решта — аргументи)
    cmd = cmd.strip().lower()  # Видаляємо зайві пробіли та переводимо команду в нижній регістр
    return cmd, *args  # Повертаємо команду та її аргументи

#Головний цикл бота, що очікує команди від користувача
def main():
    book = AddressBook()  # Порожній словник для збереження контактів
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
            print(add_contact(args, book))
        elif command == "change":  # Змінити контакт
            print(change_contact(args, book))
        elif command == "phone":  # Показати номер контакту
            print(show_phone(args, book))
        elif command == "all":  # Показати всі контакти
            print(show_all(book))
        elif command == "add-birthday": #Додати день народження
            print(add_birthday(args, book))
        elif command == "show-birthday":  #Показати день народження 
            print(show_birthday(args, book)) 
        elif command == "birthdays":   
            print(birthdays(args, book))    
        else:
            print("Invalid command.")  # Якщо команда невідома


if __name__ == "__main__":  #запуститься тільки якщо її виконати напряму, а не імпортувати як модуль.
    main()








