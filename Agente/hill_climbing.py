import random


class HillClimbingAgent:

    def _count_conflicts(self, board):
        conflicts = 0

        # verifica linhas
        for row in range(9):
            seen = []
            for col in range(9):
                if board[row][col] in seen:
                    conflicts += 1
                else:
                    seen.append(board[row][col])

        # verifica colunas
        for col in range(9):
            seen = []
            for row in range(9):
                if board[row][col] in seen:
                    conflicts += 1
                else:
                    seen.append(board[row][col])

        return conflicts

    def _fill_boxes(self, original, given):
        board = [row[:] for row in original]

        for box_row in range(3):
            for box_col in range(3):
                present = []
                free_cells = []

                for r in range(box_row * 3, box_row * 3 + 3):
                    for c in range(box_col * 3, box_col * 3 + 3):
                        if (r, c) in given:
                            present.append(board[r][c])
                        else:
                            free_cells.append((r, c))

                # preenche o 3x3 com os numeros que faltam
                missing = []
                for num in range(1, 10):
                    if num not in present:
                        missing.append(num)

                random.shuffle(missing)

                for i in range(len(free_cells)):
                    r, c = free_cells[i]
                    board[r][c] = missing[i]

        return board

    def solve(self, sudoku, metrics=None, tree=None, max_depth=100):
        original = sudoku.board
        given = set()
        for r in range(9):
            for c in range(9):
                if original[r][c] != 0:
                    given.add((r, c))

        if metrics:
            metrics.reset()
            metrics.start()

        solved = False
        board  = [row[:] for row in original]

        for restart in range(100):
            board = self._fill_boxes(original, given)
            conflicts = self._count_conflicts(board)

            print(f"Restart {restart + 1}: {conflicts} conflitos")

            if metrics:
                metrics.score_history.append(conflicts)

            for iteration in range(1000):
                if conflicts == 0:
                    solved = True
                    break

                improved = False

                for box_row in range(3):
                    for box_col in range(3):
                        # pega as celulas vazias do 3x3
                        free_cells = []
                        for r in range(box_row * 3, box_row * 3 + 3):
                            for c in range(box_col * 3, box_col * 3 + 3):
                                if (r, c) not in given:
                                    free_cells.append((r, c))

                        for i in range(len(free_cells)):
                            for j in range(i + 1, len(free_cells)):
                                r1, c1 = free_cells[i]
                                r2, c2 = free_cells[j]

                                # tenta trocar duas celulas livres
                                board[r1][c1], board[r2][c2] = board[r2][c2], board[r1][c1]
                                new_conflicts = self._count_conflicts(board)

                                if new_conflicts < conflicts:
                                    conflicts = new_conflicts
                                    improved = True
                                    break

                                # desfaz a troca
                                board[r1][c1], board[r2][c2] = board[r2][c2], board[r1][c1]

                            if improved:
                                break
                        if improved:
                            break
                    if improved:
                        break

                if not improved:
                    # reinicia se nao mlhorar
                    break

                if metrics:
                    metrics.increment_states()
                    metrics.score_history.append(conflicts)

            if solved:
                break

        if metrics:
            metrics.stop()
            if solved:
                metrics.mark_success()
            else:
                metrics.mark_fail()

        if solved:
            print("Hill Climbing: resolvido!")
            sudoku.board = board
            return sudoku

        print("Hill Climbing: nao resolvido")
        return None

    def solve_steps(self, sudoku, metrics=None, tree=None, max_depth=100):
        original = sudoku.board
        given = set()
        for r in range(9):
            for c in range(9):
                if original[r][c] != 0:
                    given.add((r, c))

        if metrics:
            metrics.reset()
            metrics.start()

        solved = False

        for restart in range(100):
            board = self._fill_boxes(original, given)
            conflicts = self._count_conflicts(board)

            print(f"Restart {restart + 1}: {conflicts} conflitos")

            if metrics:
                metrics.score_history.append(conflicts)

            yield [row[:] for row in board]

            for iteration in range(1000):
                if conflicts == 0:
                    solved = True
                    break

                improved = False

                for box_row in range(3):
                    for box_col in range(3):
                        # pega as celulas vazias do 3x3
                        free_cells = []
                        for r in range(box_row * 3, box_row * 3 + 3):
                            for c in range(box_col * 3, box_col * 3 + 3):
                                if (r, c) not in given:
                                    free_cells.append((r, c))

                        for i in range(len(free_cells)):
                            for j in range(i + 1, len(free_cells)):
                                r1, c1 = free_cells[i]
                                r2, c2 = free_cells[j]

                                # tenta trocar duas celulas livres
                                board[r1][c1], board[r2][c2] = board[r2][c2], board[r1][c1]
                                new_conflicts = self._count_conflicts(board)

                                if new_conflicts < conflicts:
                                    conflicts = new_conflicts
                                    improved = True
                                    break

                                # desfaz a troca
                                board[r1][c1], board[r2][c2] = board[r2][c2], board[r1][c1]

                            if improved:
                                break
                        if improved:
                            break
                    if improved:
                        break

                if not improved:
                    break

                if metrics:
                    metrics.increment_states()
                    metrics.score_history.append(conflicts)

                yield [row[:] for row in board]

            if solved:
                break

        if metrics:
            metrics.stop()
            if solved:
                metrics.mark_success()
            else:
                metrics.mark_fail()
