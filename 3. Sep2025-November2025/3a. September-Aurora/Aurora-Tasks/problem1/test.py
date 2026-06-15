import pytest
import os
import tempfile
import shutil
from typing import List

# Assume the solution is in a file named `solution.py`
# You will need to create a solution.py file with the target function.
from solution import generate_route_report

@pytest.fixture
def temp_dir():
    """Create a temporary directory for test CSV files and clean it up afterward."""
    directory = tempfile.mkdtemp()
    yield directory
    shutil.rmtree(directory)

def create_csv(directory: str, filename: str, data: List[str]) -> str:
    """Helper function to create a CSV file in the given directory."""
    path = os.path.join(directory, filename)
    with open(path, 'w', newline='') as f:
        f.write('\n'.join(data))
    return path

# --- Test Cases ---

def test_sample_case_truck_complete_tour(temp_dir):
    """Tests the exact sample case from the description with the corrected total_cost."""
    csv_data = [
        "A,B,10,5,highway,",
        "A,C,12,6,local,",
        "B,C,8,4,local,truck",
        "B,D,15,8,highway,",
        "C,D,9,5,local,"
    ]
    csv_path = create_csv(temp_dir, "network.csv", csv_data)
    report = generate_route_report(
        csv_path=csv_path,
        vehicle_type="truck",
        start_node="A"
    )
    
    # Path: A -> B(10) -> D(15) -> C(9*1.2=10.8) -> A(12*1.2=14.4)
    # Total Cost = 10 + 15 + 10.8 + 14.4 = 50.2
    # Total Time = 5 + 8 + 5 + 6 = 24.0
    expected = {
        "route": ["A", "B", "D", "C", "A"],
        "total_cost": 50.2,
        "total_time": 24.0,
        "is_complete_tour": True
    }
    assert report == expected

def test_van_route_all_nodes_visited_but_no_return_path(temp_dir):
    """
    Tests an incomplete tour where all nodes are visited, but a return path
    from the last node to the start does not exist.
    """
    csv_data = [
        "A,B,10,5,highway,",
        "A,C,12,6,local,",
        "B,C,8,4,local,truck",
        "B,D,15,8,highway,",
        "C,D,9,5,local,"
    ]
    csv_path = create_csv(temp_dir, "network_van.csv", csv_data)
    report = generate_route_report(
        csv_path=csv_path,
        vehicle_type="van",
        start_node="A"
    )
    
    # Path: A -> B(10) -> C(8) -> D(9)
    # All nodes visited, but no path from D back to A. Tour ends.
    # Total Cost = 10 + 8 + 9 = 27.0
    # Total Time = 5 + 4 + 5 = 14.0
    expected = {
        "route": ["A", "B", "C", "D"],
        "total_cost": 27.0,
        "total_time": 14.0,
        "is_complete_tour": False
    }
    assert report == expected

def test_incomplete_tour_stuck_midway_on_disconnected_graph(temp_dir):
    """
    Tests the critical case where the tour gets stuck and cannot visit all nodes.
    The route should end at the last visited node and not return to the start.
    """
    csv_data = [
        "A,B,10,5,highway,",  # Component 1
        "C,D,20,8,highway,"   # Component 2
    ]
    csv_path = create_csv(temp_dir, "disconnected.csv", csv_data)
    report = generate_route_report(
        csv_path=csv_path,
        vehicle_type="van",
        start_node="A"
    )

    # Path: A -> B(10). Stuck, cannot reach unvisited C or D. Tour ends.
    # The route does not return to the start.
    expected = {
        "route": ["A", "B"],
        "total_cost": 10.0,
        "total_time": 5.0,
        "is_complete_tour": False
    }
    assert report == expected

def test_cost_tie_breaking_by_node_id(temp_dir):
    """Tests that ties in effective cost are broken by the smaller node ID ('A' over 'B')."""
    csv_data = [
        "Start,A,10,5,highway,",
        "Start,B,10,5,highway,",
        "A,B,100,100,highway,"
    ]
    csv_path = create_csv(temp_dir, "tie_break.csv", csv_data)
    report = generate_route_report(
        csv_path=csv_path,
        vehicle_type="van",
        start_node="Start"
    )

    # Path: Start -> A(10, chosen over B) -> B(100) -> Start(10)
    # Total Cost = 10 + 100 + 10 = 120.0
    # Total Time = 5 + 100 + 5 = 110.0
    expected = {
        "route": ["Start", "A", "B", "Start"],
        "total_cost": 120.0,
        "total_time": 110.0,
        "is_complete_tour": True
    }
    assert report == expected

def test_isolated_start_node(temp_dir):
    """Tests the case where the starting node has no valid outbound edges."""
    csv_data = [
        "A,B,10,5,highway,truck",
        "A,C,12,6,local,truck",
        "D,E,20,10,highway,"
    ]
    csv_path = create_csv(temp_dir, "isolated.csv", csv_data)
    report = generate_route_report(
        csv_path=csv_path,
        vehicle_type="truck",
        start_node="A"
    )

    # All paths from A are restricted. Tour is stuck at the start.
    expected = {
        "route": ["A"],
        "total_cost": 0.0,
        "total_time": 0.0,
        "is_complete_tour": False
    }
    assert report == expected

def test_malformed_csv_raises_value_error(temp_dir):
    """Tests that a CSV with the wrong number of columns raises a ValueError."""
    csv_data = ["A,B,10,5"]  # Only 4 columns instead of 6
    csv_path = create_csv(temp_dir, "malformed.csv", csv_data)
    
    with pytest.raises(ValueError):
        generate_route_report(
            csv_path=csv_path,
            vehicle_type="van",
            start_node="A"
        )

def test_invalid_start_node_raises_value_error(temp_dir):
    """Tests that a start_node not in the graph raises a ValueError."""
    csv_data = ["A,B,10,5,highway,"]
    csv_path = create_csv(temp_dir, "valid.csv", csv_data)
    
    with pytest.raises(ValueError):
        generate_route_report(
            csv_path=csv_path,
            vehicle_type="van",
            start_node="Z"  # Node Z does not exist
        )

def test_empty_csv_file_raises_value_error(temp_dir):
    """Tests that an empty CSV file correctly raises a ValueError for a missing start node."""
    csv_path = create_csv(temp_dir, "empty.csv", [])

    with pytest.raises(ValueError):
        generate_route_report(
            csv_path=csv_path,
            vehicle_type="van",
            start_node="A"
        )
if __name__ == "__main__":
    # Add "test.py" to explicitly tell pytest to run tests in this file.
    exit_code = pytest.main(["-v", "-s", "test.py"])
    print(f"\nPytest finished with exit code: {exit_code}")