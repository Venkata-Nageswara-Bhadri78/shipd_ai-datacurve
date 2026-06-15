```py
from typing import List, Tuple

def gauge_field_invariance(
    lattice_charges: List[int],
    background_field: List[int],
    coupling_strength: int,
    max_iterations: int
) -> Tuple[List[int], List[int], int]:
    """
    Optimizes gauge charges while ensuring gauge invariance in a discrete lattice system.

    Args:
        lattice_charges (List[int]): Initial gauge charges for each lattice site.
            Values must be in range [-5, 5].
            Total sites must be even and between 4-16.
        background_field (List[int]): Background field affecting each lattice point.
            Must match length of lattice_charges.
        coupling_strength (int): Interaction strength between sites (1-10).
        max_iterations (int): Maximum optimization iterations (10-100).

    Returns:
        Tuple[List[int], List[int], int]: Contains:
            - optimized_charges: The optimized gauge charges
            - link_variables: Link variables between neighboring sites
            - total_energy: System's total energy after optimization

    Raises:
        ValueError: If inputs invalid or gauge invariance not achieved
        RuntimeError: If coupling_strength or max_iterations negative

    Examples:
        >>> gauge_field_invariance([1, -1, 1, -1], [0, 0, 0, 0], 1, 10)
        ([1, -1, 1, -1], [0, 0, 0], 0)

        >>> gauge_field_invariance([2, -2, 2, -2], [1, -1, 1, -1], 2, 20)
        ([-5, 5, -5, 5], [0, 0, 0], -20)
    """
    pass
```
