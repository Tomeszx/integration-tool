from typing import Self

import pycountry


class Address:
    def __init__(self, street: str, city: str, zip: str, country: str):
        self.city = city
        self.zip = zip
        self.country = country
        self.street_1, self.street_2 = self.transform_street(street)

    @staticmethod
    def transform_street(street: str) -> tuple[str, str]:
        street_1, street_2 = "", ""
        for word in street.replace("\n", " ").split(" "):
            if len(f"{street_1} {word}") <= 29:
                street_1 += f" {word}"
            elif len(f"{street_2} {word}") <= 29:
                street_2 += f" {word}"
        return street_1.strip(), street_2.strip()


class ShippingAddress(Address):
    def __init__(self, name: str, street: str, city: str, zip: str, country: str):
        super().__init__(street, city, zip, country)
        self.name = name

    @classmethod
    def from_string(cls, address: str) -> Self:
        country_code = address.split('CountryCode=')[1].strip()[0:2]
        return ShippingAddress(
                name=address.split('Name=')[1].split('|')[0],
                street=address.split('Street=')[1].split('|')[0],
                city=address.split('City=')[1].split('|')[0],
                zip=address.split('Zipcode=')[1].split('|')[0],
                country=pycountry.countries.get(alpha_2=country_code).name
            )


class ShippingAddresses:
    def __init__(self, addresses: list[ShippingAddress]):
        self.data = addresses

    @classmethod
    def from_string(cls, addresses: str) -> Self | None:
        data = []
        addresses_list = addresses.replace("\n", "").strip().split(";")
        try:
            for address in addresses_list:
                if address:
                    data.append(ShippingAddress.from_string(address))
            return ShippingAddresses(data)
        except Exception as e:
            print(e)
            return None


class ReturnAddress:
    def __init__(self, address: ShippingAddress):
        self.data = address

    @classmethod
    def from_string(cls, address: str) -> Self | None:
        try:
            return ReturnAddress(ShippingAddress.from_string(address))
        except Exception as e:
            print(e)
            return None
