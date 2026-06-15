class DFSAgent:

    def solve(self, sudoku, metrics=None, tree=None, max_depth=100):

        board = sudoku.board

        if metrics:
            metrics.reset()
            metrics.start()

        def find_empty():
            for r in range(9):
                for c in range(9):
                    if board[r][c] == 0:
                        return r, c
            return None

        def is_valid(num, row, col):

            for c in range(9):
                if board[row][c] == num:
                    return False

            for r in range(9):
                if board[r][col] == num:
                    return False

            start_row = (row // 3) * 3
            start_col = (col // 3) * 3

            for r in range(start_row, start_row + 3):
                for c in range(start_col, start_col + 3):
                    if board[r][c] == num:
                        return False

            return True

        def dfs(depth=0):

            if metrics:
                metrics.increment_states()

            if depth > max_depth:
                return False

            pos = find_empty()

            if pos is None:
                return True

            row, col = pos

            for digit in range(1, 10):

                if is_valid(digit, row, col):

                    board[row][col] = digit

                    if tree:
                        tree.push(row, col, digit)

                    if dfs(depth + 1):
                        return True

                    board[row][col] = 0

                    if tree:
                        tree.pop()

            return False

        solved = dfs()

        if metrics:
            metrics.stop()

            if solved:
                metrics.mark_success()
            else:
                metrics.mark_fail()

        return sudoku if solved else None

    def solve_steps(self, sudoku, metrics=None, tree=None, max_depth=100):
        board = [row[:] for row in sudoku.board]

        def find_empty():
            for r in range(9):
                for c in range(9):
                    if board[r][c] == 0:
                        return r, c
            return None

        def is_valid(num, row, col):
            for c in range(9):
                if board[row][c] == num:
                    return False
            for r in range(9):
                if board[r][col] == num:
                    return False
            sr, sc = (row // 3) * 3, (col // 3) * 3
            for r in range(sr, sr + 3):
                for c in range(sc, sc + 3):
                    if board[r][c] == num:
                        return False
            return True

        def dfs(depth=0):
            if depth > max_depth:
                return False
            pos = find_empty()
            if pos is None:
                return True
            row, col = pos
            for digit in range(1, 10):
                if is_valid(digit, row, col):
                    board[row][col] = digit
                    if tree:
                        tree.push(row, col, digit)
                    yield [r[:] for r in board]
                    solved = yield from dfs(depth + 1)
                    if solved:
                        return True
                    board[row][col] = 0
                    if tree:
                        tree.pop()
            return False

        yield from dfs()