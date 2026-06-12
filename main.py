from ambiente.sudoku import Sudoku
from interface.game import SudokuGUI

sudoku = Sudoku()

gui = SudokuGUI(sudoku)

gui.run()
