import random

class OTPCodeGenerator:
    
    @staticmethod
    def generate_random() -> str:
        return str(random.randint(1000, 9999))
        
    @staticmethod
    def generate_static() -> str:
        return "9999"