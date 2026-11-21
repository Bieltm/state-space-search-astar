import heapq
from hlogedu.search.algorithm import Algorithm, Solution
from hlogedu.search.node import Node


class TreeAStar(Algorithm):
    NAME = "tree-astar"

    def run(self):
        frontier = []
        expanded_count = 0
        counter = 0
        for state in self.problem.initials():
            h = self.heuristic(state)
            f = 0 + h

            node = Node(state=state, parent=None, action=None, cost=0)
            node.location = Node.Location.FRONTIER
            heapq.heappush(frontier, (f, counter, node))
            counter += 1
        while frontier:     
            f, _, current = heapq.heappop(frontier)
            current.location = Node.Location.EXPANDED

            if self.problem.is_goal(current.state):
                return Solution(
                    problem=self.problem,
                    algorithm=self,
                    node=current,
                    expanded=expanded_count,
                )

            expanded_count += 1
            current.expanded_order = expanded_count

            for action in sorted(self.problem.actions(current.state)):
                next_state = self.problem.result(current.state, action)
                step_cost = self.problem.cost(current.state, action)
                g = current.cost + step_cost
                h = self.heuristic(next_state)

                child = Node(
                    state=next_state,
                    parent=current,
                    action=action,
                    cost=g,
                )
                child.location = Node.Location.FRONTIER
                heapq.heappush(frontier, (g + h, counter, child))
                counter += 1

        return Solution(
            problem=self.problem,
            algorithm=self,
            node=None,
            expanded=expanded_count,
        )



class GraphAStar(Algorithm):
    NAME = "graph-astar"

    def run(self):
        frontier = []
        expanded_count = 0
        counter = 0
        explored = set()

        for state in self.problem.initials():
            h = self.heuristic(state)
            f = 0 + h

            node = Node(state=state, parent=None, action=None, cost=0)
            node.location = Node.Location.FRONTIER
            heapq.heappush(frontier, (f, counter, node))
            counter += 1

        while frontier:
            f, _, current = heapq.heappop(frontier)

            if current.state in explored:
                continue

            explored.add(current.state)
            current.location = Node.Location.EXPANDED

            if self.problem.is_goal(current.state):
                return Solution(
                    problem=self.problem,
                    algorithm=self,
                    node=current,
                    expanded=expanded_count,
                )

            expanded_count += 1
            current.expanded_order = expanded_count

            for action in sorted(self.problem.actions(current.state)):
                next_state = self.problem.result(current.state, action)
                if next_state in explored:
                    continue

                step_cost = self.problem.cost(current.state, action)
                g = current.cost + step_cost
                h = self.heuristic(next_state)

                child = Node(
                    state=next_state,
                    parent=current,
                    action=action,
                    cost=g,
                )
                child.location = Node.Location.FRONTIER
                heapq.heappush(frontier, (g + h, counter, child))
                counter += 1

        return Solution(
            problem=self.problem,
            algorithm=self,
            node=None,
            expanded=expanded_count,
        )