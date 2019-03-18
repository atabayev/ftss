import smtplib
import random
import hashlib
import os
from django.http import HttpResponse
from wsgiref.util import FileWrapper
import mimetypes  # Импорт класса для обработки неизвестных MIME-типов, базирующихся на расширении файла
from email import encoders  # Импортируем энкодер
from email.mime.base import MIMEBase  # Общий тип
from email.mime.text import MIMEText  # Текст/HTML
from email.mime.multipart import MIMEMultipart  # Многокомпонентный объект


def generate_token():
    random.seed()
    random_res = random.uniform(1000000, 9999999)
    result = hashlib.md5(str(random_res).encode('utf-8')).hexdigest()
    return result


def take_response_for_archive(arch_path):
    filename = os.path.basename(arch_path)
    zip_file = open(arch_path, 'rb')
    content_type = 'application/zip'
    response = HttpResponse(FileWrapper(zip_file), content_type=content_type)
    response['Content-Disposition'] = 'attachment; filename=%s' % filename
    response['Content-Length'] = os.path.getsize(arch_path)
    return response


def send_arch_to_email(addr_to, msg_subj, msg_text, files):
    addr_from = "garond@mail.ru"
    password = "Ee0609195155"
    msg = MIMEMultipart()
    if os.path.isfile(files):
        # attach_file(msg, files)
        file_name = os.path.basename(files)
        ctype, encoding = mimetypes.guess_type(files)  # Определяем тип файла на основе его расширения
        if ctype is None or encoding is not None:  # Если тип файла не определяется
            ctype = 'application/octet-stream'  # Будем использовать общий тип
        maintype, subtype = ctype.split('/', 1)  # Получаем тип и подтип
        with open(files, 'rb') as fp:
            file = MIMEBase(maintype, subtype)  # Используем общий MIME-тип
            file.set_payload(fp.read())  # Добавляем содержимое общего типа (полезную нагрузку)
            fp.close()
            encoders.encode_base64(file)  # Содержимое должно кодироваться как Base64
        file.add_header('Content-Disposition', 'attachment', filename=file_name)  # Добавляем заголовки
        msg.attach(file)  # Присоединяем файл к сообщению
    else:
        msg_text = 'Ошибка при загрузке файла, обратитесь к менеджеру'
        msg_subj = 'Ошибка: ' + msg_subj
    msg['From'] = addr_from
    msg['To'] = addr_to
    msg['Subject'] = msg_subj
    msg.attach(MIMEText(msg_text, 'plain'))
    result = True
    try:
        server = smtplib.SMTP_SSL('smtp.mail.ru', 465)  # Создаем объект SMTP
        server.login(addr_from, password)  # Получаем доступ
        server.send_message(msg)  # Отправляем сообщение
        server.quit()  # Выходим
    except:
        result = False;
    return result


send_arch_to_email('garond@mail.ru', '1', '111', 'D:\\2.jpg')
