import pygame
import os

GREY = (128, 128, 128)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RAINBOW_COLORS = [(255, 0, 0), (255, 255, 0), (0, 255, 0), (0, 255, 255), (0, 0, 255)]

WIDTH, HEIGHT = 800, 600

pygame.init()
WINDOW = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_icon(pygame.image.load("Breakout.ico"))
pygame.display.set_caption("Breakout")
clock = pygame.time.Clock()
running = True

bounce_sound = pygame.mixer.Sound("Breakout_bounce.wav")
bounce_sound.set_volume(0.25)

score = 0
lives = 5
# "NES_font/PixelEmulator-xq08.ttf"
FONT = pygame.font.Font(os.path.join(os.getcwd(), 'NES_font', 'PixelEmulator-xq08.ttf'), 40)

BOX_DS = (500, 500) #box dimensions
BOX_PADDING = 100 #cage's thickness
BOX_OUTLINE = pygame.Rect((WIDTH // 2 - (BOX_DS[0] + BOX_PADDING) // 2, HEIGHT - BOX_DS[1]),
                          (BOX_DS[0] + BOX_PADDING, BOX_DS[1] + BOX_PADDING))
#grey outline
BOX = pygame.Rect((WIDTH // 2 - BOX_DS[0] // 2, HEIGHT - BOX_DS[1] + BOX_PADDING // 2), BOX_DS)
#black box for game

class Rainbow:
    def __init__(self, ypos, columns, tile_height):
        self.YPOS = ypos
        self.COLUMNS = columns
        self.TILE_WIDTH = BOX_DS[0] // columns
        self.TILE_HEIGHT = tile_height
        self.reset()

    def get_empty(self):
        return self.tiles == [[False for xpos in range(self.COLUMNS)] for row in RAINBOW_COLORS]

    def reset(self):
        self.tiles = [[pygame.Rect(xpos * self.TILE_WIDTH + BOX.left, self.YPOS + color_index * self.TILE_HEIGHT, self.TILE_WIDTH, self.TILE_HEIGHT)
                       for xpos in range(self.COLUMNS)]
                      for color_index in range(len(RAINBOW_COLORS))]

    def draw(self):
        for colori, row in enumerate(self.tiles):
            for xpos, tile in enumerate(row):
                if tile:
                    pygame.draw.rect(WINDOW, RAINBOW_COLORS[colori], tile)

rainbow = Rainbow(200, 25, 15)

class Paddle(pygame.Rect):
    def __init__(self, xpos, ypos, width, height, speed):
        pygame.Rect.__init__(self, xpos, ypos, width, height)
        self.SPEED = speed

    def control_paddle(self):
        """Moves paddle left or right using aad keys. Checks for collision with box's edge."""
        keys = pygame.key.get_pressed()

        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            if self.left > BOX.left:
                self.left -= self.SPEED
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            if self.right < BOX.right:
                self.left += self.SPEED

PADDLE_WIDTH, PADDLE_HEIGHT = 100, 20
paddle = Paddle(WIDTH // 2 - PADDLE_WIDTH // 2, 500, PADDLE_WIDTH, PADDLE_HEIGHT, 5)

class Ball(pygame.Rect):
    def __init__(self, xpos, ypos, width, height, speed):
        pygame.Rect.__init__(self, xpos, ypos, width, height)
        self.SPEED = speed
        self.start_pos = (xpos, ypos)
        self.directions = [-1 * speed, 1 * speed]

    def reset(self):
        """Ball back at its original pos."""
        self.topleft = self.start_pos

    def detect_collision(self, rect):
        """Detects collision between ball and a Rect.
        Returns True if it collided and changes ball's direction."""
        if self.colliderect(rect):
            if self.left - rect.right in range(-5,5) and self.directions[0] < 0:
                self.directions[0] *= -1
            if self.right - rect.left in range(-5,5) and self.directions[0] > 0:
                self.directions[0] *= -1
            if self.top - rect.bottom in range(-5,5) and self.directions[1] < 0:
                self.directions[1] *= -1
            if self.bottom - rect.top in range(-5,5) and self.directions[1] > 0:
                self.directions[1] *= -1
            bounce_sound.play()
            return True
        return False
        #if rect and ball colide, checks which side collided and changes direction to bounce off.

    def move_ball(self):
        global score, lives

        if self.left < BOX.left or self.right > BOX.right:
            self.directions[0] *= -1
        if self.top < BOX.top:
            self.directions[1] *= -1
        #bounce off walls

        if self.bottom > HEIGHT:
            self.reset()
            lives -= 1
        #Ball goes off screen.

        self.detect_collision(paddle)

        for xpos, row in enumerate(rainbow.tiles):
            for ypos, tile in enumerate(row):
                if tile:
                    if self.detect_collision(tile):
                        rainbow.tiles[xpos][ypos] = False
                        score += xpos * - 1 + len(RAINBOW_COLORS)
                        #eliminates rainbow blocks
                        #adds one point per row going upwards in the rainbow.
        #rainbow collision

        self.left += self.directions[0]
        self.top += self.directions[1]
        #Moves ball.

BALL_WIDTH = rainbow.TILE_WIDTH
ball = Ball(WIDTH // 2 - BALL_WIDTH // 2, HEIGHT // 2 - BALL_WIDTH // 2, BALL_WIDTH, BALL_WIDTH, 2)

while running:
    clock.tick(60)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    WINDOW.fill(BLACK)

    pygame.draw.rect(WINDOW, GREY, BOX_OUTLINE)
    pygame.draw.rect(WINDOW, BLACK, BOX)

    if rainbow.get_empty():
        rainbow.reset()
    #Resets rainbow after it's broken completely.

    rainbow.draw()

    ball.move_ball()
    pygame.draw.rect(WINDOW, WHITE, ball)

    paddle.control_paddle()
    pygame.draw.rect(WINDOW, WHITE, paddle)

    text = FONT.render(str(score), True, WHITE)
    WINDOW.blit(text, (WIDTH // 3 - text.get_width() // 2, BOX.top // 2 - text.get_height() // 2))

    text = FONT.render(str(lives), True, WHITE)
    WINDOW.blit(text, (WIDTH * 2 // 3 - text.get_width() // 2, BOX.top // 2 - text.get_height() // 2))

    if lives == 0:
        running = False

    pygame.display.update()

pygame.quit()