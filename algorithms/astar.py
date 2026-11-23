from hlogedu.search.algorithm import Algorithm, Node, Solution
from hlogedu.search.containers import PriorityQueue


class TreeAStar(Algorithm):
    NAME = "tree-astar"

    def run(self, heuristic=None):
        if heuristic is None:
            heuristic = lambda state: 0  # sin heurística: equivale a UCS
        self.fringe = PriorityQueue(key=lambda n: n.state)  # desempate por estado, como el framework
        roots = []
        for state in self.problem.initials():
            h = heuristic(state)
            node = Node(state, h_cost=h, f_cost=h)
            node.location = Node.Location.FRINGE
            roots.append(node)
            self.fringe.push(node, node.f_cost)

        expanded = 0
        while not self.fringe.is_empty():
            node = self.fringe.pop()

            if self.problem.is_goal(node.state):
                node.location = Node.Location.PRE_EXPANDED
                return Solution(self.problem, roots, node)

            node.location = Node.Location.EXPANDED
            expanded += 1
            node.expanded_order = expanded

            for action in sorted(self.problem.actions(node.state)):
                next_state = self.problem.result(node.state, action)
                g = node.cost + self.problem.cost(node.state, action)
                h = heuristic(next_state)
                child = Node(next_state, action, g, node, h_cost=h, f_cost=g + h)
                node.add_successor(child)
                child.location = Node.Location.FRINGE
                self.fringe.push(child, child.f_cost)

        return Solution(self.problem, roots, None)


class GraphAStar(Algorithm):
    NAME = "graph-astar"

    def run(self, heuristic=None):
        if heuristic is None:
            heuristic = lambda state: 0  # sin heurística: equivale a UCS
        self.fringe = PriorityQueue(key=lambda n: n.state)  # desempate por estado, como el framework
        roots = []
        for state in self.problem.initials():
            h = heuristic(state)
            node = Node(state, h_cost=h, f_cost=h)
            node.location = Node.Location.FRINGE
            roots.append(node)
            self.fringe.push(node, node.f_cost)

        closed = set()
        expanded = 0
        while not self.fringe.is_empty():
            node = self.fringe.pop()
            if node.state in closed:
                continue

            if self.problem.is_goal(node.state):
                node.location = Node.Location.PRE_EXPANDED
                return Solution(self.problem, roots, node)

            closed.add(node.state)
            node.location = Node.Location.EXPANDED
            expanded += 1
            node.expanded_order = expanded

            for action in sorted(self.problem.actions(node.state)):
                next_state = self.problem.result(node.state, action)
                if next_state in closed:
                    continue
                g = node.cost + self.problem.cost(node.state, action)
                h = heuristic(next_state)
                child = Node(next_state, action, g, node, h_cost=h, f_cost=g + h)
                node.add_successor(child)
                child.location = Node.Location.FRINGE
                self.fringe.push(child, child.f_cost)

        return Solution(self.problem, roots, None)
