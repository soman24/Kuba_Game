# Author: Soman Khan
# Date: 6/4/2021
# Description: Class that allows playing game called Kuba

class KubaGame:
  """Representation of an instance of Kuba."""

  # Mapping of directions to (row, column) offsets
  DIRECTIONS = {
      'F': (-1, 0),
      'R': (0, 1),
      'L': (0, -1),
      'B': (1, 0),
  }

  def __init__(self, player_one, player_two):
    """Create new instance of KubaGame with two player names and colors."""
    both_players = (player_one, player_two)

    # Validate both player name and color values
    for name, color in both_players:
      if not name:
        raise ValueError(f'Player name not valid: {name}')
      if color not in 'WB':
        raise ValueError(f'Player color not valid: {color}')

    # Ensure player colors are unique
    if player_one[1] == player_two[1]:
      raise ValueError(f'Player colors must be unique {player_one[1]}')

    # Create dictionaries for each player, remembering color and tracking
    # captured neutral marbles
    self._players_info = {
        name: {'color': color, 'captured': 0}
        for name, color in both_players
    }

    # Ensure player names are unique
    if len(self._players_info) != 2:
      raise ValueError(f'Player names must be unique: {player_one[0]}')

    # Initalize current, winner, board, and last board
    self._current = None
    self._winner = None
    self._board = [
        ['W', 'W', 'X', 'X', 'X', 'B', 'B'],
        ['W', 'W', 'X', 'R', 'X', 'B', 'B'],
        ['X', 'X', 'R', 'R', 'R', 'X', 'X'],
        ['X', 'R', 'R', 'R', 'R', 'R', 'X'],
        ['X', 'X', 'R', 'R', 'R', 'X', 'X'],
        ['B', 'B', 'X', 'R', 'X', 'W', 'W'],
        ['B', 'B', 'X', 'X', 'X', 'W', 'W']
    ]
    self._last_board = self._copy_board(self._board)

  def get_marble_count(self):
    """Get the count of white, black, and red marbles."""
    counts = [0, 0, 0]

    for row in self._board:
      for cell in row:
        # Don't count absent cells
        if cell == 'X':
          continue

        # Set index of cont based on marble color
        if cell == 'W':
          i = 0
        elif cell == 'B':
          i = 1
        else:
          i = 2
        # Increment counter at index
        counts[i] += 1

    # Return counts as tuple
    return tuple(counts)

  def get_captured(self, player_name):
    """Get the number of captured marbles for the provided player name."""
    # Return 0 if the player_name is not playing
    if player_name not in self._players_info:
      return 0

    return self._players_info[player_name]['captured']

  def get_current_turn(self):
    """Get the name of the players who turn is currently is."""
    return self._current

  def get_winner(self):
    """Get the name of the winning player."""
    return self._winner

  @staticmethod
  def _boards_equal(a, b):
    """Return if both provides boards are equal."""
    # Enumerate through all the rows and cells of the first, returning
    # False if any of the cells do not equal the cell at the same position
    # in the other board
    for r, row in enumerate(a):
      for c, cell in enumerate(row):
        if cell != b[r][c]:
          return False

    # Otherwise, return True
    return True

  @staticmethod
  def _copy_board(board):
    """Make a copy of the provided board."""
    # Initalized empty new board
    copy = []
    # Iterate over all the rows of the current board, appending copies to the
    # copy board
    for row in board:
      copy.append(row.copy())
    # Return the copy board
    return copy

  def _has_legal_move(self, marble):
    """Return if the provided marble has a single leval move available."""
    # Iterate through all the direction offsets
    for offset in self.DIRECTIONS.values():
      try:
        # If the marble in the currection direction is absent, or off-board,
        # return True
        if self.get_marble((
            marble[0] + offset[0],
            marble[1] + offset[1]
        )) == 'X':
          return True
      except IndexError:
        return True
    # Otherwise, return False
    return False

  def make_move(self, player_name, marble, direction):
    """Have the player move the provided board in the provided direction."""
    # Game already won
    if self._winner:
      return False

    # Invalid direction
    if direction not in self.DIRECTIONS:
      return False

    # Invalid player name
    if player_name not in self._players_info:
      return False

    info = self._players_info[player_name]

    current = self.get_current_turn()
    # Not the players turn
    if current is not None and current != player_name:
      return False

    # Invalid marble position
    try:
      marble_color = self.get_marble(marble)
    except IndexError:
      return False

    # Not moving own marble
    if marble_color != info['color']:
      return False

    offset = self.DIRECTIONS[direction]
    behind = marble[0] + -offset[0], marble[1] + -offset[1]
    try:
      behind_color = self.get_marble(behind)
      # Cell behind marble is not empty/off board
      if behind_color != 'X':
        return False
    except IndexError:
      pass

    # Collect all marbles in the direction until a absent marble, or the board
    # end is reached
    moving_marbles = [marble]
    while True:
      last_marble = moving_marbles[-1]
      current = last_marble[0] + offset[0], last_marble[1] + offset[1]
      try:
        current_color = self.get_marble(current)
        if current_color == 'X':
          break
        moving_marbles.append(current)
      except IndexError:
        break

    board_backup = self._copy_board(self._board)

    # Move each marble value to it's destination
    for moving in moving_marbles[::-1]:
      destination = moving[0] + offset[0], moving[1] + offset[1]
      try:
        self.get_marble(destination)
        self._board[destination[0]][destination[1]] = self.get_marble(moving)
        self._board[moving[0]][moving[1]] = 'X'
      except IndexError:
        # Increment the captured counter if the marble that got moved off the
        # board was red
        if self.get_marble(moving) == 'R':
          info['captured'] += 1

    # Ensure the move did not just undo a previous move
    if self._boards_equal(self._board, self._last_board):
      self._board = board_backup
      return False
    self._last_board = board_backup

    # Set the winner to the current player if they've captured at least 7
    # neutral marbles, or of the number of opponent marbles is 0
    if info['captured'] >= 7:
      self._winner = player_name
    elif self.get_marble_count()[info['color'] == 'W'] == 0:
      self._winner = player_name
    else:
      # Initalize boolean for both players, keeping track if they have any
      # legal moves available
      have_legal_moves = {
          info['color']: False
          for info in self._players_info.values()
      }
      for r, row in enumerate(self._board):
        for c, cell in enumerate(row):
          # Ignore absent cells
          if cell not in have_legal_moves:
            continue
          if self._has_legal_move((r, c)):
            have_legal_moves[cell] = True
            # Mark them as having legal moves, and if now both players
            # have legal moves, break out of both loops
            if all(have_legal_moves.values()):
              break
        if all(have_legal_moves.values()):
          break
      # Get player colorthat does not have any legal moves available
      moveless_color = next(
          (
              color
              for color, has_legal_moves in have_legal_moves.items()
              if not has_legal_moves
          ),
          None
      )
      # If there is a color that has no legal moves, set the winner to the
      # opposite player
      if moveless_color:
        self._winner = next(
            name
            for name, info in self._players_info.items()
            if info['color'] != moveless_color
        )

    # Set the current user to the opposite of the current user
    self._current = next(
        name
        for name in self._players_info.keys()
        if name != player_name
    )

    return True

  def get_marble(self, marble):
    """Return the color of the provided marble."""
    # If either of the coordinates are negative, raise an IndexError,
    # indicating being off the board
    if marble[0] < 0 or marble[1] < 0:
      raise IndexError()
    return self._board[marble[0]][marble[1]]

  def __str__(self) -> str:  # pragma: no cover
    """Return the string representation of the game state, including board."""
    white, black, red = self.get_marble_count()
    players = list(self._players_info.items())
    lines: List[str] = [
        f'Current Turn: {self.get_current_turn()}',
        f'Counts      : W={white} B={black} R={red}',
        f'Captured    : {players[0][0]}={players[0][1]["captured"]} '
        f'{players[1][0]}={players[1][1]["captured"]}',
        '',
        '   ' + ' '.join([str(i) for i in range(7)]),
        ''
    ]
    for r, row in enumerate(self._board):
      lines.append(str(r) + '  ' + ' '.join(row) + '  ' + str(r))
    lines.append('')
    lines.append('   ' + ' '.join([str(i) for i in range(7)]))
    return '\n'.join(lines)


def main_cli():
  """Allow playing of the game via CLI."""
  game = KubaGame(('One', 'W'), ('Two', 'B'))
  while not game.get_winner():
    print()
    print(game)
    print()
    response = input('Marble to move (row column): ').strip()
    try:
      row, col = map(int, response.split(' '))
    except Exception as e:
      print(e)
      input('Enter a valid row & column')
      continue

    direction = input(
        f'Direction ({", ".join(game.DIRECTIONS.keys())}): '
    ).strip().upper()
    if not len(direction):
      input('Must enter a direction')
      continue
    if direction[0] not in game.DIRECTIONS:
      input('Enter a valid direction')
      continue
    if not game.make_move(
        game.get_current_turn() or 'One',
        (row, col),
        direction
    ):
      input('Invalid move')
      continue
  print(game.get_winner() + ' won!')


def main():
  """Execute example assertions."""
  game = KubaGame(('PlayerA', 'W'), ('PlayerB', 'B'))
  assert game.get_marble_count() == (8, 8, 13)
  assert game.get_captured('PlayerA') == 0
  assert game.get_current_turn() is None
  assert game.get_winner() is None
  assert game.make_move('PlayerA', (6, 5), 'F') is True
  assert game.make_move('PlayerA', (6, 5), 'L') is False
  assert game.get_marble((5, 5)) == 'W'


if __name__ == '__main__':
  main()
  # Uncomment to play the CLI version of the game
  # main_cli()
