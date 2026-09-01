import matplotlib.pyplot as plt

from .simulator import SimulationResult


def plot_simulation(res: list[SimulationResult], output_path: str) -> None:
    years = [x.month / 12 for x in res]
    net_profits = [x.net_profit / 10000 for x in res]
    market_values = [x.market_value / 10000 for x in res]
    loan_balances = [x.loan_balance / 10000 for x in res]

    # Use English text to ensure standard environment compatibility without font issues
    plt.rcParams["font.family"] = "sans-serif"

    fig, axes = plt.subplots(2, 1, figsize=(11, 8), sharex=True)

    axes[0].plot(
        years,
        net_profits,
        label="Cumulative Net Profit (Sell at Month)",
        color="#2ca02c",
        linewidth=2,
    )
    axes[0].axhline(
        0, color="red", linestyle="--", alpha=0.7, label="Break-even (0 JPY)"
    )
    axes[0].axvline(35, color="gray", linestyle=":", label="Loan Payoff (35 Yrs)")
    axes[0].set_ylabel("Amount (10k JPY)")
    axes[0].set_title(
        "Cumulative Net Profit if Sold at Given Month", fontsize=12, fontweight="bold"
    )
    axes[0].grid(True, linestyle=":", alpha=0.6)
    axes[0].legend(loc="upper left")

    axes[1].plot(
        years,
        market_values,
        label="Expected Market Value (Land+Bldg)",
        color="#1f77b4",
        linewidth=2,
    )
    axes[1].plot(
        years, loan_balances, label="Loan Balance", color="#ff7f0e", linewidth=2
    )
    axes[1].axvline(35, color="gray", linestyle=":", label="Loan Payoff (35 Yrs)")
    axes[1].set_xlabel("Elapsed Years")
    axes[1].set_ylabel("Amount (10k JPY)")
    axes[1].set_title("Market Value vs Loan Balance", fontsize=12, fontweight="bold")
    axes[1].grid(True, linestyle=":", alpha=0.6)
    axes[1].legend(loc="upper right")

    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    print(f"File generated at: {output_path}")
