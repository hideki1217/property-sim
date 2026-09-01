import math
from dataclasses import dataclass

from .configure import Configure, Yen


@dataclass(frozen=True)
class SimulationResult:
    month: int  # Number of months elapsed (1 to term * 24)
    cumulative_rent: Yen  # Total rental income accumulated
    cumulative_expenses: Yen  # Total operational expenses accumulated
    cumulative_repayment: Yen  # Total loan repayments made
    loan_balance: Yen  # Loan balance at the end of the current month
    market_value: Yen  # Estimated sale price at the end of the current month
    net_profit: Yen  # Total net profit accumulated if sold in the current month


def simulate(c: Configure) -> list[SimulationResult]:
    total_acquisition_cost = (
        c.prop.sale_price_of_land
        + c.prop.sale_price_of_building
        + c.prop.initial_cost
        + c.loan.initial_cost
    )
    initial_investment = total_acquisition_cost - c.loan.amount

    results = list[SimulationResult]()
    total_months = c.loan.term * 12 * 2

    remaining_loan = c.loan.amount
    cum_rent = 0
    cum_expenses = 0
    cum_repayment = 0

    for m in range(total_months):
        year_idx = m // 12

        rent = c.prop.set_rent_per_month[m] if m < len(c.prop.set_rent_per_month) else 0
        maint = (
            c.prop.maintenance_fee_per_month[m]
            if m < len(c.prop.maintenance_fee_per_month)
            else 0
        )
        repair = (
            c.prop.repair_reserve_fund_per_month[m]
            if m < len(c.prop.repair_reserve_fund_per_month)
            else 0
        )
        mgmt = (
            c.management.management_fee_per_month[m]
            if m < len(c.management.management_fee_per_month)
            else 0
        )

        land_val = (
            c.prop.market_price_of_land_per_month[m]
            if m < len(c.prop.market_price_of_land_per_month)
            else 0
        )
        bldg_val = (
            c.prop.market_price_of_building_per_month[m]
            if m < len(c.prop.market_price_of_building_per_month)
            else 0
        )

        cum_rent += rent
        cum_expenses += maint + repair + mgmt

        if m < (c.loan.term * 12):
            rate = c.loan.interest_rate_per_year[year_idx] / 12
            interest = math.floor(remaining_loan * rate)
            repayment = c.loan.repayment_per_month[m]
            remaining_loan = remaining_loan + interest - repayment
            cum_repayment += repayment
        else:
            remaining_loan = 0

        market_value = land_val + bldg_val
        operating_cash_flow = cum_rent - cum_expenses - cum_repayment
        net_profit = (
            operating_cash_flow + market_value - remaining_loan
        ) - initial_investment

        results.append(
            SimulationResult(
                month=m + 1,
                cumulative_rent=cum_rent,
                cumulative_expenses=cum_expenses,
                cumulative_repayment=cum_repayment,
                loan_balance=remaining_loan,
                market_value=market_value,
                net_profit=net_profit,
            )
        )

    return results
