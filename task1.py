from z3 import *

N = 6

def solve(extra_constraint=False):

    opt = Optimize()

    # Variables
    nuzzle  = [Int(f"n_{i}") for i in range(N)]
    prittle = [Int(f"p_{i}") for i in range(N)]
    skipple = [Int(f"s_{i}") for i in range(N)]
    crottle = [Int(f"c_{i}") for i in range(N)]
    dupple  = [Int(f"d_{i}") for i in range(N)]

    # Non-negative quantities
    for i in range(N):
        opt.add(nuzzle[i] >= 0)
        opt.add(prittle[i] >= 0)
        opt.add(skipple[i] >= 0)
        opt.add(crottle[i] >= 0)
        opt.add(dupple[i] >= 0)

    # Required quantities
    opt.add(Sum(nuzzle) == 6)
    opt.add(Sum(prittle) == 12)
    opt.add(Sum(skipple) == 15)
    opt.add(Sum(crottle) == 8)

    # Truck capacity
    for i in range(N):
        weight = (
            800 * nuzzle[i]
            + 405 * prittle[i]
            + 500 * skipple[i]
            + 2500 * crottle[i]
            + 600 * dupple[i]
        )
        blocks = (
            nuzzle[i]
            + prittle[i]
            + skipple[i]
            + crottle[i]
            + dupple[i]
        )

        opt.add(weight <= 8000)
        opt.add(blocks <= 10)

    # Prittles on at least 5 trucks
    opt.add(
        Sum([If(prittle[i] > 0, 1, 0) for i in range(N)]) >= 5
    )

    # Only 2 trucks can carry skipples
    skipple_truck = [Bool(f"skipple_truck_{i}") for i in range(N)]
    opt.add(
        Sum([If(skipple_truck[i], 1, 0) for i in range(N)]) == 2
    )

    for i in range(N):
        opt.add(
            Implies(
                Not(skipple_truck[i]),
                skipple[i] == 0
            )
        )
    # Extra constraint for part (b)
    if extra_constraint:
        for i in range(N):
            opt.add(
                Implies(
                    crottle[i] > 0,
                    dupple[i] >= 2
                )
            )

    # Objective
    total_dupples = Sum(dupple)
    opt.maximize(total_dupples)

    # Solve
    if opt.check() == sat:

        model = opt.model()

        print("--------------------------------")
        if extra_constraint:
            print("PART (b)")
        else:
            print("PART (a)")

        print("Maximum dupples:",
              model.eval(total_dupples))

        print()

        for i in range(N):
            print(
                f"Truck {i + 1}: "
                f"nuzzles={model.eval(nuzzle[i])}, "
                f"prittles={model.eval(prittle[i])}, "
                f"skipples={model.eval(skipple[i])}, "
                f"crottles={model.eval(crottle[i])}, "
                f"dupples={model.eval(dupple[i])}"
            )

        print()

# Output
solve(False)   # Part (a)
solve(True)    # Part (b)