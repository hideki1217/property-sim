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
    cumulative_rent: Yen  # 累計家賃収入
    cumulative_expenses: Yen  # 累計経費
    cumulative_repayment: Yen  # 累計ローン返済額
    cumulative_tax: Yen  # 累計税支出
    loan_balance: Yen  # 残債
    market_value: Yen  # 物件市場価格
    tax_refund: Yen  # その月の還付額
    cumulative_tax_refund: Yen  # 累計還付額
    net_profit: Yen  # 家を売った場合の総収支


def simulate(c: Configure) -> list[SimulationResult]:
    # 固定資産取得税 = 固定資産税評価額 * 固定資産取得税率
    initial_assessment = get_at(c.tax.fixed_asset_tax_assessment_value_per_year, 0, 0)
    real_estate_acquisition_tax = math.floor(
        initial_assessment * c.tax.standard_tax_rate_for_real_estate_acquisition_tax
    )

    # 不動産取得に伴う累計コスト
    total_acquisition_cost = (
        c.prop.sale_price_of_land  # 土地取得価格
        + c.prop.sale_price_of_building  # 建物取得価格
        + c.prop.initial_cost  # 建物取得に関わる雑費
        + c.loan.initial_cost  # 融資編成に関わる雑費
        + real_estate_acquisition_tax  # 固定資産取得税
    )
    # 不動産取得時の手出し = 不動産取得に伴う累計コスト - 融資額
    initial_investment = total_acquisition_cost - c.loan.amount

    results: list[SimulationResult] = []
    total_months = c.loan.term * 12 * 2

    remaining_loan = c.loan.amount  # 残債
    cum_rent = 0  # その月までの累計家賃収入
    cum_expenses = 0  # その月までの累計経費
    cum_repayment = 0  # その月までのローン返済額
    cum_tax = 0  # その月までの累計税支出
    cum_tax_refund = 0  # その月までの累計還付額

    monthly_depreciation = 0  # 一月当たりの減価償却額
    if c.tax.building_useful_life_years > 0:
        monthly_depreciation = math.floor(
            c.prop.sale_price_of_building / (c.tax.building_useful_life_years * 12)
        )  # 一月当たりの減価償却額 = 建物取得価格 / 償却期間(月)

    for m in range(total_months):
        year_idx = m // 12

        rent = get_at(c.prop.set_rent_per_month, m, 0)  # 家賃収入
        maint = get_at(c.prop.maintenance_fee_per_month, m, 0)  # 管理費
        repair = get_at(c.prop.repair_reserve_fund_per_month, m, 0)  # 修繕積立費
        mgmt = get_at(c.management.management_fee_per_month, m, 0)  # 管理手数料

        taxable_expenses = maint + mgmt
        consumption_tax = math.floor(taxable_expenses * c.tax.consumption_tax_rate)
        monthly_expenses = taxable_expenses + repair + consumption_tax  # 経費

        tax_year_idx = min(
            year_idx, max(0, len(c.tax.fixed_asset_tax_assessment_value_per_year) - 1)
        )
        annual_assessment = get_at(
            c.tax.fixed_asset_tax_assessment_value_per_year, tax_year_idx, 0
        )  # 固定資産税評価額

        monthly_fixed_asset_tax = math.floor(
            (annual_assessment * c.tax.standard_tax_rate_for_fixed_asset_tax) / 12
        )  # 固定資産税
        monthly_urban_planning_tax = math.floor(
            (annual_assessment * c.tax.maximum_tax_rate_for_urban_planning_tax) / 12
        )  # 都市計画税
        monthly_holding_tax = (
            monthly_fixed_asset_tax + monthly_urban_planning_tax
        )  # 保有税 = 固定資産税 + 都市計画税

        land_val = get_at(c.prop.market_price_of_land_per_month, m, 0)  # 土地市場価格
        bldg_val = get_at(
            c.prop.market_price_of_building_per_month, m, 0
        )  # 建物市場価格
        market_value = land_val + bldg_val  # 物件市場価格

        cum_rent += rent
        cum_expenses += monthly_expenses
        cum_tax += monthly_holding_tax

        interest = 0
        if m < (c.loan.term * 12) and remaining_loan > 0:  # ローン期間中
            rate_idx = min(year_idx, len(c.loan.interest_rate_per_year) - 1)
            rate = c.loan.interest_rate_per_year[rate_idx] / 12  # その年の金利
            interest = math.floor(remaining_loan * rate)  # 利息 = 残債 * その年の金利
            repayment = get_at(c.loan.repayment_per_month, m, 0)  # ローン返済額

            actual_repayment = min(repayment, remaining_loan + interest)
            remaining_loan = max(
                0, remaining_loan + interest - actual_repayment
            )  # 月末の残債
            cum_repayment += actual_repayment
        else:  # ローン返済後
            remaining_loan = 0

        monthly_tax_refund = 0
        if c.salary_profile is not None:
            tax_deductible_expenses = (
                monthly_expenses + monthly_holding_tax + interest + monthly_depreciation
            )  # 事業支出 = 経費 + 保有税 + 利息 + 減価償却額
            real_estate_income = (
                rent - tax_deductible_expenses
            )  # 不動産収入 = 家賃収入 - 事業支出

            if real_estate_income < 0:  # 不動産収入が負の場合は収入が減り還付が発生
                loss = abs(real_estate_income)
                monthly_tax_refund = math.floor(
                    loss * c.salary_profile.total_tax_rate
                )  # 還付額

        cum_tax_refund += monthly_tax_refund

        operating_cash_flow = (
            cum_rent - cum_expenses - cum_repayment - cum_tax
        )  # 累積CF = 累計家賃収入 - 累計経費 - 累計ローン返済 - 累計税支出
        # その月で家を売った場合の総収支
        #   = (累積CF + 物件市場価格 - 残債 + 累計還付額) - 不動産取得時の手出し
        net_profit = (
            operating_cash_flow + market_value - remaining_loan + cum_tax_refund
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
                tax_refund=monthly_tax_refund,
                cumulative_tax_refund=cum_tax_refund,
                net_profit=net_profit,
            )
        )

    return results
