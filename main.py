import unittest
import itertools


d = 'd'
s = '-'
LEFT = 'LEFT'
RIGHT = 'RIGHT'
UP = 'UP'
DOWN = 'DOWN'
CLEAN = 'CLEAN'


def get_full_path(bot_coord, vertex_path):
    return (bot_coord,) + vertex_path


def calculate_distance_for_path(vertex_path):
    distance = 0
    for i in range(1, len(vertex_path)):
        x0, y0 = vertex_path[i - 1]
        x1, y1 = vertex_path[i]
        distance += abs(x1 - x0) + abs(y1 - y0)

    return distance


def vertex_in_square(vertex, square):
    """
    vertex: (x0, y0)
    square: ((x1, y1), (x2, y2))
    """
    x0, y0 = vertex

    v1, v2 = square
    x1, y1 = v1
    x2, y2 = v2

    min_x = min(x1, x2)
    min_y = min(y1, y2)

    max_x = max(x1, x2)
    max_y = max(y1, y2)

    if min_x <= x0 <= max_x and min_y <= y0 <= max_y:
        return True

    return False


def get_nearest_vertex(posr, posc, vertexes):
    return min(
        [(v, calculate_distance_for_path([[posr, posc], v])) for v in vertexes],
        key=lambda x: x[1]
    )[0]


def get_depending_vertexes_for_original_vertex(vertex, posr, posc, board):
    vertex_m, vertex_n = vertex

    start_m = min(posr, vertex_m)
    start_n = min(posc, vertex_n)

    end_m = max(posr, vertex_m)
    end_n = max(posc, vertex_n)

    depending_vertexes = []
    for i in range(start_m, end_m + 1):
        for j in range(start_n, end_n + 1):
            if (i, j) == (vertex_m, vertex_n):
                continue

            if board[i][j] == d:
                depending_vertexes.append(tuple([i, j]))

    return depending_vertexes


def get_independent_vertexes(posr, posc, board):
    independent_vertexes = {}
    for i, line in enumerate(board):
        for j, ceil in enumerate(line):
            if ceil == d:
                if independent_vertexes.get(i) is None:
                    independent_vertexes[i] = {}
                independent_vertexes[i][j] = True

    for i in independent_vertexes.keys():
        for j in independent_vertexes[i].keys():

            for k in independent_vertexes.keys():
                if not independent_vertexes[i][j]:
                    break

                for l in independent_vertexes[k].keys():
                    if (i, j) == (k, l):
                        continue

                    if vertex_in_square((i, j), ((posr, posc), (k, l))):
                        independent_vertexes[i][j] = False
                        break

    independent_vertexes_list = []
    for i in independent_vertexes.keys():
        for j in independent_vertexes[i].keys():
            if independent_vertexes[i][j]:
                independent_vertexes_list.append(tuple([i, j]))

    return independent_vertexes_list


def get_nearest_vertexes(posr, posc, original_vertexes):
    vertex_list = []
    for i, j in original_vertexes:
        remove_vertexes = []
        accept_vertex = True

        for v in vertex_list:
            if vertex_in_square((i, j), (v, (posr, posc))):
                remove_vertexes.append(v)

            if vertex_in_square(v, ((i, j), (posr, posc))):
                accept_vertex = False

        if accept_vertex:
            vertex_list.append(tuple([i, j]))

        for vertex_to_remove in remove_vertexes:
            vertex_list.remove(vertex_to_remove)

    return vertex_list


def next_move(posr, posc, dim_x, dim_y, board):
    if board[posr][posc] == d:
        print(CLEAN)
        return CLEAN

    independent_vertexes = get_independent_vertexes(posr, posc, board)
    nearest_independent_vertex = get_nearest_vertex(posr, posc, independent_vertexes)
    #print('independent_vertexes', independent_vertexes)
    #print('nearest_independent_vertex', nearest_independent_vertex)

    depending_vertexes = get_depending_vertexes_for_original_vertex(
        nearest_independent_vertex, posr, posc, board)
    #print('depending_vertexes', depending_vertexes)

    base_vertexes = depending_vertexes + [nearest_independent_vertex]
    vertex_list = get_nearest_vertexes(posr, posc, base_vertexes)
    #print('base_vertexes', base_vertexes)
    #print('vertex_list', vertex_list)

    vertex_permutations = itertools.permutations(vertex_list)
    min_path = None
    min_distance = None

    for vertex_path in vertex_permutations:
        full_vertex_path = get_full_path((posr, posc), vertex_path)
        distance = calculate_distance_for_path(full_vertex_path)
        #print(full_vertex_path)
        #print(distance)

        if min_path is None:
            min_path = vertex_path
            min_distance = distance
        else:
            if distance < min_distance:
                min_path = vertex_path
                min_distance = distance

    if min_path is not None:
        min_i, min_j = min_path[0]
        if min_i - posr != 0:
            if min_i - posr < 0:
                print(UP)
                return UP
            else:
                print(DOWN)
                return DOWN

        if min_j - posc != 0:
            if min_j - posc > 0:
                print(RIGHT)
                return RIGHT
            else:
                print(LEFT)
                return LEFT

    return


class TestFunctions(unittest.TestCase):

    def test_get_independent_vertexes(self):
        board = (
            (d, s, d, s, d),
            (s, s, s, d, s),
            (s, s, s, s, s),
            (s, s, s, s, s),
            (d, s, s, s, s),
        )
        posr, posc = 2, 2
        expected = [(0, 0), (4, 0), (0, 4)]

        result = get_independent_vertexes(posr, posc, board)

        self.assertEqual(set(expected), set(result))

    def test_get_nearest_vertex(self):
        vertexes = ((0, 0), (4, 0), (0, 4))
        posr, posc = 1, 0
        expected = (0, 0)

        result = get_nearest_vertex(posr, posc, vertexes)

        self.assertEqual(expected, result)

    def test_get_depending_vertexes_for_original_vertex1(self):
        board = (
            (d, s, d, s, d),
            (s, s, s, d, s),
            (s, s, s, s, s),
            (s, s, s, s, s),
            (d, s, s, s, s),
        )
        posr, posc = 2, 2
        expected = [(0, 2), (1, 3)]
        vertex = (0, 4)

        result = get_depending_vertexes_for_original_vertex(vertex, posr, posc, board)

        self.assertEqual(set(expected), set(result))

    def test_get_depending_vertexes_for_original_vertex2(self):
        board = (
            (s, s, s, s, s),
            (s, s, s, s, s),
            (s, s, s, s, s),
            (s, s, s, d, s),
            (s, s, d, s, d),
        )
        posr, posc = 2, 3
        vertex = (4, 2)
        expected = [(3, 3),]

        result = get_depending_vertexes_for_original_vertex(vertex, posr, posc, board)

        self.assertEqual(set(expected), set(result))

    def test_get_nearest_vertexes1(self):
        vertexes = ((0, 2), (0, 4), (1, 3))
        posr, posc = 2, 2
        expected = ((0, 2), (1, 3))

        result = get_nearest_vertexes(posr, posc, vertexes)

        self.assertEqual(set(expected), set(result))

    def test_get_nearest_vertexes2(self):
        vertexes = ((0, 0), (4, 0), (0, 2), (0, 4), (1, 3))
        posr, posc = 2, 2
        expected = ((4, 0), (0, 2), (1, 3))

        result = get_nearest_vertexes(posr, posc, vertexes)

        self.assertEqual(set(expected), set(result))

    def test_next_move(self):
        board = (
            (s, s, s, s, s),
            (s, s, s, s, s),
            (s, s, s, s, s),
            (s, s, s, d, s),
            (s, s, d, s, d),
        )
        posr, posc = 2, 3
        expected = DOWN

        result = next_move(posr, posc, None, None, board)

        self.assertEqual(set(expected), set(result))


if __name__ == '__main__':
    unittest.main()
