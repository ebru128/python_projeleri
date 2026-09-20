import pygame
import random
import math

# Pygame Başlatma
pygame.init()

# Ekran Ayarları
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Fruit Ninja - Pygame")
clock = pygame.time.Clock()

# Renkler
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (230, 50, 50)
GREEN = (50, 205, 50)
ORANGE = (255, 165, 0)
GRAY = (50, 50, 50)

# Oyun Değişkenleri
score = 0
lives = 3
font = pygame.font.SysFont("Helvetica", 32, bold=True)

class Fruit:
    def __init__(self):
        self.radius = 30
        self.x = random.randint(100, WIDTH - 100)
        self.y = HEIGHT + self.radius
        
        # Yukarı doğru fırlatma hızı ve hafif yatay ivme
        self.vx = random.uniform(-3, 3)
        self.vy = random.uniform(-18, -13)
        self.gravity = 0.4
        
        # Rastgele Meyve Tipi veya Bomba
        self.type = random.choice(["apple", "orange", "bomb"])
        if self.type == "apple":
            self.color = RED
        elif self.type == "orange":
            self.color = ORANGE
        else:
            self.color = GRAY  # Bomba

        self.sliced = False

    def update(self):
        # Yerçekimi fiziği
        self.x += self.vx
        self.y += self.vy
        self.vy += self.gravity

    def draw(self, surface):
        if not self.sliced:
            pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.radius)
            if self.type == "bomb":
                # Bombanın fitili
                pygame.draw.line(surface, RED, (int(self.x), int(self.y - self.radius)), 
                                 (int(self.x), int(self.y - self.radius - 10)), 3)

# Meyve Listesi ve Bıçak İzi (Trail)
fruits = []
blade_trail = []
SPAWN_EVENT = pygame.USEREVENT + 1
pygame.time.set_timer(SPAWN_EVENT, 1000)  # Her 1 saniyede yeni nesne fırlat

running = True
game_over = False

while running:
    clock.tick(60)  # 60 FPS
    screen.fill(BLACK)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == SPAWN_EVENT and not game_over:
            fruits.append(Fruit())

    if not game_over:
        # Fare Hareketini ve Bıçak İzini Takip Et
        mouse_pos = pygame.mouse.get_pos()
        mouse_pressed = pygame.mouse.get_pressed()[0]  # Sol tık basılı mı?

        if mouse_pressed:
            blade_trail.append(mouse_pos)
            if len(blade_trail) > 10:  # İz uzunluğunu sınırla
                blade_trail.pop(0)
        else:
            blade_trail.clear()

        # Meyveleri Güncelle ve Çiz
        for fruit in fruits[:]:
            fruit.update()
            fruit.draw(screen)

            # Kesme Kontrolü (Fare tıklaması veya sürüklemesi ile temas var mı?)
            if mouse_pressed and not fruit.sliced:
                distance = math.hypot(mouse_pos[0] - fruit.x, mouse_pos[1] - fruit.y)
                if distance < fruit.radius:
                    fruit.sliced = True
                    if fruit.type == "bomb":
                        game_over = True
                    else:
                        score += 10
                        fruits.remove(fruit)

            # Ekrandan Düşen Meyveleri Temizle ve Can Düş
            if fruit.y > HEIGHT + 50:
                if not fruit.sliced and fruit.type != "bomb":
                    lives -= 1
                    if lives <= 0:
                        game_over = True
                fruits.remove(fruit)

        # Bıçak İzini Çiz (Çizgi şeklinde)
        if len(blade_trail) > 1:
            pygame.draw.lines(screen, WHITE, False, blade_trail, 4)

        # Skor ve Can Bilgisi
        score_text = font.render(f"Skor: {score}", True, WHITE)
        lives_text = font.render(f"Can: {lives}", True, RED)
        screen.blit(score_text, (20, 20))
        screen.blit(lives_text, (WIDTH - 130, 20))

    else:
        # Game Over Ekranı
        over_text = font.render("OYUN BİTTİ! Skorunuz: " + str(score), True, WHITE)
        restart_text = font.render("Yeniden Başlamak İçin 'R' Tuşuna Basın", True, ORANGE)
        screen.blit(over_text, (WIDTH // 2 - 180, HEIGHT // 2 - 50))
        screen.blit(restart_text, (WIDTH // 2 - 250, HEIGHT // 2 + 10))

        keys = pygame.key.get_pressed()
        if keys[pygame.K_r]:
            score = 0
            lives = 3
            fruits.clear()
            blade_trail.clear()
            game_over = False

    pygame.display.flip()

pygame.quit()