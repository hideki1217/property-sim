from property_sim.configure import Configure, Loan, Management, Property, Tax
from property_sim.simulator import simulate
from property_sim.visualizer import plot_simulation


def rc_construction(y: int) -> float:
    if y == 0:
        return 1.0
    if y < 5:
        return 0.95
    if y < 10:
        return 0.89
    if y < 15:
        return 0.81
    if y < 20:
        return 0.73
    if y < 25:
        return 0.64
    if y < 40:
        return 0.55
    if y < 60:
        return 0.33
    return 0.2


def test_with_tax() -> None:
    term = 35
    c = Configure(
        prop=Property(
            3190_0000 - 1760_0000,
            1760_0000,
            110_0000,
            [10_0500 for _ in range(term * 2 * 12)],
            [5910 for _ in range(term * 2 * 12)],
            [1480 for _ in range(term * 2 * 12)],
            [
                (3190_0000 - 1760_0000) * (0.8) * ((0.98) ** (i // 12))
                for i in range(term * 2 * 12)
            ],
            [1760_0000 for _ in range(term * 2 * 12)],
        ),
        management=Management([8683 for _ in range(term * 2 * 12)]),
        loan=Loan(
            3290_0000,
            term,
            10_0000,
            [0.025 for _ in range(term * 12)],
            [11_7616 for _ in range(term * 12)],
        ),
        tax=Tax(
            0.1,
            0.014,
            0.003,
            0.04,
            [
                ((3190_0000 - 1760_0000) * 0.7 + 1760_0000 * 0.7) * rc_construction(y)
                for y in range(term * 2)
            ],
        ),
    )
    res = simulate(c)
    plot_simulation(res, "./property_sim-with_tax.png")


def test_without_tax() -> None:
    term = 35
    c = Configure(
        prop=Property(
            3190_0000 - 1760_0000,
            1760_0000,
            110_0000,
            [10_0500 for _ in range(term * 2 * 12)],
            [5910 for _ in range(term * 2 * 12)],
            [1480 for _ in range(term * 2 * 12)],
            [
                (3190_0000 - 1760_0000) * (0.8) * ((0.98) ** (i // 12))
                for i in range(term * 2 * 12)
            ],
            [1760_0000 for _ in range(term * 2 * 12)],
        ),
        management=Management([8683 for _ in range(term * 2 * 12)]),
        loan=Loan(
            3290_0000,
            term,
            10_0000,
            [0.025 for _ in range(term * 12)],
            [11_7616 for _ in range(term * 12)],
        ),
        tax=Tax(
            0,
            0,
            0,
            0,
            [0 for _ in range(term * 2)],
        ),
    )
    res = simulate(c)
    plot_simulation(res, "./property_sim-without_tax.png")
