from z3 import *

MAX_STEPS = 36

def check_k(k):
    solver = Solver()

    #Program state after each iteration
    a = [Int(f"a_{i}") for i in range(MAX_STEPS + 1)]
    b = [Int(f"b_{i}") for i in range(MAX_STEPS + 1)]

    #True = take the if branch, False = take the else branch
    branch = [Bool(f"branch_{i}") for i in range(MAX_STEPS)]

    #Initial state
    solver.add(a[0] == 1)
    solver.add(b[0] == 1)

    for i in range(MAX_STEPS):

        #If the loop is still running, take one of the two branches.
        solver.add(
            Implies(
                a[i] < 180,

                If(
                    branch[i],

                    #if (__nondet__()) is true
                    And(
                        b[i + 1] == b[i] + 3,
                        a[i + 1] == a[i] + 2 * b[i + 1]
                    ),

                    #else
                    And(
                        b[i + 1] == b[i] + a[i],
                        a[i + 1] == a[i] + 5
                    )
                )
            )
        )
        #Once the loop has terminated, keep the state unchanged.
        solver.add(
            Implies(
                a[i] >= 180,
                And(
                    a[i + 1] == a[i],
                    b[i + 1] == b[i]
                )
            )
        )

    #Crash is possible if we terminate with b = 190 + k
    crash = Or([
        And(
            a[i] >= 180,
            b[i] == 190 + k
        )
        for i in range(MAX_STEPS + 1)
    ])

    solver.add(crash)

    result = solver.check()

    if result == sat:
        model = solver.model()

        print(f"k = {k}: CRASH POSSIBLE")

        #Print one complete execution
        for i in range(MAX_STEPS + 1):
            ai = model.eval(a[i])
            bi = model.eval(b[i])

            print(f"  step {i}: a = {ai}, b = {bi}")

            if ai.as_long() >= 180:
                break

        print()
        return True

    else:
        print(f"k = {k}: SAFE")
        return False

#Test all values of k
for k in range(11):
    check_k(k)