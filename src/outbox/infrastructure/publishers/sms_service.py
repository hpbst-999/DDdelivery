from typing import Any
from datetime import datetime


class SmsSenderPublisher:
    def __init__(self, api_key: str | None = None, base_url: str | None = None):
        self.api_key = api_key
        self.base_url = base_url

    async def send_sms(self, payload: dict[str, Any]) -> None:
        phone_number = payload["phone_number"]
        code = payload["code"]
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")       
        print(f"Phone_number: {phone_number}--SMS: {code}--time: {current_time}")
