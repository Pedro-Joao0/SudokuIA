import pygame

WIDTH = 540
HEIGHT = 600

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)


class SudokuGUI:

    def __init__(self, board):

        pygame.init()

        self.screen = pygame.display.set_mode(
            (WIDTH, HEIGHT)
        )

        pygame.display.set_caption(
            "Sudoku Solver IA"
        )

        self.board = board

    def draw_board(self):

        self.screen.fill(WHITE)

        for row in range(10):

            width = 4 if row % 3 == 0 else 1

            pygame.draw.line(
                self.screen,
                BLACK,
                (0, row * 60),
                (540, row * 60),
                width
            )

            pygame.draw.line(
                self.screen,
                BLACK,
                (row * 60, 0),
                (row * 60, 540),
                width
            )

    def run(self):

        running = True

        while running:

            for event in pygame.event.get():

                if event.type == pygame.QUIT:
                    running = False

            self.draw_board()

            pygame.display.update()

        pygame.quit()