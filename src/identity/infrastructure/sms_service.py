from datetime import datetime
from src.identity.application.interfaces import ISmsSender
from src.identity.domain.value_objects import PhoneNumber

class SmsSender(ISmsSender):
    def send_sms(self, phone_number:PhoneNumber, text: str) -> None:
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")       
        print(f"Phone_number: {phone_number.value}--SMS: {text}--time: {current_time}")

