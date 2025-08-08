from dataclasses import dataclass
from decimal import Decimal

from currency import rub, usd
from exceptions import NegativeValueException, NotComparisonException


@dataclass
class Money:
    """Количество денег в определённой валюте"""
    
    value: Decimal = 0
    currency: str = rub

    def __add__(self, other):
        if self.currency == other.currency:
            return Money(value=self.value+other.value, currency=self.currency)
        else:
            raise NotComparisonException
    
    def __sub__(self, other):
        if self.currency == other.currency:
            return Money(value=self.value-other.value, currency=self.currency)
        else:
            raise NotComparisonException
    
    def __eq__(self, other):
        if self.currency == other.currency:
            return self.value == other.value
        else:
            raise NotComparisonException

class Wallet:
    """Кошелёк с несколькими валютами"""

    def __init__(self, money=None):
        self.currencies = {}
        if money:
            self.currencies[money.currency] = money

    def __getitem__(self, currency):
        return self.currencies.get(currency, Money(value=0, currency=currency))

    def __setitem__(self, currency, money):
        self.currencies[currency] = money

    def __delitem__(self, currency):
        self.currencies.pop(currency, None)

    def __contains__(self, currency):
        return currency in self.currencies

    def __len__(self):
        return len(self.currencies)
    
    def __repr__(self):
        return str(self.currencies)

    def add(self, money):
        current = self[money.currency]
        self[money.currency] = current + money
        return self

    def sub(self, money):
        current = self[money.currency]
        result = current - money
        if result.value < 0:
            raise NegativeValueException("Resulting money value cannot be negative.")
        self[money.currency] = result
        return self



def main():
    ten_rubles = Money(1) + Money(8) + Money(1, rub)
    wallet = Wallet()
    print(wallet)
    wallet.add(ten_rubles)
    print(wallet)
    wallet.add(Money(1000000, usd))
    print(wallet)


if __name__ == "__main__":
    main()