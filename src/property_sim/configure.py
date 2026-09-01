import math
from dataclasses import dataclass

Yen = int
Year = int


@dataclass(frozen=True)
class Property:
    sale_price_of_land: Yen
    sale_price_of_building: Yen
    initial_cost: Yen

    set_rent_per_month: list[Yen]
    maintenance_fee_per_month: list[Yen]
    repair_reserve_fund_per_month: list[Yen]

    market_price_of_land_per_month: list[Yen]
    market_price_of_building_per_month: list[Yen]


@dataclass(frozen=True)
class Management:
    management_fee_per_month: list[Yen]


@dataclass(frozen=True)
class Loan:
    amount: Yen
    term: Year
    initial_cost: Yen
    interest_rate_per_year: list[float]

    repayment_per_month: list[Yen]

    def __post_init__(self) -> None:
        assert self.term <= len(self.interest_rate_per_year)
        assert len(self.repayment_per_month) >= int(self.term * 12)
        assert self.validate_balance()

    def validate_balance(self) -> bool:
        remaining = self.amount

        for y in range(self.term):
            interest_rate_per_month = self.interest_rate_per_year[y] / 12
            for m in range(12):
                interest = math.floor(remaining * interest_rate_per_month)
                remaining += interest
                remaining -= self.repayment_per_month[y * 12 + m]

        return (remaining / self.amount) < 0.999


@dataclass(frozen=True)
class Configure:
    prop: Property
    management: Management
    loan: Loan
