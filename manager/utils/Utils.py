from pyfcm import FCMNotification

FB_API_KEY = "AAAAhBEZdCs:APA91bEC4UGYnE_D2bhT3eMWqy4BEv_9bindwcC8AEc4qU_lIbZZxN82dBkzn5tjm65o6jNRntQmtmky7gnjKgJKVY1WClPrUkIGAIXVe-pEbDP_Z4x-0YVoZgImxFFxSBGJaIQAilbW"


def send_push_notification(msg_title, msg_body, devices_reg_id):
    push_service = FCMNotification(api_key=FB_API_KEY)
    registration_id = devices_reg_id
    message_title = msg_title
    message_body = msg_body
    result = push_service.notify_multiple_devices(
        registration_ids=registration_id,
        message_title=message_title,
        message_body=message_body)
    return result


def send_orders_archive():
    pass


if __name__ == '__main__':
    send_push_notification("Новый заказ!",
                           "Поступил новый заказ",
                           ['c7XeC_UEpBU:APA91bEmR1-MIzm8hPMz1W_6jPZobhG5AAMJihGDaHfX9DMCoeYdcU3FvkrGPQJ859S5-bY2E3Oahqtf3tgwx9O5XIEDLWfKMY4edYiqnsysW0E0hV27NUUX8I0pAL9lmW0jra9yN7XU'])
