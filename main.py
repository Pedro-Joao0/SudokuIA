from Ambiente.sudoku import Sudoku
from Interface.game import SudokuGUI

sudoku = Sudoku()

gui = SudokuGUI(sudoku)

gui.run()
