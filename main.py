from dataclasses import dataclass
import random
import sys
from typing import List, Tuple


def can_place(board, row, col, num: int):
    """Checks if placing num at board[row][col] is valid."""
    for i in range(9):
        if board[row][i] == str(num) or board[i][col] == str(num):
            return False
    start_row, start_col = (row // 3) * 3, (col // 3) * 3
    for i in range(start_row, start_row + 3):
        for j in range(start_col, start_col + 3):
            if board[i][j] == str(num):
                return False
    return True


def solve_sudoku(board):
    """Solves the Sudoku board using a backtracking approach."""
    for row in range(9):
        for col in range(9):
            if board[row][col] == ".":
                for num in range(1, 10):
                    if can_place(board, row, col, num):
                        board[row][col] = str(num)
                        if solve_sudoku(board):
                            return True
                        board[row][col] = "."
                return False
    return True


def get_board_display(board, current_cell: Tuple[int, int]):
    """
    From the board state, create a string that formats everything nicely

    current_cell: The cell the user is currently guessing for
    """
    R, C = len(board), len(board[0])
    board_str = " _________________________\n"

    for i in range(R):
        row_str = ""
        if i > 0 and i % 3 == 0:
            board_str += " -------------------------\n"

        for j in range(C):
            if j % 3 == 0:
                row_str += f" |"
            if i == current_cell[0] and j == current_cell[1]:
                row_str += f"{ANSIEscapeSequences.TEXT_RED_BOLD}"
                row_str += " _"
                row_str += f"{ANSIEscapeSequences.TEXT_BASE}"
            else:
                row_str += f" {board[i][j]}"
        row_str += " | \n"
        board_str += row_str

    board_str += " -------------------------\n"

    return board_str


@dataclass
class SudokuBoardArguments:
    """Object used to store"""

    # The higher the difficulty, the more cells we will remove from the generated board
    difficulty: int


MIN_DIFFICULTY = 10
MAX_DIFFICULTY = 60


def validate_sudoku_args(args: SudokuBoardArguments):
    """
    Validates a set of arguments passed to the generate_sudoku function.

    If any invalid parameters were passed, we will update the SudokuBoardArguments object by reference
    """

    # Check if we were passed an integer
    if type(args.difficulty) != type(1):
        print(
            f"Invalid difficulty value {args.difficulty}. We will use a default difficulty of {MIN_DIFFICULTY + (MAX_DIFFICULTY-MIN_DIFFICULTY)//2}"
        )
        args.difficulty = MIN_DIFFICULTY + (MAX_DIFFICULTY - MIN_DIFFICULTY) // 2

    elif args.difficulty < MIN_DIFFICULTY:
        print(
            f"A difficulty of {args.difficulty} was passed, which is less than the minimum of {MIN_DIFFICULTY}. Automatically updating difficulty to {MIN_DIFFICULTY}."
        )
        args.difficulty = MIN_DIFFICULTY
    elif args.difficulty > MAX_DIFFICULTY:
        print(
            f"A difficulty of {args.difficulty} was passed, which is greater than the maximum of {MAX_DIFFICULTY}. Automatically updating difficulty to {MAX_DIFFICULTY}."
        )
        args.difficulty = MAX_DIFFICULTY


def randomize_board(board):
    """
    Due to how we generate the solutions for the board, each board will initially have
    the same numbers in every cell. For instance board[0][0] will always be 1 if it exists,
    and you could solve the board by placing 1 there if it doesnt.

    This function will simply map all occurances of a value x in the board, to some other value in
    the interval [1,9]. This will not impact the solvability of the board.
    """

    # Initialize a hashmap to store the correct conversions for a number x->y
    convert = {
        "1": None,
        "2": None,
        "3": None,
        "4": None,
        "5": None,
        "6": None,
        "7": None,
        "8": None,
        "9": None,
    }

    # Initialize a set to store the characters which we can remap numbers to
    remapable_nums = set(["1", "2", "3", "4", "5", "6", "7", "8", "9"])

    # set to store numbers which have already been used to remap another number
    for i in range(1, 10):
        # if the current num was already chosen as a remap target, cont
        if str(i) not in remapable_nums:
            continue

        # after choosing a number, remove i and the picked number from remapable nums
        map_to = random.choice(list(remapable_nums))
        remapable_nums.discard(map_to)
        remapable_nums.discard(str(i))

        # also remove i from remapable nums since we will map map_to to i
        convert[map_to] = str(i)
        convert[str(i)] = map_to

    for i in range(len(board)):
        for j in range(len(board[0])):
            # Only remap the value if this cell contains a number
            board[i][j] = convert[board[i][j]] if board[i][j] != "." else "."


def generate_sudoku(args: SudokuBoardArguments):
    """Generates a solvable Sudoku board."""

    # In order to guarantee our board is solvable, we will generate an empty board,
    # solve that empty board, then remove some cells from it.
    board = [["." for _ in range(9)] for _ in range(9)]
    solve_sudoku(board)

    # Validate passed arguments, updating them if invalid
    validate_sudoku_args(args)

    # Remove some cells to create a puzzle
    cells_to_remove = args.difficulty
    while cells_to_remove > 0:
        row = random.randint(0, 8)
        col = random.randint(0, 8)
        if board[row][col] != ".":
            board[row][col] = "."
            cells_to_remove -= 1
    return board


class ANSIEscapeSequences:
    """
    Storing ANSI escape sequences here for convenience
    """

    TEXT_RED_BOLD = "\x1b[1;31m"
    TEXT_BASE = "\x1b[0m"


def swap_to_ansi(sequence: ANSIEscapeSequences):
    sys.stdout.write(sequence)


class TextUIComponent:
    def __init__(self, text: str, y_index: int = 0, x_index: int = 0):
        self.text = text
        self.y_index = y_index
        self.x_index = x_index


class UIBuffer:
    _instance = None
    components: List[TextUIComponent] = []
    _previous_lines = 0

    def __new__(cls):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    @staticmethod
    def draw():
        # sort the UI components by y_index first
        UIBuffer.sort_by_y_index()
        # render all the components to a string
        text = UIBuffer.render_to_string()

        # clear only the number of lines used by the previous output
        UIBuffer.clear_previous_output()

        # print the new UI content
        print(text, end="")

        # track the number of lines in the current output for the next draw call
        UIBuffer._previous_lines = text.count("\n") + 1

        # clear the components in the buffer
        UIBuffer.clear()

    @staticmethod
    def add(component: TextUIComponent):
        UIBuffer.components.append(component)

    @staticmethod
    def remove(component: TextUIComponent):
        UIBuffer.components.remove(component)

    @staticmethod
    def sort_by_y_index():
        UIBuffer.components.sort(key=lambda component: component.y_index)

    @staticmethod
    def clear():
        UIBuffer.components.clear()

    @staticmethod
    def render_to_string() -> str:
        """
        Note: explicitly call UIBuffer.sort_by_y_index() before rendering to string
        """
        comps_text = [component.text for component in UIBuffer.components]
        return "".join(comps_text)

    @staticmethod
    def clear_previous_output():
        # move the cursor up by the number of lines in the previous output and clear them
        if UIBuffer._previous_lines > 0:
            sys.stdout.write("\x1b[{}F".format(UIBuffer._previous_lines))  # Move up
            sys.stdout.write("\x1b[J")  # Clear from cursor to end of screen
            sys.stdout.flush()


def generate_hint(number: int) -> str:
    # Ensure the number is positive
    number = abs(number)

    # Generate random coefficients a and b
    a = random.randint(1, 10)  # Adjust the range as needed
    b = random.randint(-10, 10)  # Adjust the range as needed

    # disallow 0
    if b == 0:
        b += 1

    # Calculate c to ensure the equation has a solution
    c = a * number + b

    op = "+" if b >= 1 else "-"

    # Construct the equation string
    equation = f"{a if a > 1 else ''}x {op} {abs(b)} = {c}"

    # Construct the hint text
    hint_text = f"HINT - Solve for x: {equation}"

    return hint_text


def play_game(args: SudokuBoardArguments):
    board = generate_sudoku(args)

    randomize_board(board)

    for i in range(len(board)):
        for j in range(len(board[0])):
            # we update the cell to _ to indicate what cell we are selecting for
            while board[i][j] == "." or board[i][j] == "_":
                board[i][j] = "_"
                candidate = None

                board_component = TextUIComponent(get_board_display(board, (i, j)), 0)
                dialog_component = TextUIComponent(
                    f"What number should we place at {i}, {j} ?: ", 100
                )

                while not candidate:
                    UIBuffer.add(board_component)
                    UIBuffer.add(dialog_component)
                    UIBuffer.draw()
                    try:
                        _candidate = int(input())
                    except KeyboardInterrupt:
                        exit()
                    except ValueError:
                        # * this is a hack, manually incrementing the _newline_count to prevent incorrect inputs from
                        # * desync-ing the linecounts in our UIBuffer
                        UIBuffer._previous_lines += 1
                        continue
                    if _candidate <= 0 or _candidate >= 10:
                        UIBuffer.add(TextUIComponent("Invalid input", 5))
                        continue
                    else:
                        candidate = _candidate

                if can_place(board, i, j, candidate):
                    board[i][j] = str(candidate)
                else:
                    is_solvable = 0
                    for num in range(1, 10):
                        if can_place(board, i, j, num):

                            hint_component = TextUIComponent(
                                f"{generate_hint(num)}\n", 2
                            )
                            UIBuffer.add(hint_component)
                            is_solvable = True
                            break
                    if not is_solvable:
                        print("You lost!")
                        exit()

    print("\x1b[2J")  # Clear the screen
    print(get_board_display(board, (i, j)), end="")
    print("\nYou won!")


play_game(SudokuBoardArguments(15))
