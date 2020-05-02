import math
from multiprocessing import Pool

# For mypy typing
from typing import Optional, Dict, List, Tuple
from typing_extensions import Final


# Exception thrown when a coloring is found
# So we don't confuse a valid coloring with a garden-varity exception
class ValidColoring(Exception):
    pass


def get_child(a: int, b: int, x: int) -> int:
    return a * x ** 2 + b * x


def get_all_children(i: int, child_deltas: List[int], length: int) -> List[int]:
    return [i + delta for delta in child_deltas if i + delta <= length]


# Check constraints given that n was just colored
def check_constraints(
    coloring: Dict[int, Optional[int]], x: int, child_dict: Dict[int, List[int]]
) -> bool:
    # We color from right-to-left, so we check if any ax^2+bx has the same color
    for i in child_dict[x]:
        if coloring[x] == coloring[i]:
            return False
    # Otherwise the coloring so far is fine
    # If we just colored 1, we're done and have found a valid coloring
    if x == 1:
        raise ValidColoring("valid coloring found")
    else:
        return True


def color_brute_force(
    coloring: Dict[int, Optional[int]],
    i: int,
    possible_colors: List[int],
    child_dict: Dict[int, List[int]],
):
    for color in possible_colors:
        # Try coloring the current node
        coloring[i] = color
        # Check if that color violates any ax^2+bx constraints
        # If not, color the next i
        if check_constraints(coloring, i, child_dict):
            color_brute_force(coloring, i - 1, possible_colors, child_dict)
        # else: if it violates, continue to the next color
    # If all colors are tried and none works, backtrack!
    coloring[i] = None
    return


def check_polyvdw_number(a: int, b: int, n_colors: int, length: int) -> str:
    # Collection of colored integers
    integers: Dict[int, Optional[int]] = dict(
        zip(range(1, length + 1), [None] * length)
    )

    possible_colors: Final[List[int]] = [i for i in range(1, n_colors + 1)]

    # Largest x such that 1 + ax^2 + bx is colorable
    max_child_delta: Final[int] = int(
        (-b + math.sqrt(b ** 2 + 4 * a * (length - 1))) / (2 * a)
    )
    # All deltas such that i + delta is (potentially) a child
    child_deltas: Final[List[int]] = [
        get_child(a, b, x) for x in range(1, max_child_delta + 1)
    ]
    child_dict: Final[Dict[int, List[int]]] = {
        i: get_all_children(i, child_deltas, length) for i in range(1, length + 1)
    }

    # WLOG start by coloring the first (last) number
    integers[length] = 1
    # Look for a valid coloring, starting at the next number
    color_brute_force(integers, length - 1, possible_colors, child_dict)
    # If this completes without throwing an exception,
    # we have shown that there are no valid colorings of [length]
    return f"no valid colorings: W({a}x^2+{b}x;3)<={length}"


# Listed values from Appedix B, Table 2
table: List[Tuple[int, int, int]] = [
    (1, 0, 29),
    (1, 1, 73),
    (1, 2, 64),
    (1, 3, 37),
    (1, 4, 65),
    (1, 5, 55),
    (2, 0, 57),
    (2, 1, 76),
    (2, 2, 145),
    (2, 3, 95),
    (2, 4, 127),
    (3, 0, 85),
    (3, 1, 65),
    (3, 2, 123),
    (3, 3, 217),
    (3, 5, 109),
    (4, 0, 113),
    (4, 1, 156),
    (4, 2, 151),
    (4, 4, 289),
    (5, 0, 141),
    (5, 1, 253),
    (5, 5, 361),
]


def check_number(args: Tuple[int, int, int]) -> Tuple[str, str]:
    (a, b, number) = args
    print(f"starting {a}, {b}")
    # Verify value in table - no valid colorings for [number]
    le = check_polyvdw_number(a, b, 3, number)
    # Also check that number-1 has a coloring
    try:
        check_polyvdw_number(a, b, 3, number - 1)
    except ValidColoring:
        gt = f"coloring found: W({a}x^2+{b}x;3)>{number-1}"

    print(f"FINISHED {a}, {b}")
    return (le, gt)


# Check table entries in parallel
multi = True
if __name__ == "__main__":
    if multi:
        with Pool(7) as p:
            checked = p.map(check_number, table)
    else:
        checked = [check_number(t) for t in table]
    for (ge, lt) in checked:
        print(ge)
        print(lt)
