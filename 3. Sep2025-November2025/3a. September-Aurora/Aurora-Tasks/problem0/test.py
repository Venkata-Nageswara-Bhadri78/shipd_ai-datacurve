import unittest
import networkx as nx
import random
import time
import numpy as np
from typing import List, Dict, Any, Tuple
from solution import optimize_delivery_routes, IncrementalTSPSolver, GraphChangeTracker


class TestOptimizeDeliveryRoutes(unittest.TestCase):
    def setUp(self):
        random.seed(42)
        np.random.seed(42)

    def validate_output_format(self, result: Tuple[List[int], Dict[str, Any]]) -> None:
        self.assertIsInstance(result, tuple)
        self.assertEqual(len(result), 2)
        route, metrics = result
        self.assertIsInstance(route, list)
        for node in route:
            self.assertIsInstance(node, int)
        self.assertIsInstance(metrics, dict)
        required_keys = {"total_cost", "total_time", "is_valid"}
        self.assertEqual(set(metrics.keys()), required_keys)
        self.assertIsInstance(metrics["total_cost"], float)
        self.assertIsInstance(metrics["total_time"], float)
        self.assertIsInstance(metrics["is_valid"], bool)

    def test_exact_sample_input_from_prompt(self):
        """Test exact sample input from prompt."""
        G = nx.Graph()
        edges = [
            (0, 1, {"cost": 10, "time": 5}),
            (1, 2, {"cost": 15, "time": 7}),
            (2, 0, {"cost": 20, "time": 10}),
            (0, 3, {"cost": 5, "time": 2}),
            (3, 2, {"cost": 8, "time": 4}),
            (1, 3, {"cost": 12, "time": 6}),
        ]
        G.add_edges_from(edges)
        result = optimize_delivery_routes(G, 0)
        route, metrics = result
        self.validate_output_format(result)
        self.assertTrue(metrics["is_valid"])

    def test_all_error_conditions_comprehensive(self):
        """Test all error conditions comprehensively."""
        # Invalid graph type
        with self.assertRaises(ValueError) as cm:
            optimize_delivery_routes("not_a_graph", 0)
        self.assertIn("NetworkX Graph", str(cm.exception))
        
        # Disconnected graph (more than 2 nodes)
        graph = nx.Graph()
        graph.add_edge(0, 1, cost=1, time=1)
        graph.add_edge(2, 3, cost=1, time=1)
        with self.assertRaises(ValueError) as cm:
            optimize_delivery_routes(graph, 0)
        self.assertIn("not fully connected", str(cm.exception))
        
        # Invalid start node
        graph = nx.Graph()
        graph.add_edge(0, 1, cost=1, time=1)
        with self.assertRaises(ValueError) as cm:
            optimize_delivery_routes(graph, 999)
        self.assertIn("Start node does not exist", str(cm.exception))
        
        # Negative cost
        graph = nx.Graph()
        graph.add_edge(0, 1, cost=-5, time=3)
        with self.assertRaises(ValueError) as cm:
            optimize_delivery_routes(graph, 0)
        self.assertIn("Negative edge weight", str(cm.exception))
        
        # Negative time  
        graph = nx.Graph()
        graph.add_edge(0, 1, cost=5, time=-3)
        with self.assertRaises(ValueError) as cm:
            optimize_delivery_routes(graph, 0)
        self.assertIn("Negative edge weight", str(cm.exception))
        
        # Negative weight
        graph = nx.Graph()
        graph.add_edge(0, 1, weight=-5)
        with self.assertRaises(ValueError) as cm:
            optimize_delivery_routes(graph, 0)
        self.assertIn("Negative edge weight", str(cm.exception))

    def test_all_edge_cases_complete(self):
        """Test all edge cases with complete coverage."""
        # Empty graph
        result = optimize_delivery_routes(nx.Graph(), 0)
        self.assertEqual(result[0], [])
        self.assertFalse(result[1]["is_valid"])
        
        # Single node
        graph = nx.Graph()
        graph.add_node(5)
        result = optimize_delivery_routes(graph, 5)
        self.assertEqual(result[0], [5])
        self.assertTrue(result[1]["is_valid"])
        
        # Two connected nodes
        graph = nx.Graph()
        graph.add_edge(1, 2, cost=10.5, time=5.2)
        result = optimize_delivery_routes(graph, 1)
        self.assertEqual(len(result[0]), 3)
        self.assertEqual(result[1]["total_cost"], 21.0)
        self.assertTrue(result[1]["is_valid"])
        
        # Two disconnected nodes - should not raise error, return invalid
        graph = nx.Graph()
        graph.add_node(1)
        graph.add_node(2)
        result = optimize_delivery_routes(graph, 1)
        self.assertEqual(result[0], [1])
        self.assertFalse(result[1]["is_valid"])

    def test_graph_change_tracker_complete_coverage(self):
        """Test graph change tracker complete coverage."""
        graph = nx.Graph()
        graph.add_edge(0, 1, cost=1, time=1)
        graph.add_edge(1, 2, cost=2, time=2)
        
        tracker = GraphChangeTracker(graph)
        self.assertIsNotNone(tracker.original_graph)
        self.assertEqual(len(tracker.edge_changes), 0)
        
        # Test edge change tracking
        tracker.track_edge_change(0, 1, 1.0, 1.0, 2.0, 2.0)
        self.assertEqual(len(tracker.edge_changes), 1)
        self.assertIn((0, 1), tracker.edge_changes)
        
        # Test node failure tracking  
        tracker.track_node_failure(1)
        self.assertIn(1, tracker.node_failures)
        
        # Test get affected edges with no solution
        affected = tracker.get_affected_edges()
        self.assertIn((0, 1), affected)
        
        # Test get affected edges with solution
        tracker.last_solution = [0, 1, 2]
        affected = tracker.get_affected_edges()
        self.assertTrue(len(affected) > 0)
        
        # Test clear changes
        tracker.clear_changes()
        self.assertEqual(len(tracker.edge_changes), 0)
        self.assertEqual(len(tracker.node_failures), 0)

    def test_distance_matrix_creation_all_branches(self):
        """Test distance matrix creation with all branch scenarios."""
        # Test with valid graph
        graph = nx.Graph()
        graph.add_edge(0, 1, cost=5, time=3)
        solver = IncrementalTSPSolver(graph, 0)
        cost_matrix, time_matrix = solver._create_distance_matrices()
        self.assertEqual(cost_matrix.shape, (2, 2))
        
        # Test with empty edges
        graph = nx.Graph()
        graph.add_node(0)
        graph.add_node(1)
        solver = IncrementalTSPSolver(graph, 0)
        cost_matrix, time_matrix = solver._create_distance_matrices()
        self.assertEqual(cost_matrix[0, 1], 1e6)
        
        # Test negative value handling
        graph = nx.Graph()
        graph.add_edge(0, 1, cost=-5, time=-3)
        solver = IncrementalTSPSolver(graph, 0)
        cost_matrix, time_matrix = solver._create_distance_matrices()
        self.assertEqual(cost_matrix[0, 1], 5)
        self.assertEqual(time_matrix[0, 1], 3)

    def test_distance_matrix_scipy_exception_and_fallback(self):
        """Test scipy exception handling and fallback."""
        graph = nx.Graph()
        graph.add_edge(0, 1, cost=5, time=3)
        solver = IncrementalTSPSolver(graph, 0)
        
        # Mock floyd_warshall to raise exception
        import scipy.sparse.csgraph as csgraph
        original_floyd = csgraph.floyd_warshall
        def mock_floyd(*args, **kwargs):
            raise Exception("Mock scipy exception")
        csgraph.floyd_warshall = mock_floyd
        
        try:
            cost_matrix, time_matrix = solver._create_distance_matrices()
            self.assertEqual(cost_matrix.shape, (2, 2))
            self.assertEqual(cost_matrix[0, 0], 0)
            self.assertEqual(cost_matrix[0, 1], 5)
        finally:
            csgraph.floyd_warshall = original_floyd
        
        # Test infinity handling in scipy success case
        def mock_floyd_with_inf(*args, **kwargs):
            matrix = np.full((2, 2), np.inf)
            matrix[0, 0] = 0
            matrix[1, 1] = 0
            matrix[0, 1] = 5
            matrix[1, 0] = 5
            return matrix
        
        csgraph.floyd_warshall = mock_floyd_with_inf
        try:
            cost_matrix, time_matrix = solver._create_distance_matrices()
            self.assertTrue(np.all(cost_matrix[cost_matrix != 0] >= 5))
        finally:
            csgraph.floyd_warshall = original_floyd

    def test_route_metrics_all_cases(self):
        """Test route metrics calculation all cases."""
        graph = nx.Graph()
        graph.add_edge(0, 1, cost=5, time=3)
        graph.add_edge(1, 2, cost=4, time=2)
        graph.add_edge(2, 0, cost=6, time=4)
        solver = IncrementalTSPSolver(graph, 0)
        solver.cost_matrix, solver.time_matrix = solver._create_distance_matrices()
        
        # Empty route
        cost, time_val = solver._calculate_route_metrics([])
        self.assertEqual(cost, 0.0)
        self.assertEqual(time_val, 0.0)
        
        # Single node
        cost, time_val = solver._calculate_route_metrics([0])
        self.assertEqual(cost, 0.0)
        
        # Complete cycle (ends with start)
        cost, time_val = solver._calculate_route_metrics([0, 1, 2, 0])
        self.assertEqual(cost, 15.0)
        
        # Incomplete cycle (auto-return to start)
        cost, time_val = solver._calculate_route_metrics([0, 1, 2])
        self.assertEqual(cost, 15.0)
        
        # Route length > 1 but last != first
        cost, time_val = solver._calculate_route_metrics([0, 1])
        expected_cost = solver.cost_matrix[0, 1] + solver.cost_matrix[1, 0]
        self.assertEqual(cost, expected_cost)

    def test_incremental_route_updates_comprehensive(self):
        """Test incremental route updates comprehensive."""
        graph = nx.Graph()
        graph.add_edge(0, 1, cost=5, time=3)
        graph.add_edge(1, 2, cost=4, time=2)
        graph.add_edge(2, 0, cost=6, time=4)
        solver = IncrementalTSPSolver(graph, 0)
        solver.cost_matrix, solver.time_matrix = solver._create_distance_matrices()
        
        # No current route
        solver.current_route = None
        route = solver._incremental_route_update([(0, 1)])
        self.assertEqual(route[0], 0)
        
        # No affected edges
        solver.current_route = [0, 1, 2]
        route = solver._incremental_route_update([])
        self.assertEqual(route[0], 0)
        
        # With affected edges in route
        solver.current_route = [0, 1, 2]
        solver.current_cost = 100.0
        route = solver._incremental_route_update([(0, 1)])
        self.assertIsInstance(route, list)
        
        # Edge not in current route
        route = solver._incremental_route_update([(3, 4)])
        self.assertIsInstance(route, list)

    def test_local_search_comprehensive_coverage(self):
        """Test local search comprehensive coverage."""
        graph = nx.Graph()
        for i in range(5):
            for j in range(i+1, 5):
                graph.add_edge(i, j, cost=random.randint(1, 10), time=random.randint(1, 10))
        solver = IncrementalTSPSolver(graph, 0)
        solver.cost_matrix, solver.time_matrix = solver._create_distance_matrices()
        
        # Adjacent nodes (difference = 1)
        route = [0, 1, 2, 3, 4]
        variants = solver._local_search_around_edge(route, 1, 2)
        self.assertIsInstance(variants, list)
        
        # Wraparound case (first and last positions)
        variants = solver._local_search_around_edge(route, 0, 4)
        self.assertIsInstance(variants, list)
        
        # Nodes not in route
        variants = solver._local_search_around_edge([0, 2, 4], 1, 3)
        self.assertEqual(len(variants), 0)
        
        # ValueError case (node not found)
        route_with_missing = [0, 2, 4]
        variants = solver._local_search_around_edge(route_with_missing, 1, 2)
        self.assertEqual(len(variants), 0)

    def test_nearest_neighbor_complete(self):
        """Test nearest neighbor complete."""
        graph = nx.Graph()
        graph.add_edge(0, 1, cost=5, time=3)
        graph.add_edge(1, 2, cost=4, time=2)
        graph.add_edge(2, 0, cost=6, time=4)
        solver = IncrementalTSPSolver(graph, 0)
        solver.cost_matrix, solver.time_matrix = solver._create_distance_matrices()
        
        route = solver._nearest_neighbor()
        self.assertEqual(len(route), 3)
        self.assertEqual(route[0], 0)
        self.assertIn(1, route)
        self.assertIn(2, route)
        
        # Test with larger graph to ensure all unvisited nodes processed
        graph = nx.complete_graph(6)
        for u, v in graph.edges():
            graph[u][v]['cost'] = random.randint(1, 10)
            graph[u][v]['time'] = random.randint(1, 10)
        solver = IncrementalTSPSolver(graph, 0)
        solver.cost_matrix, solver.time_matrix = solver._create_distance_matrices()
        route = solver._nearest_neighbor()
        self.assertEqual(len(route), 6)
        self.assertEqual(len(set(route)), 6)

    def test_two_opt_improvement_all_branches(self):
        """Test two opt improvement all branches."""
        # Small route (< 4 nodes) - should return unchanged
        graph = nx.Graph()
        graph.add_edge(0, 1, cost=5, time=3)
        solver = IncrementalTSPSolver(graph, 0)
        solver.cost_matrix, solver.time_matrix = solver._create_distance_matrices()
        route = [0, 1]
        improved = solver._two_opt_improvement(route)
        self.assertEqual(improved, route)
        
        # Larger route with improvement opportunities
        graph = nx.complete_graph(6)
        for u, v in graph.edges():
            graph[u][v]['cost'] = random.randint(1, 10)
            graph[u][v]['time'] = random.randint(1, 10)
        solver = IncrementalTSPSolver(graph, 0)
        solver.cost_matrix, solver.time_matrix = solver._create_distance_matrices()
        
        # Deliberately bad route to trigger improvements
        route = [0, 5, 1, 4, 2, 3]
        improved = solver._two_opt_improvement(route)
        self.assertEqual(len(improved), 6)
        
        # Test max iterations reached
        original_route = list(range(6))
        improved = solver._two_opt_improvement(original_route)
        self.assertIsInstance(improved, list)
        
        # Test j - i == 1 skip condition
        route = [0, 1, 2, 3]
        improved = solver._two_opt_improvement(route)
        self.assertIsInstance(improved, list)

    def test_scipy_optimization_all_branches(self):
        """Test scipy optimization with all branch conditions."""
        graph = nx.complete_graph(5)
        for u, v in graph.edges():
            graph[u][v]['cost'] = random.randint(1, 10)
            graph[u][v]['time'] = random.randint(1, 10)
        solver = IncrementalTSPSolver(graph, 0)
        solver.cost_matrix, solver.time_matrix = solver._create_distance_matrices()
        
        # Small route (< 4) returns unchanged
        route = [0, 1, 2]
        result = solver._scipy_optimization(route)
        self.assertEqual(result, route)
        
        # Exception in minimize - should return original route
        route = list(range(5))
        import scipy.optimize as opt
        original_minimize = opt.minimize
        
        def mock_exception(*args, **kwargs):
            raise Exception("Mock exception")
        
        opt.minimize = mock_exception
        try:
            result = solver._scipy_optimization(route)
            self.assertEqual(result, route)  # Should return original route on exception
        finally:
            opt.minimize = original_minimize
        
        # Test objective function exception handling
        original_calculate = solver._calculate_route_metrics
        def mock_calculate_exception(route):
            raise Exception("Calculation exception")
        
        solver._calculate_route_metrics = mock_calculate_exception
        try:
            result = solver._scipy_optimization(route)
            self.assertEqual(result, route)  # Should return original on objective exception
        finally:
            solver._calculate_route_metrics = original_calculate

    def test_dynamic_changes_all_scenarios(self):
        """Test dynamic changes all scenarios."""
        graph = nx.complete_graph(4)
        for u, v in graph.edges():
            graph[u][v]['cost'] = random.randint(1, 10)
            graph[u][v]['time'] = random.randint(1, 10)
        solver = IncrementalTSPSolver(graph, 0)
        
        original_random = random.random
        original_choice = random.choice
        
        # No change (probability > 0.1)
        random.random = lambda: 0.5
        solver._simulate_dynamic_changes()
        
        # Trigger change, then node failure (prob < 0.5)
        call_count = [0]
        def mock_random_node_failure():
            call_count[0] += 1
            return 0.05 if call_count[0] == 1 else 0.2
        random.random = mock_random_node_failure
        random.choice = lambda x: x[0] if x else None
        solver._simulate_dynamic_changes()
        
        # Trigger change, then edge change (prob >= 0.5)
        call_count = [0]
        def mock_random_edge_change():
            call_count[0] += 1
            return 0.05 if call_count[0] == 1 else 0.7
        random.random = mock_random_edge_change
        edges_list = list(graph.edges())
        random.choice = lambda x: edges_list[0] if edges_list else (0, 1)
        solver._simulate_dynamic_changes()
        
        # Restore
        random.random = original_random
        random.choice = original_choice

    def test_solve_method_complete_coverage(self):
        """Test solve method complete coverage."""
        # Test n <= 10 (triggers two_opt)
        graph = nx.complete_graph(8)
        for u, v in graph.edges():
            graph[u][v]['cost'] = random.randint(1, 10)
            graph[u][v]['time'] = random.randint(1, 10)
        solver = IncrementalTSPSolver(graph, 0, time_limit=2.0)
        result = solver.solve()
        self.assertIsNotNone(solver.cost_matrix)
        self.assertIsInstance(result[0], list)
        
        # Test n <= 8 and sufficient time (triggers scipy)
        import time as time_module
        original_time = time_module.time
        call_count = [0]
        def mock_time():
            call_count[0] += 1
            return 0.0 if call_count[0] <= 2 else 0.1
        time_module.time = mock_time
        
        try:
            solver = IncrementalTSPSolver(graph, 0, time_limit=2.0)
            result = solver.solve()
            self.assertIsInstance(result[0], list)
        finally:
            time_module.time = original_time
        
        # Test n > 10 (skips two_opt)
        graph = nx.complete_graph(12)
        for u, v in graph.edges():
            graph[u][v]['cost'] = random.randint(1, 10)
            graph[u][v]['time'] = random.randint(1, 10)
        solver = IncrementalTSPSolver(graph, 0)
        result = solver.solve()
        self.assertIsInstance(result[0], list)
        
        # Test with existing matrices and affected edges
        graph = nx.complete_graph(5)
        for u, v in graph.edges():
            graph[u][v]['cost'] = random.randint(1, 10)
            graph[u][v]['time'] = random.randint(1, 10)
        solver = IncrementalTSPSolver(graph, 0)
        solver.cost_matrix, solver.time_matrix = solver._create_distance_matrices()
        solver.change_tracker.track_edge_change(0, 1, 5.0, 3.0, 10.0, 6.0)
        result = solver.solve()
        self.assertIsInstance(result[0], list)

    def test_solve_route_formatting_all_cases(self):
        """Test solve route formatting comprehensive cases."""
        graph = nx.Graph()
        graph.add_edge(0, 1, cost=5, time=3)
        graph.add_edge(1, 2, cost=4, time=2)
        graph.add_edge(2, 0, cost=6, time=4)
        solver = IncrementalTSPSolver(graph, 0)
        
        # Mock to force wrong start route
        original_nearest = solver._nearest_neighbor
        def mock_nearest():
            return [1, 2, 0]  # Wrong start
        solver._nearest_neighbor = mock_nearest
        
        try:
            result = solver.solve()
            route, metrics = result
            # Should still be invalid due to validation logic
            self.assertFalse(metrics["is_valid"])
        finally:
            solver._nearest_neighbor = original_nearest

    def test_solve_exception_handling_complete(self):
        """Test solve exception handling complete."""
        graph = nx.Graph()
        graph.add_edge(0, 1, cost=5, time=3)
        solver = IncrementalTSPSolver(graph, 0)
        
        # Exception in main solve flow
        original_create = solver._create_distance_matrices
        def mock_exception():
            raise Exception("Mock exception")
        solver._create_distance_matrices = mock_exception
        
        try:
            result = solver.solve()
            self.assertEqual(result[0], [0])
            self.assertFalse(result[1]["is_valid"])
        finally:
            solver._create_distance_matrices = original_create

    def test_comprehensive_attribute_combinations(self):
        """Test comprehensive attribute combinations."""
        # All possible attribute combinations
        test_cases = [
            {"cost": 5},
            {"time": 3}, 
            {"weight": 7},
            {"cost": 5, "time": 3},
            {"cost": 5, "weight": 7},
            {"time": 3, "weight": 7},
            {"cost": 5, "time": 3, "weight": 7},
            {}
        ]
        
        for i, attrs in enumerate(test_cases):
            graph = nx.Graph()
            graph.add_edge(0, 1, **attrs)
            graph.add_edge(1, 2, **attrs)
            graph.add_edge(2, 0, **attrs)
            result = optimize_delivery_routes(graph, 0)
            self.validate_output_format(result)

    def test_time_limit_control_coverage(self):
        """Test time limit control coverage."""
        graph = nx.complete_graph(8)
        for u, v in graph.edges():
            graph[u][v]['cost'] = random.randint(1, 10)
            graph[u][v]['time'] = random.randint(1, 10)
        
        # Test time limit preventing scipy optimization
        import time as time_module
        original_time = time_module.time
        call_count = [0]
        def mock_time_exceeded():
            call_count[0] += 1
            if call_count[0] <= 2:
                return 0.0
            else:
                return 10.0
        
        time_module.time = mock_time_exceeded
        try:
            solver = IncrementalTSPSolver(graph, 0, time_limit=1.0)
            result = solver.solve()
            self.assertIsInstance(result, tuple)
        finally:
            time_module.time = original_time

    def test_matrix_creation_edge_cases(self):
        """Test uncovered matrix creation scenarios."""
        graph = nx.Graph()
        graph.add_edge(0, 1, cost=5, time=3)
        solver = IncrementalTSPSolver(graph, 0)
        
        import scipy.sparse.csgraph as csgraph
        original_floyd = csgraph.floyd_warshall
        
        # Test the empty finite case - only diagonal elements are finite
        def mock_floyd_empty_finite(*args, **kwargs):
            matrix = np.full((2, 2), np.inf)
            matrix[0, 0] = 0
            matrix[1, 1] = 0
            return matrix
        
        csgraph.floyd_warshall = mock_floyd_empty_finite
        try:
            cost_matrix, time_matrix = solver._create_distance_matrices()
            # The finite_costs array should only contain diagonal 0s
            # So len(finite_costs) > 0 but max will be 0, so large_cost = max(0 * 100, 1e6) = 1e6
            self.assertEqual(cost_matrix[0, 1], 1e6)
            self.assertEqual(cost_matrix[1, 0], 1e6)
        finally:
            csgraph.floyd_warshall = original_floyd

    def test_matrix_infinity_and_finite_handling(self):
        """Test matrix infinity and finite value handling."""
        graph = nx.Graph()
        graph.add_edge(0, 1, cost=5, time=3)
        solver = IncrementalTSPSolver(graph, 0)
        
        import scipy.sparse.csgraph as csgraph
        original_floyd = csgraph.floyd_warshall
        
        # Test case where we have finite values > 0 to trigger max * 100 logic
        def mock_floyd_with_large_finite(*args, **kwargs):
            matrix = np.array([[0.0, 10.0], [10.0, 0.0]])
            # Add infinity that should be replaced
            matrix[0, 1] = np.inf  
            return matrix
        
        csgraph.floyd_warshall = mock_floyd_with_large_finite
        try:
            cost_matrix, time_matrix = solver._create_distance_matrices()
            # finite_costs should contain [0, 10], max = 10, large_cost = max(10*100, 1e6) = 1000
            # So inf should be replaced with 1000
            self.assertTrue(cost_matrix[0, 1] == 1000.0)
        finally:
            csgraph.floyd_warshall = original_floyd

    def test_two_opt_improvement_branches(self):
        """Test two-opt improvement with all branch conditions."""
        graph = nx.complete_graph(8)
        for u, v in graph.edges():
            graph[u][v]['cost'] = random.randint(1, 20)
            graph[u][v]['time'] = random.randint(1, 20)
        
        solver = IncrementalTSPSolver(graph, 0)
        solver.cost_matrix, solver.time_matrix = solver._create_distance_matrices()
        
        route = [0, 7, 1, 6, 2, 5, 3, 4]
        original_calculate = solver._calculate_route_metrics
        call_count = [0]
        def mock_calculate_with_improvement(route):
            call_count[0] += 1
            if call_count[0] == 1:
                return 1000.0, 500.0
            elif call_count[0] == 2:
                return 50.0, 25.0
            else:
                return original_calculate(route)
        
        solver._calculate_route_metrics = mock_calculate_with_improvement
        try:
            improved_route = solver._two_opt_improvement(route)
            self.assertIsInstance(improved_route, list)
            self.assertEqual(len(improved_route), 8)
        finally:
            solver._calculate_route_metrics = original_calculate

    def test_scipy_objective_function_coverage(self):
        """Test scipy optimization objective function edge cases."""
        graph = nx.complete_graph(6)
        for u, v in graph.edges():
            graph[u][v]['cost'] = random.randint(1, 10)
            graph[u][v]['time'] = random.randint(1, 10)
        
        solver = IncrementalTSPSolver(graph, 0)
        solver.cost_matrix = np.full((6, 6), np.nan)
        solver.time_matrix = np.full((6, 6), np.nan)
        
        route = list(range(6))
        result = solver._scipy_optimization(route)
        self.assertEqual(result, route)

    def test_missing_branch_coverage(self):
        """Test remaining uncovered branches in solve method."""
        graph = nx.Graph()
        graph.add_edge(0, 1, cost=5, time=3)
        graph.add_edge(1, 2, cost=4, time=2)
        graph.add_edge(2, 0, cost=6, time=4)
        
        tracker = GraphChangeTracker(graph)
        tracker.last_solution = [0, 1, 2, 0]
        tracker.track_node_failure(1)
        
        affected = tracker.get_affected_edges()
        found_affected = False
        for edge in affected:
            if 1 in edge:
                found_affected = True
                break
        self.assertTrue(found_affected)
        
        solver = IncrementalTSPSolver(graph, 0)
        solver.cost_matrix, solver.time_matrix = solver._create_distance_matrices()
        
        # Force invalid route by making route too short
        original_nearest = solver._nearest_neighbor
        def mock_short_route():
            return [0, 1]  # Too short
        solver._nearest_neighbor = mock_short_route
        
        try:
            result = solver.solve()
            route, metrics = result
            self.assertFalse(metrics["is_valid"])
        finally:
            solver._nearest_neighbor = original_nearest

    def test_route_formatting_edge_cases(self):
        """Test route formatting and validation edge cases."""
        graph = nx.Graph()
        graph.add_edge(0, 1, cost=5, time=3)
        graph.add_edge(1, 2, cost=4, time=2)
        graph.add_edge(2, 0, cost=6, time=4)
        solver = IncrementalTSPSolver(graph, 0)
        solver.cost_matrix, solver.time_matrix = solver._create_distance_matrices()
        
        # Force invalid by mocking to return wrong start
        original_nearest = solver._nearest_neighbor
        def mock_wrong_start():
            return [1, 0, 2]  # Wrong start
        solver._nearest_neighbor = mock_wrong_start
        
        try:
            result = solver.solve()
            self.assertFalse(result[1]["is_valid"])
        finally:
            solver._nearest_neighbor = original_nearest

    def test_comprehensive_coverage_final(self):
        """Final comprehensive test to catch any remaining uncovered branches."""
        
        # Test large graph with all optimization paths
        graph = nx.complete_graph(15)
        for u, v in graph.edges():
            graph[u][v]['cost'] = random.randint(1, 10)
            graph[u][v]['time'] = random.randint(1, 10)
        
        solver = IncrementalTSPSolver(graph, 0, time_limit=3.0)
        
        # Set up scenario with existing route and changes
        solver.current_route = list(range(15))
        solver.current_cost = 200.0
        solver.current_time = 150.0
        solver.cost_matrix, solver.time_matrix = solver._create_distance_matrices()
        
        # Add changes to track
        solver.change_tracker.track_edge_change(0, 1, 5.0, 3.0, 10.0, 6.0)
        solver.change_tracker.track_node_failure(14)
        solver.change_tracker.last_solution = list(range(15))
        
        result = solver.solve()
        
        # Verify all components worked
        self.assertIsInstance(result[0], list)
        self.assertIsInstance(result[1], dict)
        self.assertIn("total_cost", result[1])
        self.assertIn("total_time", result[1])
        self.assertIn("is_valid", result[1])
        
        # Force failure case by setting None matrices and route
        solver.best_route = None
        solver.cost_matrix = None
        solver.time_matrix = None
        
        # Mock _create_distance_matrices to raise exception
        original_create = solver._create_distance_matrices
        def mock_exception():
            raise Exception("Mock exception")
        solver._create_distance_matrices = mock_exception
        
        try:
            result = solver.solve()
            self.assertEqual(result[0], [0])
            self.assertFalse(result[1]["is_valid"])
        finally:
            solver._create_distance_matrices = original_create


def run_all_tests():
    suite = unittest.TestLoader().loadTestsFromTestCase(TestOptimizeDeliveryRoutes)   
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    total_tests = result.testsRun
    failures = len(result.failures)
    errors = len(result.errors)
    passed = total_tests - failures - errors
    
    print(f"\n{'='*60}")
    print("TEST EXECUTION SUMMARY")
    print(f"{'='*60}")
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {passed}")
    print(f"Failed: {failures}")
    print(f"Errors: {errors}")
    print(f"Success Rate: {(passed/total_tests*100):.1f}%")
    print(f"{'='*60}")
    
    return passed, failures + errors


if __name__ == "__main__":
    print("Running unit tests for optimize_delivery_routes function...")
    print("="*60)
    
    passed, failed = run_all_tests()
    print(f"\nFINAL RESULT: {passed} PASSED, {failed} FAILED")