from z3 import Solver, Int, Bool, Or, And, Implies, Abs, If, sat, is_true

def solve_pcb_layout_z3():
    s = Solver()

    pcb_dims = {
        1: (20, 20),
        2: (22, 27)
    }

    chips = {
        1:  {"w": 5, "h": 6,  "warm": True},
        2:  {"w": 5, "h": 6,  "warm": True},
        3:  {"w": 4, "h": 6,  "warm": False},
        4:  {"w": 4, "h": 10, "warm": False},
        5:  {"w": 5, "h": 7,  "warm": False},
        6:  {"w": 3, "h": 7,  "warm": True},
        7:  {"w": 7, "h": 7,  "warm": False},
        8:  {"w": 6, "h": 10, "warm": False},
        9:  {"w": 6, "h": 12, "warm": False},
        10: {"w": 4, "h": 10, "warm": False},
        11: {"w": 6, "h": 9,  "warm": False},
        12: {"w": 5, "h": 11, "warm": False},
        13: {"w": 6, "h": 10, "warm": False},
        14: {"w": 5, "h": 10, "warm": False},
    }

    fixed_positions = [
        {"pcb": 1, "x1": 0,  "y1": 0,  "x2": 12, "y2": 8},
        {"pcb": 2, "x1": 0,  "y1": 0,  "x2": 14, "y2": 12},
        {"pcb": 2, "x1": 15, "y1": 22, "x2": 22, "y2": 27},
    ]

    x = {}        # Bottom-left X
    y = {}        # Bottom-left Y
    w_eff = {}    # Effective width
    h_eff = {}    # Effective height
    rot = {}      # Rotation boolean (True = 90 deg)
    pcb = {}      # PCB ID (1 or 2)
    x_center = {} # Doubled center X (2 * xc)
    y_center = {} # Doubled center Y (2 * yc)

    for i, chip in chips.items():
        x[i] = Int(f"x_{i}")
        y[i] = Int(f"y_{i}")
        w_eff[i] = Int(f"w_eff_{i}")
        h_eff[i] = Int(f"h_eff_{i}")
        rot[i] = Bool(f"rot_{i}")
        pcb[i] = Int(f"pcb_{i}")
        x_center[i] = Int(f"xc_{i}")
        y_center[i] = Int(f"yc_{i}")

        # PCB Selection constraint
        s.add(Or(pcb[i] == 1, pcb[i] == 2))

        # Bottom-left non-negative
        s.add(x[i] >= 0, y[i] >= 0)

        # Effective Dimensions based on rotation
        s.add(Implies(rot[i], And(w_eff[i] == chip["h"], h_eff[i] == chip["w"])))
        s.add(Implies(rot[i] == False, And(w_eff[i] == chip["w"], h_eff[i] == chip["h"])))

        # PCB Boundary Constraints
        s.add(Implies(pcb[i] == 1, And(x[i] + w_eff[i] <= pcb_dims[1][0], y[i] + h_eff[i] <= pcb_dims[1][1])))
        s.add(Implies(pcb[i] == 2, And(x[i] + w_eff[i] <= pcb_dims[2][0], y[i] + h_eff[i] <= pcb_dims[2][1])))

        # Doubled Center Coordinates (avoids float arithmetic)
        s.add(x_center[i] == 2 * x[i] + w_eff[i])
        s.add(y_center[i] == 2 * y[i] + h_eff[i])

    # ------------------------------------------------------------------
    # 3. Non-Overlapping Constraints
    # ------------------------------------------------------------------
    chip_ids = list(chips.keys())

    # Between dynamic chips
    for i in range(len(chip_ids)):
        for j in range(i + 1, len(chip_ids)):
            c1, c2 = chip_ids[i], chip_ids[j]

            # If placed on same PCB, at least one boundary separation must hold
            no_overlap = Or(
                x[c1] + w_eff[c1] <= x[c2],  # c1 left of c2
                x[c2] + w_eff[c2] <= x[c1],  # c2 left of c1
                y[c1] + h_eff[c1] <= y[c2],  # c1 below c2
                y[c2] + h_eff[c2] <= y[c1]   # c2 below c1
            )
            s.add(Implies(pcb[c1] == pcb[c2], no_overlap))

    # Between dynamic chips and pre-placed fixed chips
    for i, chip in chips.items():
        for fc in fixed_positions:
            no_fixed_overlap = Or(
                x[i] + w_eff[i] <= fc["x1"],
                fc["x2"] <= x[i],
                y[i] + h_eff[i] <= fc["y1"],
                fc["y2"] <= y[i]
            )
            s.add(Implies(pcb[i] == fc["pcb"], no_fixed_overlap))

    # ------------------------------------------------------------------
    # 4. Thermal Constraints (20 units in X or Y)
    # ------------------------------------------------------------------
    # Doubled distance threshold = 2 * 20 = 40
    THERMAL_DIST_DOUBLED = 40
    warm_chip_ids = [i for i, c in chips.items() if c["warm"]]

    for i in range(len(warm_chip_ids)):
        for j in range(i + 1, len(warm_chip_ids)):
            c1, c2 = warm_chip_ids[i], warm_chip_ids[j]

            thermal_sep = Or(
                Abs(x_center[c1] - x_center[c2]) >= THERMAL_DIST_DOUBLED,
                Abs(y_center[c1] - y_center[c2]) >= THERMAL_DIST_DOUBLED
            )
            # Must satisfy thermal separation if placed on the same PCB
            s.add(Implies(pcb[c1] == pcb[c2], thermal_sep))

    # ------------------------------------------------------------------
    # 5. Execute Solver & Print Solution
    # ------------------------------------------------------------------
    if s.check() == sat:
        m = s.model()
        print("=== Z3 LAYOUT SOLUTION FOUND ===\n")

        for board_id in [1, 2]:
            print(f"--- PCB {board_id} ({pcb_dims[board_id][0]}x{pcb_dims[board_id][1]}) ---")

            # Print fixed pre-placed chips
            for fc in fixed_positions:
                if fc["pcb"] == board_id:
                    print(f"  [Fixed Chip] Box: [{fc['x1']}..{fc['x2']}, {fc['y1']}..{fc['y2']}] "
                          f"| Size: {fc['x2']-fc['x1']}x{fc['y2']-fc['y1']}")

            # Print solved dynamic chips
            for i in chip_ids:
                if m[pcb[i]].as_long() == board_id:
                    x_val = m[x[i]].as_long()
                    y_val = m[y[i]].as_long()
                    w_val = m[w_eff[i]].as_long()
                    h_val = m[h_eff[i]].as_long()
                    r_val = is_true(m[rot[i]]) if hasattr(m[rot[i]], 'decl') else False
                    
                    warm_str = " (WARM)" if chips[i]["warm"] else ""
                    rot_str = "Rotated 90 deg" if r_val else "Standard"

                    print(f"  Chip {i:2d}{warm_str:7s} | Box: [{x_val:2d}..{x_val+w_val:2d}, {y_val:2d}..{y_val+h_val:2d}] "
                          f"| Size: {w_val:2d}x{h_val:2d} | Orientation: {rot_str}")
            print()
    else:
        print("No feasible solution found.")

if __name__ == "__main__":
    solve_pcb_layout_z3()