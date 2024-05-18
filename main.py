import pygame
import client  # Importing the client.py as a module

# Initialize Pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 500, 700
FONT_SIZE = 60
INPUT_BOX_HEIGHT = 50
BUTTON_WIDTH, BUTTON_HEIGHT = 200, 50

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
LIGHT_GRAY = (220, 220, 220)
TITLE_COLOR = (8, 230, 250)

# Fonts
FONT = pygame.font.SysFont('Comic Sans MS', FONT_SIZE)
INPUT_FONT = pygame.font.SysFont('Comic Sans MS', 30)
TITLE_FONT = pygame.font.SysFont('Comic Sans MS', 30)


def main_menu():
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Tic-Tac-Toe Main Menu")

    # Load background image
    background_image = pygame.image.load('background.png')
    background_image = pygame.transform.scale(background_image, (WIDTH, HEIGHT))

    input_box = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 - 25, 200, INPUT_BOX_HEIGHT)
    button_box = pygame.Rect(WIDTH // 2 - BUTTON_WIDTH // 2, HEIGHT // 2 + 50, BUTTON_WIDTH, BUTTON_HEIGHT)

    name = ''
    active = False
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                return None
            if event.type == pygame.MOUSEBUTTONDOWN:
                if input_box.collidepoint(event.pos):
                    active = True
                else:
                    active = False
                if button_box.collidepoint(event.pos) and name:
                    running = False
            if event.type == pygame.KEYDOWN:
                if active:
                    if event.key == pygame.K_RETURN:
                        running = False
                    elif event.key == pygame.K_BACKSPACE:
                        name = name[:-1]
                    else:
                        name += event.unicode

        screen.blit(background_image, (0, 0))

        # Render the title
        title_surface = TITLE_FONT.render("Enter your name:", True, WHITE)
        title_rect = title_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 75))
        screen.blit(title_surface, title_rect)

        # Render the current text
        txt_surface = INPUT_FONT.render(name, True, WHITE)
        width = max(200, txt_surface.get_width() + 10)
        input_box.w = width

        # Draw input box with background color and border

        pygame.draw.rect(screen, WHITE, input_box, 2)
        screen.blit(txt_surface, (input_box.x + 5, input_box.y + 5))

        # Render the button text
        button_text = FONT.render('PLAY', True, TITLE_COLOR)
        button_text_rect = button_text.get_rect(center=button_box.center)
        screen.blit(button_text, button_text_rect)

        pygame.display.flip()

    return name

if __name__ == "__main__":
    player_name = main_menu()
    if player_name:
        game = client.Game(player_name)
        game.run()
