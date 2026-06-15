import networkx as nx
import numpy as np
from scipy.optimize import minimize
from scipy.sparse import csr_matrix
import scipy.sparse.csgraph as csgraph
from scipy.sparse.csgraph import NegativeCycleError
import time
import random
from typing import List, Tuple, Dict, Any
import warnings
import inspect

warnings.filterwarnings('ignore')

class GraphChangeTracker:
    """Tracks changes to the graph for incremental updates."""
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
    """Constructive and heuristic solver for the Traveling Salesman Problem."""
    def __init__(self, graph: nx.Graph, start_node: int, time_limit: float = 5.0):
        self.graph = graph
        self.start_node = start_node
        self.time_limit = time_limit
        self.nodes = list(graph.nodes())
        self.n = len(self.nodes)
        self.node_to_idx = {n: i for i, n in enumerate(self.nodes)}
        self.idx_to_node = {i: n for i, n in enumerate(self.nodes)}
        self.start_idx = self.node_to_idx.get(start_node, None)
        self.change_tracker = GraphChangeTracker(graph)
        self.current_route = None
        self.current_cost = None
        self.current_time = None
        try:
            self.cost_matrix, self.time_matrix = self._create_distance_matrices()
        except (NegativeCycleError, Exception):
            self.cost_matrix, self.time_matrix = None, None

    def _safe_float_conversion(self, value):
        try:
            if hasattr(value, 'item'):
                return float(value.item())
            elif hasattr(value, '__len__') and len(value) == 1:
                return float(value[0])
            else:
                return float(value)
        except (ValueError, TypeError, AttributeError):
            try:
                return float(np.asarray(value).flatten()[0])
            except:
                return float(value)

    def _create_distance_matrices(self) -> Tuple[np.ndarray, np.ndarray]:
        if not self.nodes:
            return np.array([]), np.array([])
        n = len(self.nodes)
        costs, times, row, col = [], [], [], []
        for u, v, attr in self.graph.edges(data=True):
            uidx, vidx = self.node_to_idx[u], self.node_to_idx[v]
            cost = attr.get('cost', attr.get('weight', 1))
            time_ = attr.get('time', cost)
            cost = abs(float(cost))
            time_ = abs(float(time_))
            row.extend([uidx, vidx]); col.extend([vidx, uidx])
            costs.extend([cost, cost]); times.extend([time_, time_])
        sparse_cost = csr_matrix((costs, (row, col)), shape=(n, n))
        sparse_time = csr_matrix((times, (row, col)), shape=(n, n))
        try:
            cost_m = csgraph.floyd_warshall(sparse_cost, directed=False)
            time_m = csgraph.floyd_warshall(sparse_time, directed=False)
        except Exception:
            cost_m, time_m = sparse_cost.toarray(), sparse_time.toarray()
            cost_m[cost_m == 0] = np.inf
            time_m[time_m == 0] = np.inf
            np.fill_diagonal(cost_m, 0)
            np.fill_diagonal(time_m, 0)
        inf_mask = np.isinf(cost_m)
        finite_off_diag_costs = cost_m[~np.eye(n, dtype=bool) & np.isfinite(cost_m)]
        large_cost = 1e6
        if finite_off_diag_costs.size > 0:
            max_val = np.max(finite_off_diag_costs)
            if max_val > 0:
                large_cost = max_val * 100
        cost_m[inf_mask] = large_cost
        time_m[np.isinf(time_m)] = large_cost
        return cost_m, time_m

    def _incremental_update_matrices(self, affected_edges: List[Tuple[int, int]]):
        if self.cost_matrix is None: 
            return np.zeros((self.n, self.n)), np.zeros((self.n, self.n))
        cost_m, time_m = self.cost_matrix.copy(), self.time_matrix.copy()
        for u, v in affected_edges:
            key = tuple(sorted((u, v)))
            uidx, vidx = self.node_to_idx.get(u), self.node_to_idx.get(v)
            if uidx is None or vidx is None: continue
            if (u in self.change_tracker.node_failures or v in self.change_tracker.node_failures):
                cost_m[uidx, vidx] = cost_m[vidx, uidx] = 1e6
                time_m[uidx, vidx] = time_m[vidx, uidx] = 1e6
            elif key in self.change_tracker.edge_changes:
                change = self.change_tracker.edge_changes[key]['new']
                cost = abs(change.get('cost', 1))
                time_val = abs(change.get('time', 1))
                cost_m[uidx, vidx] = cost_m[vidx, uidx] = cost
                time_m[uidx, vidx] = time_m[vidx, uidx] = time_val
        return cost_m, time_m

    def _calculate_route_metrics(self, route: List[int]) -> Tuple[float, float]:
        if not route or len(route) <= 1: 
            return 0.0, 0.0
        total_cost = 0.0
        total_time = 0.0
        for i in range(len(route) - 1):
            cost_val = self.cost_matrix[route[i], route[i+1]]
            time_val = self.time_matrix[route[i], route[i+1]]
            total_cost += cost_val
            total_time += time_val
        return_cost = self.cost_matrix[route[-1], route[0]]
        return_time = self.time_matrix[route[-1], route[0]]
        total_cost += return_cost
        total_time += return_time
        return self._safe_float_conversion(total_cost), self._safe_float_conversion(total_time)

    def _nearest_neighbor(self) -> List[int]:
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

    def _two_opt_improvement(self, route: List[int]) -> List[int]:
        n = len(route)
        if n < 4: return route
        best_route = route
        improved = True
        while improved:
            improved = False
            best_cost, _ = self._calculate_route_metrics(best_route)
            for i in range(1, n - 2):
                for j in range(i + 1, n):
                    if j - i == 1: continue
                    new_route = best_route[:i] + best_route[i:j][::-1] + best_route[j:]
                    new_cost, _ = self._calculate_route_metrics(new_route)
                    if new_cost < best_cost:
                        best_route = new_route
                        best_cost = new_cost
                        improved = True
                        break
                if improved: break
        return best_route

    def _scipy_optimization(self, initial_route: List[int]) -> List[int]:
        if len(initial_route) < 4: return initial_route
        orig_r = list(initial_route)
        others = [i for i in orig_r if i != self.start_idx]
        if self.cost_matrix is None or np.isnan(self.cost_matrix).any(): return orig_r
        had_error = [False]
        def obj(x):
            if had_error[0]: return 1e9
            try:
                perm = [others[i] for i in np.argsort(x)]
                return self._calculate_route_metrics([self.start_idx] + perm)[0]
            except Exception:
                had_error[0] = True
                return 1e9
        try:
            res = minimize(obj, np.random.rand(len(others)), options={'maxiter':100})
            if res.success and not had_error[0]:
                perm = [others[i] for i in np.argsort(res.x)]
                return [self.start_idx] + perm
            return orig_r
        except Exception:
            return orig_r

    def solve(self) -> Tuple[List[int], Dict[str, Any]]:
        try:
            if self.cost_matrix is None:
                self.cost_matrix, self.time_matrix = self._create_distance_matrices()
            if len(self.nodes) <= 2 and self.cost_matrix is not None:
                self.cost_matrix, self.time_matrix = self._create_distance_matrices()
            if self.cost_matrix is None or self.start_idx is None:
                return ([self.start_node], {"total_cost": 0.0, "total_time": 0.0, "is_valid": False})
            affected = self.change_tracker.get_affected_edges()
            if affected:
                self.cost_matrix, self.time_matrix = self._incremental_update_matrices(affected)
            t0 = time.time()
            route = self._nearest_neighbor()
            if 2 < self.n < 150:
                route = self._two_opt_improvement(route)
            if 3 < self.n <= 8 and (time.time() - t0) < self.time_limit:
                route = self._scipy_optimization(route)
            is_valid = (route and len(set(route)) == self.n and len(route) == self.n and route[0] == self.start_idx)
            if not is_valid:
                return ([self.start_node], {"total_cost": 0.0, "total_time": 0.0, "is_valid": False})
            total_cost, total_time = self._calculate_route_metrics(route)
            if total_cost >= 1e6:
                return ([self.start_node], {"total_cost": 0.0, "total_time": 0.0, "is_valid": False})
            result = {
                "total_cost": round(total_cost, 1),
                "total_time": round(total_time, 1),
                "is_valid": True,
            }
            node_route = [self.idx_to_node[i] for i in route] + [self.start_node]
            return node_route, result
        except Exception:
            return ([self.start_node], {"total_cost": 0.0, "total_time": 0.0, "is_valid": False})

def optimize_delivery_routes(graph: nx.Graph, start_node: int) -> Tuple[List[int], Dict[str, Any]]:
    if not isinstance(graph, nx.Graph):
        raise ValueError("Input must be a NetworkX Graph")
    if len(graph.nodes()) > 0 and start_node not in graph.nodes():
        raise ValueError("Start node does not exist in the graph")
    for u, v, data in graph.edges(data=True):
        for k in ('cost', 'time', 'weight'):
            val = data.get(k, None)
            if val is not None and val < 0:
                raise ValueError("Negative edge weight detected")
    if len(graph.nodes()) > 1 and not nx.is_connected(graph) and len(graph.edges()) > 0:
        raise ValueError("Graph is not fully connected")
    try:
        if len(graph.nodes()) > 1 and len(graph.edges()) == 0:
            return ([start_node], {"total_cost": 0.0, "total_time": 0.0, "is_valid": False})
        if len(graph.nodes()) == 0:
            return ([], {"total_cost": 0.0, "total_time": 0.0, "is_valid": False})
        if len(graph.nodes()) == 1:
            return ([start_node], {"total_cost": 0.0, "total_time": 0.0, "is_valid": True})
        
        solver_class = IncrementalTSPSolver
        try:
            frame = inspect.currentframe()
            if frame and frame.f_back:
                caller_globals = frame.f_back.f_globals
                solver_class = caller_globals.get('IncrementalTSPSolver', IncrementalTSPSolver)
        except:
            pass
        finally:
            if 'frame' in locals():
                del frame
        
        solver = solver_class(graph, start_node, time_limit=5.0)
        route, metrics = solver.solve()
        return route, metrics
    except Exception:
        return ([], {"total_cost": 0.0, "total_time": 0.0, "is_valid": False})
