from dataclasses import dataclass, field
from decimal import Decimal, ROUND_HALF_UP
from typing import Iterable, Protocol


def _money(x) -> Decimal:
    return (Decimal(str(x)) if not isinstance(x, Decimal) else x).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


@dataclass
class OrderItem:
    """Позиция заказа"""
    name: str
    price: Decimal
    qty: int = 1

    def total(self) -> Decimal:
        return _money(self.price) * self.qty


@dataclass
class Order:
    """Заказ с исходными данными для выбора скидок"""
    items: Iterable[OrderItem] = field(default_factory=list)
    coupon_fixed: Decimal | None = None
    coupon_percent: float | None = None
    is_loyal: bool = False

    def subtotal(self) -> Decimal:
        s = Decimal("0")
        for it in self.items:
            s += it.total()
        return _money(s)


@dataclass
class AppliedDiscount:
    """Применённая скидка"""
    name: str
    amount: Decimal


class Discount(Protocol):
    """Интерфейс стратегии скидки"""
    name: str
    priority: int
    def is_applicable(self, order: Order) -> bool: ...
    def compute(self, order: Order, current_total: Decimal) -> Decimal: ...


@dataclass
class FixedAmountDiscount:
    """Фиксированная скидка"""
    amount: Decimal
    name: str = "Фиксированная"
    priority: int = 10

    def is_applicable(self, order: Order) -> bool:
        return self.amount is not None and _money(self.amount) > 0

    def compute(self, order: Order, current_total: Decimal) -> Decimal:
        return _money(min(_money(self.amount), current_total))


@dataclass
class PercentDiscount:
    """Процентная скидка"""
    percent: float
    name: str = "Процентная"
    priority: int = 20

    def __post_init__(self):
        if not (0 <= float(self.percent) <= 100):
            raise ValueError("Percent must be between 0 and 100")

    def is_applicable(self, order: Order) -> bool:
        return float(self.percent) > 0

    def compute(self, order: Order, current_total: Decimal) -> Decimal:
        return _money(current_total * Decimal(str(self.percent)) / Decimal("100"))


@dataclass
class LoyaltyDiscount:
    """Скидка за лояльность"""
    percent: float = 5.0
    name: str = "Лояльность"
    priority: int = 30

    def is_applicable(self, order: Order) -> bool:
        return order.is_loyal and float(self.percent) > 0

    def compute(self, order: Order, current_total: Decimal) -> Decimal:
        return _money(current_total * Decimal(str(self.percent)) / Decimal("100"))


def select_discounts(order: Order) -> list[Discount]:
    ds: list[Discount] = []
    if order.coupon_fixed is not None:
        ds.append(FixedAmountDiscount(_money(order.coupon_fixed)))
    if order.coupon_percent is not None:
        ds.append(PercentDiscount(float(order.coupon_percent)))
    if order.is_loyal:
        ds.append(LoyaltyDiscount())
    ds.sort(key=lambda d: d.priority)
    return ds


def apply_discounts(order: Order, discounts: list[Discount] | None = None) -> tuple[Decimal, list[AppliedDiscount]]:
    total = order.subtotal()
    applied: list[AppliedDiscount] = []
    ds = discounts if discounts is not None else select_discounts(order)
    for d in ds:
        if not d.is_applicable(order):
            continue
        amount = _money(d.compute(order, total))
        if amount <= 0:
            continue
        total = _money(max(Decimal("0"), total - amount))
        applied.append(AppliedDiscount(d.name, amount))
    return total, applied



def main():
    items = [OrderItem("Книга \"Основы Python\"", Decimal("1000")),
             OrderItem("Ручка", Decimal("49.90"), qty=2)]
    order = Order(items=items, coupon_fixed=Decimal("100"), coupon_percent=10, is_loyal=True)
    total, applied = apply_discounts(order)
    print(f"Сумма: {order.subtotal()}₽ → {total}₽; " + ", ".join(f"{a.name}: -{a.amount}₽" for a in applied))


if __name__ == "__main__":
    main()
