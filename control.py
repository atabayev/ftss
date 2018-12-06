import json
import requests
import os


def manager_reg():
    post_data = {"name": "Yeldos", "surname": "Atabayev", "email": "yeldos@mail.ru",
                 "phone": "70111111", "username": "Yel", "password": "0609", "pswd": "for_add"}
    requests.post('http://localhost:8000/management/new/', data=post_data)

    post_data = {"name": "Azamat", "surname": "Zhubandykov", "email": "azamat@mail.ru",
                 "phone": "70111122", "username": "Aza", "password": "0609", "pswd": "for_add"}
    r = requests.post('http://localhost:8000/management/new/', data=post_data)
    return r.text


def manager_auth():
    post_data = {"username": "Yel", "password": "0609"}
    r = requests.get('http://localhost:8000/management/authentication/', params=post_data)
    return (r.text)


def translator_reg():
    d = json.loads(manager_auth())
    post_data = {"name": "Адильхан", "surname": "Сапаров", "email": "garond@mail.ru",
                 "phone": "70122211", "direction": "Медицина, ИТ", "username": "AdilkhanS",
                 "password": "0609", "token": d["token"]}
    requests.post('http://localhost:8000/translator/new/', data=post_data)

    post_data = {"name": "Газиз", "surname": "Конаков", "email": "garond@mail.ru",
                 "phone": "70122222", "direction": "Медицина", "username": "GazizK",
                 "password": "0609", "token": d["token"]}
    requests.post('http://localhost:8000/translator/new/', data=post_data)

    post_data = {"name": "Асет", "surname": "Рыскул", "email": "garond@mail.ru",
                 "phone": "70122233", "direction": "ИТ", "username": "AsetR",
                 "password": "0609", "token": d["token"]}
    r = requests.post('http://localhost:8000/translator/new/', data=post_data)
    return r.text


def translator_auth():
    post_data = {"username": "AdilkhanS", "password": "0609"}
    r = requests.get('http://localhost:8000/translator/authentication/', params=post_data)
    return r.text


def client_reg():
    post_data = {"name": "Максат", "surname": "Акабнов", "email": "maksat@mail.ru", "phone": "7013331111"}
    requests.post('http://localhost:8000/registration/reg/', data=post_data)

    post_data = {"name": "Гульназ", "surname": "Абдыкалыкова", "email": "gulnaz@mail.ru", "phone": "7013332222"}
    requests.post('http://localhost:8000/registration/reg/', data=post_data)

    post_data = {"name": "Нурхан", "surname": "Шилдебай", "email": "nurhan@mail.ru", "phone": "7013333333"}
    r = requests.post('http://localhost:8000/registration/reg/', data=post_data)
    return r.text


def new_order():
    post_data = {"language": "Русский - Казахский", "pages": "50", "myid": "AM7013331111", "urgency": "2"}
    files = [('files', open('/home/yel/111/1.jpg', 'rb')),
             ('files', open('/home/yel/111/2.jpg', 'rb')),
             ('files', open('/home/yel/111/3.jpg', 'rb'))]
    r = requests.post('http://localhost:8000/orders/new/', data=post_data, files=files)
    print(r.text)

    post_data = {"language": "Китайский - Казахский", "pages": "74", "myid": "AG7013332222", "urgency": "2"}
    files = [('files', open('/home/yel/111/4.jpg', 'rb')),
             ('files', open('/home/yel/111/5.jpg', 'rb')),
             ('files', open('/home/yel/111/6.jpg', 'rb')),
             ('files', open('/home/yel/111/7.jpg', 'rb'))]
    r = requests.post('http://localhost:8000/orders/new/', data=post_data, files=files)
    print(r.text)

    post_data = {"language": "Казахский - Корейский", "pages": "113", "myid": "SHN7013333333", "urgency": "2"}
    files = [('files', open('/home/yel/111/8.jpg', 'rb')),
             ('files', open('/home/yel/111/9.jpg', 'rb')),
             ('files', open('/home/yel/111/10.jpg', 'rb')),
             ('files', open('/home/yel/111/11.jpg', 'rb')),
             ('files', open('/home/yel/111/12.jpg', 'rb')),
             ('files', open('/home/yel/111/13.gif', 'rb')),
             ('files', open('/home/yel/111/14.png', 'rb'))]
    r = requests.post('http://localhost:8000/orders/new/', data=post_data, files=files)
    print(r.text)

    post_data = {"language": "Корейский - Китайский", "pages": "27", "myid": "AG7013332222",
                 "urgency": "2"}
    files = [('files', open('/home/yel/111/15.jpg', 'rb'))]
    r = requests.post('http://localhost:8000/orders/new/', data=post_data, files=files)
    print(r.text)


def add_translators_to_order():
    token = json.loads(manager_auth())

    post_data = {"oid": "20181113023", "tid": "SA70122211, KG70122222, RA70122233", "token": token["token"]}
    r = requests.post('http://localhost:8000/management/atto/', data=post_data)
    print(r.text)

    # post_data = {"oid": "20181105002", "tid": "SA70122211, KG70122222, RA70122233", "token": token["token"]}
    # requests.post('http://localhost:8000/management/atto/', data=post_data)
    #
    # post_data = {"oid": "20181106001", "tid": "SA70122211, KG70122222, RA70122233", "token": token["token"]}
    # r = requests.post('http://localhost:8000/management/atto/', data=post_data)
    # return r.text


def main():
    pass
    # manager_reg()
    # translator_reg()
    # client_reg()
    #new_order()
    # add_translators_to_order()


if __name__ == '__main__':
    main()

