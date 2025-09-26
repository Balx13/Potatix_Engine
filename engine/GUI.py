if __name__ == "__main__":

    import pygame
    import chess
    from search import alphabeta
    # --- Beállítások ---
    WIDTH, HEIGHT = 640, 640
    SQ_SIZE = WIDTH // 8
    FPS = 144

    # Pygame inicializálás
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Sakk GUI - ember vs motor")
    clock = pygame.time.Clock()

    # Színek
    WHITE = (238, 238, 210)
    GREEN = (118, 150, 86)
    BLACK = (0, 0, 0)

    # Unicode bábuk
    UNICODE_PIECES = {
        "P": "♙",
        "N": "♘",
        "B": "♗",
        "R": "♖",
        "Q": "♕",
        "K": "♔",
        "p": "♟",
        "n": "♞",
        "b": "♝",
        "r": "♜",
        "q": "♛",
        "k": "♚",
    }

    # Font választás (Windows alatt biztos működik)
    font = pygame.font.SysFont("segoeuisymbol", 64)

    # Sakktábla
    board = chess.Board()
    selected_square = None
    running = True
    human_turn = True


    if human_turn:
        print("Te lépsz")

    def draw_board(screen, board):
        """Tábla és bábuk kirajzolása"""
        colors = [WHITE, GREEN]
        for r in range(8):
            for c in range(8):
                color = colors[(r + c) % 2]
                pygame.draw.rect(
                    screen,
                    color,
                    pygame.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE)
                )
        for square in chess.SQUARES:
            piece = board.piece_at(square)
            if piece:
                col = chess.square_file(square)
                row = 7 - chess.square_rank(square)
                text = UNICODE_PIECES[piece.symbol()]
                render = font.render(text, True, BLACK)
                text_rect = render.get_rect(
                    center=(col*SQ_SIZE + SQ_SIZE//2, row*SQ_SIZE + SQ_SIZE//2)
                )
                screen.blit(render, text_rect)

    def get_square_under_mouse(pos):
        """Visszaadja, melyik mezőre kattintottak"""
        x, y = pos
        col = x // SQ_SIZE
        row = 7 - (y // SQ_SIZE)
        return chess.square(col, row)

    def main():
        global WIDTH, HEIGHT, SQ_SIZE, FPS, WHITE, GREEN, BLACK, UNICODE_PIECES, font, board, selected_square, running, human_turn

        # Fő ciklus
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                # Ember kattintás
                if human_turn and event.type == pygame.MOUSEBUTTONDOWN:
                    square = get_square_under_mouse(event.pos)
                    if selected_square is None:
                        piece = board.piece_at(square)
                        if piece and piece.color == board.turn:
                            selected_square = square
                    else:
                        move = chess.Move(selected_square, square)
                        if move in board.legal_moves:
                            board.push(move)
                            human_turn = False
                        selected_square = None

            # Rajzolás
            draw_board(screen, board)
            pygame.display.flip()

            # Motor lép
            if not human_turn and not board.is_game_over():
                print("Motor lép")
                eval_score, move = alphabeta(board, False,4, float('-inf'), float('inf'))
                if move is not None and move in board.legal_moves:
                    board.push(move)
                    human_turn = True
                    print("Te lépsz")

            # Rajzolás
            draw_board(screen, board)
            pygame.display.flip()
            clock.tick(FPS)

    main()

    pygame.quit()
