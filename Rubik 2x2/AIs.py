import heapq, time
from Cube import *
from Heuristic import *


class A_Star:
    def __init__(self, cube, heuristic=Heuristic.manhattanDistance):
        self.cube = cube
        self.heuristic = heuristic

    def solve(self, timeout=float('inf')):
        start_time = time.time()
        start_state = State(self.cube, None, 0, 0, None)
        goal_state = State(Cube(self.cube.size), None, 0, 0, None)
        explored = set()
        fringe = [start_state]
        heapq.heapify(fringe)

        print("starting solve")
        while len(fringe) > 0:
            if time.time() - start_time >= timeout:
                print('time: ' + str(time.time()))
                raise Exception('Code timed out')

            current_state = heapq.heappop(fringe)
            #print(current_state)
            if current_state.current_state.isSolved():
                return self.find_path(start_state, current_state)
            if current_state.__hash__() in explored:
                continue
            for i in current_state.current_state.children('2x'):
                if i.__hash__() not in explored:
                    new_addition = State(i[1], current_state, current_state.depth+1+self.heuristic(i[1]), current_state.depth+1, i[0])
                    heapq.heappush(fringe, new_addition)
                    explored.add(current_state.__hash__())

    def find_path(self, start_state, end_state):
        last_state = end_state
        path = [ [last_state.move, last_state.current_state] ]
        last_state = last_state.parent_state

        while last_state != None and start_state.current_state.__hash__() != path[0][1].__hash__():
            path = [ [last_state.move, last_state.current_state] ] + path
            last_state = last_state.parent_state

        return path


class State:
    def __init__(self, current_state, parent_state, fValue, depth, move):
        self.current_state = current_state
        self.parent_state = parent_state
        self.fValue = fValue
        self.depth = depth
        self.move = move

    def __eq__(self, other):
        if self.current_state == other:
            return True
        return False

    def __lt__(self, other):
        return self.fValue < other.fValue

    def __bool__(self):
        return True

    def __hash__(self):
        return self.current_state.__hash__()

    def __str__(self):
        return "depth:" + str(self.depth) + "; fValue:" + str(self.fValue) + "; current_state:" + str(self.current_state.__hash__()) + '; move:' + str(self.move) + '; solved:' + str(self.current_state.isSolved())