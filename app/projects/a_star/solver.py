import heapq

GOAL = (1, 2, 3, 4, 5, 6, 7, 8, 0)
GOAL_POSITIONS = {value: divmod(index, 3) for index, value in enumerate(GOAL)}


def manhattan(state):
    distance = 0
    for i, value in enumerate(state):
        if value == 0:
            continue

        x1, y1 = divmod(i, 3)
        x2, y2 = GOAL_POSITIONS[value]
        distance += abs(x1 - x2) + abs(y1 - y2)

    return distance


def get_neighbors(state):
    neighbors = []
    zero_index = state.index(0)
    x, y = divmod(zero_index, 3)

    for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        nx, ny = x + dx, y + dy

        if 0 <= nx < 3 and 0 <= ny < 3:
            new_index = nx * 3 + ny
            new_state = list(state)
            new_state[zero_index], new_state[new_index] = (
                new_state[new_index],
                new_state[zero_index],
            )
            neighbors.append(tuple(new_state))

    return neighbors


def reconstruct_path(came_from, current):
    path = [current]

    while current in came_from:
        current = came_from[current]
        path.append(current)

    path.reverse()
    return path


def is_solvable(state):
    values = [x for x in state if x != 0]
    inversions = 0

    for i in range(len(values)):
        for j in range(i + 1, len(values)):
            if values[i] > values[j]:
                inversions += 1

    return inversions % 2 == 0


def astar_with_tree(start):
    if not is_solvable(start):
        return {
            "solution": [],
            "tree_nodes": []
        }

    open_heap = []
    start_h = manhattan(start)
    heapq.heappush(open_heap, (start_h, 0, start))

    came_from = {}
    g_score = {start: 0}
    closed_set = set()

    node_id_map = {start: 0}
    tree_nodes = [{
        "id": 0,
        "state": list(start),
        "g": 0,
        "h": start_h,
        "f": start_h,
        "parent_id": None,
        "status": "open"
    }]
    next_id = 1

    while open_heap:
        f, g, current = heapq.heappop(open_heap)

        if current in closed_set:
            continue

        current_id = node_id_map[current]
        tree_nodes[current_id]["status"] = "expanded"

        if current == GOAL:
            tree_nodes[current_id]["status"] = "goal"
            return {
                "solution": [list(step) for step in reconstruct_path(came_from, current)],
                "tree_nodes": tree_nodes
            }

        closed_set.add(current)

        for neighbor in get_neighbors(current):
            if neighbor in closed_set:
                continue

            tentative_g = g_score[current] + 1

            if neighbor not in g_score or tentative_g < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g

                h = manhattan(neighbor)
                f = tentative_g + h

                heapq.heappush(open_heap, (f, tentative_g, neighbor))

                if neighbor not in node_id_map:
                    node_id_map[neighbor] = next_id
                    tree_nodes.append({
                        "id": next_id,
                        "state": list(neighbor),
                        "g": tentative_g,
                        "h": h,
                        "f": f,
                        "parent_id": current_id,
                        "status": "open"
                    })
                    next_id += 1
                else:
                    node_id = node_id_map[neighbor]
                    tree_nodes[node_id]["g"] = tentative_g
                    tree_nodes[node_id]["h"] = h
                    tree_nodes[node_id]["f"] = f
                    tree_nodes[node_id]["parent_id"] = current_id
                    if tree_nodes[node_id]["status"] != "goal":
                        tree_nodes[node_id]["status"] = "open"

    return {
        "solution": [],
        "tree_nodes": tree_nodes
    }