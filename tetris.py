import pygame
import random
import sys

# =================================================
# GENEL AYARLAR
# =================================================
CELL = 30
COLS = 10
ROWS = 20
WIDTH = COLS * CELL
HEIGHT = ROWS * CELL
SIDE = 240
SCREEN_WIDTH = WIDTH + SIDE
FPS = 60

BLACK = (0, 0, 0)
GRAY  = (40, 40, 40)
WHITE = (255, 255, 255)
RED   = (255, 0, 0) 

COLORS = [
    (0, 255, 255), (255, 255, 0), (128, 0, 128),
    (0, 255, 0), (255, 0, 0), (0, 0, 255), (255, 165, 0)
]

SHAPES = [
    [[1,1,1,1]], [[1,1],[1,1]], [[0,1,0],[1,1,1]],
    [[0,1,1],[1,1,0]], [[1,1,0],[0,1,1]], [[1,0,0],[1,1,1]], [[0,0,1],[1,1,1]]
]

class Piece:
    def __init__(self, x, y, shape, color):
        self.x = x
        self.y = y
        self.shape = shape
        self.color = color

    def rotate(self):
        self.shape = list(zip(*self.shape[::-1]))

def create_grid(locked):
    grid = [[BLACK for _ in range(COLS)] for _ in range(ROWS)]
    for (x, y), color in locked.items():
        if y >= 0:
            grid[y][x] = color
    return grid

def valid_space(piece, grid):
    for y, row in enumerate(piece.shape):
        for x, cell in enumerate(row):
            if cell:
                px = piece.x + x
                py = piece.y + y
                if px < 0 or px >= COLS or py >= ROWS:
                    return False
                if py >= 0 and grid[py][px] != BLACK:
                    return False
    return True

def clear_rows(grid, locked):
    cleared = 0
    for y in range(ROWS - 1, -1, -1):
        if BLACK not in grid[y]:
            cleared += 1
            for x in range(COLS):
                locked.pop((x, y), None)
            for (lx, ly) in sorted(list(locked), key=lambda k: k[1], reverse=True):
                if ly < y:
                    locked[(lx, ly + 1)] = locked.pop((lx, ly))
    return cleared

def draw_text_middle(surface, text, score):
    """Oyun bitişinde büyük yazı ve skoru gösterir"""
    font_big = pygame.font.SysFont("arial", 60, bold=True)
    font_small = pygame.font.SysFont("arial", 30, bold=True)
    
    label_msg = font_big.render(text, True, RED)
    label_score = font_small.render(f"TOPLAM PUAN: {score}", True, WHITE)
    
    # Ortala
    surface.blit(label_msg, (WIDTH // 2 - label_msg.get_width() // 2, HEIGHT // 2 - 50))
    surface.blit(label_score, (WIDTH // 2 - label_score.get_width() // 2, HEIGHT // 2 + 30))

def draw_grid(surface):
    for x in range(COLS):
        pygame.draw.line(surface, GRAY, (x*CELL, 0), (x*CELL, HEIGHT))
    for y in range(ROWS):
        pygame.draw.line(surface, GRAY, (0, y*CELL), (WIDTH, y*CELL))

def draw_side(surface, score, level, speed):
    font = pygame.font.SysFont("arial", 18)
    lines = [
        "KONTROLLER", "← → : Hareket", "↓   : Hizli dus",
        "↑   : Dondur", "SPACE: Aninda dus", "ESC  : Menu",
        "", f"Skor   : {score}", f"Seviye : {level}", f"Hiz    : {round(speed,3)} sn"
    ]
    y = 20
    for text in lines:
        surface.blit(font.render(text, True, WHITE), (WIDTH + 15, y))
        y += 26

def draw_window(surface, grid, score, level, speed):
    surface.fill(BLACK)
    for y in range(ROWS):
        for x in range(COLS):
            pygame.draw.rect(surface, grid[y][x], (x*CELL, y*CELL, CELL, CELL))
    draw_grid(surface)
    draw_side(surface, score, level, speed)

def get_piece():
    i = random.randint(0, len(SHAPES)-1)
    return Piece(COLS//2 - 1, 0, SHAPES[i], COLORS[i]) # Y koordinatı 0 yapıldı

def speed_menu(screen):
    font_big = pygame.font.SysFont("arial", 36)
    font = pygame.font.SysFont("arial", 24)
    options = [("1 - Yavas", 0.16), ("2 - Normal", 0.12), ("3 - Hizli", 0.08), ("4 - COK HIZLI", 0.04)]
    
    while True:
        screen.fill(BLACK)
        title = font_big.render("HIZ SEC (X5 MODU)", True, WHITE)
        screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 120))
        y = 200
        for text, _ in options:
            screen.blit(font.render(text, True, WHITE), (SCREEN_WIDTH//2 - 120, y))
            y += 45
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key in [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4]:
                    return options[event.key - pygame.K_1][1]

def game(screen, start_speed):
    clock = pygame.time.Clock()
    locked = {}
    piece = get_piece()
    score, level, lines = 0, 1, 0
    fall_speed, fall_time = start_speed, 0

    while True:
        grid = create_grid(locked)
        fall_time += clock.get_rawtime()
        clock.tick(FPS)

        # Otomatik Düşme
        if fall_time / 1000 >= fall_speed:
            fall_time = 0
            piece.y += 1
            if not valid_space(piece, grid):
                piece.y -= 1
                # Kilitle
                for y, row in enumerate(piece.shape):
                    for x, cell in enumerate(row):
                        if cell:
                            locked[(piece.x + x, piece.y + y)] = piece.color
                
                # Satır temizle ve skor güncelle
                cleared = clear_rows(grid, locked)
                if cleared > 0:
                    lines += cleared
                    score += cleared * 100
                    if lines >= level * 5:
                        level += 1
                        fall_speed = max(0.02, fall_speed - 0.01)

                # Yeni parça oluştur
                piece = get_piece()
                
                # Yeni parça direkt çakışıyorsa OYUN BİTTİ
                if not valid_space(piece, grid):
                    draw_window(screen, grid, score, level, fall_speed)
                    draw_text_middle(screen, "GAME OVER", score)
                    pygame.display.update()
                    pygame.time.delay(3000)
                    return

        # Klavye Kontrolleri
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE: return
                if event.key == pygame.K_LEFT:
                    piece.x -= 1
                    if not valid_space(piece, grid): piece.x += 1
                elif event.key == pygame.K_RIGHT:
                    piece.x += 1
                    if not valid_space(piece, grid): piece.x -= 1
                elif event.key == pygame.K_DOWN:
                    piece.y += 1
                    if not valid_space(piece, grid): piece.y -= 1
                elif event.key == pygame.K_UP:
                    old = piece.shape
                    piece.rotate()
                    if not valid_space(piece, grid): piece.shape = old
                elif event.key == pygame.K_SPACE:
                    while True:
                        piece.y += 1
                        if not valid_space(piece, grid):
                            piece.y -= 1
                            break

        # Aktif parçayı grid'e geçici olarak ekle
        for y, row in enumerate(piece.shape):
            for x, cell in enumerate(row):
                if cell and piece.y + y >= 0:
                    grid[piece.y + y][piece.x + x] = piece.color
        
        draw_window(screen, grid, score, level, fall_speed)
        pygame.display.update()

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, HEIGHT))
    pygame.display.set_caption("Tetris X5 Fixed")
    while True:
        speed = speed_menu(screen)
        game(screen, speed)

if __name__ == "__main__":
    main()