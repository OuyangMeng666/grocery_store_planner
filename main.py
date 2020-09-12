import telepot
import time
import json
import Flask
import requests
from telepot.loop import MessageLoop
from telepot.namedtuple import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

product_dictionary = {"бытовые товары": "01000", "зубная паста": "01001", "мыло": "01002", "стиральный порошек": "01003",
                      "туалетная бумага": "01004", "маска для лица": "01005", "хлеб": "02010",
                      "батон": "02011", "кукурузный хлеб": "02012", "молочка": "03000", "молоко": "03010",
                      "творог": "03020", "йогурт": "03030", "греческий йогурт": "03031",
                      "сыр": "03030", "моцарелла": "03031", "масло": "03040", "творожный сыр": "03050",
                      "мороженое": "03060", "сметана": "03070", "овощи": "04000", "помидоры": "04001",
                      "огурцы": "04020", "баклажаны": "04030", "кукуруза": "04040", "пекинская капуста": "04050",
                      "перец болгарский": "04060", "зелень": "04070", "укроп": "04071", "петрушка": "04072",
                      "кинза": "04073",
                      "фрукты": "05000", "бананы": "05010", "яблоки": "05020", "лимон": "05030",
                      "имбирь": "05040", "ягоды": "05050",
                      "мясо": "06010", "курица": "06020", "говядина": "06030", "яйца": "06040", "креветки": "06050",
                      "орехи": "10010"}

# написать метод, который спрашивает количество товара, необходимого купить (опционально)
# добавить ui на ткинтере или на питоновской библиотеке для андроида

class Sorter:
    def __init__(self):
        self.encoded_list = []
        self.other = []
        self.new_products = {}

    def get_other(self):
        return self.other

    def get_encoded(self):
        return self.encoded_list

    def get_new_products(self):
        return self.new_products

    def self_encode_product(self, item, item_index):
        print("Encoding ", item, " ", item_index)
        not_exist = True
        i = 1
        while not_exist:
            if item_index[:-1] + str(i) not in product_dictionary.values():
                print("Resulting index is ", item_index[:-1] + str(i))
                product_dictionary[item] = item_index[:-1] + str(i)
                self.add_to_encoded(item)
                self.new_products[item] = item_index
                not_exist = False
            else:
                i += 1

    def sorting_products(self):
        self.encoded_list = sorted(self.encoded_list)

    def add_to_encoded(self, item):
        self.encoded_list.append(product_dictionary[item])

    def add_to_other(self, item):
        self.other.append(item)
        print("Added to other item " + item)

    @staticmethod
    def if_exists(item):
        if item in product_dictionary:
            return True
        else:
            return False

    def output_list(self):
        current_department = self.encoded_list[0][:2]
        print(current_department)
        output_string = ""
        for code in self.encoded_list:
            for item, num in product_dictionary.items():
                if code == num:
                    if code[:2] == current_department:
                        output_string += item
                        output_string += "\n"
                    else:
                        output_string += "\n"
                        output_string += item
                        output_string += "\n"
                        current_department = code[:2]
                    break
        return output_string

    def output_other(self):
        output_str = ""
        for item in self.other:
            output_str += item
            output_str += "\n"
        return output_str

    def clean_list(self):
        self.encoded_list = []
        self.other = []

class User():
    def __init__(self, chat_id):
        self.status = "Start"
        self.product = ""
        self.sort_obj = Sorter()

    def sorter(self):
        return self.sort_obj

    def get_status(self):
        return self.status

    def change_status(self, status):
        self.status = status

    def get_product(self):
        return self.product

    def change_product(self, product):
        self.product = product


bot = telepot.Bot('1187352721:AAEU2YwIDfvVD9xO2MskgwAFR4gGHyGlZds')
bot.setWebhook("https://shopperlistone.herokuapp.com/", max_connections=1)

users = {}

app = Flask(__name__)

def back_to_basic_stage(chat_id):
    users[chat_id].change_product("")
    users[chat_id].change_status("Getting products")
    bot.sendMessage(chat_id, "Продолжайте ввод продуктов или напишите всё для завершения")

@app.route('/{}'.format(secret), methods=["POST"])
def handle(msg):
    update = request.get_json()
    global status
    global product
    if "message" in update:
        text = update["message"]["text"]
        chat_id = update["message"]["chat"]["id"]
      print(text)
      if chat_id not in users.keys():
          users[chat_id] = User(chat_id)
      if users[chat_id].get_status() == "Start":
          if update["message"]["text"] == "/start":
              bot.sendMessage(chat_id, """
  Привет! Я бот-планировщик покупок.
  Введите покупки по одной. Для окончания списка введите 'всё': """)
          else:
              users[chat_id].change_status("Getting products")
      if users[chat_id].get_status() == "Getting products" and update["message"]["text"].lower() in ["всё", "все"]:
          users[chat_id].sorter().sorting_products()
          bot.sendMessage(chat_id, "Ваш продуктовый список готов")
          if users[chat_id].sorter().get_encoded():
              bot.sendMessage(chat_id, users[chat_id].sorter().output_list())
          else:
              bot.sendMessage(chat_id, "Сортированный списк пуст")
          if users[chat_id].sorter().get_other():
              bot.sendMessage(chat_id, "Продукты из неопределенной категории:")
              bot.sendMessage(chat_id, users[chat_id].sorter().output_other())
          with open("products.txt", "a", encoding='utf-8') as file:
              file.write(str(users[chat_id].sorter().get_new_products()))
          users[chat_id].sorter().clean_list()
          bot.sendMessage(chat_id, "Списки очищены. Для работы со следующим списком, начните вводить продукты")
          status = "Start"
      if users[chat_id].get_status() == "Getting products" and update["message"]["text"].lower() not in ["всё", "все"]:
          sorter = users[chat_id].sorter()
          print(sorter)
          if sorter.if_exists(update["message"]["text"].lower()):
              users[chat_id].sorter().add_to_encoded(update["message"]["text"].lower())
              bot.sendMessage(chat_id, "Продукт " + update["message"]["text"] + " добавлен")
          else:
              users[chat_id].change_status("New product")
              users[chat_id].change_producttext.lower())
      if users[chat_id].get_status() == "New product":
          markup = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="Да"), KeyboardButton(text="Нет")]], resize_keyboard=True)
          bot.sendMessage(chat_id, "Добавить " + users[chat_id].get_product() + " в словарь?", reply_markup=markup)
          users[chat_id].change_status("Managing list")
      if users[chat_id].get_status() == "Managing list" and update["message"]["text"] not in ["Да", "Нет"]:
          bot.sendMessage(chat_id, "Пожалуйста, введите Да или Нет")
      if users[chat_id].get_status() == "Managing list" and update["message"]["text"] == "Да":
          users[chat_id].change_status("Encoding")
      if users[chat_id].get_status() == "Managing list" and update["message"]["text"] == "Нет":
          users[chat_id].sorter().add_to_other(users[chat_id].get_product().lower())
          bot.sendMessage(chat_id, "Пожалуйста, введите следующий продукт или напишите 'всё' для вывода списка", reply_markup=ReplyKeyboardRemove())
          users[chat_id].change_status("Getting products")
      if users[chat_id].get_status() == "Encoding" and update["message"]["text"] not in ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"]:
          bot.sendMessage(chat_id, """
  Введите категорию продукта:
  1. бытовые товары
  2. хлебобулочные изделия
  3. молочная продукция
  4. овощи
  5. фрукты
  6. мясные продукты
  7. рыбные продукты
  8. консервы
  9. напитки
  10. другие
  """, reply_markup=ReplyKeyboardRemove())
      if update["message"]["text"] == "1" and users[chat_id].get_status() == "Encoding":
          bot.sendMessage(chat_id, "Добавляем в словарь продукт " + users[chat_id].get_product())
          users[chat_id].sorter().self_encode_product(users[chat_id].get_product(), "01000")
          back_to_basic_stage(chat_id)

      if update["message"]["text"] == "2" and users[chat_id].get_status() == "Encoding":
          bot.sendMessage(chat_id, "Добавляем в словарь продукт " + users[chat_id].get_product())
          users[chat_id].sorter().self_encode_product(product, "02000")
          back_to_basic_stage(chat_id)

      if update["message"]["text"] == "3" and users[chat_id].get_status() == "Encoding":
          bot.sendMessage(chat_id, "Добавляем в словарь продукт " + users[chat_id].get_product())
          users[chat_id].sorter().self_encode_product(users[chat_id].get_product(), "03000")
          back_to_basic_stage(chat_id)

      if update["message"]["text"] == "4" and users[chat_id].get_status() == "Encoding":
          bot.sendMessage(chat_id, "Добавляем в словарь продукт " + users[chat_id].get_product())
          users[chat_id].sorter().self_encode_product(users[chat_id].get_product(), "04000")
          back_to_basic_stage(chat_id)

      if update["message"]["text"] == "5" and users[chat_id].get_status() == "Encoding":
          bot.sendMessage(chat_id, "Добавляем в словарь продукт " + users[chat_id].get_product())
          users[chat_id].sorter().self_encode_product(users[chat_id].get_product(), "05000")
          back_to_basic_stage(chat_id)

      if update["message"]["text"] == "6" and users[chat_id].get_status() == "Encoding":
          bot.sendMessage(chat_id, "Добавляем в словарь продукт " + users[chat_id].get_product())
          users[chat_id].sorter().self_encode_product(users[chat_id].get_product(), "06000")
          back_to_basic_stage(chat_id)

      if update["message"]["text"] == "7" and users[chat_id].get_status() == "Encoding":
          bot.sendMessage(chat_id, "Добавляем в словарь продукт " + users[chat_id].get_product())
          users[chat_id].sorter().self_encode_product(users[chat_id].get_product(), "07000")
          back_to_basic_stage(chat_id)

      if update["message"]["text"] == "8" and users[chat_id].get_status() == "Encoding":
          bot.sendMessage(chat_id, "Добавляем в словарь продукт " + users[chat_id].get_product())
          users[chat_id].sorter().self_encode_product(product, "08000")
          back_to_basic_stage(chat_id)

      if update["message"]["text"] == "9" and users[chat_id].get_status() == "Encoding":
          bot.sendMessage(chat_id, "Добавляем в словарь продукт " + users[chat_id].get_product())
          users[chat_id].sorter().self_encode_product(users[chat_id].get_product(), "09000")
          back_to_basic_stage(chat_id)

      if update["message"]["text"] == "10" and users[chat_id].get_status() == "Encoding":
          bot.sendMessage(chat_id, "Добавляем в словарь продукт " + users[chat_id].get_product())
          users[chat_id].sorter().self_encode_product(users[chat_id].get_product(), "10000")
          back_to_basic_stage(chat_id)
    return "OK"


#MessageLoop(bot, handle).run_as_thread()
#print('Listening ...')

#while 1:
#    time.sleep(10)

