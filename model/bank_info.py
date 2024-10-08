from schwifty import IBAN, bic


def extract_bank_account_number(market: str, iban: str) -> tuple[str, str]:
    for account in iban.replace(" ", "").replace("\n", "").split(";"):
        if market in account.split('IBAN:')[0].split(',') and 'IBAN:' in account:
            iban_number = account.split("IBAN:")[1]
            return IBAN(iban_number).compact, "IBAN/SWIFT"
        elif market in account.split('Account:')[0].split(',') and 'Account:' in account:
            account_number = account.split("Account:")[1]
            return account_number, "Bank transfer"

    raise ValueError(f'The Iban is not correct. Please check if {market=} is not missing or if the number is correct')


class Iban:
    def __init__(self, market: str, iban: str):
        if iban.count(";") == 0:
            self.number = IBAN(iban).compact
            self.type = "IBAN/SWIFT"
        else:
            self.number, self.type = extract_bank_account_number(market, iban)

def extract_bank_code(market: str, bank_code: str) -> str:
    for account in bank_code.replace(" ", "").replace("\n", "").split(";"):
        if market in account.split('SWIFT:')[0].split(',') and 'SWIFT:' in account:
            bank_code = account.split("SWIFT:")[1]
            return bic.BIC(bank_code).compact
        elif f"{market}CODE:" in account:
            account_number = account.split("CODE:")[1]
            return account_number

    raise ValueError(f'Issue while updating {bank_code} on {market=}.')


class BankCode:
    def __init__(self, market: str, bank_code: str):
        if bank_code.count(";") == 0:
            self.number = bic.BIC(bank_code).compact
        else:
            self.number = extract_bank_code(market, bank_code)
