from pickle import TRUE
import pygame
import random
import time

from pygame.constants import SCRAP_SELECTION

pygame.init()

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
        self.is_paused = False

    def main(self):
        screen = pygame.display.set_mode((self.screen_w, self.screen_h))
        clock = pygame.time.Clock()
        screen.fill(pygame.Color("black"))
        gs = GameState()
        running = True
        while(running):
            clock.tick(60)
            for action in pygame.event.get():
                if action.type == pygame.QUIT:
                    running = False
                elif action.type == pygame.KEYDOWN:
                    if self.is_paused and action.key != pygame.K_ESCAPE:
                        continue
                    if action.key == pygame.K_LEFT:
                        gs.moveLeft()
                    elif action.key == pygame.K_RIGHT:
                        gs.moveRight()
                    elif action.key == pygame.K_UP:
                        gs.rotatePiece()
                    elif action.key == pygame.K_DOWN:
                        gs.moveDown()
                    elif action.key == pygame.K_c:
                        gs.hodlPiece()
                    elif action.key == pygame.K_SPACE:
                        gs.dropPiece()
                    elif action.key == pygame.K_ESCAPE:
                        self.is_paused = not self.is_paused
            if self.is_paused:
                self.show_pause_screen()
            else:
                gs.update()
                self.drawBoard(screen, gs)
                pygame.display.flip()
        
        pygame.quit()

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
                                 pygame.Rect(col * self.TILE_SIZE, row * self.TILE_SIZE, self.TILE_SIZE, self.TILE_SIZE))        

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
        self.log = []
        self.nextPieces = []
        self.holdPiece = None
        self.images = ['I', 'O', 'T', 'L', 'J', 'S', 'Z']
        self.currentPiece = None
        self.spawnPieces()
        self.last_move_time = time.time()
        self.updates = []

    def spawnPieces(self):
        while len(self.nextPieces) < 4:
            new_piece = random.choice(self.images)
            self.nextPieces.append(Piece(new_piece))

        self.currentPiece = self.nextPieces.pop(0)

        # Debugging
        # print(self.currentPiece.type, end = " // ")
        # print([k.type for k in self.nextPieces])
        for r, c in self.currentPiece.get_cells():
            if self.board[r][c] != 0:  # Game over condition (spawn area occupied)
                # print(self.board)
                # print(self.currentPiece.get_cells())
                print("Game Over!")
                pygame.quit()
                exit()
            else:
                self.board[r][c] = self.currentPiece.type

    def update(self):
        current_positions = self.currentPiece.get_cells()
        new_positions = [(r + 1, c) for r, c in current_positions]

        if time.time() - self.last_move_time > 1:
            self.last_move_time = time.time()

            if all((r < self.rows and self.board[r][c] == 0) or ((r,c) in current_positions) for r, c in new_positions): 
                # Clear old position
                for r, c in current_positions:
                    self.board[r][c] = 0
                                
                # Move piece down
                self.currentPiece.row += 1  
                
                # Place at new position
                for r, c in self.currentPiece.get_cells():
                    self.board[r][c] = self.currentPiece.type  
            else:
                # Lock the piece and spawn a new one
                print("Locking piece")
                self.placePiece()

    def canMoveDown(self):
        return all(
            r + 1 < self.rows and self.board[r + 1][c] == 0
            for r, c in self.currentPiece.get_cells()
        )

    def placePiece(self):
        for r, c in self.currentPiece.get_cells():
            if 0 <= r < self.rows and 0 <= c < self.cols:
                self.board[r][c] = self.currentPiece.type
        
        # Spawn a new piece
        self.clearFullRows()
        self.spawnPieces()
    
    def clearFullRows(self):
        for row in range(self.rows):
            if all(self.board[row][col] != 0 for col in range(self.cols)):  # Row is full
                self.board.pop(row)  # Remove the full row
                self.board.insert(0, [0] * self.cols)  # Insert an empty row at the top

    def rotatePiece(self):
        shape_center = self.currentPiece.shape[2]
        new_shape = []
        new_positions = []
        print(self.currentPiece.cells, "**************")

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
    
    def validate_rotation(self, new_pos):
        current_positions = self.currentPiece.get_cells()

        # Check if the new positions are valid: within bounds and not colliding
        for r, c in new_pos:
            # Check if the position is out of bounds
            if not (0 <= r < self.rows and 0 <= c < self.cols):
                print("Rotation out of bounds.")
                return False  # Rotation is not valid, out of bounds
            
            # Check if the position is occupied by another piece (not the current piece's cells)
            if self.board[r][c] != 0 and (r, c) not in current_positions:
                print("Spot occupied by another piece.")
                return False  # Rotation is not valid, occupied spot

        # Clear the current piece's old positions on the board
        for r, c in current_positions:
            self.board[r][c] = 0

        print("Rotating piece")

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
            
            print("Moving piece left")
            
            # Move piece down
            self.currentPiece.col -= 1  
            
            # Place at new position
            for r, c in self.currentPiece.get_cells():
                self.board[r][c] = self.currentPiece.type
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
            
            print("Moving piece right")
            
            # Move piece down
            self.currentPiece.col += 1  
            
            # Place at new position
            for r, c in self.currentPiece.get_cells():
                self.board[r][c] = self.currentPiece.type
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
            
            print("Moving piece down")
            
            # Move piece down
            self.currentPiece.row += 1  
            
            # Place at new position
            for r, c in self.currentPiece.get_cells():
                self.board[r][c] = self.currentPiece.type  
        else:
            # Lock the piece and spawn a new one
            print("Locking piece")
            self.placePiece()

    def holdPiece(self):
        pass

    def dropPiece(self):
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
                
                # Set the piece in the new position
                for r, c in self.currentPiece.get_cells():
                    self.board[r][c] = self.currentPiece.type
                current_positions = self.currentPiece.get_cells()  # Update current_positions to the new one
            else:
                # Lock the piece in place and spawn a new piece
                print("Locking piece")
                self.placePiece()  # Lock the piece and spawn a new one
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