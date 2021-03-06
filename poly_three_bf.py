import math
from multiprocessing import Pool
import os

from numba import jit

# For mypy typing
from typing import List, Tuple
from typing_extensions import Final


# Exception thrown when a coloring is found
# So we don't confuse a valid coloring with a garden-varity exception
class ValidColoring(Exception):
    pass


@jit
def get_child(a: int, b: int, x: int) -> int:
    return a * x ** 2 + b * x


@jit
def get_all_children(i: int, child_deltas: List[int], length: int) -> List[int]:
    return [i + delta for delta in child_deltas if i + delta < length]


# Check constraints given that n was just colored
@jit
def check_constraints(
    coloring: List[int], x: int, child_lists: List[List[int]]
) -> bool:
    # We color from right-to-left, so we check if any ax^2+bx has the same color
    for i in child_lists[x]:
        if coloring[x] == coloring[i]:
            return False
    # Otherwise the coloring so far is fine
    # If we just colored 0, we're done and have found a valid coloring
    if x == 0:
        raise ValidColoring("valid coloring found")
    else:
        return True


@jit
def color_brute_force(
    coloring: List[int], i: int, n_colors: int, child_lists: List[List[int]],
):
    for color in range(n_colors):
        # Try coloring the current node
        coloring[i] = color
        # Check if that color violates any ax^2+bx constraints
        # If not, color the next i
        if check_constraints(coloring, i, child_lists):
            color_brute_force(coloring, i - 1, n_colors, child_lists)
        # else: if it violates, continue to the next color
    # If all colors are tried and none works, backtrack!
    coloring[i] = -1
    return


@jit
def check_polyvdw_number(a: int, b: int, n_colors: int, length: int):
    # Collection of colored integers
    integers: List[int] = [-1] * length

    # Largest x such that 0 + ax^2 + bx is colorable
    max_child_delta: Final[int] = int(
        (-b + math.sqrt(b ** 2 + 4 * a * length)) / (2 * a)
    )
    # All deltas such that i + delta is (potentially) a child
    child_deltas: Final[List[int]] = [
        get_child(a, b, x) for x in range(1, max_child_delta + 1)
    ]
    child_lists: Final[List[List[int]]] = [
        get_all_children(i, child_deltas, length) for i in range(length)
    ]

    # WLOG start by coloring the first (last) number
    integers[length - 1] = 0
    # Look for a valid coloring, starting at the next number
    color_brute_force(integers, length - 2, n_colors, child_lists)
    # If this completes without throwing an exception,
    # we have shown that there are no valid colorings of [length]


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
    check_polyvdw_number(a, b, 3, number)
    le = f"no valid colorings: W({a}x^2+{b}x;3)<={number}"
    with open(os.path.expanduser(f"~/W({a}x^2+{b}x;3)<={number}.txt"), "w") as f:
        f.write(le)
    # Also check that number-1 has a coloring
    try:
        check_polyvdw_number(a, b, 3, number - 1)
    except ValidColoring:
        gt = f"coloring found: W({a}x^2+{b}x;3)>{number-1}"
        with open(os.path.expanduser(f"~/W({a}x^2+{b}x;3)>{number-1}.txt"), "w") as f:
            f.write(gt)

    print(f"FINISHED {a}, {b}")
    return (le, gt)


# Check table entries in parallel
multi = True
if __name__ == "__main__":
    if multi:
        with Pool(8) as p:
            checked = p.map(check_number, table)
    else:
        checked = [check_number(t) for t in table]
    for (le, gt) in checked:
        print(le)
        print(gt)
