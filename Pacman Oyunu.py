import pygame
import sys
import math

# Pygame'i başlat
pygame.init()

# Ekran Boyutları ve Renkler
GENISLIK, YUKSEKLIK = 600, 600
pygame.display.set_caption("Python Pac-Man")
ekran = pygame.display.set_mode((GENISLIK, YUKSEKLIK))

# Renk Tanımları
SIYAH = (0, 0, 0)
SARI = (255, 255, 0)
MAVI = (0, 0, 255)
BEYAZ = (255, 255, 255)
KIRMIZI = (255, 0, 0)
PEMBE = (255, 105, 180)

# Oyun Hızı
SAAT = pygame.time.Clock()
FPS = 60

# Harita Tasarımı (1: Duvar, 0: Yem, 2: Boş Yol)
HARITA = [
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 1, 1, 0, 0, 1, 0, 0, 1, 1, 0, 1, 0, 1],
    [1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1],
    [1, 0, 0, 0, 1, 1, 2, 1, 1, 0, 0, 0, 0, 0, 1],
    [1, 0, 1, 0, 1, 2, 2, 2, 1, 0, 1, 0, 1, 0, 1],
    [1, 0, 1, 0, 1, 1, 1, 1, 1, 0, 1, 0, 1, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
]

HUZRE_BOYUTU = 40

# Pac-Man Sınıfı
class Pacman:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.hiz = 4
        self.yon_x = 1
        self.yon_y = 0
        self.boyut = 15
        self.puan = 0
        self.agiz_acik = True

    def hareket_et(self, duvarlar):
        # Gelecekteki konumu hesapla
        yeni_x = self.x + self.yon_x * self.hiz
        yeni_y = self.y + self.yon_y * self.hiz

        # Duvar çarpışma kontrolü
        pacman_kutusu = pygame.Rect(yeni_x - self.boyut, yeni_y - self.boyut, self.boyut * 2, self.boyut * 2)
        carpisma = False

        for duvar in duvarlar:
            if pacman_kutusu.colliderect(duvar):
                carpisma = True
                break

        if not carpisma:
            self.x = yeni_x
            self.y = yeni_y

    def ciz(self, pencere):
        merkez = (int(self.x), int(self.y))
        pygame.draw.circle(pencere, SARI, merkez, self.boyut)

        # Pac-Man'in ağzını hareket yönüne göre siyah bir üçgenle oluştur.
        yon_acisi = math.atan2(self.yon_y, self.yon_x) if self.yon_x or self.yon_y else 0
        agiz_acisi = math.radians(32 if self.agiz_acik else 12)
        agiz_sol = (
            int(self.x + math.cos(yon_acisi - agiz_acisi) * self.boyut),
            int(self.y + math.sin(yon_acisi - agiz_acisi) * self.boyut),
        )
        agiz_sag = (
            int(self.x + math.cos(yon_acisi + agiz_acisi) * self.boyut),
            int(self.y + math.sin(yon_acisi + agiz_acisi) * self.boyut),
        )
        pygame.draw.polygon(pencere, SIYAH, [merkez, agiz_sol, agiz_sag])

        # Küçük göz, görünümü emojiye yaklaştırır.
        goz_x = int(self.x + math.cos(yon_acisi - math.pi / 2) * 7)
        goz_y = int(self.y + math.sin(yon_acisi - math.pi / 2) * 7)
        pygame.draw.circle(pencere, SIYAH, (goz_x, goz_y), 2)


class Canavar:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.hiz = 2
        self.boyut = 15

    def hareket_et(self, pacman, duvarlar):
        # Canavar önce daha uzak olduğu eksende ilerlemeyi dener.
        fark_x = pacman.x - self.x
        fark_y = pacman.y - self.y
        eksenler = [(1, 0), (-1, 0)] if abs(fark_x) >= abs(fark_y) else [(0, 1), (0, -1)]
        eksenler += [(0, 1), (0, -1)] if abs(fark_x) >= abs(fark_y) else [(1, 0), (-1, 0)]

        for yon_x, yon_y in eksenler:
            if (yon_x and fark_x * yon_x < 0) or (yon_y and fark_y * yon_y < 0):
                continue

            yeni_x = self.x + yon_x * self.hiz
            yeni_y = self.y + yon_y * self.hiz
            canavar_kutusu = pygame.Rect(
                yeni_x - self.boyut, yeni_y - self.boyut,
                self.boyut * 2, self.boyut * 2
            )
            if not any(canavar_kutusu.colliderect(duvar) for duvar in duvarlar):
                self.x = yeni_x
                self.y = yeni_y
                return

    def carpisti_mi(self, pacman):
        uzaklik = pygame.Vector2(self.x, self.y).distance_to((pacman.x, pacman.y))
        return uzaklik < self.boyut + pacman.boyut

    def ciz(self, pencere):
        merkez = (int(self.x), int(self.y))
        pygame.draw.circle(pencere, PEMBE, merkez, self.boyut)
        pygame.draw.rect(pencere, PEMBE, (int(self.x - self.boyut), int(self.y), self.boyut * 2, self.boyut))
        pygame.draw.circle(pencere, BEYAZ, (int(self.x - 6), int(self.y - 3)), 4)
        pygame.draw.circle(pencere, BEYAZ, (int(self.x + 6), int(self.y - 3)), 4)
        pygame.draw.circle(pencere, SIYAH, (int(self.x - 6), int(self.y - 3)), 2)
        pygame.draw.circle(pencere, SIYAH, (int(self.x + 6), int(self.y - 3)), 2)

# Ana Oyun Döngüsü
def oyunu_baslat():
    pacman = Pacman(60, 60)
    canavar = Canavar(540, 300)
    duvarlar = []
    yemler = []

    # Haritayı Çözümleme
    for satir_idx, satir in enumerate(HARITA):
        for sutun_idx, hucre in enumerate(satir):
            x = sutun_idx * HUZRE_BOYUTU
            y = satir_idx * HUZRE_BOYUTU

            if hucre == 1:
                duvarlar.append(pygame.Rect(x, y, HUZRE_BOYUTU, HUZRE_BOYUTU))
            elif hucre == 0:
                yemler.append(pygame.Rect(x + 18, y + 18, 5, 5))

    font = pygame.font.SysFont("Arial", 20, bold=True)

    calisiyor = True
    while calisiyor:
        SAAT.tick(FPS)

        # Olay (Event) Yönetimi
        for olay in pygame.event.get():
            if olay.type == pygame.QUIT:
                calisiyor = False

            if olay.type == pygame.KEYDOWN:
                if olay.key == pygame.K_LEFT:
                    pacman.yon_x = -1
                    pacman.yon_y = 0
                elif olay.key == pygame.K_RIGHT:
                    pacman.yon_x = 1
                    pacman.yon_y = 0
                elif olay.key == pygame.K_UP:
                    pacman.yon_x = 0
                    pacman.yon_y = -1
                elif olay.key == pygame.K_DOWN:
                    pacman.yon_x = 0
                    pacman.yon_y = 1

        # Pac-Man'in ağzını hafifçe hareket ettir.
        pacman.agiz_acik = (pygame.time.get_ticks() // 140) % 2 == 0

        # Pacman Hareket
        pacman.hareket_et(duvarlar)
        canavar.hareket_et(pacman, duvarlar)

        if canavar.carpisti_mi(pacman):
            messagebox.showerror("Oyun Bitti", "Canavar seni yakaladı! 👻")
            calisiyor = False
            continue

        # Yem Toplama Kontrolü
        pacman_kutusu = pygame.Rect(pacman.x - pacman.boyut, pacman.y - pacman.boyut, pacman.boyut * 2, pacman.boyut * 2)
        for yem in yemler[:]:
            if pacman_kutusu.colliderect(yem):
                yemler.remove(yem)
                pacman.puan += 10

        # Ekran Çizimleri
        ekran.fill(SIYAH)

        # Duvarları Çiz
        for duvar in duvarlar:
            pygame.draw.rect(ekran, MAVI, duvar, 2)

        # Yemleri Çiz
        for yem in yemler:
            pygame.draw.rect(ekran, BEYAZ, yem)

        # Pacman'i Çiz
        pacman.ciz(ekran)
        canavar.ciz(ekran)

        # Skor Yazısı
        skor_text = font.render(f"Puan: {pacman.puan}", True, BEYAZ)
        ekran.blit(skor_text, (10, 10))

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    oyunu_baslat()