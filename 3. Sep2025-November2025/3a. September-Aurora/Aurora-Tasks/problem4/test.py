import unittest
import networkx as nx
from solution import optimize_delivery_routes

class TestOptimizeDeliveryRoutes(unittest.TestCase):
    def setUp(self):
        self.graph = nx.Graph()
        edges = [
            (0, 1, {"cost": 10, "time": 5}),
            (1, 2, {"cost": 15, "time": 7}),
            (2, 0, {"cost": 20, "time": 10}),
            (0, 3, {"cost": 5, "time": 2}),
            (3, 2, {"cost": 8, "time": 4}),
            (1, 3, {"cost": 12, "time": 6}),
        ]
        self.graph.add_edges_from(edges)

    def test_valid_route(self):
        route, result = optimize_delivery_routes(self.graph, 0)
        self.assertTrue(result["is_valid"])
        self.assertEqual(route[0], 0)
        self.assertEqual(route[-1], 0)
        self.assertAlmostEqual(result["total_cost"], 38.0, places=1)
        self.assertAlmostEqual(result["total_time"], 18.0, places=1)
        self.assertEqual(len(route), len(set(route)) + 1)
        self.assertSetEqual(set(route[:-1]), set(self.graph.nodes()))

    def test_invalid_start_node(self):
        with self.assertRaises(ValueError):
            optimize_delivery_routes(self.graph, 100)

    def test_disconnected_graph(self):
        g = nx.Graph()
        g.add_nodes_from([0, 1, 2])
        g.add_edge(0, 1, cost=5, time=3)
        with self.assertRaises(ValueError):
            optimize_delivery_routes(g, 0)

    def test_negative_edge_weight(self):
        g = nx.Graph()
        g.add_edge(0, 1, cost=-1, time=4)
        with self.assertRaises(ValueError):
            optimize_delivery_routes(g, 0)

    def test_empty_graph(self):
        g = nx.Graph()
        route, result = optimize_delivery_routes(g, 0)
        self.assertFalse(result["is_valid"])
        self.assertEqual(len(route), 0)

    def test_single_node_graph(self):
        g = nx.Graph()
        g.add_node(0)
        route, result = optimize_delivery_routes(g, 0)
        self.assertTrue(result["is_valid"])
        self.assertEqual(route, [0])

if __name__ == "__main__":
    unittest.main()
