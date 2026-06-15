import csv
from typing import Dict, Any, List, Tuple


class RouteGraph:
    def __init__(self):
        self.graph = {}
        self.nodes = set()

    def add_edge(self, node1: str, node2: str, base_cost: float, base_time: float,
                 road_type: str, vehicle_restriction: str):
        if node1 not in self.graph:
            self.graph[node1] = []
        if node2 not in self.graph:
            self.graph[node2] = []
        self.graph[node1].append((node2, base_cost, base_time, road_type, vehicle_restriction))
        self.graph[node2].append((node1, base_cost, base_time, road_type, vehicle_restriction))


def parse_csv(csv_path: str, vehicle_type: str) -> RouteGraph:
    graph = RouteGraph()
    try:
        with open(csv_path, newline='') as f:
            reader = csv.reader(f)
            for idx, row in enumerate(reader):
                if len(row) != 6:
                    raise ValueError(f"Malformed CSV: row {idx+1} does not have 6 columns")
                node1, node2, base_cost_str, base_time_str, road_type, vehicle_restriction = row
                
                node1 = node1.strip()
                node2 = node2.strip()
                road_type = road_type.strip()
                vehicle_restriction = vehicle_restriction.strip()

                graph.nodes.update([node1, node2])

                try:
                    base_cost = float(base_cost_str)
                    base_time = float(base_time_str)
                except ValueError:
                    raise ValueError(f"Malformed CSV: row {idx+1} base_cost or base_time is not a number")
                if road_type not in ('highway', 'local'):
                    raise ValueError(f"Malformed CSV: row {idx+1} road_type must be 'highway' or 'local'")
                
                # Skip edge if vehicle_restriction matches vehicle_type
                if vehicle_restriction == vehicle_type:
                    continue

                graph.add_edge(node1, node2, base_cost, base_time, road_type, vehicle_restriction)
    except FileNotFoundError:
        raise ValueError(f"CSV file not found: {csv_path}")
    return graph


def effective_cost(base_cost: float, road_type: str, vehicle_type: str) -> float:
    if road_type == "local" and vehicle_type == "truck":
        return base_cost * 1.2
    return base_cost


def nearest_neighbor_tour(graph: RouteGraph, start_node: str, vehicle_type: str) -> Tuple[List[str], float, float, bool]:
    if start_node not in graph.nodes:
        raise ValueError("Invalid or missing start_node")

    visited = set()
    route = [start_node]
    total_cost = 0.0
    total_time = 0.0
    current_node = start_node
    visited.add(current_node)

    while len(visited) < len(graph.nodes):
        neighbors = []
        for neighbor, base_cost, base_time, road_type, vehicle_restriction in graph.graph.get(current_node, []):
            if neighbor in visited:
                continue
            cost = effective_cost(base_cost, road_type, vehicle_type)
            neighbors.append((neighbor, cost, base_time))
        if not neighbors:
            break
        neighbors.sort(key=lambda x: (x[1], x[0]))
        next_node, edge_cost, edge_time = neighbors[0]
        route.append(next_node)
        total_cost += edge_cost
        total_time += edge_time
        current_node = next_node
        visited.add(current_node)

    if len(visited) == len(graph.nodes):
        return_edge = None
        for neighbor, base_cost, base_time, road_type, vehicle_restriction in graph.graph.get(current_node, []):
            if neighbor == start_node:
                cost = effective_cost(base_cost, road_type, vehicle_type)
                return_edge = (cost, base_time)
                break

        if return_edge is not None:
            route.append(start_node)
            total_cost += return_edge[0]
            total_time += return_edge[1]

    is_complete = (len(visited) == len(graph.nodes)) and (route[-1] == start_node)
    return route, total_cost, total_time, is_complete


def generate_route_report(csv_path: str, vehicle_type: str, start_node: str) -> Dict[str, Any]:
    graph = parse_csv(csv_path, vehicle_type)
    if len(graph.nodes) == 0:
        raise ValueError("Invalid or missing start_node")
    route, total_cost, total_time, is_complete = nearest_neighbor_tour(graph, start_node, vehicle_type)
    return {
        "route": route,
        "total_cost": round(total_cost, 1),
        "total_time": round(total_time, 1),
        "is_complete_tour": is_complete
    }