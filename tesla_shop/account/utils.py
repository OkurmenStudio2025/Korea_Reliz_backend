import requests
import logging
from decouple import config
import uuid

logger = logging.getLogger(__name__)

def send_sms(phone_number, verification_code):    
    login = config('LOGIN')
    password = config('PASSWORD')
    transactionId = str(uuid.uuid4())
    sender = config('SENDER')
    text = verification_code
    phone = phone_number

    xml_data = f"""<?xml version="1.0" encoding="UTF-8"?>
    <message>
        <login>{login}</login>
        <pwd>{password}</pwd>
        <id>{transactionId}</id>
        <sender>{sender}</sender>
        <text>{text}</text>
        <phones>
            <phone>{phone}</phone>
        </phones>
    </message>"""
    
    url = 'https://smspro.nikita.kg/api/message'
    headers = {'Content-Type': 'application/xml'}

    try:
        response = requests.post(url, data=xml_data, headers=headers)
        response.raise_for_status()  
        logger.info('Ответ сервера: %s', response.text)
        
        return response.text
    except requests.exceptions.RequestException as e:
        logger.error('Ошибка при отправке SMS: %s', e)
        return None
