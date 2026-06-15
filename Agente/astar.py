import heapq


class AStarAgent:

    def solve(self, sudoku, metrics=None, tree=None, max_nodes=200000):

        board = [row[:] for row in sudoku.board]

        if metrics:
            metrics.reset()
            metrics.start()

        def board_key(b):
            return tuple(tuple(r) for r in b)

        def find_empty(b):
            for r in range(9):
                for c in range(9):
                    if b[r][c] == 0:
                        return r, c
            return None

        def is_valid(num, row, col, b):
            for c in range(9):
                if b[row][c] == num:
                    return False
            for r in range(9):
                if b[r][col] == num:
                    return False
            sr, sc = (row // 3) * 3, (col // 3) * 3
            for r in range(sr, sr + 3):
                for c in range(sc, sc + 3):
                    if b[r][c] == num:
                        return False
            return True

        def heuristic(b):
            # simple heuristic: number of empty cells
            empties = 0
            for r in range(9):
                for c in range(9):
                    if b[r][c] == 0:
                        empties += 1
            return empties

        start_key = board_key(board)
        visited = set()
        heap = []  # elements are (f, g, board)

        g0 = 0
        h0 = heuristic(board)
        heapq.heappush(heap, (g0 + h0, g0, board))

        nodes = 0

        while heap and nodes < max_nodes:
            f, g, node = heapq.heappop(heap)
            key = board_key(node)

            if key in visited:
                continue

            visited.add(key)

            if metrics:
                metrics.increment_states()

            nodes += 1

            pos = find_empty(node)
            if pos is None:
                if metrics:
                    metrics.stop()
                    metrics.mark_success()
                sudoku.board = node
                return sudoku

            row, col = pos

            for digit in range(1, 10):
                if is_valid(digit, row, col, node):
                    child = [r[:] for r in node]
                    child[row][col] = digit
                    child_key = board_key(child)
                    if child_key in visited:
                        continue
                    new_g = g + 1
                    h = heuristic(child)
                    heapq.heappush(heap, (new_g + h, new_g, child))

        if metrics:
            metrics.stop()
            metrics.mark_fail()

        return None

    def solve_steps(self, sudoku, metrics=None, tree=None, max_nodes=200000):
        board = [row[:] for row in sudoku.board]

        def board_key(b):
            return tuple(tuple(r) for r in b)

        def find_empty(b):
            for r in range(9):
                for c in range(9):
                    if b[r][c] == 0:
                        return r, c
            return None

        def is_valid(num, row, col, b):
            for c in range(9):
                if b[row][c] == num:
                    return False
            for r in range(9):
                if b[r][col] == num:
                    return False
            sr, sc = (row // 3) * 3, (col // 3) * 3
            for r in range(sr, sr + 3):
                for c in range(sc, sc + 3):
                    if b[r][c] == num:
                        return False
            return True

        def heuristic(b):
            empties = 0
            for r in range(9):
                for c in range(9):
                    if b[r][c] == 0:
                        empties += 1
            return empties

        visited = set()
        heap = []
        g0 = 0
        h0 = heuristic(board)
        heapq.heappush(heap, (g0 + h0, g0, board))

        nodes = 0

        while heap and nodes < max_nodes:
            f, g, node = heapq.heappop(heap)
            key = board_key(node)

            if key in visited:
                continue

            visited.add(key)

            if metrics:
                metrics.increment_states()

            nodes += 1

            # yield the current node for visualization
            yield [r[:] for r in node]

            pos = find_empty(node)
            if pos is None:
                return

            row, col = pos

            for digit in range(1, 10):
                if is_valid(digit, row, col, node):
                    child = [r[:] for r in node]
                    child[row][col] = digit
                    child_key = board_key(child)
                    if child_key in visited:
                        continue
                    new_g = g + 1
                    h = heuristic(child)
                    heapq.heappush(heap, (new_g + h, new_g, child))

        return