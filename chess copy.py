import pygame
import os
import sys
import time

# Initialize pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 700, 700
ROWS, COLS = 8, 8
SQUARE_SIZE = (WIDTH // COLS)
LOG_WIDTH = 200
IMAGES = {}

# Load images
def load_images():
    pieces = ['wP', 'wR', 'wN', 'wB', 'wQ', 'wK',
              'bP', 'bR', 'bN', 'bB', 'bQ', 'bK']
    for piece in pieces:
        IMAGES[piece] = pygame.transform.scale(
            pygame.image.load(os.path.join("images", piece + ".png")),
            (SQUARE_SIZE/1.5, SQUARE_SIZE/1.5)
        )

# Sounds
move_sound = pygame.mixer.Sound("sounds/move.wav")
capture_sound = pygame.mixer.Sound("sounds/capture.wav")

# Board setup
def create_board():
    return [
        ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
        ["bP"] * 8,
        [""] * 8,
        [""] * 8,
        [""] * 8,
        [""] * 8,
        ["wP"] * 8,
        ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"],
    ]

# Drawing the board
def draw_board(win, board, selected, hovered, turn, move_log, message, captured_white, captured_black, turn_durations, turn_start_time):
    win.fill(pygame.Color("gray"))
    offset_y = 0  # No status bar height for this layout

    # Board
    colors = [pygame.Color("darkred"), pygame.Color("black")]
    for r in range(ROWS):
        for c in range(COLS):
            color = colors[(r + c) % 2]
            pygame.draw.rect(win, color, pygame.Rect(c*SQUARE_SIZE, r*SQUARE_SIZE + offset_y, SQUARE_SIZE, SQUARE_SIZE))

            # Highlight selected cell
            if (r, c) == selected:
                pygame.draw.rect(win, pygame.Color("deepskyblue"), (c*SQUARE_SIZE, r*SQUARE_SIZE+offset_y, SQUARE_SIZE, SQUARE_SIZE), 5)

            # Highlight hovered cell
            if (r, c) == hovered:
                border = pygame.Color("green") if selected and is_valid_move(board, selected, (r, c), turn) else pygame.Color("yellow")
                pygame.draw.rect(win, border, (c*SQUARE_SIZE, r*SQUARE_SIZE+offset_y, SQUARE_SIZE, SQUARE_SIZE), 3)

            piece = board[r][c]
            if piece != "":
                win.blit(IMAGES[piece], pygame.Rect(c*SQUARE_SIZE+15, r*SQUARE_SIZE+15+offset_y, SQUARE_SIZE, SQUARE_SIZE))

    # Move log and turn display
    log_rect = pygame.Rect(WIDTH, 0, LOG_WIDTH, HEIGHT)
    pygame.draw.rect(win, pygame.Color("lightgray"), log_rect)
    font = pygame.font.SysFont(None, 24)

    # Current turn & time
    turn_text = f"Turn: {'White' if turn == 'w' else 'Black'}"
    time_elapsed = int(time.time() - turn_start_time)
    time_text = f"Time: {time_elapsed}s"
    win.blit(font.render(turn_text, True, pygame.Color("darkblue")), (WIDTH + 10, 10))
    win.blit(font.render(time_text, True, pygame.Color("darkgreen")), (WIDTH + 10, 30))

    

    # Captured pieces layout
    y_offset = 80
    row_offset = 0  # Counter for each row of captured pieces

    win.blit(font.render("White Captures:", True, pygame.Color("black")), (WIDTH + 10, y_offset))
    y_offset += 30  # Increase spacing for captured pieces section

    # Draw White Captures
    for i, piece in enumerate(captured_white):
        win.blit(IMAGES[piece], (WIDTH + 10 + (i % 4) * 40, y_offset + (i // 4) * 40))
    
    y_offset += 60  # Increase offset before Black Captures
    win.blit(font.render("Black Captures:", True, pygame.Color("black")), (WIDTH + 10, y_offset))

    # Draw Black Captures
    for i, piece in enumerate(captured_black):
        win.blit(IMAGES[piece], (WIDTH + 10 + (i % 4) * 40, y_offset + 20 + (i // 4) * 40))

    # Move history
    for i, move in enumerate(move_log[-25:]):
        txt = font.render(move, True, pygame.Color("black"))
        win.blit(txt, (WIDTH+10, 400+i*20))


# Move logic
def is_valid_move(board, start, end, turn):
    sr, sc = start
    er, ec = end
    piece = board[sr][sc]
    dest = board[er][ec]

    if piece == "" or piece[0] != turn:
        return False
    if dest != "" and dest[0] == turn:
        return False

    dr, dc = er - sr, ec - sc
    kind = piece[1]

    if kind == 'P':
        dir = -1 if turn == 'w' else 1
        start_row = 6 if turn == 'w' else 1
        if dc == 0 and dest == "":
            if dr == dir or (sr == start_row and dr == 2*dir and board[sr+dir][sc] == ""):
                return True
        elif abs(dc) == 1 and dr == dir and dest != "":
            return True
    elif kind == 'R':
        if sr == er or sc == ec:
            return clear_path(board, start, end)
    elif kind == 'N':
        if (abs(dr), abs(dc)) in [(2,1), (1,2)]:
            return True
    elif kind == 'B':
        if abs(dr) == abs(dc):
            return clear_path(board, start, end)
    elif kind == 'Q':
        if sr == er or sc == ec or abs(dr) == abs(dc):
            return clear_path(board, start, end)
    elif kind == 'K':
        if max(abs(dr), abs(dc)) == 1:
            return True
    return False

def clear_path(board, start, end):
    sr, sc = start
    er, ec = end
    dr = 1 if er > sr else -1 if er < sr else 0
    dc = 1 if ec > sc else -1 if ec < sc else 0
    r, c = sr + dr, sc + dc
    while (r, c) != (er, ec):
        if board[r][c] != "":
            return False
        r += dr
        c += dc
    return True

# Main game loop
def main():
    win = pygame.display.set_mode((WIDTH + LOG_WIDTH, HEIGHT))
    pygame.display.set_caption("2 Player Chess")
    load_images()
    board = create_board()
    clock = pygame.time.Clock()
    selected = None
    turn = 'w'
    hovered = None
    move_log = []
    history = []
    captured_white = []
    captured_black = []
    message = ""
    turn_start_time = time.time()
    turn_durations = {"w": 0, "b": 0}
    running = True

    while running:
        draw_board(win, board, selected, hovered, turn, move_log, message, captured_white, captured_black, turn_durations, turn_start_time)
        pygame.display.flip()
        clock.tick(60)
        message = ""

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEMOTION:
                mx, my = event.pos
                if my < HEIGHT:
                    hovered = ((my) // SQUARE_SIZE, mx // SQUARE_SIZE)
                else:
                    hovered = None

            elif event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos
                if WIDTH-110 <= mx <= WIDTH-10 and HEIGHT-50 <= my <= HEIGHT-10:
                    board = create_board()
                    move_log = []
                    selected = None
                    turn = 'w'
                    history = []
                    captured_white = []
                    captured_black = []
                    continue

                if my < HEIGHT:
                    row, col = my // SQUARE_SIZE, mx // SQUARE_SIZE
                    if selected:
                        if is_valid_move(board, selected, (row, col), turn):
                            piece = board[selected[0]][selected[1]]
                            captured = board[row][col] != ""
                            if captured:
                                if board[row][col][0] == 'w':
                                    captured_black.append(board[row][col])
                                else:
                                    captured_white.append(board[row][col])

                            board[row][col] = piece
                            board[selected[0]][selected[1]] = ""
                            move_log.append(f"{piece} {chr(selected[1]+97)}{8-selected[0]}->{chr(col+97)}{8-row}")
                            turn = 'b' if turn == 'w' else 'w'
                            if captured:
                                capture_sound.play()
                            else:
                                move_sound.play()
                        selected = None
                    else:
                        if board[row][col] != "" and board[row][col][0] == turn:
                            selected = (row, col)

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_u and history:
                    last = history.pop()
                    start, end, captured = last
                    board[start[0]][start[1]] = board[end[0]][end[1]]
                    board[end[0]][end[1]] = captured
                    turn = 'b' if turn == 'w' else 'w'
                    move_log.pop()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
