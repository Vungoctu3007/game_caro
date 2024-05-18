import sys
import socket
import threading
import pygame

# Initialize Pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 600, 900
GRID_SIZE = 3
CELL_SIZE = WIDTH // GRID_SIZE
FONT_SIZE = 60
CHAT_FONT_SIZE = 20
CHAT_BOX_HEIGHT = 200

# Colors
GREEN = (1, 101, 179)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
CHAT_BG_COLOR = (200, 200, 200)

# Fonts
FONT = pygame.font.SysFont('Comic Sans MS', FONT_SIZE)
CHAT_FONT = pygame.font.SysFont('Comic Sans MS', CHAT_FONT_SIZE)

class SocketChat:
    def __init__(self):
        self.IP = "localhost"
        self.PORT = 5555
        self.client_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)

    def receive(self):
        message = self.client_socket.recv(1024).decode("utf-8")
        return message

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

        threading.Thread(target=self.handle_incoming_messages).start()

    def handle_incoming_messages(self):
        while self.running:
            message = self.chat_object.receive()
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
                    text = FONT.render(self.board[i][j], True, RED if self.board[i][j] == "X" else BLUE)
                    self.screen.blit(text, (j * CELL_SIZE + CELL_SIZE // 3, i * CELL_SIZE + CELL_SIZE // 4))

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

    def toggle_turn(self):
        self.turn = "O" if self.turn == "X" else "X"

    def check_winner(self):
        winning_states = [
            [(0, 0), (0, 1), (0, 2)],
            [(1, 0), (1, 1), (1, 2)],
            [(2, 0), (2, 1), (2, 2)],
            [(0, 0), (1, 0), (2, 0)],
            [(0, 1), (1, 1), (2, 1)],
            [(0, 2), (1, 2), (2, 2)],
            [(0, 0), (1, 1), (2, 2)],
            [(0, 2), (1, 1), (2, 0)],
        ]
        for state in winning_states:
            if self.board[state[0][0]][state[0][1]] != "" and \
                self.board[state[0][0]][state[0][1]] == self.board[state[1][0]][state[1][1]] == self.board[state[2][0]][state[2][1]]:
                winner = self.board[state[0][0]][state[0][1]]
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
                if y < WIDTH:
                    i, j = y // CELL_SIZE, x // CELL_SIZE
                    if self.board[i][j] == "" and self.player == self.turn:
                        self.board[i][j] = self.player
                        self.chat_object.write(f"{i} {j}")
                        self.toggle_turn()
                        self.check_winner()
                elif pygame.Rect(0, WIDTH, WIDTH, CHAT_BOX_HEIGHT).collidepoint(event.pos):
                    if 455 <= x <= 505 and HEIGHT - 50 <= y <= HEIGHT - 10:
                        self.chat_object.write(f"CHAT:{self.name}: {''.join(self.chat_input)}")
                        self.chat_messages.append(f"Me: {''.join(self.chat_input)}")
                        self.chat_input = []
                        self.show_chat = True
                    elif 10 <= x <= 50 and HEIGHT - 50 <= y <= HEIGHT - 10:
                        self.show_chat = not self.show_chat
        elif event.type == pygame.KEYDOWN:
            if not self.game_over:
                if event.key == pygame.K_RETURN:
                    self.chat_object.write(f"CHAT:{self.name}: {''.join(self.chat_input)}")
                    self.chat_messages.append(f"Me: {''.join(self.chat_input)}")
                    self.chat_input = []
                    self.show_chat = True
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

if __name__ == "__main__":
    name = input("Enter your name: ")
    game = Game(name)
