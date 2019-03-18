from django.core.files import File
# from pyfcm import FCMNotification
import shutil
import datetime
import os


def generate_id():
    file_name = 'last.date'
    today = datetime.date.today().isoformat()
    if not os.path.exists(file_name):
        my_file = File(open(file_name, 'w'))
        my_file.write(today)
        my_file.close()
        return ''.join(today.split('-')) + enum(False)
    my_file = File(open(file_name, 'rt'))
    last_date = my_file.read()
    my_file.close()
    if last_date == '':
        last_date = today
        my_file = File(open(file_name, 'w'))
        my_file.write(today)
        my_file.close()
    if today > last_date:
        my_file = File(open(file_name, 'w'))
        my_file.write(today)
        my_file.close()
        return ''.join(today.split('-')) + enum(True)
    else:
        return ''.join(today.split('-')) + enum(False)


def enum(is_reset):
    file_name = 'enum'
    if is_reset:
        my_file = File(open(file_name, 'wt'))
        my_file.close()
    l = '999'
    if os.path.exists(file_name):
        my_file = File(open(file_name, 'rt'))
        l = my_file.read()
        my_file.close()
        if l == '':
            l = '0'
    my_file = File(open(file_name, 'wt'))
    res = {
        0 <= int(l) < 9: '00' + str((lambda x: x + 1)(int(l))),
        9 <= int(l) < 99: '0' + str((lambda x: x + 1)(int(l))),
        99 <= int(l) < 999: str((lambda x: x + 1)(int(l))),
        999 <= int(l): '001',
    }.get(True, 0)
    my_file.write(res)
    my_file.close()
    return res


def validate_file_extension(value):
    import os
    from django.core.exceptions import ValidationError
    ext = os.path.splitext(value.name)[1]  # [0] returns path+filename
    valid_extensions = ['.pdf', '.doc', '.docx', '.jpg', 'png', '.png', '.xlsx', '.xls']
    if not ext.lower() in valid_extensions:
        raise ValidationError(u'Unsupported file extension.')


def content_file_name(instance, filename):
    upload_dir = os.path.join('orders_files', instance.ord_id + "_")
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir)
    return os.path.join(upload_dir, filename)


def content_file_name_for_result(instance, filename):
    upload_dir = os.path.join('orders_files', 'result')
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir)
    return os.path.join(upload_dir, filename)


def create_archive_file(oid, folder):
    files_path = os.path.join('orders_files', oid)
    path_to_save = os.path.join('orders_files', folder)
    zip_name = os.path.join(path_to_save, oid)
    try:
        shutil.make_archive(zip_name, 'zip', files_path)
    except Exception as e:
        return 'error'
    return zip_name + '.zip'


def send_push_notification_to():
    # push_service = FCMNotification(api_key="<api-key>")
    # TODO: Реализовать отправку пуш-уведомлении (цена за заказ, заказ готов, отказ и т.д.)
    return
