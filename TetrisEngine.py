import pygame
import random
import time
import joblib
import json
import numpy as np
from services.database import  save_game
from pygame.constants import SCRAP_SELECTION
from tf_keras.models import load_model
from services.model import CustomLoss
from functools import partial
from sklearn.preprocessing import LabelEncoder

pygame.init()
pygame.mixer.init()
# MAKE NEXT LINE A COMMENT TO LISTEN TO MUSIC
pygame.mixer.music.set_volume(0)
ClearSFX = pygame.mixer.Sound("assets/audio/sfx/ClearLine.mp3")
GameOverSFX = pygame.mixer.Sound("assets/audio/sfx/GameOver.mp3")
RotationSFX = pygame.mixer.Sound("assets/audio/sfx/Rotation.mp3")
TetrisSFX = pygame.mixer.Sound("assets/audio/sfx/TetrisClear.mp3")

le_piece = LabelEncoder()
le_move = LabelEncoder()
le_piece.fit(['I', 'O', 'T', 'S', 'Z', 'J', 'L', 'none'])

# Rebeca, Valeria
class Graphics():
    def __init__(self):
        #self.pieces = []
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

    def drawTitleScreen(self):
        pygame.mixer.music.load('assets/audio/TitleScreenMusic.mp3')
        pygame.mixer.music.play(-1)
        screen = pygame.display.set_mode((self.screen_w + self.side_width * 2,
                                          self.screen_h + self.TILE_SIZE * 2))
        screen.fill(pygame.Color("#929292"))

        font = pygame.font.Font("fonts/BungeeTint-Regular.ttf", 120)
        text = font.render('Tetris', True, (255, 255, 255))  
        font = pygame.font.Font("fonts/RubikMonoOne-Regular.ttf", 28)
        text2 = font.render('Start', True, (0, 0, 0))  
        text3 = font.render('Auto-play', True, (0,0,0))
        border_color = pygame.Color('black')
        
        # TITLE
        screen.blit(text, (self.side_width + self.screen_w // 2 - text.get_width() // 2, 
                        screen.get_height() // 2 - text.get_height() // 2 - 200))  # Center the text
        
        # BUTTON 1
        button1_rect = pygame.Rect(
            self.side_width + self.screen_w // 2 - 125,  # 125 = 250 // 2
            screen.get_height() // 2 - 30,              # 30 = 60 // 2
            250, 60
        )
        border1 = button1_rect.inflate(6,6)
        pygame.draw.rect(screen, border_color, border1)
        pygame.draw.rect(screen, pygame.Color('#c1c0c0'), button1_rect)

        text2_pos = (
            button1_rect.x + (button1_rect.width - text2.get_width()) // 2,
            button1_rect.y + (button1_rect.height - text2.get_height()) // 2
        )
        screen.blit(text2, text2_pos)
        
        # BUTTON 2
        button2_rect = pygame.Rect(
            self.side_width + self.screen_w // 2 - 120,  # 120 = 240 // 2
            screen.get_height() // 2 - 30 + 200,
            250, 60
        )
        border2 = button2_rect.inflate(6,6)
        pygame.draw.rect(screen, border_color, border2)
        pygame.draw.rect(screen, pygame.Color('#c1c0c0'), button2_rect)

        text3_pos = (
            button2_rect.x + (button2_rect.width - text3.get_width()) // 2,
            button2_rect.y + (button2_rect.height - text3.get_height()) // 2
        )
        screen.blit(text3, text3_pos)


        waiting = True
        colors = [
            pygame.Color("cyan"), pygame.Color("blue"), pygame.Color("orange"),
            pygame.Color("yellow"), pygame.Color("green"), pygame.Color("purple"),
            pygame.Color("red")
            ]
        
        last_color_change = pygame.time.get_ticks()  # Save initial time 
        color_change_interval = 300
        current_color=random.choice(colors)
        while waiting:
            screen_width, screen_height = screen.get_size()
            TILE_SIZE = 30
            
            current_time = pygame.time.get_ticks()
            if current_time - last_color_change >= color_change_interval:
                last_color_change = current_time  # Update time of last change
                current_color = random.choice(colors)  # Change random color 

            #borders 
            for x in range(0, screen_width + TILE_SIZE, TILE_SIZE):
                for y in [0, screen_height - TILE_SIZE]:
                    rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)
                    pygame.draw.rect(screen,current_color, rect)  
                    pygame.draw.rect(screen, pygame.Color("black"), rect, 1) 
            
            for y in range(0, screen_height + TILE_SIZE, TILE_SIZE):
                for x in [0, screen_width - TILE_SIZE]:
                    rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)
                    pygame.draw.rect(screen, current_color, rect)  
                    pygame.draw.rect(screen, pygame.Color("black"), rect, 1) 
            
            pygame.display.flip()  # Update the display

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    location = pygame.mouse.get_pos()
                    col = location[0]
                    row = location[1]

                    if (305 <= row <= 365) and (281 <= col <= 521):
                        #print("Startgame selected")
                        waiting = False  # Salir del bucle cuando se presiona una tecla / Continuar con el juego
                        pygame.mixer.music.stop()
                        self.main()
                    elif (505 <= row <= 565) and (281 <= col <= 521):
                        # AUTO-PLAY (AI)
                        self.main('AI')
                        #print("Autoplay selected")
                        pass
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        waiting = False  # Salir del bucle cuando se presiona una tecla
                        pygame.mixer.music.stop()
                        self.main()

    def main(self, mode=None):
        pygame.mixer.music.load('assets/audio/TetrisMusic.mp3')
        screen = pygame.display.get_surface()
        clock = pygame.time.Clock()
        screen.fill(pygame.Color("grey73"))
        gs = GameState()
        self.drawBorder(screen)
        self.draw_sides(screen, gs)
        pygame.mixer.music.play(-1)
        running = True
        if mode == 'AI':
            gs.auto_play()
            running = False
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
                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        location = pygame.mouse.get_pos()
                        col = location[0]
                        row = location[1]

                        if (390 <= row <= 450) and (280 <= col <= 520): #(280 <= col <= 520)
                            del(gs)
                            waiting = False  # Salir del bucle cuando se presiona una tecla
                            pygame.mixer.music.stop()
                            self.drawTitleScreen()
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_SPACE:
                            del(gs)
                            waiting = False  # Salir del bucle cuando se presiona una tecla
                            pygame.mixer.music.stop()
                            self.drawTitleScreen()

    def play_music(self):
        pygame.mixer.music.unpause()

    def stop_music(self):
        pygame.mixer.music.pause()

    def show_pause_screen(self):
        font = pygame.font.Font("fonts/BungeeShade-Regular.ttf", 72)
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
        
        #font = pygame.font.Font("fonts/RubikMonoOne-Regular.ttf", 40)
        font = pygame.font.SysFont("Arial", 48)
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
        font = pygame.font.Font("fonts/RubikMonoOne-Regular.ttf", 40)
        text = font.render('Hold', True, (255, 255, 255))  # White text
        screen.blit(text, (self.side_width // 2 - text.get_width() // 2 - 10, 
                        (self.TILE_SIZE*2 + (self.screen_h // 2 - self.side_rows * self.TILE_SIZE)) // 2 - text.get_height() // 2))
        text2 = font.render('Next', True, (255, 255, 255))  # White text
        screen.blit(text2, (self.side_width // 2 - text.get_width() // 2 + self.side_width + self.screen_w, 
                        (self.TILE_SIZE*2 + (self.screen_h // 2 - self.side_rows * self.TILE_SIZE)) // 2 - text.get_height() // 2))
        text3 = font.render('Score', True, (255, 255, 255))  # White text
        screen.blit(text3, (self.side_width // 2 - text.get_width() // 2 - 30, 
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

        self.stop_music()
        self.music_paused = True
        GameOverSFX.play()

        font = pygame.font.Font("fonts/BungeeShade-Regular.ttf", 70)
        font2 = pygame.font.Font("fonts/RubikMonoOne-Regular.ttf", 28)
        text = font.render('Game Over', True, (255, 255, 255))  # White text
        text2 = font.render(f'Score: {gs.score}', True, (255, 255, 255))  # White text
        text3 = font2.render('Play again', True, (0,0,0))
        screen = pygame.display.get_surface()

        overlay = pygame.Surface((screen.get_width(), screen.get_height()), pygame.SRCALPHA)  # Transparent surface
        overlay.fill((0, 0, 0, 192))  # Semi-transparent black (RGBA: 192 = 25% transparency)

        # Fill the screen with the translucent overlay
        screen.blit(overlay, (0, 0))
        
        screen.blit(text, (self.side_width + game_over_w // 2 - text.get_width() // 2, 
                        screen.get_height() // 2 - text.get_height() // 2 - game_over_h // 2))  # Center the text
        screen.blit(text2, (self.side_width + game_over_w // 2 - text2.get_width() // 2, 
                        screen.get_height() // 2 - text2.get_height() // 2))  # Center the text
        
        button3_rect = pygame.Rect(self.side_width + game_over_w // 2 - 250 // 2,
        screen.get_height() // 2 - 60 // 2 + game_over_h // 2, 250,60)

        border3 = button3_rect.inflate(6,6)
        pygame.draw.rect(screen,"black", border3)
        pygame.draw.rect(screen, "grey73", button3_rect)

        # Centrar el texto dentro del botón
        text3_pos = (
            button3_rect.x + (button3_rect.width - text3.get_width()) // 2,
            button3_rect.y + (button3_rect.height - text3.get_height()) // 2
        )
        screen.blit(text3, text3_pos)

        pygame.display.flip()  # Update the display

# Ana, Arturo
class GameState(): #10x20
    def __init__(self):
        self.board = [ #Tablero / grid [[0]*10 for _ in range(20)]
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
        self.log = [] # For training purposes log[-1]
        self.images = ['I', 'O', 'T', 'L', 'J', 'S', 'Z']
        self.currentPiece = None
        self.projected_coords = []

        # Optimizing
        self.init_board = None
        self.init_time = None
        self.last_score = 0

        # Piece placing criteria
        self.lock_delay = 0
        self.LOCK_LIMIT = 3

        # Flags
        self.score = 0
        self.last_move_time = time.time()
        self.hold_used = False
        self.is_paused = False
        self.game_ended = False
        self.AI_playing = False
        
        # Next Pieces
        self.nextPieces = [] # 'K' 'L' 'O'
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

        # Difficulty increment
        self.SPEED_FACTOR = 1

        self.spawnPieces()

    def getMoves(self): #optimize movements
        moves = []

        # Cantidad de rotaciones
        rotations = self.log.count('r') % 4
        if rotations > 0:
            moves.extend(['r'] * abs(rotations))

        # Cantidad de movimientos laterales
        side_moves = self.log.count('L') - self.log.count('R')
        if side_moves < 0:
            moves.extend(['R'] * abs(side_moves))
        elif side_moves > 0:
            moves.extend(['L'] * abs(side_moves))

        # Cantidad de movimientos hacia abajo
        down = self.log.count('d')
        if down > 0: moves.extend(['d'] * down)

        if 'C' in self.log:
            moves.extend('C')

        if 'D' in self.log:
            moves.extend('D')

        return moves

    def spawnPieces(self):
        while len(self.nextPieces) < 4:
            new_piece = random.choice(self.images)
            self.nextPieces.append(Piece(new_piece))

        self.currentPiece = self.nextPieces.pop(0) # 'K' 'L' 'O'
        
        # Debugging
        # print(self.currentPiece.type, end = " // ")
        # print([k.type for k in self.nextPieces])
        if any(self.board[r][c] != 0 for r,c in self.currentPiece.get_cells()):
            print("Game Over!")
            self.game_ended = True # pygame.quit()
            if self.holdPiece is not None:
                save_game(self.init_board, self.board, self.currentPiece.type, self.Next_pieces,
                                 self.holdPiece.type, self.moves, self.last_move_score,
                                 self.hold_used, self.game_ended)
            else:
                save_game(self.init_board, self.board, self.currentPiece.type, self.Next_pieces,
                                 None, self.moves, self.last_move_score,
                                 self.hold_used, self.game_ended)
            return

        for r, c in self.currentPiece.get_cells():
            self.board[r][c] = self.currentPiece.type

        self.init_time = time.time()
        self.init_board = self.board

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

        '''last_speed = self.SPEED_FACTOR
        self.SPEED_FACTOR = 1 - 0.1*(self.score // 1000)

        if self.SPEED_FACTOR <= 0.10: self.SPEED_FACTOR = 0.10
        if last_speed != self.SPEED_FACTOR: print(f"New gravity speed: {self.SPEED_FACTOR}")'''

        if time.time() - self.last_move_time > 1 * self.SPEED_FACTOR:
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

        turn_time = time.time() - self.init_time
        self.moves = self.log #self.getMoves()
        self. Next_pieces = [piece.type for piece in self.nextPieces]

        # Puntaje obtenido en el turno
        self.last_move_score = self.score - self.last_score

        # Debugging
        # print([self.currentPiece.type, Next_pieces, moves,
        #        self.last_score, turn_time, self.hold_used, self.game_ended])
        if not self.AI_playing: # PREVENTS FROM MAKING UNOPTIMIZED INSERTS WHILE TRAINING
            if self.holdPiece is not None:
                save_game(self.init_board, self.board, self.currentPiece.type, self.Next_pieces,
                                    self.holdPiece.type, self.moves, self.last_move_score,
                                    self.hold_used, self.game_ended)
            else:
                save_game(self.init_board, self.board, self.currentPiece.type, self.Next_pieces,
                                    'none', self.moves, self.last_move_score,
                                    self.hold_used, self.game_ended)
        # ELSE
        # self.dbConnection.insert(self.init_board, self.board, self.currentPiece.type, Next_pieces,
        #                          None/Null, moves, self.last_score, turn_time,
        #                          self.hold_used, self.game_ended)

        # Spawn a new piece
        self.clearFullRows()
        self.spawnPieces()
        self.log.clear()
        self.hold_used = False

        if self.AI_playing:
            self.auto_play()

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

        if count == 4:
            TetrisSFX.play()
        elif count >= 1:
            ClearSFX.play()
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
            RotationSFX.play()
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
            # for r, c in self.holdPiece.get_cells():
            #     self.holdPieceGrid[r][c] = 0
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
                self.score += 2*count
                self.placePiece()  # Lock the piece and spawn a new one
                break  # Exit the loop since the piece has been locked

    # AUTO-PLAY
    def auto_play(self):
        self.AI_playing = True
        gpx = Graphics()
        clock = pygame.time.Clock()
        custom_loss_with_classes = partial(CustomLoss, num_classes=6)
        model = load_model("models/tetris_AI.h5", custom_objects={"CustomLoss": custom_loss_with_classes})
        tokenizer = joblib.load("models/tokenizer.pkl")

        index_to_word = {
            1: 'R', 2: 'L', 3: 'r', 4: 'D', 5: 'C', 6: 'd'
        }

        while not self.game_ended:
            # Draw the board
            gpx.drawBoard(pygame.display.get_surface(), self)
            pygame.display.flip()

            # Prediction for current piece
            X_input = self.prepare_input()
            print("Prepared input shape:", X_input.shape)  # Debug input shape
            predicted_probs = model.predict(X_input)

            # Decode the predicted move(s)
            predicted_ids = np.argmax(predicted_probs[0], axis=-1)  # Adjust if output is multi-dimensional
            print(f"Predicted indices: {predicted_ids}")  # Debug predicted indices

            decoded_moves = [index_to_word.get(idx, '?') for idx in predicted_ids]
            print(f"Decoded moves: {decoded_moves}")  # Debug decoded moves

            # If decoded_moves is still empty or contains '?', it means there was a problem
            if not decoded_moves:
                print("Warning: Empty or invalid moves, skipping...")
            else:
                # Perform the predicted moves
                print("Executing moves:", decoded_moves)
                for move in decoded_moves:
                    if move == 'R':
                        self.moveRight()
                    elif move == 'L':
                        self.moveLeft()
                    elif move == 'D':
                        self.dropPiece()
                        break  # Usually ends the move sequence
                    elif move == 'd':
                        self.moveDown()
                    elif move == 'r':
                        self.rotatePiece()
                    elif move == 'C':
                        self.hold_Piece()

            # Update board state (gravity, clearing lines, spawning new piece, etc.)
            self.update()

            # Draw again
            gpx.drawBoard(pygame.display.get_surface(), self)
            pygame.display.flip()

            # Control game speed
            clock.tick(3)  # Try 3 FPS for visible AI moves



    # def auto_play(self):
    #     self.AI_playing = True
    #     gpx = Graphics()
    #     clock = pygame.time.Clock()
    #     clock.tick(60)
    #     gpx.drawBoard(pygame.display.get_surface(), self)
    #     pygame.display.flip()

    #     model = load_model('models/tetris_AI.h5')
    #     tokenizer = joblib.load("models/tokenizer.pkl")

    #     X_input = self.prepare_input()
    #     predicted_probs = model.predict(X_input)

    #     predicted_id = int(np.argmax(predicted_probs))
    #     #predicted_seq = np.argmax(predicted_probs, axis=-1)[0]
    #     #decoded_moves = tokenizer.sequences_to_texts([predicted_seq])[0].split()

    #     # check if predicted_seq is valid
    #     if predicted_id in tokenizer.index_word:
    #         decoded_moves = tokenizer.sequences_to_texts([[predicted_id]])[0].split()
    #     else:
    #         print("Invalid prediction:", predicted_id)
    #         decoded_moves = []

    #     if not decoded_moves:
    #         print("Empty move list, skipping...")
    #         self.update()
    #         gpx.drawBoard(pygame.display.get_surface(), self)
    #         pygame.display.flip()
    #         return

    #     print(decoded_moves, "***************************************")

    #     for move in decoded_moves:
    #         if move == 'R':
    #             self.moveRight()
    #         elif move == 'L':
    #             self.moveLeft()
    #         elif move == 'D':
    #             self.dropPiece()
    #         elif move == 'd':
    #             self.moveDown()
    #         elif move == 'r':
    #             self.rotatePiece()
    #         elif move == 'C':
    #             self.hold_Piece()

    #     self.update()
    #     gpx.drawBoard(pygame.display.get_surface(), self)
    #     pygame.display.flip()

        # while not self.game_ended:
        #     X_input = self.prepare_input()
        #     predicted_probs = model.predict(X_input)

        #     predicted_seq = np.argmax(predicted_probs, axis=-1)[0]
        #     decoded_moves = tokenizer.sequences_to_texts([predicted_seq])[0].split()

        #     print(decoded_moves, "***************************************")

        #     #for move in decoded_moves:
        #     i = 0
        #     print(len(decoded_moves), "+++++++++++++++++++++++++++++++++++++++")
        #     #for move in decoded_moves:
        #     while i < len(decoded_moves):
        #         #if time.time() - self.last_move_time > 0.5:
        #         move = decoded_moves[i]
        #         print(move, "///////////////////////////")
        #         if move == 'R':
        #             self.moveRight()
        #         elif move == 'L':
        #             self.moveLeft()
        #         elif move == 'D':
        #             self.dropPiece()
        #         elif move == 'd':
        #             self.moveDown()
        #         elif move == 'r':
        #             self.rotatePiece()
        #         elif move == 'C':
        #             self.hold_Piece()
        #         i += 1
        #     self.update()
        #     gpx.drawBoard(pygame.display.get_surface(), self)
        #     pygame.display.flip()

    def piece_to_int(self, piece):
        piece_map = {
            0: 0,  # Vacío
            'I': 1,  # Pieza I
            'L': 2,  # Pieza L
            'J': 3,  # Pieza J
            'O': 4,  # Pieza O
            'S': 5,  # Pieza S
            'Z': 6,  # Pieza Z
            'T': 7   # Pieza T
        }
        # Puedes hacer un mapeo de piezas específicas a enteros, por ejemplo:
        return piece_map.get(piece, 0)

    def process_board(self):
        # Asegúrate de que `board` es una lista de listas, que representa el tablero
        processed_board = [self.piece_to_int(piece) for row in self.board for piece in row]
        return np.array(processed_board)

    def prepare_input(self):
        le_piece = joblib.load("models/label_encoder.pkl")
        board_flat = self.process_board()

        current_encoded = le_piece.transform([self.currentPiece.type])[0]
        next_encoded = le_piece.transform([self.nextPieces[-1].type])[0]
        hold_encoded = le_piece.transform([self.holdPiece.type if self.holdPiece else 'none'])[0]
        hold_used = int(self.hold_used)

        X_input = np.hstack([board_flat, current_encoded, next_encoded, hold_encoded, hold_used])
        return X_input.reshape(1, -1)

#Jerry    
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