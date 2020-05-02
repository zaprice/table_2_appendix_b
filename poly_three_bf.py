import math

# For mypy typing
from typing import Optional, Dict, List, Tuple
from typing_extensions import Final


def get_child(a: int, b: int, x: int) -> int:
    return a * x ** 2 + b * x


def get_all_children(i: int, child_deltas: List[int], length: int) -> List[int]:
    return [i + delta for delta in child_deltas if i + delta <= length]


def last_uncolored(coloring: Dict[int, Optional[int]]) -> int:
    return len(coloring) - list(coloring.values())[::-1].index(None)


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
        # print(coloring)
        raise Exception("valid coloring found")
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


def check_polyvdw_number(a: int, b: int, n_colors: int, number: int):
    length = number
    # Collection of colored integers
    integers: Dict[int, Optional[int]] = dict(
        zip(range(1, length + 1), [None] * length)
    )
    # WLOG start by coloring the first (last) numbers
    integers[length] = 1

    possible_colors: Final[List[int]] = [i for i in range(1, n_colors + 1)]

    # Largest x such that 1 + ax^2 + bx is colorable
    max_child_delta: Final[int] = int(
        (-b + math.sqrt(b ** 2 + 4 * a * length)) / (2 * a)
    )
    # All delta such that i + delta is (potentially) a child
    child_deltas: Final[List[int]] = [
        get_child(a, b, x) for x in range(1, max_child_delta + 1)
    ]

    child_dict: Final[Dict[int, List[int]]] = {
        i: get_all_children(i, child_deltas, length) for i in range(1, length + 1)
    }

    color_brute_force(integers, length - 1, possible_colors, child_dict)


table: List[Tuple[int, int, int]] = [
    (1, 0, 29),
    (1, 1, 73),
    (1, 2, 64),
    (1, 3, 37),
    (1, 4, 65),
    (1, 5, 55),
    # (2, 0, 57),
    # (2, 1, 76),
    # (2, 2, 145),
    # (2, 3, 95),
    # (2, 4, 127),
    # (3, 0, 85),
    # (3, 1, 65),
    # (3, 2, 123),
    # (3, 3, 217),
    # (3, 5, 109),
    # (4, 0, 113),
    # (4, 1, 156),
    # (4, 2, 151),
    # (4, 4, 289),
    # (5, 0, 141),
    # (5, 1, 253),
    # (5, 5, 361),
]


for (a, b, number) in table:
    check_polyvdw_number(a, b, 3, number)
    try:
        check_polyvdw_number(a, b, 3, number - 1)
    except Exception:
        print(f"coloring found: W({a}x^2+{b}x;3)>{number-1}")
