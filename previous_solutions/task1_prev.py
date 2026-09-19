from z3 import *

# Total number of trucks
N = 6

"""
• Six nuzzles, each of weight 800 kg.
• Twelve prittles, each of weight 405 kg.
• Fifteen skipples, each of weight 500 kg.
• Eight crottles, each of weight 2500 kg.
• A number of dupples, each of weight 600 kg
"""
def solve(part_b_constraint=False):
    s = Solver()

    # Set of integer variables representing the number of type of good in each truck i
    nuzzle = [Int(f"n_{i}") for i in range(N)]
    prittle = [Int(f"p_{i}") for i in range(N)]
    skipple = [Int(f"s_{i}") for i in range(N)]
    crottle = [Int(f"c_{i}") for i in range(N)]
    dupple  = [Int(f"d_{i}") for i in range(N)]

    goods = [nuzzle, prittle, skipple, crottle, dupple]
    weights = [800,405,500,2500,600]
    good_quantity = [6,12,15,8, None]

    for good in goods:
        for item in good:
            s.add(item >= 0)

    for i in range(N):
        s.add(Sum([weight*good[i] for weight, good in zip(weights, goods)]) <= 8000)
        s.add(Sum([good[i] for good in goods]) <= 10)

    # Required quantities
    for good, quantity in zip(goods, good_quantity):
        if quantity is not None:
            s.add(Sum(good) == quantity)


    # Boolean mawk for trucks that can caeey skipples
    skipple_truck = [Bool(f"skipple_truck_{i}") for i in range(N)]
    s.add(Sum([If(skipple_truck[i], 1, 0) for i in range(N)]) == 2)

    # Prittles have to be distributed over at least 5 trucks
    s.add(Sum([If(prittle[i] > 0, 1, 0) for i in range(N)]) >= 5)

    # Condition: if a truck is not designed for skipples -> there shouldn't be skipples in it
    for i in range(N):
        s.add(Implies(Not(skipple_truck[i]),skipple[i] == 0))

    if part_b_constraint:
        for i in range(N):
            s.add(Implies(crottle[i] > 0, dupple[i] >= 2))


    k = 0
    best_model = None
    while True:
        s.add(Sum(dupple) >= k + 1)      
        if s.check() != sat:
            break                        
        best_model = s.model()          
        k += 1

        
    print(f"Maximum dupples:{k}\n")
    print()
    for i in range(N):
        print(f"Truck {i + 1}: " + ", ".join(
            f"{name}={best_model.eval(good[i])}"
            for name, good in zip(["nuzzles", "prittles", "skipples", "crottles", "dupples"], goods)
        ))
    print()

# def solve(extra_constraint=False):

#     opt = Optimize()

#     # Variables
#     nuzzle  = [Int(f"n_{i}") for i in range(N)]
#     prittle = [Int(f"p_{i}") for i in range(N)]
#     skipple = [Int(f"s_{i}") for i in range(N)]
#     crottle = [Int(f"c_{i}") for i in range(N)]
#     dupple  = [Int(f"d_{i}") for i in range(N)]

#     # Non-negative quantities
#     for i in range(N):
#         opt.add(nuzzle[i] >= 0)
#         opt.add(prittle[i] >= 0)
#         opt.add(skipple[i] >= 0)
#         opt.add(crottle[i] >= 0)
#         opt.add(dupple[i] >= 0)

#     # Required quantities
#     opt.add(Sum(nuzzle) == 6)
#     opt.add(Sum(prittle) == 12)
#     opt.add(Sum(skipple) == 15)
#     opt.add(Sum(crottle) == 8)

#     # Truck capacity
#     for i in range(N):
#         weight = 800*nuzzle[i] + 405*prittle[i] + 500*skipple[i]+ 2500*crottle[i] + 600*dupple[i]
#         blocks = nuzzle[i] + prittle[i] + skipple[i] + crottle[i] + dupple[i]

#         # Constraints on trucs capacity: 8000 kg, 10 blocks max
#         opt.add(weight <= 8000)
#         opt.add(blocks <= 10)

#     # Prittles have to be distributed over at least 5 trucks
#     opt.add(Sum([If(prittle[i] > 0, 1, 0) for i in range(N)]) >= 5)

#     # Only 2 trucks can carry skipples
#     skipple_truck = [Bool(f"skipple_truck_{i}") for i in range(N)]
#     opt.add(Sum([If(skipple_truck[i], 1, 0) for i in range(N)]) == 2)

#     # Condition: if a truck is not designed for skipples -> there shouldn't be skipples in it
#     for i in range(N):
#         opt.add(Implies(Not(skipple_truck[i]),skipple[i] == 0))

#     # Extra constraint for part (b)
#     if extra_constraint:
#         for i in range(N):opt.add(Implies(crottle[i] > 0,dupple[i] >= 2))

#     # Task 1: finx the max number of dupples to be transported in 1 run
#     total_dupples = Sum(dupple)
#     opt.maximize(total_dupples)

#     if opt.check() == sat:
#         model = opt.model()

#         if extra_constraint:
#             print("PART (b)")
#         else:
#             print("PART (a)")

#         print("Maximum dupples:",model.eval(total_dupples))

#         print()

#         for i in range(N):
#             print(
#                 f"Truck {i + 1}: "
#                 f"nuzzles={model.eval(nuzzle[i])}, "
#                 f"prittles={model.eval(prittle[i])}, "
#                 f"skipples={model.eval(skipple[i])}, "
#                 f"crottles={model.eval(crottle[i])}, "
#                 f"dupples={model.eval(dupple[i])}"
#             )

#         print()

# Output
solve(False)   # Part (a)
solve(True)    # Part (b)


#from z3 import *

# Declare trucks

baseline_capacity_per_truck = 8000 # Kilograms
pcs_per_truck = 10

# trucks = [Int('t_%d' % (i+1)) for i in range(6)]
# trucks_with_skipples = [Bool('t_%d' % (i+1)) for i in range (6)]

# s = Solver()
# s.add(trucks_with_skipples[0] == True)  
# s.add(trucks_with_skipples[1] == True)
# for i in range(2, 6):
#     s.add(trucks_with_skipples[i] == False)  

# types_of_goods = ["nuzzles", "prittles", "skipples", "crottles", "dupples"]
# for type in types_of_goods:
#     exec(f"{type} = [Int('{type}') for i in range(6)]") # Number of each type of good in each truck