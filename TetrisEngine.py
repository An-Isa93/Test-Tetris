import pygame
import random
import time

from pygame.constants import SCRAP_SELECTION

pygame.init()
pygame.mixer.init()
pygame.mixer.music.load('audio/TetrisMusic.mp3')

class Graphics():
    def __init__(self):
        self.pieces = []
        self.screen_w = 300
        self.screen_h = 600
        self.rows = 20
        self.cols = 10
        self.TILE_SIZE = self.screen_h // self.rows
        self.colors = {
            0: pygame.Color('black'),
            'I': pygame.Color(100, 149, 237), #light blue
            'O': pygame.Color('yellow'),
            'T': pygame.Color('purple'),
            'L': pygame.Color('orange'),
            'J': pygame.Color('blue'),
            'S': pygame.Color('green'),
            'Z': pygame.Color('red')
        }
        self.music_stopped = False

        # Side spaces
        # self.extra_height = 20 (TILE_SIZE)
        self.side_width = 260
        self.side_rows = 8
        self.side_cols = 4

    def main(self):
        screen = pygame.display.set_mode((self.screen_w + self.side_width * 2,
                                          self.screen_h + self.TILE_SIZE * 2))
        clock = pygame.time.Clock()
        screen.fill(pygame.Color("grey73"))
        gs = GameState()
        self.drawBorder(screen)
        self.draw_sides(screen, gs)
        pygame.mixer.music.play(-1)
        running = True
        while(running):
            clock.tick(60)
            for action in pygame.event.get():
                if action.type == pygame.QUIT or gs.game_ended:
                    running = False
                elif action.type == pygame.KEYDOWN:
                    if (gs.is_paused and action.key != pygame.K_ESCAPE):
                        continue
                    elif gs.game_ended:
                        break
                    elif (gs.is_paused and action.key == pygame.K_ESCAPE):
                        screen.fill(pygame.Color('grey73'))
                        self.drawBorder(screen)
                        self.draw_sides(screen, gs)
                        self.play_music()
                        self.music_stopped = False
                    if action.key == pygame.K_LEFT:
                        gs.moveLeft()
                    elif action.key == pygame.K_RIGHT:
                        gs.moveRight()
                    elif action.key == pygame.K_UP:
                        gs.rotatePiece()
                    elif action.key == pygame.K_DOWN:
                        gs.moveDown()
                    elif action.key == pygame.K_c:
                        gs.hold_Piece()
                    elif action.key == pygame.K_SPACE:
                        gs.dropPiece()
                    elif action.key == pygame.K_ESCAPE:
                        gs.is_paused = not gs.is_paused
                        if gs.is_paused:
                            self.stop_music()  # Pause music if game is paused
                            self.music_paused = True  # Track that music is paused
                        else:
                            self.play_music()  # Unpause music when game is unpaused
                            self.music_paused = False
            if gs.is_paused:
                self.show_pause_screen()
            elif gs.game_ended:
                break
            else:
                gs.update()
                self.drawBoard(screen, gs)
                pygame.display.flip()
        
        if gs.game_ended:
            self.draw_GameOver(gs)
            
            waiting = True
            while waiting:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        exit()
                    elif event.type == pygame.KEYDOWN:
                        waiting = False  # Salir del bucle cuando se presiona una tecla

    def play_music(self):
        pygame.mixer.music.unpause()

    def stop_music(self):
        pygame.mixer.music.pause()

    def show_pause_screen(self):
        font = pygame.font.SysFont('Arial', 48)
        text = font.render('Paused', True, (255, 255, 255))  # White text
        screen = pygame.display.get_surface()
        screen.fill((0, 0, 0))  # Fill the screen with black
        screen.blit(text, (screen.get_width() // 2 - text.get_width() // 2, 
                        screen.get_height() // 2 - text.get_height() // 2))  # Center the text
        pygame.display.flip()  # Update the display

    def drawBoard(self, screen, gs):
        for row in range(self.rows):
            for col in range(self.cols):
                pygame.draw.rect(screen, self.colors[gs.board[row][col]],
                                 pygame.Rect(col * self.TILE_SIZE + self.side_width, row * self.TILE_SIZE + self.TILE_SIZE, self.TILE_SIZE, self.TILE_SIZE))
        self.draw_sides(screen, gs)
        self.drawProyection(screen, gs)

    def drawProyection(self, screen, gs):
        for r,c in gs.projected_coords:
            pygame.draw.rect(screen, self.colors[gs.currentPiece.type],
                    pygame.Rect(c * self.TILE_SIZE + self.side_width,
                               r * self.TILE_SIZE + self.TILE_SIZE, self.TILE_SIZE, self.TILE_SIZE))
            pygame.draw.rect(screen, pygame.Color('black'),
                    pygame.Rect(c * self.TILE_SIZE + self.side_width + 1,
                               r * self.TILE_SIZE + self.TILE_SIZE + 1, self.TILE_SIZE - 2, self.TILE_SIZE - 2))

    def draw_sides(self, screen, gs):
        # left side (hold piece and score)
        for row in range(4):
            for col in range(4):
                pygame.draw.rect(screen, self.colors[gs.holdPieceGrid[row-1][col]] if 1<= row<= 2 else pygame.Color('black'),
                    pygame.Rect(col * self.TILE_SIZE + (self.side_width - self.side_cols * self.TILE_SIZE) // 2 - 10,
                                row * self.TILE_SIZE + self.TILE_SIZE + (self.screen_h // 2 - self.side_rows * self.TILE_SIZE),
                                self.TILE_SIZE, self.TILE_SIZE))
                
        pygame.draw.rect(screen, pygame.Color('grey48'),
                    pygame.Rect(self.side_width // 2 - 75,
                                (self.TILE_SIZE*2 + (self.screen_h // 2) + 35),
                                self.TILE_SIZE * 4 + 10, self.TILE_SIZE * 3))
        
        font = pygame.font.SysFont('Arial', 48)
        text = font.render(str(gs.score), True, (0,0,0))  # White text
        screen.blit(text, (self.side_width // 2 - 75 + (self.TILE_SIZE * 4 + 10 - text.get_width()) // 2, 
                        (self.TILE_SIZE*2 + (self.screen_h // 2) + 50)))

        # right side (next pieces)
        for row in range(self.side_rows):
            for col in range(self.side_cols):
                pygame.draw.rect(screen, self.colors[gs.nextPiecesGrid[row][col]],
                    pygame.Rect(col * self.TILE_SIZE + self.screen_w + self.side_width + (self.side_width - self.side_cols * self.TILE_SIZE) // 2,
                                row * self.TILE_SIZE + self.TILE_SIZE + (self.screen_h // 2 - self.side_rows * self.TILE_SIZE),
                                self.TILE_SIZE, self.TILE_SIZE))            
    
    def drawBorder(self, screen):
        font = pygame.font.SysFont('Arial', 48)
        text = font.render('Hold', True, (255, 255, 255))  # White text
        screen.blit(text, (self.side_width // 2 - text.get_width() // 2 - 10, 
                        (self.TILE_SIZE*2 + (self.screen_h // 2 - self.side_rows * self.TILE_SIZE)) // 2 - text.get_height() // 2))
        text2 = font.render('Next', True, (255, 255, 255))  # White text
        screen.blit(text2, (self.side_width // 2 - text.get_width() // 2 + self.side_width + self.screen_w, 
                        (self.TILE_SIZE*2 + (self.screen_h // 2 - self.side_rows * self.TILE_SIZE)) // 2 - text.get_height() // 2))
        text3 = font.render('Score', True, (255, 255, 255))  # White text
        screen.blit(text3, (self.side_width // 2 - text.get_width() // 2 - 20, 
                        (self.TILE_SIZE*2 + (self.screen_h // 2)) - text.get_height() // 2))

        for row in range(self.rows+2):
            for col in range(self.cols+2):
                pygame.draw.rect(screen, pygame.Color('black'),
                                 pygame.Rect(col * self.TILE_SIZE + self.side_width - self.TILE_SIZE, row * self.TILE_SIZE, self.TILE_SIZE, self.TILE_SIZE))

                pygame.draw.rect(screen, pygame.Color('grey48'),
                                 pygame.Rect(col * self.TILE_SIZE + self.side_width - self.TILE_SIZE, row * self.TILE_SIZE, self.TILE_SIZE-2, self.TILE_SIZE-2))

    def draw_GameOver(self, gs):
        game_over_w = self.screen_w
        game_over_h = (self.screen_w) * 9 // 16

        font = pygame.font.SysFont('Arial', 48)
        text = font.render('Game Over', True, (255, 255, 255))  # White text
        text2 = font.render(f'Score: {gs.score}', True, (255, 255, 255))  # White text
        screen = pygame.display.get_surface()

        overlay = pygame.Surface((screen.get_width(), screen.get_height()), pygame.SRCALPHA)  # Transparent surface
        overlay.fill((0, 0, 0, 192))  # Semi-transparent black (RGBA: 192 = 25% transparency)

        # Fill the screen with the translucent overlay
        screen.blit(overlay, (0, 0))
        
        screen.blit(text, (self.side_width + game_over_w // 2 - text.get_width() // 2, 
                        screen.get_height() // 2 - text.get_height() // 2 - game_over_h // 2))  # Center the text
        screen.blit(text2, (self.side_width + game_over_w // 2 - text.get_width() // 2, 
                        screen.get_height() // 2 - text.get_height() // 2))  # Center the text
        pygame.display.flip()  # Update the display

class GameState(): #10x20
    def __init__(self):
        self.board = [ #Tablero / grid
            [0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0],
        ]
        self.rows = 20
        self.cols = 10
        self.log = [] # For training purposes
        self.images = ['I', 'O', 'T', 'L', 'J', 'S', 'Z']
        self.currentPiece = None
        self.last_move_time = time.time()
        self.updates = []
        self.hold_used = False
        self.projected_coords = []

        # Piece placing criteria
        self.lock_delay = 0
        self.LOCK_LIMIT = 3

        # Flags
        self.score = 0
        self.is_paused = False
        self.game_ended = False

        # Next Pieces
        self.nextPieces = []
        self.nextPiecesGrid = [
            [0,0,0,0], # Piece 1
            [0,0,0,0],
            [0,0,0,0], 
            [0,0,0,0], # Piece 2
            [0,0,0,0],
            [0,0,0,0], 
            [0,0,0,0], # Piece 3
            [0,0,0,0],
            [0,0,0,0]
        ]

        # Hold piece
        self.holdPiece = None
        self.holdPieceGrid = [
            [0,0,0,0],
            [0,0,0,0]
        ]

        self.spawnPieces()

    def spawnPieces(self):
        while len(self.nextPieces) < 4:
            new_piece = random.choice(self.images)
            self.nextPieces.append(Piece(new_piece))

        self.currentPiece = self.nextPieces.pop(0)

        # Debugging
        # print(self.currentPiece.type, end = " // ")
        # print([k.type for k in self.nextPieces])
        if any(self.board[r][c] != 0 for r,c in self.currentPiece.get_cells()):
            print("Game Over!")
            self.game_ended = True # pygame.quit()
            return

        for r, c in self.currentPiece.get_cells():
            self.board[r][c] = self.currentPiece.type

        # Spawn next pieces
        # Clear preview grid
        self.nextPiecesGrid = [[0] * 4 for _ in range(9)]  # Now 9 rows for spacing

        # Spawn next pieces in the preview grid
        for i, piece in enumerate(self.nextPieces[:3]):  # Only display the next 3 pieces
            type = piece.type
            s_r = 3 * i # Each piece starts at row `3*i`, column 1 for centering
            s_c = 0

            if type in {'I', 'J', 'Z'}:
                s_c = 0  # I-piece is wider, so shift left
            elif type in {'O', 'T'}:
                s_c = 1  # Default center for 3-wide pieces
            else:  # L and J
                s_c = 2 

            # Adjust the shape to fit within the section
            pseudo_shape = [(r + s_r, c + s_c) for r, c in piece.shape]

            # Ensure the piece stays within bounds
            for r, c in pseudo_shape:
                if 0 <= r < 9 and 0 <= c < 4:
                    self.nextPiecesGrid[r][c] = type

        # Debugging output
        # print([p.type for p in self.nextPieces])
        # for row in self.nextPiecesGrid:
        #     print(row)
        self.getProjection()

    def update(self):
        current_positions = self.currentPiece.get_cells()
        new_positions = [(r + 1, c) for r, c in current_positions]
        
        self.getProjection()

        if self.game_ended:
            return

        if time.time() - self.last_move_time > 1:
            self.last_move_time = time.time()

            if all((r < self.rows and self.board[r][c] == 0) or ((r,c) in current_positions) for r, c in new_positions): 
                # Clear old position
                for r, c in current_positions:
                    self.board[r][c] = 0
                                
                # Move piece down
                self.currentPiece.row += 1 
                self.lock_delay = 1
                
                # Place at new position
                for r, c in self.currentPiece.get_cells():
                    self.board[r][c] = self.currentPiece.type  
            else:
                self.lock_delay += 1
                # Lock the piece and spawn a new one
                # print("Locking piece")
                if self.lock_delay >= self.LOCK_LIMIT:
                    self.placePiece()

    def placePiece(self):
        for r, c in self.currentPiece.get_cells():
            if 0 <= r < self.rows and 0 <= c < self.cols:
                self.board[r][c] = self.currentPiece.type
        
        # Spawn a new piece
        self.clearFullRows()
        self.spawnPieces()
        self.log.clear()
        self.hold_used = False

    def getProjection(self):
        # Clone the current piece to avoid modifying the original
        piece_copy = Piece(self.currentPiece.type)
        piece_copy.row = self.currentPiece.row
        piece_copy.col = self.currentPiece.col
        piece_copy.shape = self.currentPiece.shape

        while True:
            # Calculate new projected positions
            new_positions = [(r + 1, c) for r, c in piece_copy.get_cells()]

            # Check if moving down is possible
            if all((r < self.rows and self.board[r][c] == 0)  or ((r, c) in piece_copy.get_cells()) for r, c in new_positions):
                piece_copy.row += 1  # Move the copied piece down
            else:
                break  # Stop when it collides

        # Store the final projected coordinates
        piece_copy_cells = set(piece_copy.get_cells())
        original_piece_cells = set(self.currentPiece.get_cells())

        # Find the difference
        self.projected_coords = list(piece_copy_cells - original_piece_cells)

    def clearFullRows(self):
        count = 0
        for row in range(self.rows):
            if all(self.board[row][col] != 0 for col in range(self.cols)):  # Row is full
                self.board.pop(row)  # Remove the full row
                self.board.insert(0, [0] * self.cols)  # Insert an empty row at the top
                count += 1
        self.score += 100*count

    def rotatePiece(self):
        new_shape = []
        new_positions = []
        #print(self.currentPiece.cells, "**************")

        pivot = self.currentPiece.shape[2]
        
        if self.currentPiece.type == 'O':
            return
        elif self.currentPiece.type == 'I':
            if self.currentPiece.shape == [(0,0), (0,1), (0,2), (0,3)]:  # Horizontal → Vertical
                new_shape = [(-1,2), (0,2), (1,2), (2,2)]
            elif self.currentPiece.shape == [(-1,2), (0,2), (1,2), (2,2)]:  # Vertical → 180°
                new_shape = [(1,0), (1,1), (1,2), (1,3)]
            elif self.currentPiece.shape == [(1,0), (1,1), (1,2), (1,3)]:  # 180° → 270°
                new_shape = [(-1,1), (0,1), (1,1), (2,1)]
            elif self.currentPiece.shape == [(-1,1), (0,1), (1,1), (2,1)]:  # 270° → Back to horizontal
                new_shape = [(0,0), (0,1), (0,2), (0,3)]
        else:
            new_shape = [((c - pivot[1]) + pivot[0], -(r - pivot[0]) + pivot[1]) 
                     for r, c in self.currentPiece.shape]
        
        new_positions = self.currentPiece.get_cells(new_shape)

        if self.validate_rotation(new_positions):
            self.currentPiece.cells = new_positions
            self.currentPiece.shape = new_shape
            self.log.append('r') # as R is for Right
    
    def validate_rotation(self, new_pos):
        current_positions = self.currentPiece.get_cells()

        # Check if the new positions are valid: within bounds and not colliding
        for r, c in new_pos:
            # Check if the position is out of bounds
            if not (0 <= r < self.rows and 0 <= c < self.cols):
                # print("Rotation out of bounds.")
                return False  # Rotation is not valid, out of bounds
            
            # Check if the position is occupied by another piece (not the current piece's cells)
            if self.board[r][c] != 0 and (r, c) not in current_positions:
                # print("Spot occupied by another piece.")
                return False  # Rotation is not valid, occupied spot

        # Clear the current piece's old positions on the board
        for r, c in current_positions:
            self.board[r][c] = 0

        # print("Rotating piece")

        # Update the board with the new rotated positions
        self.currentPiece.cells = new_pos
        
        for r, c in new_pos:
            self.board[r][c] = self.currentPiece.type
        return True

    def update_board(self, new_pos):
        # Assuming you have the logic for updating the board when a piece is placed
        for r, c in new_pos:
            self.board[r][c] = self.currentPiece.type

    def moveLeft(self):
        current_positions = self.currentPiece.get_cells()
        new_positions = [(r, c - 1) for r, c in current_positions]

        if all((c >= 0 and self.board[r][c] == 0) or ((r,c) in current_positions) for r, c in new_positions): 
            # Clear old position
            for r, c in current_positions:
                self.board[r][c] = 0
            
            # print("Moving piece left")
            
            # Move piece down
            self.currentPiece.col -= 1  
            
            # Place at new position
            for r, c in self.currentPiece.get_cells():
                self.board[r][c] = self.currentPiece.type

            self.log.append('L')
        else:
            # Lock the piece and spawn a new one
            for r, c in current_positions:
                self.board[r][c] = self.currentPiece.type

    def moveRight(self):
        current_positions = self.currentPiece.get_cells()
        new_positions = [(r, c + 1) for r, c in current_positions]

        if all((c < self.cols  and self.board[r][c] == 0) or ((r,c) in current_positions) for r, c in new_positions): 
            # Clear old position
            for r, c in current_positions:
                self.board[r][c] = 0
            
            # print("Moving piece right")
            
            # Move piece down
            self.currentPiece.col += 1  
            
            # Place at new position
            for r, c in self.currentPiece.get_cells():
                self.board[r][c] = self.currentPiece.type

            self.log.append('R')
        else:
            # Lock the piece and spawn a new one
            for r, c in current_positions:
                self.board[r][c] = self.currentPiece.type

    def moveDown(self):
        current_positions = self.currentPiece.get_cells()
        new_positions = [(r + 1, c) for r, c in current_positions]

        if all((r < self.rows and self.board[r][c] == 0) or ((r,c) in current_positions) for r, c in new_positions): 
            # Clear old position
            for r, c in current_positions:
                self.board[r][c] = 0
            
            # print("Moving piece down")
            
            # Move piece down
            self.currentPiece.row += 1  
            
            # Place at new position
            for r, c in self.currentPiece.get_cells():
                self.board[r][c] = self.currentPiece.type  

            self.log.append('d') # since D is for Drop
            self.score += 1
        else:
            # Lock the piece and spawn a new one
            # print("Locking piece")
            self.placePiece()

    def hold_Piece(self):
        if self.hold_used:
            # Can't change twice in a row with the same piece
            return

        for r,c in self.currentPiece.get_cells():
            self.board[r][c] = 0

        # If there's no held piece, store the current one and spawn a new piece
        if self.holdPiece is None:
            self.holdPiece = self.currentPiece
            self.spawnPieces()  # Spawn new piece after first hold
        else:
            for r, c in self.holdPiece.get_cells():
                self.board[r][c] = 0
            # Swap current piece with the held one
            self.currentPiece, self.holdPiece = self.holdPiece, self.currentPiece
            self.spawnHoldPiece()

        # Update the hold piece preview
        self.updateHoldGrid()
        self.log.append('C')
        self.hold_used = True

    def updateHoldGrid(self):
        """ Updates the hold piece grid for previewing the held piece. """
        self.holdPieceGrid = [[0] * 4 for _ in range(2)]  # 2-row display

        if not self.holdPiece:
            return  # No piece held yet

        type = self.holdPiece.type

        # Centering offsets based on piece shape
        center_offsets = {
            'I': 0, 'J': 0, 'Z': 0,
            'O': 1, 'T': 1,
            'L': 2, 'S': 2
        }
        s_c = center_offsets.get(type, 1)  # Default to 1

        # Generate a pseudo-positioned shape
        self.holdPiece.shape = Piece.piece_shapes[self.holdPiece.type]
        pseudo_shape = [(r, c + s_c) for r, c in self.holdPiece.shape]

        # Ensure piece is placed within the 2-row grid
        for r, c in pseudo_shape:
            if 0 <= r < 2 and 0 <= c < 4:  # Prevent index errors
                self.holdPieceGrid[r][c] = type

        # Debugging output
        # print("Hold Piece:", self.holdPiece.type)
        # for row in self.holdPieceGrid:
        #     print(row)

    def spawnHoldPiece(self):
        self.currentPiece = Piece(self.currentPiece.type)
        for r, c in self.currentPiece.get_cells():
            if self.board[r][c] != 0:  # Game over condition (spawn area occupied)
                print("Game Over!")
                self.game_ended = True #pygame.quit()
                # exit()
            else:
                self.board[r][c] = self.currentPiece.type

    def dropPiece(self):
        count = 0
        current_positions = self.currentPiece.get_cells()
        while True:
            new_positions = [(r + 1, c) for r, c in current_positions]

            # Check if the piece can still move down
            if all((r < self.rows and self.board[r][c] == 0) or ((r, c) in current_positions) for r, c in new_positions):
                # Move the piece down by 1 row
                for r, c in current_positions:
                    self.board[r][c] = 0  # Clear the current position
                
                # Update the row and piece position
                self.currentPiece.row += 1
                count += 1
                
                # Set the piece in the new position
                for r, c in self.currentPiece.get_cells():
                    self.board[r][c] = self.currentPiece.type
                current_positions = self.currentPiece.get_cells()  # Update current_positions to the new one
            else:
                # Lock the piece in place and spawn a new piece
                # print("Locking piece")
                self.log.append('D')
                self.placePiece()  # Lock the piece and spawn a new one
                self.score += 2*count
                break  # Exit the loop since the piece has been locked
    
class Piece():
    start_positions = {  # Initial spawn locations
        'I': (0, 3), 'O': (0, 4), 'T': (0, 4),
        'L': (0, 5), 'J': (0, 3), 'S': (0, 5), 'Z': (0, 3)
    }

    piece_shapes = {  # Tetris shapes in relative (row, col) positions
        'I': [(0, 0), (0, 1), (0, 2), (0, 3)],
        'O': [(0, 0), (0, 1), (1, 0), (1, 1)],
        'T': [(0, 0), (1, -1), (1, 0), (1, 1)],
        'L': [(0, 0), (1, 0), (1, -1), (1, -2)],
        'J': [(0, 0), (1, 0), (1, 1), (1, 2)],
        'S': [(0, 0), (0, 1), (1, 0), (1, -1)],
        'Z': [(0, 0), (0, 1), (1, 1), (1, 2)]
    }

    def __init__(self, piece_type):
        self.type = piece_type
        self.shape = Piece.piece_shapes[piece_type]
        self.row, self.col = Piece.start_positions[piece_type]
        self.cells = self.get_cells()

    def get_cells(self, cells=None):
        if cells==None:
            return [(self.row + r, self.col + c) for r, c in self.shape]
        else:
            return [(self.row + r, self.col + c) for r, c in cells]