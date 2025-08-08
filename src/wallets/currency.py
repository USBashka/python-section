from dataclasses import dataclass



@dataclass(frozen=True)
class Currency:
    code: str
    name: str
    symbol: str = "¤"

    def __eq__(self, other):
        return self.code == other.code
    
    def __repr__(self):
        return self.code


rub = Currency("RUB", "Рубль", "₽")
usd = Currency("USD", "Доллар", "$")
eur = Currency("EUR", "Евро", "€")
jpy = Currency("JPY", "Иена", "¥")
btc = Currency("BTC", "Биткоин", "₿")
