def gauge_field_invariance(
    lattice_charges: list[int], background_field: list[int], coupling_strength: int, max_iterations: int
) -> tuple[list[int], list[int], int]:
    # Input validation
    if not (4 <= len(lattice_charges) <= 16) or len(lattice_charges) % 2 != 0:
        raise ValueError("Lattice size must be even and between 4 and 16")
    if len(lattice_charges) != len(background_field):
        raise ValueError("Background field must match lattice size")
    if not (1 <= coupling_strength <= 10):
        raise ValueError("Coupling strength must be between 1 and 10")
    if not (10 <= max_iterations <= 100):
        raise ValueError("Max iterations must be between 10 and 100")

    # Validate charge values
    if not all(-5 <= charge <= 5 for charge in lattice_charges):
        raise ValueError("Charges must be between -5 and 5")

    n = len(lattice_charges)

    # Initialize link variables (one less than lattice points due to periodic boundary)
    link_variables = [0] * (n - 1)

    # Helper function to calculate local energy
    def calculate_local_energy(idx: int, charges: list[int], links: list[int]) -> int:
        local_energy = charges[idx] * background_field[idx]
        if idx > 0:
            local_energy += coupling_strength * (charges[idx] * charges[idx - 1]) * links[idx - 1]
        if idx < n - 1:
            local_energy += coupling_strength * (charges[idx] * charges[idx + 1]) * links[idx]
        return local_energy

    # Helper function to calculate total system energy
    def calculate_total_energy(charges: list[int], links: list[int]) -> int:
        total = sum(calculate_local_energy(i, charges, links) for i in range(n))
        gauge_energy = sum(links[i] * links[i] for i in range(n - 1))
        return total + gauge_energy * coupling_strength

    # Helper function to check gauge invariance
    def check_gauge_invariance(charges: list[int], links: list[int]) -> bool:
        charge_flow = sum(charges[i] * links[i] for i in range(n - 1))
        return charge_flow == 0

    # Initialize optimized charges as copy of input
    optimized_charges = lattice_charges.copy()

    for _ in range(max_iterations):
        # Update link variables
        for i in range(n - 1):
            best_link = 0
            min_energy = float("inf")
            for link_val in range(-5, 6):
                old_link = link_variables[i]
                link_variables[i] = link_val
                if check_gauge_invariance(optimized_charges, link_variables):
                    current_energy = calculate_total_energy(optimized_charges, link_variables)
                    if current_energy < min_energy:
                        min_energy = current_energy
                        best_link = link_val
                link_variables[i] = old_link
            link_variables[i] = best_link

        # Update charges
        for i in range(n):
            best_charge = optimized_charges[i]
            min_energy = calculate_total_energy(optimized_charges, link_variables)
            for charge in range(-5, 6):
                old_charge = optimized_charges[i]
                optimized_charges[i] = charge
                if check_gauge_invariance(optimized_charges, link_variables):
                    current_energy = calculate_total_energy(optimized_charges, link_variables)
                    if current_energy < min_energy:
                        min_energy = current_energy
                        best_charge = charge
                optimized_charges[i] = old_charge
            optimized_charges[i] = best_charge

    final_energy = calculate_total_energy(optimized_charges, link_variables)
    if not check_gauge_invariance(optimized_charges, link_variables):
        raise ValueError("Failed to find valid gauge-invariant configuration")

    return optimized_charges, link_variables, final_energy
