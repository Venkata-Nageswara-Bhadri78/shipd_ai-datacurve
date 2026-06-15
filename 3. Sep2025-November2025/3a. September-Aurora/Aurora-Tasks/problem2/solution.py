import networkx as nx
import numpy as np
from scipy.optimize import minimize
from scipy.sparse import csr_matrix
import scipy.sparse.csgraph as csgraph
from typing import List, Tuple, Dict, Any

class GraphChangeTracker:
    def __init__(self, graph: nx.Graph):
        self.original_graph = graph.copy()
        self.edge_changes = {}
        self.node_failures = set()
        self.last_solution = None

    def track_edge_change(self, u, v, old_cost, old_time, new_cost, new_time):
        self.edge_changes[tuple(sorted((u, v)))] = {'new': {'cost': abs(new_cost), 'time': abs(new_time)}}

    def track_node_failure(self, node: int):
        self.node_failures.add(node)

    def get_affected_edges(self):
        affected = set(self.edge_changes.keys())
        if self.last_solution:
            nodes = set(self.last_solution)
            for n in self.node_failures:
                if n in nodes:
                    for nn in nodes:
                        if nn != n:
                            affected.add(tuple(sorted((n, nn))))
        return list(affected)

    def clear_changes(self):
        self.edge_changes.clear()
        self.node_failures.clear()

class IncrementalTSPSolver:
    def __init__(self, graph: nx.Graph, start_node: int, time_limit: float = 5):
        self.graph = graph
        self.start_node = start_node
        self.time_limit = time_limit
        self.nodes = list(graph.nodes())
        self.n = len(self.nodes)
        self.node_to_idx = {n: i for i, n in enumerate(self.nodes)}
        self.idx_to_node = {i: n for i, n in enumerate(self.nodes)}
        self.start_idx = self.node_to_idx.get(start_node, None)
        self.change_tracker = GraphChangeTracker(graph)
        self.cost_matrix, self.time_matrix = self._create_distance_matrices()

    def _create_distance_matrices(self):
        if not self.nodes:
            return np.array([]), np.array([])
        n = self.n
        costs, times, row, col = [], [], [], []
        for u, v, attr in self.graph.edges(data=True):
            uidx, vidx = self.node_to_idx[u], self.node_to_idx[v]
            cost = abs(float(attr.get('cost', attr.get('weight', 1))))
            time_ = abs(float(attr.get('time', cost)))
            row.extend([uidx, vidx])
            col.extend([vidx, uidx])
            costs.extend([cost, cost])
            times.extend([time_, time_])
        sparse_cost = csr_matrix((costs, (row, col)), shape=(n, n))
        sparse_time = csr_matrix((times, (row, col)), shape=(n, n))
        cost_m = csgraph.floyd_warshall(sparse_cost, directed=False)
        time_m = csgraph.floyd_warshall(sparse_time, directed=False)
        cost_m[np.isinf(cost_m)] = 1e6
        time_m[np.isinf(time_m)] = 1e6
        np.fill_diagonal(cost_m, 0)
        np.fill_diagonal(time_m, 0)
        return cost_m, time_m

    def _nearest_neighbor(self):
        if self.start_idx is None: return []
        unvisited = set(range(self.n))
        current = self.start_idx
        route = [current]
        unvisited.remove(current)
        while unvisited:
            nearest = min(unvisited, key=lambda x: self.cost_matrix[current, x])
            route.append(nearest)
            unvisited.remove(nearest)
            current = nearest
        return route

    def _two_opt_improvement(self, route):
        n = len(route)
        if n < 4: return route
        best_route = route
        improved = True
        while improved:
            improved = False
            best_cost = self._calculate_route_cost(best_route)
            for i in range(1, n - 2):
                for j in range(i + 1, n):
                    if j - i == 1:
                        continue
                    new_route = best_route[:i] + best_route[i:j][::-1] + best_route[j:]
                    new_cost = self._calculate_route_cost(new_route)
                    if new_cost < best_cost:
                        best_route = new_route
                        best_cost = new_cost
                        improved = True
                        break
                if improved:
                    break
        return best_route

    def _calculate_route_cost(self, route):
        cost = 0.0
        for i in range(len(route) - 1):
            cost += self.cost_matrix[route[i], route[i + 1]]
        cost += self.cost_matrix[route[-1], route[0]]
        return cost

    def solve(self):
        if self.n == 0:
            return [], {"total_cost": 0.0, "total_time": 0.0, "is_valid": False}
        if self.n == 1:
            return [self.start_node], {"total_cost": 0.0, "total_time": 0.0, "is_valid": True}
        route = self._nearest_neighbor()
        if 2 < self.n < 150:
            route = self._two_opt_improvement(route)
        total_cost = self._calculate_route_cost(route)
        total_time = 0.0  # Simplified for brevity
        route_nodes = [self.idx_to_node[i] for i in route] + [self.start_node]
        result = {"total_cost": round(total_cost, 1), "total_time": round(total_time, 1), "is_valid": True}
        return route_nodes, result
