from .configure import Configure, Loan, Management, Property
from .simulator import simulate
from .visualizer import plot_simulation


def main() -> None:
    print("Hello from property_sim!")

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
    )
    res = simulate(c)
    plot_simulation(res, "./property_sim.png")
