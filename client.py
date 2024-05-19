import sys
import socket
import threading
import pygame

# Initialize Pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 500, 900
GRID_SIZE = 10
CELL_SIZE = WIDTH // GRID_SIZE
FONT_SIZE = 60
CHAT_FONT_SIZE = 20
CHAT_BOX_HEIGHT = 300  # Adjusted height for chat box

# Colors
GREEN = (1, 101, 179)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

# Fonts
FONT = pygame.font.SysFont('Comic Sans MS', FONT_SIZE)
CHAT_FONT = pygame.font.SysFont('Comic Sans MS', CHAT_FONT_SIZE)

class SocketChat:
    def __init__(self):
        self.IP = "localhost"
        self.PORT = 5555
        self.client_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)

    #receive data from server
    def receive(self):
        try:
            message = self.client_socket.recv(1024).decode("utf-8")
            return message
        except OSError as e:
            print("Error receiving data:", e)
            return None
    #send data
    def write(self, msg: str):
        self.client_socket.send(msg.encode("utf-8"))

class Game:
    def __init__(self, name):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Tic-Tac-Toe with Chat")
        self.chat_object = SocketChat()
        self.chat_object.client_socket.connect((self.chat_object.IP, self.chat_object.PORT))
        self.chat_object.write(f"NAME:{name}")  # Send the player's name to the server
        self.player = self.chat_object.receive()
        self.name = name  # Store the player's name
        self.turn = "X"
        self.other_player = "O" if self.player == "X" else "X"
        self.board = [["" for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        self.chat_messages = []
        self.chat_input = []
        self.chat_scroll_y = 0
        self.running = True
        self.show_chat = True
        self.game_over = False
        #start new thread to receive messages form the server
        threading.Thread(target=self.handle_incoming_messages).start()

    def handle_incoming_messages(self):
        while self.running:
            message = self.chat_object.receive() # receive message from server
            if message.startswith("CHAT:"):
                self.chat_messages.append(message[5:])
            elif message.startswith("WINNER:"):
                winner = message.split(":")[1]
                self.show_winner_message(winner)
                self.reset_game()
            else:
                i, j = map(int, message.split(" "))
                self.board[i][j] = self.turn
                self.toggle_turn()
                self.check_winner()

    def draw_grid(self):
        for x in range(0, WIDTH, CELL_SIZE):
            pygame.draw.line(self.screen, BLACK, (x, 0), (x, WIDTH))
        for y in range(0, WIDTH, CELL_SIZE):
            pygame.draw.line(self.screen, BLACK, (0, y), (WIDTH, y))

    def draw_board(self):
        for i in range(GRID_SIZE):
            for j in range(GRID_SIZE):
                if self.board[i][j] != "":
                    if self.board[i][j] == "X":
                        text = FONT.render("X", True, RED)
                    else:
                        text = FONT.render("O", True, BLUE)
                    text_rect = text.get_rect(center=(j * CELL_SIZE + CELL_SIZE // 2, i * CELL_SIZE + CELL_SIZE // 2))
                    self.screen.blit(text, text_rect)

    def draw_chat_box(self):
        chat_bg_rect = pygame.Rect(0, WIDTH, WIDTH, CHAT_BOX_HEIGHT)
        pygame.draw.rect(self.screen, WHITE, chat_bg_rect)

        chat_input_bg_rect = pygame.Rect(WIDTH // 2 - 200, HEIGHT - 90, 400, 40)
        pygame.draw.rect(self.screen, GREEN, chat_input_bg_rect)

        chat_input_text = "".join(self.chat_input[-31:])
        chat_input_surf = CHAT_FONT.render(chat_input_text if chat_input_text else "Chat here", True, WHITE)
        input_text_rect = chat_input_surf.get_rect(center=(WIDTH // 2, HEIGHT - 70))
        self.screen.blit(chat_input_surf, input_text_rect)

        chat_surface = pygame.Surface((WIDTH - 20, CHAT_BOX_HEIGHT - 40))
        chat_surface.fill(WHITE)
        pygame.draw.rect(chat_surface, BLACK, chat_surface.get_rect(), 2)
        y_offset = CHAT_BOX_HEIGHT - 70 + self.chat_scroll_y
        for message in reversed(self.chat_messages):
            message_surface = CHAT_FONT.render(message, True, BLACK)
            chat_surface.blit(message_surface, (10, y_offset))
            y_offset -= CHAT_FONT_SIZE + 5
        self.screen.blit(chat_surface, (10, HEIGHT - CHAT_BOX_HEIGHT - 60))

    def draw_player_info(self):
        player_color = RED if self.player == "X" else BLUE
        player_info_surface = CHAT_FONT.render(f"Player: {self.player} ({self.name}) Turn: {self.turn}", True, player_color)
        self.screen.blit(player_info_surface, (10, WIDTH + 5))

        pygame.draw.rect(self.screen, GREEN, (WIDTH - 110, WIDTH + 5, 100, 35))
        restart_text = CHAT_FONT.render("Restart", True, WHITE)
        self.screen.blit(restart_text, (WIDTH - 100, WIDTH + 8))

    def toggle_turn(self):
        self.turn = "O" if self.turn == "X" else "X"

    def check_winner(self):
        winning_states = []
        # Horizontal winning states
        for i in range(GRID_SIZE):
            for j in range(GRID_SIZE - 4):
                winning_states.append([(i, j + k) for k in range(5)])

        # Vertical winning states
        for i in range(GRID_SIZE - 4):
            for j in range(GRID_SIZE):
                winning_states.append([(i + k, j) for k in range(5)])

        # Diagonal winning states (top-left to bottom-right)
        for i in range(GRID_SIZE - 4):
            for j in range(GRID_SIZE - 4):
                winning_states.append([(i + k, j + k) for k in range(5)])

        # Diagonal winning states (top-right to bottom-left)
        for i in range(GRID_SIZE - 4):
            for j in range(4, GRID_SIZE):
                winning_states.append([(i + k, j - k) for k in range(5)])

        for state in winning_states:
            symbols = [self.board[i][j] for i, j in state]
            if symbols[0] != "" and all(symbol == symbols[0] for symbol in symbols):
                winner = symbols[0]
                self.show_winner_message(winner)
                self.chat_object.write(f"WINNER:{winner}")
                pygame.time.wait(1000)
                self.reset_game()
                break

    def reset_game(self):
        self.board = [["" for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        self.game_over = False

    def show_winner_message(self, winner):
        winner_font = pygame.font.SysFont('Comic Sans MS', 80)
        winner_text = winner_font.render(f"{winner} Wins!", True, RED if winner == "X" else BLUE)
        winner_text_rect = winner_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        self.screen.blit(winner_text, winner_text_rect)
        pygame.display.flip()
        pygame.time.wait(3000)

    def handle_event(self, event):
        if event.type == pygame.QUIT:
            self.running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if not self.game_over:
                x, y = event.pos
                if WIDTH - 110 <= x <= WIDTH - 10 and WIDTH + 5 <= y <= WIDTH + 45:
                    self.reset_game()  # Thiết lập lại trò chơi khi nhấn nút choi lại
                if y < WIDTH:
                    i, j = y // CELL_SIZE, x // CELL_SIZE
                    if self.board[i][j] == "" and self.player == self.turn:
                        self.board[i][j] = self.player
                        self.chat_object.write(f"{i} {j}")
                        self.toggle_turn()
                        self.check_winner()
                elif pygame.Rect(0, WIDTH, WIDTH, CHAT_BOX_HEIGHT).collidepoint(event.pos):
                    if 10 <= x <= WIDTH - 10 and HEIGHT - 90 <= y <= HEIGHT - 50:
                        self.show_chat = True
                    elif 455 <= x <= 505 and HEIGHT - 50 <= y <= HEIGHT - 10:
                        self.chat_object.write(f"CHAT:{self.name}: {''.join(self.chat_input)}")
                        self.chat_messages.append(f"Me: {''.join(self.chat_input)}")
                        self.chat_input = []
                        self.show_chat = True
        elif event.type == pygame.KEYDOWN:
            if not self.game_over and self.show_chat:
                if event.key == pygame.K_RETURN:
                    self.chat_object.write(f"CHAT:{self.name}: {''.join(self.chat_input)}")
                    self.chat_messages.append(f"Me: {''.join(self.chat_input)}")
                    self.chat_input = []
                elif event.key == pygame.K_BACKSPACE:
                    if self.chat_input:
                        self.chat_input.pop()
                else:
                    self.chat_input.append(event.unicode)


    def run(self):
        while self.running:
            self.screen.fill(WHITE)
            self.draw_grid()
            self.draw_board()
            self.draw_chat_box()
            self.draw_player_info()

            for event in pygame.event.get():
                self.handle_event(event)
            pygame.display.flip()
        pygame.quit()
        self.chat_object.client_socket.close()

