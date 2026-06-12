import pygame
from metricas.metrics import Metrics
from agente.dfs import DFSAgent
from agente.astar import AStarAgent
from agente.hill_climbing import HillClimbingAgent

from metricas.search_tree import SearchTree, SearchNode

# ── layout ────────────────────────────────────────────────────────────────
BOARD_W  = 540
BOARD_H  = 540
CELL     = 60
CTRL_H   = 160
PANEL_W  = 480
GAP      = 20
WIN_W    = BOARD_W + GAP + PANEL_W
WIN_H    = BOARD_H + CTRL_H

# ── palette (monochrome only) ─────────────────────────────────────────────
WHITE = (255, 255, 255)
BLACK = (0,   0,   0)
LGRAY = (210, 210, 210)
MGRAY = (150, 150, 150)

ALGOS = ["DFS", "A*", "HC"]


# ─────────────────────────────────────────────────────────────────────────
class DepthInput:
    """Single-line numeric text input."""

    def __init__(self, rect, font):
        self.rect    = rect
        self.font    = font
        self.text    = "20"
        self.focused = False

    def handle_event(self, ev):
        if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
            self.focused = self.rect.collidepoint(ev.pos)
        if self.focused and ev.type == pygame.KEYDOWN:
            if ev.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif ev.unicode.isdigit() and len(self.text) < 3:
                self.text += ev.unicode

    @property
    def value(self):
        return max(1, int(self.text)) if self.text else 1

    def draw(self, surf):
        pygame.draw.rect(surf, WHITE, self.rect)
        pygame.draw.rect(surf, BLACK, self.rect, 2 if self.focused else 1)
        t = self.font.render(self.text or "0", True, BLACK)
        surf.blit(t, t.get_rect(center=self.rect.center))


# ─────────────────────────────────────────────────────────────────────────
class TreePanel:
    """Scrollable, collapsible search-tree view."""

    ROW_H   = 21
    INDENT  = 14
    CHEV_W  = 14
    TITLE_H = 28

    def __init__(self, rect, font):
        self.rect        = rect
        self.font        = font
        self.tree        = None
        self.scroll      = 0
        self._flat       = []
        self._chev_rects = {}

    def set_tree(self, tree):
        self.tree   = tree
        self.scroll = 0

    def handle_click(self, pos):
        for nid, rect in self._chev_rects.items():
            if rect.collidepoint(pos):
                node = next((n for n, _ in self._flat if id(n) == nid), None)
                if node:
                    node.collapsed = not node.collapsed
                return

    def handle_scroll(self, ev):
        if self.rect.collidepoint(pygame.mouse.get_pos()):
            self.scroll = max(0, self.scroll - ev.y * self.ROW_H * 3)

    def _flatten(self, node, indent, max_depth, out):
        out.append((node, indent))
        if not node.collapsed and indent < max_depth:
            for child in node.children:
                self._flatten(child, indent + 1, max_depth, out)

    def draw(self, surf, max_depth):
        self._flat       = []
        self._chev_rects = {}

        pygame.draw.rect(surf, WHITE, self.rect)
        pygame.draw.rect(surf, BLACK, self.rect, 1)

        # title bar
        title_bar = pygame.Rect(self.rect.x, self.rect.y, self.rect.w, self.TITLE_H)
        pygame.draw.rect(surf, LGRAY, title_bar)
        pygame.draw.line(surf, BLACK,
                         (self.rect.x, self.rect.y + self.TITLE_H),
                         (self.rect.right, self.rect.y + self.TITLE_H), 1)
        t = self.font.render("Árvore de Busca", True, BLACK)
        surf.blit(t, (self.rect.x + 8, self.rect.y + 6))

        # content clip region
        content_y = self.rect.y + self.TITLE_H + 2
        clip = pygame.Rect(self.rect.x + 1, content_y,
                           self.rect.w - 2, self.rect.h - self.TITLE_H - 2)
        surf.set_clip(clip)

        if self.tree is None:
            pass
        else:
            self._flatten(self.tree.root, 0, max_depth, self._flat)

            for i, (node, indent) in enumerate(self._flat):
                y = content_y + i * self.ROW_H - self.scroll
                if y + self.ROW_H < clip.top or y > clip.bottom:
                    continue

                x = self.rect.x + 6 + indent * self.INDENT

                if node.children:
                    chev = "▶" if node.collapsed else "▼"
                    ct   = self.font.render(chev, True, BLACK)
                    cr   = ct.get_rect(topleft=(x, y + 2))
                    surf.blit(ct, cr)
                    self._chev_rects[id(node)] = cr.inflate(8, 4)
                else:
                    dot = self.font.render("·", True, MGRAY)
                    surf.blit(dot, (x + 2, y + 2))

                lbl = self.font.render(node.label(), True, BLACK)
                surf.blit(lbl, (x + self.CHEV_W, y + 2))

        surf.set_clip(None)


# ─────────────────────────────────────────────────────────────────────────
class SudokuGUI:

    def __init__(self, sudoku):
        pygame.init()

        self.screen = pygame.display.set_mode((WIN_W, WIN_H))
        pygame.display.set_caption("Sudoku Solver IA")

        self.num_font = pygame.font.SysFont("arial", 34)
        self.num_bold = pygame.font.SysFont("arial", 34, bold=True)
        self.ui_font  = pygame.font.SysFont("arial", 15)
        self.lbl_font = pygame.font.SysFont("arial", 13)

        self.sudoku   = sudoku
        self.original = self._copy(sudoku)

        self.given = getattr(sudoku, 'given', {
            (r, c)
            for r in range(9) for c in range(9)
            if sudoku.board[r][c] != 0
        })

        self.agents = {
            "DFS": DFSAgent(),
            "A*":  AStarAgent(),
            "HC":  HillClimbingAgent(),
        }

        self.metrics      = Metrics()
        self.result_board = None
        self.current_algo = "DFS"
        self.solved       = False
        self.btn_rects    = {}

        panel_rect = pygame.Rect(BOARD_W + GAP, 0, PANEL_W, WIN_H)
        self.tree_panel = TreePanel(panel_rect, self.ui_font)

        self.depth_input = DepthInput(
            pygame.Rect(108, BOARD_H + 52, 52, 22),
            self.ui_font
        )

    # ── helpers ───────────────────────────────────────────────────────────

    def _copy(self, sudoku):
        if hasattr(sudoku, 'copy'):
            return sudoku.copy()
        import copy as _c
        return _c.deepcopy(sudoku)

    # ── drawing ───────────────────────────────────────────────────────────

    def _draw_board(self):
        pygame.draw.rect(self.screen, WHITE, (0, 0, BOARD_W, BOARD_H))
        for i in range(10):
            w = 3 if i % 3 == 0 else 1
            pygame.draw.line(self.screen, BLACK, (0, i*CELL), (BOARD_W, i*CELL), w)
            pygame.draw.line(self.screen, BLACK, (i*CELL, 0), (i*CELL, BOARD_H), w)

    def _draw_numbers(self):
        board = self.sudoku.board
        for r in range(9):
            for c in range(9):
                gv = board[r][c]
                sv = self.result_board.board[r][c] if self.result_board else 0
                d  = gv if gv != 0 else sv
                if d == 0:
                    continue
                fnt = self.num_bold if (r, c) in self.given else self.num_font
                t   = fnt.render(str(d), True, BLACK)
                self.screen.blit(t, t.get_rect(center=(c*CELL + CELL//2, r*CELL + CELL//2)))

    def _draw_controls(self):
        pygame.draw.rect(self.screen, WHITE, (0, BOARD_H, BOARD_W, CTRL_H))
        pygame.draw.line(self.screen, BLACK, (0, BOARD_H), (BOARD_W, BOARD_H), 2)

        self.btn_rects = {}

        # row 1 — algorithm
        y = BOARD_H + 18
        self.screen.blit(self.lbl_font.render("Algoritmo:", True, BLACK), (12, y + 4))
        for i, name in enumerate(ALGOS):
            r = pygame.Rect(108 + i * 76, y, 68, 24)
            self.btn_rects[name] = r
            sel = self.current_algo == name
            pygame.draw.rect(self.screen, BLACK if sel else WHITE, r)
            pygame.draw.rect(self.screen, BLACK, r, 1)
            t = self.ui_font.render(name, True, WHITE if sel else BLACK)
            self.screen.blit(t, t.get_rect(center=r.center))

        # row 2 — max depth
        y = BOARD_H + 52
        self.screen.blit(self.lbl_font.render("Prof. máx:", True, BLACK), (12, y + 4))
        self.depth_input.rect = pygame.Rect(108, y, 52, 22)
        self.depth_input.draw(self.screen)

        # row 3 — actions
        y = BOARD_H + 88
        for label, rx, enabled in [
            ("Resolver",   12,  True),
            ("Reiniciar",   100, True),
        ]:
            r = pygame.Rect(rx, y, 80, 24)
            self.btn_rects[label] = r
            col = BLACK if enabled else LGRAY
            pygame.draw.rect(self.screen, WHITE, r)
            pygame.draw.rect(self.screen, col, r, 1)
            t = self.ui_font.render(label, True, col)
            self.screen.blit(t, t.get_rect(center=r.center))

        # row 4 — metrics
        if self.metrics.execution_time > 0 or self.metrics.states_explored > 0:
            status = "Resolvido" if self.solved else "Falhou"
            info   = (f"Tempo: {self.metrics.execution_time:.4f}s  |  "
                      f"Estados: {self.metrics.states_explored}  |  {status}")
            self.screen.blit(self.lbl_font.render(info, True, BLACK), (12, BOARD_H + 126))

    # ── interaction ───────────────────────────────────────────────────────

    def _handle_click(self, pos):
        for label, rect in self.btn_rects.items():
            if rect.collidepoint(pos):
                if label in ALGOS:
                    self.current_algo = label
                elif label == "Resolver":
                    self._run_solve()
                elif label == "Reiniciar":
                    self._reset()
                return
        self.tree_panel.handle_click(pos)

    def _run_solve(self):
        board        = self._copy(self.original)
        self.metrics = Metrics()
        agent        = self.agents[self.current_algo]
        tree         = SearchTree()

        try:
            result = agent.solve(board, self.metrics, tree, self.depth_input.value)
        except TypeError:
            try:
                result = agent.solve(board, self.metrics)
            except TypeError:
                result = agent.solve(board)

        self.tree_panel.set_tree(tree)
        tree.root.collapsed = False

        if result is not None:
            self.result_board = result
            self.solved       = True
        else:
            self.result_board = None
            self.solved       = False

    def _reset(self):
        self.sudoku       = self._copy(self.original)
        self.result_board = None
        self.solved       = False
        self.metrics      = Metrics()
        self.tree_panel.set_tree(None)

    # ── main loop ─────────────────────────────────────────────────────────

    def run(self):
        clock   = pygame.time.Clock()
        running = True

        while running:
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT:
                    running = False
                elif ev.type == pygame.MOUSEBUTTONDOWN:
                    self._handle_click(ev.pos)
                    self.depth_input.handle_event(ev)
                elif ev.type == pygame.KEYDOWN:
                    self.depth_input.handle_event(ev)
                elif ev.type == pygame.MOUSEWHEEL:
                    self.tree_panel.handle_scroll(ev)

            self.screen.fill(WHITE)
            self._draw_board()
            self._draw_numbers()
            self._draw_controls()
            self.tree_panel.draw(self.screen, self.depth_input.value)
            pygame.display.update()
            clock.tick(60)

        pygame.quit()