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
    send_push_notification("Привет",
                           "Это из Pycharm",
                           'cQSt72wQL1U:APA91bGkjTfHrUf8Qn9FaxyaQ4yml1OjsJlEtpf4qeF4qMee2yhItQFQrOA03A1UsCyFm_Qo37vlI1f-zFH2R1u1CIMdQwOVk2oisZ3OuSyrd_q-MT5yPbmoWXR6TboaHz19jlorIAkd')
