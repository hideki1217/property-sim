import math
from dataclasses import dataclass
from typing import Sequence, TypeVar

from .configure import Configure, Yen

T = TypeVar("T")


def get_at(seq: Sequence[T], index: int, default: T) -> T:
    return seq[index] if index < len(seq) else default


@dataclass(frozen=True)
class SimulationResult:
    month: int
    cumulative_rent: Yen
    cumulative_expenses: Yen
    cumulative_repayment: Yen
    cumulative_tax: Yen
    loan_balance: Yen
    market_value: Yen
    net_profit: Yen


def simulate(c: Configure) -> list[SimulationResult]:
    initial_assessment = get_at(c.tax.fixed_asset_tax_assessment_value_per_year, 0, 0)
    real_estate_acquisition_tax = math.floor(
        initial_assessment * c.tax.standard_tax_rate_for_real_estate_acquisition_tax
    )

    total_acquisition_cost = (
        c.prop.sale_price_of_land
        + c.prop.sale_price_of_building
        + c.prop.initial_cost
        + c.loan.initial_cost
        + real_estate_acquisition_tax
    )
    initial_investment = total_acquisition_cost - c.loan.amount

    results: list[SimulationResult] = []
    total_months = c.loan.term * 12 * 2

    remaining_loan = c.loan.amount
    cum_rent = 0
    cum_expenses = 0
    cum_repayment = 0
    cum_tax = 0

    for m in range(total_months):
        year_idx = m // 12

        rent = get_at(c.prop.set_rent_per_month, m, 0)
        maint = get_at(c.prop.maintenance_fee_per_month, m, 0)
        repair = get_at(c.prop.repair_reserve_fund_per_month, m, 0)
        mgmt = get_at(c.management.management_fee_per_month, m, 0)

        taxable_expenses = maint + mgmt
        consumption_tax = math.floor(taxable_expenses * c.tax.consumption_tax_rate)
        monthly_expenses = taxable_expenses + repair + consumption_tax

        # Property Tax (Fixed Asset Tax/Urban Planning Tax)
        tax_year_idx = min(
            year_idx, max(0, len(c.tax.fixed_asset_tax_assessment_value_per_year) - 1)
        )
        annual_assessment = get_at(
            c.tax.fixed_asset_tax_assessment_value_per_year, tax_year_idx, 0
        )

        monthly_fixed_asset_tax = math.floor(
            (annual_assessment * c.tax.standard_tax_rate_for_fixed_asset_tax) / 12
        )
        monthly_urban_planning_tax = math.floor(
            (annual_assessment * c.tax.maximum_tax_rate_for_urban_planning_tax) / 12
        )
        monthly_holding_tax = monthly_fixed_asset_tax + monthly_urban_planning_tax

        # Property Price
        land_val = get_at(c.prop.market_price_of_land_per_month, m, 0)
        bldg_val = get_at(c.prop.market_price_of_building_per_month, m, 0)
        market_value = land_val + bldg_val

        cum_rent += rent
        cum_expenses += monthly_expenses
        cum_tax += monthly_holding_tax

        # Loan Repayment Calculation
        if m < (c.loan.term * 12) and remaining_loan > 0:
            rate_idx = min(year_idx, len(c.loan.interest_rate_per_year) - 1)
            rate = c.loan.interest_rate_per_year[rate_idx] / 12
            interest = math.floor(remaining_loan * rate)
            repayment = get_at(c.loan.repayment_per_month, m, 0)

            actual_repayment = min(repayment, remaining_loan + interest)
            remaining_loan = max(0, remaining_loan + interest - actual_repayment)
            cum_repayment += actual_repayment
        else:
            remaining_loan = 0

        # Profit and Loss Statement
        operating_cash_flow = cum_rent - cum_expenses - cum_repayment - cum_tax
        net_profit = (
            operating_cash_flow + market_value - remaining_loan
        ) - initial_investment

        results.append(
            SimulationResult(
                month=m + 1,
                cumulative_rent=cum_rent,
                cumulative_expenses=cum_expenses,
                cumulative_repayment=cum_repayment,
                cumulative_tax=cum_tax,
                loan_balance=remaining_loan,
                market_value=market_value,
                net_profit=net_profit,
            )
        )

    return results
