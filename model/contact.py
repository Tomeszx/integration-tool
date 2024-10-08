from phonenumbers import format_number, parse, PhoneNumberFormat


class Contact:
    def __init__(self, name: str, emails: list[str], phone: str, home_market: str):
        self.name_1 = name
        self.email_1 = emails[0]
        self.phone = phone
        self.name_2 = None
        self.email_2 = None
        if len(emails) > 1:
            self.name_2 = name
            self.email_2 = emails[1]