import tkinter as tk  # import tkinter as tk (abbreviation) to bring modules name to current namespace
from tkinter import font  # font for gameplay design
from typing import NamedTuple
from itertools import cycle


# Define player class. label will store player signs X or O, color will store color of player signs.
class Player(NamedTuple):
    label: str
    color: str


# Define move class. row and col store coordinates that identifies players move. Label will hold player signs, however
# label defaults to empty string because player move has not been specified yet.
class Move(NamedTuple):
    row: int
    col: int
    label: str = ""


# 3 by 3 grid
BOARD_SIZE = 3
DEFAULT_PLAYERS = (
    Player(label="X", color="blue"),
    Player(label="O", color="green")
)


# Define TTTGame class initialize with two arguments players (tuple representing X and 0) and board_size.
class TicTacToeGame:
    def __init__(self, players=DEFAULT_PLAYERS, board_size=BOARD_SIZE):
        self._players = cycle(players)  # cyclical iterator over the input tuple of players
        self.board_size = board_size
        self.current_player = next(self._players)
        self.winner_combo = []  # Combination of cells that defines a winner
        self._current_moves = []  # List of player's moves in a given game.
        self._has_winner = False
        self._winning_combos = []  # List containing the cell combinations that define a win
        self._setup_board()

    # To keep track of every move on board use ._current_moves, which you'll update whenever makes a move
    # ._winning_combos to store winning combinations
    def _setup_board(self):
        self._current_moves = [
            [Move(row, col) for col in range(self.board_size)]
            for row in range(self.board_size)
        ]
        self._winning_combos = self._get_winning_combos()

    # Iterate over the rows on the grid, getting the coordinates of every cell and building a sublist of coordinates.
    # Each sublist of coordinates represents a winning combination.
    # Create sublist containing coordinates of each cell in the grid columns. Do same for 1st and 2nd diagonal.
    # Return list of lists containing all possible winning combos.
    def _get_winning_combos(self):
        rows = [
            [(move.row, move.col) for move in row]
            for row in self._current_moves  # main input for this method
        ]
        columns = [list(col) for col in zip(*rows)]
        first_diagonal = [row[i] for i, row in enumerate(rows)]
        second_diagonal = [col[j] for j, col in enumerate(reversed(columns))]
        return rows + columns + [first_diagonal, second_diagonal]

    # Define is_valid_move to take a move object as an argument
    # get coordinates from move input and assign to row, col
    # Check if move is valid, as in if the selected cell has not been selected by other player.
    # check is game doesn't have a winner yet
    # return boolean value if no winner yet and selected cell is empty (untouched by other player)
    def is_valid_move(self, move):
        row, col = move.row, move.col
        move_was_not_played = self._current_moves[row][col].label == ""
        no_winner = not self._has_winner
        return no_winner and move_was_not_played

    # Define process_move which takes move object as an argument
    # Get .row and .col coordinates from move input
    # assign inputted moves to the item [row][col] in the list of current moves.
    # start loop over the winning combos and retrieve all the labels from the moves in the current winning combination.
    # The result is then converted into a set object.
    # Store in variable is_win a boolean expression that determines if current move is a win or not.
    # Check content of is_win. if variable holds True the ._has_winner is set to True and function terminates.
    def process_move(self, move):
        row, col = move.row, move.col
        self._current_moves[row][col] = move
        for combo in self._winning_combos:
            results = set(self._current_moves[n][m].label for n, m in combo)
            is_win = (len(results) == 1) and ("" not in results)
            if is_win:
                self._has_winner = True
                self.winner_combo = combo
                break

    # Define method to return boolean value stored in ._has_winner to check if current match has winner or not
    def has_winner(self):
        return self._has_winner

    # Define method to check if all moves have been played and there is no winner i.e. DRAW
    # Use all() function to check if all the moves in ._current_moves have a label different from the empty string.
    # If so then all cells have been played.
    def is_tied(self):
        no_winner = not self._has_winner
        played_moves = (
            move.label for row in self._current_moves for move in row
        )
        return no_winner and all(played_moves)

    # Define method to toggle between players after each move.
    # Call next() on iterator self._player to allow next player to make move after each turn
    def toggle_player(self):
        self.current_player = next(self._players)

    # Define reset game function.
    # Create for loop to reset all current moves to an empty move object.
    # set winner to false and empty winner combo list.
    def reset_game(self):
        for row, row_content in enumerate(self._current_moves):
            for col, _ in enumerate(row_content):
                row_content[col] = Move(row, col)
        self._has_winner = False
        self.winner_combo = []


# class TTT inherits from Tk to create GUI window where game will be played.
# Call super() function to initialise parent class.
# self.title defines the text to show on the window's title bar.
# _cells (non-public) hold empty dict which will map the cells on the game board made up of rows and columns.
class TicTacToeBoard(tk.Tk):
    def __init__(self, game):
        super().__init__()
        self.title("Tic-Tac-Toe Game")
        self._cells = {}
        self._game = game  # inject game logic into initializer. Full access to game logic from game-board
        self._create_menu()  # inject main menu into game board.
        self._create_board_display()
        self._create_board_grid()

    # Define menu function.
    # Create menu_bar variable that will contain instance of a menu.
    # Config menu bar object as main menu of current Tkinter window.
    # Create another instance if menu to provide file menu.
    # add command play again to file menu and set to reset_board method.
    # add exit command
    def _create_menu(self):
        menu_bar = tk.Menu(master=self)
        self.config(menu=menu_bar)
        file_menu = tk.Menu(master=menu_bar)
        file_menu.add_command(label="Play Again", command=self.reset_board)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=quit)
        menu_bar.add_cascade(label="File", menu=file_menu)

    # Call reset_game function.
    # Update board display to hold initial text "ready?"
    # Create for loop over buttons on board.
    # Restore every button highlight background, text and fg to their initial state.
    def reset_board(self):
        self._game.reset_game()
        self._update_display(msg="Ready?")
        for button in self._cells.keys():
            button.config(highlightbackground="lightblue")
            button.config(text="")
            button.config(fg="black")

    # Create frame object to hold game display. master=self meaning main window will be frame's parent
    # .pack() geometry manager to place frame object on the main window's top border.
    # fill=tk.X ensures frame auto resize
    # Create label object inside frame object and the label should display 'are you ready' text
    # pack display label inside frame using geometry manager .pack().
    def _create_board_display(self):
        display_frame = tk.Frame(master=self)
        display_frame.pack(fill=tk.X)
        self.display = tk.Label(master=display_frame, text="Ready?", font=font.Font(size=28, weight="bold"), )
        self.display.pack()

    # .pack() geometry manager will place frame object on the main window.
    # Frame will occupy area under game display
    # Loop that iterates from 0-2 representing row coordinates of each cell in the grid.
    # Configure width and minsize.
    # loop over 3 column coordinates and create button object for every cell on the grid.
    # Add every new button to _cells dict. Buttons are keys and their values are coordinates expressed as (row, col)
    # Add every button to main window using .grid() geometry manager.
    def _create_board_grid(self):
        grid_frame = tk.Frame(master=self)
        grid_frame.pack()
        for row in range(self._game.board_size):  # inject game logic - allowing you to change board size
            self.rowconfigure(row, weight=1, minsize=50)
            self.columnconfigure(row, weight=1, minsize=75)
            for col in range(self._game.board_size):  # inject game logic - allowing you to change board size
                button = tk.Button(
                    master=grid_frame,
                    text="",
                    font=font.Font(size=36, weight="bold"),
                    fg="black",
                    width=3,
                    height=2,
                    highlightbackground="lightblue"
                )
                self._cells[button] = (row, col)
                button.bind("<ButtonPress-1>", self.play)  # Connect every button on game-board to .play() method
                button.grid(
                    row=row,
                    column=col,
                    padx=5,
                    pady=5,
                    sticky="nsew"
                )

    # Define method that processes the event of player selection of cell inside event loop.
    # Retrieve widget that triggered current event.
    # Unpack the clicked_btn coordinates into two local variables row and col.
    # Create new move object using the row, col and current players label as arguments.
    # If statement to check if the players move is valid or not. if valid, then if code block runs, otherwise nothing.
    # Update the clicked button by calling ._update_button() to display players label and color. Update everything else.
    def play(self, event):
        clicked_btn = event.widget
        row, col = self._cells[clicked_btn]
        move = Move(row, col, self._game.current_player.label)
        if self._game.is_valid_move(move):
            self._update_button(clicked_btn)
            self._game.process_move(move)
            if self._game.is_tied():
                self._update_display(msg="Tied Game!", color="red")
            elif self._game.has_winner():
                self._highlight_cells()
                msg = f'Player "{self._game.current_player.label}" won!'
                color = self._game.current_player.color
                self._update_display(msg, color)
            else:
                self._game.toggle_player()
                msg = f"{self._game.current_player.label}'s turn"
                self._update_display(msg)

    # Define update button method to call config on clicked button and assign text attribute and foreground color
    # to current players label and color.
    def _update_button(self, clicked_btn):
        clicked_btn.config(text=self._game.current_player.label)
        clicked_btn.config(fg=self._game.current_player.color)

    # Define update display to use dict-style subscript notation to tweak text and color of game display.
    def _update_display(self, msg, color="black"):
        self.display["text"] = msg
        self.display["fg"] = color

    # Define highlight cells to iterate over items in cells dict to highlight row of winning cell combination.
    def _highlight_cells(self):
        for button, coordinates in self._cells.items():
            if coordinates in self._game.winner_combo:
                button.config(highlightbackground="red")


# Define function for your game. Instantiate game then run its main loop by calling .mainloop
# Create game variable and assign to TicTacToeGame to handle game logic
# Create board variable to assign to TTTBoard(game) class constructor so game logic is injected into game board.
def main():
    game = TicTacToeGame()
    board = TicTacToeBoard(game)
    board.mainloop()


# Allows control over execution of code.
if __name__ == "__main__":
    main()
