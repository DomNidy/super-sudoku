from dataclasses import dataclass
import random
import sys
from typing import List, Tuple
from math import log2


MIN_DIFFICULTY = 1
MAX_DIFFICULTY = 60


class ANSIEscapeSequences:
    """
    Storing ANSI escape sequences here for convenience
    """

    RESET = "\x1b[0m"
    BACKGROUND_GREEN = "\x1b[48;5;22m"
    BACKGROUND_RED = "\x1b[48;5;196m"
    BACKGROUND_BLUE = "\x1b[48;5;18m"
    BACKGROUND_WHITE = "\x1b[48;5;253m"
    FOREGROUND_YELLOW = "\x1b[38;5;226m"
    FOREGROUND_BLUE = "\x1b[38;5;36m"
    FOREGROUND_DARKBLUE = "\x1b[38;5;17m"
    FOREGROUND_WHITE = "\x1b[38;5;253m"
    FOREGROUND_WHITER = "\x1b[38;5;255m"
    ITALIC = "\x1b[3m"


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


def get_board_display(board, current_cell: Tuple[int, int] | None = None):
    """
    From the board state, create a string that formats everything nicely

    current_cell: The cell the user is currently guessing for, if none, no highlighting will be done
    """
    R, C = len(board), len(board[0])
    board_str = f"{ANSIEscapeSequences.RESET} _________________________\n"

    for i in range(R):
        row_str = f"{ANSIEscapeSequences.RESET}"

        if i > 0 and i % 3 == 0:

            board_str += f" -------------------------\n"

        for j in range(C):
            if j % 3 == 0:
                row_str += f" |"
            if current_cell and i == current_cell[0] and j == current_cell[1]:
                row_str += f" {ANSIEscapeSequences.BACKGROUND_WHITE}{ANSIEscapeSequences.FOREGROUND_BLUE}"
                row_str += "_"
                row_str += f"{ANSIEscapeSequences.RESET}"
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
    hint_text = f"{ANSIEscapeSequences.ITALIC}{ANSIEscapeSequences.FOREGROUND_BLUE}HINT{ANSIEscapeSequences.RESET} - Solve for x: {equation}"

    return hint_text


def play_game(ctx: "SudokuContext", args: SudokuBoardArguments):
    board = generate_sudoku(args)
    guess_count = 0

    randomize_board(board)

    for i in range(len(board)):
        for j in range(len(board[0])):
            # we update the cell to _ to indicate what cell we are selecting for
            while board[i][j] == "." or board[i][j] == "_":
                board[i][j] = "_"
                candidate = None

                header_component = TextUIComponent(
                    f"{ANSIEscapeSequences.BACKGROUND_BLUE}{ANSIEscapeSequences.FOREGROUND_YELLOW}---=== SUPER SUDOKU ===---{ANSIEscapeSequences.RESET}\n"
                )
                signature_component = TextUIComponent(
                    f"     {ANSIEscapeSequences.ITALIC}by Dominic Nidy{ANSIEscapeSequences.RESET}\n"
                )
                board_component = TextUIComponent(get_board_display(board, (i, j)), 0)
                dialog_component = TextUIComponent(
                    f"What number should we place at {i}, {j} ?: ",
                    100,
                )

                while not candidate:
                    UIBuffer.add(header_component)
                    UIBuffer.add(signature_component)
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
                        UIBuffer.add(
                            TextUIComponent(
                                f"{ANSIEscapeSequences.BACKGROUND_RED}Invalid input{ANSIEscapeSequences.RESET} ",
                                5,
                            )
                        )
                        continue
                    if _candidate <= 0 or _candidate >= 10:
                        UIBuffer.add(
                            TextUIComponent(
                                f"{ANSIEscapeSequences.BACKGROUND_RED}Invalid input{ANSIEscapeSequences.RESET} ",
                                5,
                            )
                        )
                        continue
                    else:
                        candidate = _candidate
                        guess_count += 1

                if can_place(board, i, j, candidate):
                    board[i][j] = str(candidate)
                else:
                    is_solvable = 0
                    for num in range(1, 10):
                        if can_place(board, i, j, num):

                            hint_component = TextUIComponent(
                                f"{generate_hint(num)}\n", 2
                            )
                            UIBuffer.add(
                                TextUIComponent(
                                    f"{ANSIEscapeSequences.BACKGROUND_RED}WRONG{ANSIEscapeSequences.RESET} ",
                                    5,
                                )
                            )
                            UIBuffer.add(hint_component)
                            is_solvable = True
                            break
                    if not is_solvable:
                        print(
                            f"\n{ANSIEscapeSequences.BACKGROUND_RED}You lost!{ANSIEscapeSequences.RESET}"
                        )
                        print(
                            f"{ANSIEscapeSequences.ITALIC}Why? One of your moves made the board unsolvable. In {ANSIEscapeSequences.BACKGROUND_BLUE}{ANSIEscapeSequences.FOREGROUND_YELLOW}SUPER SUDOKU{ANSIEscapeSequences.RESET}, you\n{ANSIEscapeSequences.ITALIC}cannot undo previous moves."
                        )
                        input("Press enter to continue...")
                        return -1

    score = SudokuScore(guess_count, args.difficulty)
    ctx.add_score(score)

    UIBuffer.add(header_component)
    UIBuffer.add(TextUIComponent(get_board_display(board)))
    UIBuffer.add(
        TextUIComponent(
            f"\n{ANSIEscapeSequences.RESET}{ANSIEscapeSequences.BACKGROUND_GREEN}{ANSIEscapeSequences.FOREGROUND_WHITE}You won!\n{ANSIEscapeSequences.RESET}",
            2,
        )
    )
    UIBuffer.add(
        TextUIComponent(
            f"\nSCORE: {score}\n",
            2,
        )
    )
    UIBuffer.draw()
    input("Press enter to continue...")


class SudokuScore:
    def __init__(self, guess_count: int, difficulty: int):
        assert difficulty != 0, "An error occured, invalid difficulty of 0"
        self.guess_count = guess_count
        self.difficulty = difficulty

        self.score = difficulty**2 * (81 - min(80, guess_count)) / max(1, difficulty)
        self.score /= 15
        self.score = int(self.score)

    def __lt__(self, other: "SudokuScore"):
        return self.score >= other.score

    def __str__(self) -> str:
        return f"{ANSIEscapeSequences.FOREGROUND_WHITER}{self.score}{ANSIEscapeSequences.RESET} {ANSIEscapeSequences.ITALIC}(with {self.guess_count} guess(es) and difficulty of {self.difficulty}){ANSIEscapeSequences.RESET}"


class SudokuContext:
    def __init__(self) -> None:
        self.scores: List[SudokuScore] = []

    def add_score(self, score: SudokuScore):
        assert isinstance(
            score, SudokuScore
        ), "Runtime error occured, this is likely a bug. Sorry :P"
        self.scores.append(score)

    def has_scores(self) -> bool:
        return len(self.scores) > 0


def display_menu(ctx: SudokuContext) -> SudokuBoardArguments:
    header_component = TextUIComponent(
        f"{ANSIEscapeSequences.BACKGROUND_BLUE}{ANSIEscapeSequences.FOREGROUND_YELLOW}---=== SUPER SUDOKU ===---{ANSIEscapeSequences.RESET}\n",
        0,
    )
    signature_component = TextUIComponent(
        f"     {ANSIEscapeSequences.ITALIC}by Dominic Nidy{ANSIEscapeSequences.RESET}\n",
        1,
    )
    options_dialog_component = TextUIComponent(
        f"\n\nSelect difficulty level ({MIN_DIFFICULTY}-{MAX_DIFFICULTY}): ", 100
    )

    sudoku_options = None
    while not sudoku_options:
        UIBuffer.add(header_component)
        UIBuffer.add(signature_component)
        UIBuffer.add(options_dialog_component)
        if ctx.has_scores():
            ctx.scores.sort()
            scores = "\n".join(
                [f" {i+1}. {ctx.scores[i]}" for i in range(len(ctx.scores))]
            )
            UIBuffer.add(
                TextUIComponent(
                    f"\n{ANSIEscapeSequences.BACKGROUND_WHITE}{ANSIEscapeSequences.FOREGROUND_DARKBLUE}Scores:{ANSIEscapeSequences.RESET}\n{scores}\n",
                    2,
                )
            )
        else:
            UIBuffer.add(
                TextUIComponent(
                    f"\n{ANSIEscapeSequences.ITALIC}Play some games to see your scores!{ANSIEscapeSequences.RESET}\n",
                    2,
                )
            )
        UIBuffer.draw()

        try:
            _difficulty = int(input())

            if _difficulty < MIN_DIFFICULTY or _difficulty > MAX_DIFFICULTY:
                UIBuffer.add(
                    TextUIComponent(
                        f"{ANSIEscapeSequences.BACKGROUND_RED}Invalid input{ANSIEscapeSequences.RESET} ",
                        5,
                    )
                )
                continue
            else:
                sudoku_options = SudokuBoardArguments(_difficulty)
        except KeyboardInterrupt:
            exit()
        except ValueError:
            # * this is a hack, manually incrementing the _newline_count to prevent incorrect inputs from
            # * desync-ing the linecounts in our UIBuffer
            UIBuffer.add(
                TextUIComponent(
                    f"\n{ANSIEscapeSequences.BACKGROUND_RED}Invalid input{ANSIEscapeSequences.RESET} ",
                    5,
                )
            )
    return sudoku_options


if __name__ == "__main__":
    # Context object used to store state, things like scores
    ctx = SudokuContext()
 
    while 1:
        sudoku_options = display_menu(ctx)
        play_game(ctx, sudoku_options)
