from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List, Any, Tuple, Set, Optional
from collections import defaultdict, deque
from concurrent.futures import ThreadPoolExecutor, Future
import threading
import math
import time
import heapq
import asyncio

# ==================== Core Enums and Data Models ====================

class ResourceState(Enum):
    """Enum representing different states of hotel resources"""
    AVAILABLE = 1
    UNAVAILABLE = 2
    MAINTENANCE = 3
    PARTIAL = 4


@dataclass
class TimeSlot:
    """Represents a time-based availability slot for resources"""
    start_time: int
    end_time: int
    capacity: int
    used: int = 0
    state: ResourceState = ResourceState.AVAILABLE

    def available_capacity(self) -> int:
        """Calculate remaining capacity in this time slot"""
        if self.state == ResourceState.UNAVAILABLE or self.state == ResourceState.MAINTENANCE:
            return 0
        return max(0, self.capacity - self.used)

    def can_allocate(self, required_capacity: int = 1) -> bool:
        """Check if allocation is possible for required capacity"""
        if self.state == ResourceState.UNAVAILABLE or self.state == ResourceState.MAINTENANCE:
            return False
        return self.available_capacity() >= required_capacity

    def allocate(self, capacity: int = 1) -> bool:
        if self.can_allocate(capacity):
            self.used += capacity
            return True
        return False

    def release(self, capacity: int = 1):
        self.used = max(0, self.used - capacity)


@dataclass
class MultiLayerNode:
    """Represents a room/space node with multi-layer time-based availability"""
    node_id: int
    floor: int = 1
    location: Tuple[float, float] = (0.0, 0.0)
    room_type: str = "standard"
    amenities: Set[str] = field(default_factory=set)
    timeslots: Dict[int, TimeSlot] = field(default_factory=dict)  # layer -> timeslot
    lock: threading.Lock = field(default_factory=threading.Lock)

    def get_available_layers(self, required_capacity: int = 1) -> List[int]:
        """Get list of layers where node has available capacity"""
        layers = []
        for layer, slot in self.timeslots.items():
            if slot.can_allocate(required_capacity):
                layers.append(layer)
        return layers

    def allocate_resource(self, layer: int, capacity: int = 1) -> bool:
        """Allocate specified capacity on given layer"""
        with self.lock:
            slot = self.timeslots.get(layer)
            if not slot:
                return False
            return slot.allocate(capacity)

    def release_resource(self, layer: int, capacity: int = 1):
        """Release previously allocated capacity on given layer"""
        with self.lock:
            slot = self.timeslots.get(layer)
            if slot:
                slot.release(capacity)


@dataclass
class MultiLayerEdge:
    """Represents connection between nodes with capacity and cost metrics"""
    from_node: int
    to_node: int
    layer: int
    capacity: int = 1
    used: int = 0
    base_cost: float = 1.0
    corridor_type: str = "standard"

    def get_residual_capacity(self) -> int:
        """Calculate remaining flow capacity on this edge"""
        return max(0, self.capacity - self.used)

    def get_dynamic_cost(self, congestion_factor: float = 1.0) -> float:
        """Calculate dynamic cost based on current congestion"""
        # Simple congestion model: cost increases as usage approaches capacity
        if self.capacity <= 0:
            return float('inf')
        load_ratio = self.used / self.capacity
        # Non-linear penalty as it gets crowded
        penalty = (1.0 + 3.0 * (load_ratio ** 2)) * congestion_factor
        return self.base_cost * penalty


# ==================== Core Graph Structure ====================

class AdvancedMultiLayerGraph:
    """Multi-layer graph structure for hotel layout and time-based resource management"""

    def __init__(self, max_layers: int = 100):
        """Initialize multi-layer graph with specified maximum layers"""
        self.max_layers = max_layers
        self.layers: List[Tuple[int, int]] = []  # list of (start, end)
        self.nodes: Dict[int, MultiLayerNode] = {}
        self.edges: Dict[Tuple[int, int, int], MultiLayerEdge] = {}
        self.layer_adj: Dict[int, Dict[int, List[int]]] = defaultdict(lambda: defaultdict(list))
        self.available_nodes_cache: Dict[int, Set[int]] = {}
        self.cache_lock = threading.Lock()
        self.graph_lock = threading.RLock()

    def add_time_layer(self, start_time: int, end_time: int) -> int:
        """Add new time layer to graph structure"""
        with self.graph_lock:
            if len(self.layers) >= self.max_layers:
                raise ValueError("Max layers exceeded")
            layer_idx = len(self.layers)
            self.layers.append((start_time, end_time))
            # Initialize timeslots for existing nodes
            for node in self.nodes.values():
                if layer_idx not in node.timeslots:
                    node.timeslots[layer_idx] = TimeSlot(start_time, end_time, capacity=node.timeslots.get(0, TimeSlot(0,0,1)).capacity, state=ResourceState.AVAILABLE)
            self._invalidate_cache(layer_idx)
            return layer_idx

    def add_node_with_location(self, node_id: int, capacity: int,
                               location: Tuple[float, float], floor: int = 1,
                               room_type: str = "standard", amenities: Set[str] = None):
        """Add node with spatial location and metadata"""
        with self.graph_lock:
            if amenities is None:
                amenities = set()
            if node_id not in self.nodes:
                node = MultiLayerNode(node_id=node_id, floor=floor, location=location,
                                      room_type=room_type, amenities=amenities)
                # Initialize timeslots for all existing layers
                for layer_idx, (st, et) in enumerate(self.layers):
                    node.timeslots[layer_idx] = TimeSlot(st, et, capacity=capacity, state=ResourceState.AVAILABLE)
                # If no layers yet, still prepare baseline timeslot at layer 0 lazily on first layer add
                if not self.layers:
                    node.timeslots[0] = TimeSlot(0, 0, capacity=capacity, state=ResourceState.AVAILABLE)
                self.nodes[node_id] = node
            else:
                # Update metadata and capacities for new layers
                node = self.nodes[node_id]
                node.location = location
                node.floor = floor
                node.room_type = room_type
                node.amenities = amenities or node.amenities
                for layer_idx, (st, et) in enumerate(self.layers):
                    if layer_idx not in node.timeslots:
                        node.timeslots[layer_idx] = TimeSlot(st, et, capacity=capacity, state=ResourceState.AVAILABLE)

    def add_edge_with_distance(self, from_node: int, to_node: int, layer: int,
                               capacity: int, corridor_type: str = "standard"):
        """Add edge with calculated distance and corridor properties"""
        with self.graph_lock:
            a = self.nodes.get(from_node)
            b = self.nodes.get(to_node)
            if a is None or b is None:
                raise KeyError("Both nodes must exist before adding an edge")
            # Euclidean distance as base cost
            dist = math.dist(a.location, b.location)
            base_cost = dist if dist > 0 else 1.0
            edge_key = (from_node, to_node, layer)
            self.edges[edge_key] = MultiLayerEdge(from_node, to_node, layer, capacity=capacity,
                                                  base_cost=base_cost, corridor_type=corridor_type)
            # Undirected assumption for hotel corridors; add both directions if not present
            self.layer_adj[layer][from_node].append(to_node)
            rev_key = (to_node, from_node, layer)
            if rev_key not in self.edges:
                self.edges[rev_key] = MultiLayerEdge(to_node, from_node, layer, capacity=capacity,
                                                     base_cost=base_cost, corridor_type=corridor_type)
                self.layer_adj[layer][to_node].append(from_node)
            self._invalidate_cache(layer)

    def get_available_nodes_fast(self, layer: int, required_capacity: int = 1) -> Set[int]:
        """Retrieve available nodes with caching optimization"""
        with self.cache_lock:
            cached = self.available_nodes_cache.get(layer)
            if cached is not None:
                return set(cached)
        # Build cache
        result = set()
        with self.graph_lock:
            for nid, node in self.nodes.items():
                slot = node.timeslots.get(layer)
                if slot and slot.can_allocate(required_capacity):
                    result.add(nid)
        with self.cache_lock:
            self.available_nodes_cache[layer] = set(result)
        return result

    def bulk_update_availability(self, updates: List[Tuple[int, int, ResourceState]]):
        """Process multiple availability updates atomically"""
        with self.graph_lock:
            for node_id, layer, state in updates:
                node = self.nodes.get(node_id)
                if not node:
                    continue
                slot = node.timeslots.get(layer)
                if not slot:
                    continue
                slot.state = state
                if state in (ResourceState.UNAVAILABLE, ResourceState.MAINTENANCE):
                    # free any used allocations (rollback)
                    slot.used = min(slot.used, slot.capacity)  # keep invariants
                self._invalidate_cache(layer)

    def _invalidate_cache(self, layer: int):
        """Invalidate cached data for specific layer"""
        with self.cache_lock:
            if layer in self.available_nodes_cache:
                del self.available_nodes_cache[layer]

    def _invalidate_all_caches(self):
        """Clear all cached availability data"""
        with self.cache_lock:
            self.available_nodes_cache.clear()

    # Utility to run Dijkstra on the physical graph for transit distance
    def shortest_path_costs_on_layer(self, layer: int, start: int,
                                     corridor_penalty: Dict[Tuple[int, int], int] = None) -> Dict[int, float]:
        """Compute shortest path costs on a given layer from start node"""
        if corridor_penalty is None:
            corridor_penalty = {}
        adj = self.layer_adj[layer]
        dist = defaultdict(lambda: float('inf'))
        dist[start] = 0.0
        pq = [(0.0, start)]
        while pq:
            d, u = heapq.heappop(pq)
            if d > dist[u]:
                continue
            for v in adj.get(u, []):
                e = self.edges.get((u, v, layer))
                if not e:
                    continue
                base = e.base_cost
                # corridor capacity penalty: lower capacity => higher cost
                cap = e.capacity
                cap_penalty = 1.0 + (1.0 / max(1, cap))
                # external penalty overrides for specific corridors
                extra = 0.0
                if corridor_penalty and (u, v) in corridor_penalty:
                    # interpret value as capacity limit -> higher penalty if limit is small
                    limit = corridor_penalty[(u, v)]
                    extra = 1.0 + (1.0 / max(1, limit))
                cost = base * cap_penalty + extra
                nd = d + cost
                if nd < dist[v]:
                    dist[v] = nd
                    heapq.heappush(pq, (nd, v))
        return dist


# ==================== Flow Optimization Engine ====================

class ProductionMinCostMaxFlow:
    """Min-cost max-flow solver for optimal resource allocation"""

    def __init__(self, graph: AdvancedMultiLayerGraph):
        """Initialize flow solver with graph reference"""
        self.graph = graph
        # Flow network structures
        self.N = 0
        self.res_adj: List[List[int]] = []
        self.to: List[int] = []
        self.cap: List[int] = []
        self.cost: List[float] = []
        self.rev: List[int] = []
        self.source = -1
        self.sink = -1
        self.node_index_guest: Dict[int, int] = {}
        self.node_index_room: Dict[int, int] = {}
        self.guest_of_index: Dict[int, int] = {}
        self.room_of_index: Dict[int, int] = {}

    def _init_network(self, total_nodes: int):
        self.N = total_nodes
        self.res_adj = [[] for _ in range(self.N)]
        self.to = []
        self.cap = []
        self.cost = []
        self.rev = []

    def _add_edge(self, u: int, v: int, c: int, w: float):
        # forward
        self.res_adj[u].append(len(self.to))
        self.to.append(v)
        self.cap.append(c)
        self.cost.append(w)
        fwd_idx = len(self.to) - 1
        # reverse
        self.res_adj[v].append(len(self.to))
        self.to.append(u)
        self.cap.append(0)
        self.cost.append(-w)
        rev_idx = len(self.to) - 1
        self.rev.append(rev_idx)
        self.rev.append(fwd_idx)

    def build_layered_flow_network(self, target_layer: int, guest_requests: Dict[int, Dict[str, Any]]):
        """Construct flow network from graph structure and requests"""
        # Determine available rooms in this layer
        available_rooms = self.graph.get_available_nodes_fast(target_layer, required_capacity=1)
        rooms = sorted(list(available_rooms))
        guests = sorted(list(guest_requests.keys()))

        # Precompute transit costs from lobby (choose min node id as proxy, or explicit)
        lobby = None
        if 'lobby_node' in guest_requests.get(guests[0], {}):  # optional per request
            lobby = guest_requests[guests[0]]['lobby_node']
        else:
            lobby = min(self.graph.nodes.keys()) if self.graph.nodes else 0

        # corridor penalties from constraints (if provided at request level)
        corridor_penalty = {}
        # If all guest requests share the same constraints map, try to extract it
        any_req = guest_requests[guests[0]] if guests else {}
        constraints = any_req.get('constraints', {})
        cap_pen = constraints.get('corridor_capacity', {})
        if isinstance(cap_pen, dict):
            corridor_penalty = cap_pen

        dist_from_lobby = self.graph.shortest_path_costs_on_layer(target_layer, lobby, corridor_penalty=corridor_penalty)

        # Build nodes: source + guests + rooms + sink
        self.source = 0
        guest_start = 1
        room_start = guest_start + len(guests)
        self.sink = room_start + len(rooms)
        total_nodes = self.sink + 1
        self._init_network(total_nodes)
        self.node_index_guest.clear()
        self.node_index_room.clear()
        self.guest_of_index.clear()
        self.room_of_index.clear()

        # Map indices
        for i, g in enumerate(guests):
            idx = guest_start + i
            self.node_index_guest[g] = idx
            self.guest_of_index[idx] = g
        for j, r in enumerate(rooms):
            idx = room_start + j
            self.node_index_room[r] = idx
            self.room_of_index[idx] = r

        # Source->Guest edges
        for g in guests:
            gi = self.node_index_guest[g]
            self._add_edge(self.source, gi, 1, 0.0)

        # Room->Sink edges with capacity equal to room timeslot capacity
        for r in rooms:
            ri = self.node_index_room[r]
            slot = self.graph.nodes[r].timeslots.get(target_layer)
            room_cap = slot.available_capacity() if slot else 0
            if room_cap <= 0:
                continue
            self._add_edge(ri, self.sink, room_cap, 0.0)

        # Guest->Room edges
        for g in guests:
            req = guest_requests[g]
            preferred = set(req.get('preferred_rooms', []))
            avoid = set(req.get('avoid_rooms', []))
            desired_floor = req.get('preferred_floor', None)
            amenities_required: Set[str] = set(req.get('amenities', []))
            # Weights
            base_pref_bonus = req.get('preference_bonus', -5.0)  # negative reduces cost (preferred)
            non_pref_penalty = req.get('non_preference_penalty', 1.0)
            avoid_penalty = req.get('avoid_penalty', 50.0)
            floor_penalty = req.get('floor_mismatch_penalty', 2.0)
            amenity_penalty = req.get('amenity_missing_penalty', 10.0)
            congestion_factor = float(req.get('congestion_factor', 1.0))

            for r in rooms:
                # basic availability already checked
                node = self.graph.nodes[r]
                # Hard filter: avoid rooms list
                if r in avoid:
                    # still create edge with high cost to keep solution feasible if necessary
                    pass
                # Hard filter amenities if requested strictly
                missing_amenities = amenities_required - node.amenities
                # Cost components
                transit_cost = dist_from_lobby.get(r, 10.0)  # default if unreachable
                cost = transit_cost

                # Preference cost
                if r in preferred:
                    cost += base_pref_bonus
                else:
                    cost += non_pref_penalty

                # Avoid penalty
                if r in avoid:
                    cost += avoid_penalty

                # Floor preference
                if desired_floor is not None and node.floor != desired_floor:
                    cost += floor_penalty

                # Amenity penalty
                if missing_amenities:
                    cost += amenity_penalty * len(missing_amenities)

                # Corridor dynamic congestion multiplier
                cost *= congestion_factor

                # Create edge Guest->Room with capacity 1
                gi = self.node_index_guest[g]
                ri = self.node_index_room[r]
                self._add_edge(gi, ri, 1, cost)

    def successive_shortest_path(self) -> Tuple[int, float]:
        """Execute successive shortest path algorithm for min-cost flow"""
        flow = 0
        total_cost = 0.0
        # Node potentials for reduced costs
        pi = [0.0] * self.N

        while True:
            dist = [float('inf')] * self.N
            parent_edge = [-1] * self.N
            inqueue = [False] * self.N
            dist[self.source] = 0.0

            # Dijkstra with potentials
            pq = [(0.0, self.source)]
            while pq:
                d, u = heapq.heappop(pq)
                if d > dist[u]:
                    continue
                for ei in self.res_adj[u]:
                    v = self.to[ei]
                    if self.cap[ei] <= 0:
                        continue
                    rcost = self.cost[ei] + pi[u] - pi[v]
                    nd = d + rcost
                    if nd < dist[v]:
                        dist[v] = nd
                        parent_edge[v] = ei
                        heapq.heappush(pq, (nd, v))

            if dist[self.sink] == float('inf'):
                break  # no more augmenting paths

            # Update potentials
            for i in range(self.N):
                if dist[i] < float('inf'):
                    pi[i] += dist[i]

            # Augment one unit of flow (all supplies are 1 per guest)
            # Find bottleneck
            aug = float('inf')
            v = self.sink
            while v != self.source:
                ei = parent_edge[v]
                if ei == -1:
                    aug = 0
                    break
                aug = min(aug, self.cap[ei])
                v = self.to[self.rev[ei]]
            if aug == 0 or aug == float('inf'):
                break
            # Apply augmentation
            v = self.sink
            path_cost = 0.0
            while v != self.source:
                ei = parent_edge[v]
                self.cap[ei] -= aug
                self.cap[self.rev[ei]] += aug
                path_cost += self.cost[ei]
                v = self.to[self.rev[ei]]
            flow += int(aug)
            total_cost += path_cost * aug

        return flow, total_cost

    def extract_allocation(self, guest_requests: Dict[int, Dict[str, Any]]) -> Dict[int, int]:
        """Extract final room allocation from computed flow"""
        allocation: Dict[int, int] = {}
        # For each guest node, find outgoing edges to rooms where residual cap increased (flow sent)
        for gi_index, g in self.guest_of_index.items():
            # scan edges from gi_index
            for ei in self.res_adj[gi_index]:
                v = self.to[ei]
                # v is room node if in mapping
                if v in self.room_of_index:
                    # If reverse edge has positive capacity, it means forward flow was sent
                    rev_ei = self.rev[ei]
                    if self.cap[rev_ei] > 0:
                        room_id = self.room_of_index[v]
                        allocation[g] = room_id
                        break
        return allocation


# ==================== Real-Time Scheduling Engine ====================

class RealTimeSchedulingEngine:
    """Concurrent request processor with load balancing and SLA management"""

    def __init__(self, graph: AdvancedMultiLayerGraph, max_concurrent_requests: int = 50):
        """Initialize scheduling engine with concurrency limits"""
        self.graph = graph
        self.executor = ThreadPoolExecutor(max_workers=max_concurrent_requests)
        self.metrics_lock = threading.Lock()
        self.metrics = {
            'requests_total': 0.0,
            'requests_succeeded': 0.0,
            'avg_latency_ms': 0.0,
        }

    def submit_allocation_request(self, request_id: str,
                                   guest_requests: Dict[int, Dict[str, Any]],
                                   target_layers: List[int],
                                   constraints: Dict[str, Any],
                                   priority: str = 'standard') -> Dict[int, int]:
        """Submit and process allocation request with priority handling"""
        # Synchronous processing for determinism in this reference implementation
        start = time.time()
        try:
            allocation = self._process_multi_layer_allocation(request_id, guest_requests, target_layers, constraints, priority)
            with self.metrics_lock:
                self.metrics['requests_total'] += 1
                self.metrics['requests_succeeded'] += 1
                lat = (time.time() - start) * 1000.0
                # Running average
                prev_avg = self.metrics['avg_latency_ms']
                n = self.metrics['requests_total']
                self.metrics['avg_latency_ms'] = prev_avg + (lat - prev_avg) / max(1.0, n)
            return allocation
        except Exception:
            with self.metrics_lock:
                self.metrics['requests_total'] += 1
                lat = (time.time() - start) * 1000.0
                prev_avg = self.metrics['avg_latency_ms']
                n = self.metrics['requests_total']
                self.metrics['avg_latency_ms'] = prev_avg + (lat - prev_avg) / max(1.0, n)
            return {}

    def _process_multi_layer_allocation(self, request_id: str,
                                        guest_requests: Dict[int, Dict[str, Any]],
                                        target_layers: List[int],
                                        constraints: Dict[str, Any],
                                        priority: str) -> Dict[int, int]:
        """Process allocation across multiple time layers"""
        best_allocation = {}
        best_cost = float('inf')
        best_layer = None

        for layer in target_layers:
            solver = ProductionMinCostMaxFlow(self.graph)
            # Inject constraints into requests so costs can use them
            reqs = {}
            for gid, req in guest_requests.items():
                # copy and enrich with constraints
                merged = dict(req)
                merged['constraints'] = constraints
                # If preferred floor exists in constraints, cascade as soft preference
                if 'preferred_floor' in constraints and 'preferred_floor' not in merged:
                    merged['preferred_floor'] = constraints['preferred_floor']
                reqs[gid] = merged

            # Build and solve flow
            solver.build_layered_flow_network(layer, reqs)
            solver.successive_shortest_path()
            allocation = solver.extract_allocation(reqs)

            if not allocation:
                continue
            if not self._validate_complex_constraints(allocation, layer, constraints):
                continue
            cost = self._calculate_holistic_cost(allocation, layer, reqs, constraints)
            if cost < best_cost:
                best_cost = cost
                best_allocation = allocation
                best_layer = layer

        if best_allocation and best_layer is not None:
            self._apply_allocation_to_graph(best_allocation, best_layer)
        return best_allocation

    def _validate_complex_constraints(self, allocation: Dict[int, int],
                                      layer: int, constraints: Dict[str, Any]) -> bool:
        """Validate allocation against complex constraint rules"""
        # Example validations:
        # - overlap_threshold: limit number of simultaneous assignments per floor
        overlap_threshold = constraints.get('overlap_threshold', None)
        if overlap_threshold is not None:
            floor_counts = defaultdict(int)
            for guest, room in allocation.items():
                floor = self.graph.nodes[room].floor
                floor_counts[floor] += 1
            for f, cnt in floor_counts.items():
                if cnt > overlap_threshold:
                    return False
        # More complex rules can be inserted here.
        return True

    def _calculate_holistic_cost(self, allocation: Dict[int, int], layer: int,
                                 guest_requests: Dict[int, Dict[str, Any]],
                                 constraints: Dict[str, Any]) -> float:
        """Calculate comprehensive cost including transit and preferences"""
        # For a simple holistic measure, sum transit costs and penalties for not meeting preferences
        lobby = constraints.get('lobby_node', min(self.graph.nodes.keys()) if self.graph.nodes else 0)
        corridor_penalty = constraints.get('corridor_capacity', {})
        dist = self.graph.shortest_path_costs_on_layer(layer, lobby, corridor_penalty=corridor_penalty)
        total = 0.0
        for g, r in allocation.items():
            req = guest_requests.get(g, {})
            base = dist.get(r, 10.0)
            # Add soft penalty if not in preferred
            preferred = set(req.get('preferred_rooms', []))
            if preferred and r not in preferred:
                total += 2.0
            total += base
        return total

    def _apply_allocation_to_graph(self, allocation: Dict[int, int], layer: int):
        """Apply computed allocation to graph state"""
        # Reserve capacity on nodes (rooms) for the corresponding layer
        for guest, room in allocation.items():
            node = self.graph.nodes.get(room)
            if node:
                node.allocate_resource(layer, 1)
        # Invalidate availability cache for this layer
        self.graph._invalidate_cache(layer)

    def get_performance_metrics(self) -> Dict[str, float]:
        """Retrieve current performance and SLA metrics"""
        with self.metrics_lock:
            return dict(self.metrics)


# ==================== Public Integration Function ====================

def optimize_allocation(
    graph: Dict[int, List[int]],
    room_availability: Dict[int, bool], 
    guest_preferences: Dict[int, List[int]],
    logistical_constraints: Dict[str, Any]
) -> Dict[int, int]:
    """
    Main optimization function integrating multi-layer graph, min-cost flow, and real-time scheduling
    """
    # Build multi-layer graph
    mg = AdvancedMultiLayerGraph(max_layers=100)

    # Create a single time layer if none; using simple time window [0, 24)
    layer0 = mg.add_time_layer(0, 24)

    # Create node coordinates heuristically (grid based on id) for distances
    def node_coords(nid: int) -> Tuple[float, float]:
        # Simple deterministic placement: x = nid % 10, y = nid // 10
        return (float(nid % 10), float(nid // 10))

    # Add nodes with capacities; rooms are capacity 1 by default in hotels
    for nid in set(graph.keys()) | set(room_availability.keys()):
        cap = 1
        loc = node_coords(nid)
        floor = int(nid // 100) + 1 if nid >= 100 else 1  # rough floor heuristic
        mg.add_node_with_location(nid, capacity=cap, location=loc, floor=floor, room_type="standard", amenities=set())

    # Add edges based on adjacency; capacity from constraints if specified
    corridor_caps = logistical_constraints.get('corridor_capacity', {})
    for u, nbrs in graph.items():
        for v in nbrs:
            # Obtain capacity for this corridor if specified; otherwise default to 5
            cap = corridor_caps.get((u, v), corridor_caps.get((v, u), 5))
            mg.add_edge_with_distance(u, v, layer0, capacity=cap, corridor_type="standard")

    # Apply room availability
    updates = []
    for room_id, avail in room_availability.items():
        state = ResourceState.AVAILABLE if avail else ResourceState.UNAVAILABLE
        updates.append((room_id, layer0, state))
    mg.bulk_update_availability(updates)

    # Build guest request structures
    guest_requests: Dict[int, Dict[str, Any]] = {}
    for gid, prefs in guest_preferences.items():
        guest_requests[gid] = {
            'preferred_rooms': prefs,
            # propagate constraints that might influence costs
            'preferred_floor': logistical_constraints.get('preferred_floor', None),
            'congestion_factor': 1.0,
            'preference_bonus': -5.0,  # prefer listed rooms
            'non_preference_penalty': 1.0,
            'avoid_penalty': 50.0,
            'floor_mismatch_penalty': 2.0,
            'amenity_missing_penalty': 10.0,
        }

    # Process allocation using RealTimeSchedulingEngine
    engine = RealTimeSchedulingEngine(mg, max_concurrent_requests=16)
    allocation = engine.submit_allocation_request(
        request_id="req-1",
        guest_requests=guest_requests,
        target_layers=[layer0],
        constraints=logistical_constraints,
        priority='standard'
    )

    return allocation

if __name__ == "__main__":
    # Sample Input
    sample_graph = {
        1: [2, 3],
        2: [1, 4, 5], 
        3: [1, 5],
        4: [2, 5],
        5: [2, 3, 4]
    }
    
    sample_availability = {
        1: True,
        2: True,
        3: False,
        4: True,
        5: True
    }
    
    sample_preferences = {
        101: [2, 5],
        102: [1, 3],
        103: [4],
        104: [2, 3, 5]
    }
    
    sample_constraints = {
        'corridor_capacity': {(2, 5): 2},
        'maintenance_times': {3: [10, 14]},
        'preferred_floor': 2,
        'overlap_threshold': 2
    }
    
    # Execute allocation
    result = optimize_allocation(
        sample_graph,
        sample_availability, 
        sample_preferences,
        sample_constraints
    )
    
    # Print result
    print(result)