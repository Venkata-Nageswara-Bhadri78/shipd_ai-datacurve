import pytest
from solution import gauge_field_invariance

def test_basic_gauge_field():
    assert gauge_field_invariance(
        lattice_charges=[1, -1, 1, -1],
        background_field=[0, 0, 0, 0],
        coupling_strength=1,
        max_iterations=10
    ) == ([1, -1, 1, -1], [0, 0, 0], 0)

def test_nonzero_background():
    assert gauge_field_invariance(
        lattice_charges=[2, -2, 2, -2],
        background_field=[1, -1, 1, -1],
        coupling_strength=2,
        max_iterations=20
    ) == ([-5, 5, -5, 5], [0, 0, 0], -20)

def test_strong_coupling():
    assert gauge_field_invariance(
        lattice_charges=[3, -3, 3, -3],
        background_field=[2, -2, 2, -2],
        coupling_strength=5,
        max_iterations=50
    )[::2] == ([-5, 5, -5, 5], -40)

def test_larger_lattice():
    assert gauge_field_invariance(
        lattice_charges=[1, -1, 1, -1, 2, -2, 2, -2],
        background_field=[1, 0, 0, -1, -1, 1, 2, -2],
        coupling_strength=7,
        max_iterations=50
    ) == ([-5, -1, 1, 5, 5, -5, -5, 5], [0, 0, 0, 0, 0, 0, 0], -40)

def test_invalid_max_iterations():
    with pytest.raises(ValueError):
        gauge_field_invariance(
            lattice_charges=[2, -1, 1, -2],
            background_field=[1, 1, -1, -1],
            coupling_strength=4,
            max_iterations=-40
        )

def test_empty_lattice():
    with pytest.raises(ValueError):
        gauge_field_invariance(
            lattice_charges=[],
            background_field=[],
            coupling_strength=5,
            max_iterations=10
        )
