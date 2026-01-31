import pygame
import random
import sys

# --- Константы и Настройки ---
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 700
BG_COLOR = (30, 30, 30)  # Темно-серый фон
CARD_WIDTH = 80
CARD_HEIGHT = 120
GAP = 10
FPS = 30

# Цвета UNO
RED = (255, 50, 50)
GREEN = (50, 200, 50)
BLUE = (50, 50, 255)
YELLOW = (255, 200, 0)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (100, 100, 100)

COLORS = {"Красный": RED, "Зеленый": GREEN, "Синий": BLUE, "Желтый": YELLOW}
COLOR_NAMES = list(COLORS.keys())
RANKS = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'Block', 'Rev', '+2']
WILD_CARDS = ['Wild', '+4']

class Card:
    def __init__(self, color_name, rank, is_wild=False):
        self.color_name = color_name
        self.rank = rank
        self.is_wild = is_wild
        self.rect = None  # Будет хранить позицию для клика

    def get_color(self):
        if self.color_name and self.color_name in COLORS:
            return COLORS[self.color_name]
        return BLACK # Для диких карт пока цвет не выбран

    def draw(self, surface, x, y, face_up=True):
        self.rect = pygame.Rect(x, y, CARD_WIDTH, CARD_HEIGHT)
        
        if face_up:
            # Основа карты
            color = self.get_color()
            if self.is_wild and self.color_name is None:
                # Градиент или просто черный для дикой карты
                pygame.draw.rect(surface, BLACK, self.rect)
                pygame.draw.rect(surface, WHITE, self.rect, 2)
            else:
                pygame.draw.rect(surface, color, self.rect)
                pygame.draw.rect(surface, WHITE, self.rect, 2)

            # Текст на карте
            font = pygame.font.SysFont('Arial', 30, bold=True)
            text_color = BLACK if self.color_name == "Желтый" else WHITE
            text = font.render(self.rank, True, text_color)
            text_rect = text.get_rect(center=self.rect.center)
            surface.blit(text, text_rect)
            
            # Маленькие цифры в углах
            small_font = pygame.font.SysFont('Arial', 14, bold=True)
            corner_text = small_font.render(self.rank, True, text_color)
            surface.blit(corner_text, (x + 5, y + 5))
            
        else:
            # Рубашка карты (скрытая)
            pygame.draw.rect(surface, (50, 50, 50), self.rect)
            pygame.draw.rect(surface, WHITE, self.rect, 2)
            pygame.draw.circle(surface, RED, self.rect.center, 15)

class Deck:
    def __init__(self):
        self.cards = []
        self.build()
        self.shuffle()

    def build(self):
        for c_name in COLOR_NAMES:
            for r in RANKS:
                self.cards.append(Card(c_name, r))
        for _ in range(4):
            for w in WILD_CARDS:
                self.cards.append(Card(None, w, is_wild=True))

    def shuffle(self):
        random.shuffle(self.cards)

    def draw_card(self):
        return self.cards.pop() if self.cards else None

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("UNO - 4 Игрока")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont('Arial', 24)

        self.deck = Deck()
        # 0 - Игрок, 1,2,3 - Боты
        self.players = [[], [], [], []] 
        self.turn_index = 0
        self.direction = 1
        self.top_card = None
        self.current_color = None
        
        self.message = "Ваш ход!"
        self.wild_color_selection = False # Флаг выбора цвета
        
        self.deal_cards()
        self.timer = 0 # Таймер для задержки хода ботов

    def deal_cards(self):
        for _ in range(7):
            for i in range(4):
                self.players[i].append(self.deck.draw_card())
        
        self.top_card = self.deck.draw_card()
        while self.top_card.is_wild:
            self.deck.cards.append(self.top_card)
            self.deck.shuffle()
            self.top_card = self.deck.draw_card()
            
        self.current_color = self.top_card.color_name

    def is_valid_move(self, card):
        if card.is_wild: return True
        if card.color_name == self.current_color: return True
        if card.rank == self.top_card.rank: return True
        return False

    def next_turn(self):
        self.turn_index = (self.turn_index + self.direction) % 4
        self.message = f"Ходит Игрок {self.turn_index}..."
        self.timer = pygame.time.get_ticks() # Сброс таймера для задержки

    def apply_card(self, card):
        self.top_card = card
        
        # Эффекты
        if card.rank == 'Rev':
            self.direction *= -1
        elif card.rank == 'Block':
            self.turn_index = (self.turn_index + self.direction) % 4
        
        # Простая обработка Wild (для игрока выбор цвета отдельно)
        if not card.is_wild:
            self.current_color = card.color_name
        
        # Если это бот ставит Wild, он выбирает случайный цвет
        if card.is_wild and self.turn_index != 0:
            self.current_color = random.choice(COLOR_NAMES)
            self.message = f"Бот выбрал {self.current_color}"

    def draw_ui(self):
        self.screen.fill(BG_COLOR)
        
        # Рисуем центр (колода и сброс)
        center_x, center_y = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
        
        # Колода (рубашкой вверх)
        pygame.draw.rect(self.screen, GRAY, (center_x - CARD_WIDTH - 20, center_y - CARD_HEIGHT//2, CARD_WIDTH, CARD_HEIGHT))
        deck_text = self.font.render("Колода", True, WHITE)
        self.screen.blit(deck_text, (center_x - CARD_WIDTH - 20, center_y - CARD_HEIGHT//2 - 30))

        # Сброс (текущая карта)
        # Если карта дикая, рисуем её с текущим выбранным цветом
        display_card = self.top_card
        if display_card.is_wild and self.current_color:
             # Визуальный трюк: создаем временную карту для отображения цвета
             pass 
        
        # Рисуем карту сброса
        # Рисуем рамку текущего цвета вокруг сброса
        color_rgb = COLORS.get(self.current_color, WHITE)
        pygame.draw.rect(self.screen, color_rgb, (center_x + 20 - 5, center_y - CARD_HEIGHT//2 - 5, CARD_WIDTH + 10, CARD_HEIGHT + 10), 3)
        self.top_card.draw(self.screen, center_x + 20, center_y - CARD_HEIGHT//2)

        # Статус текст
        status = self.font.render(f"Цвет: {self.current_color} | {self.message}", True, WHITE)
        self.screen.blit(status, (20, 20))

        # Отрисовка рук
        self.draw_hands()
        
        # Выбор цвета (если нужно)
        if self.wild_color_selection:
            self.draw_color_picker()

        pygame.display.flip()

    def draw_hands(self):
        # Игрок 0 (Мы) - Внизу
        hand = self.players[0]
        start_x = (SCREEN_WIDTH - (len(hand) * (CARD_WIDTH + GAP))) // 2
        for i, card in enumerate(hand):
            card.draw(self.screen, start_x + i * (CARD_WIDTH + GAP), SCREEN_HEIGHT - CARD_HEIGHT - 20, face_up=True)

        # Игрок 1 (Бот) - Слева
        hand_len = len(self.players[1])
        start_y = (SCREEN_HEIGHT - (hand_len * 30)) // 2
        for i in range(hand_len):
            # Рисуем просто прямоугольники-рубашки боком
            rect = pygame.Rect(20, start_y + i * 30, CARD_HEIGHT, CARD_WIDTH)
            pygame.draw.rect(self.screen, (50,50,50), rect)
            pygame.draw.rect(self.screen, WHITE, rect, 1)

        # Игрок 2 (Бот) - Сверху
        hand_len = len(self.players[2])
        start_x = (SCREEN_WIDTH - (hand_len * 30)) // 2
        for i in range(hand_len):
            rect = pygame.Rect(start_x + i * 30, 20, CARD_WIDTH, CARD_HEIGHT)
            pygame.draw.rect(self.screen, (50,50,50), rect)
            pygame.draw.rect(self.screen, WHITE, rect, 1)

        # Игрок 3 (Бот) - Справа
        hand_len = len(self.players[3])
        start_y = (SCREEN_HEIGHT - (hand_len * 30)) // 2
        for i in range(hand_len):
            rect = pygame.Rect(SCREEN_WIDTH - CARD_HEIGHT - 20, start_y + i * 30, CARD_HEIGHT, CARD_WIDTH)
            pygame.draw.rect(self.screen, (50,50,50), rect)
            pygame.draw.rect(self.screen, WHITE, rect, 1)

    def draw_color_picker(self):
        # Меню выбора цвета по центру
        pygame.draw.rect(self.screen, (20, 20, 20), (300, 200, 400, 200))
        pygame.draw.rect(self.screen, WHITE, (300, 200, 400, 200), 2)
        
        options = [("Красный", RED, 320, 250), ("Зеленый", GREEN, 410, 250), 
                   ("Синий", BLUE, 500, 250), ("Желтый", YELLOW, 590, 250)]
        
        self.color_rects = []
        for name, color, x, y in options:
            rect = pygame.Rect(x, y, 80, 80)
            pygame.draw.rect(self.screen, color, rect)
            self.color_rects.append((name, rect))

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.wild_color_selection:
                    # Обработка клика по выбору цвета
                    mx, my = pygame.mouse.get_pos()
                    for name, rect in self.color_rects:
                        if rect.collidepoint(mx, my):
                            self.current_color = name
                            self.wild_color_selection = False
                            self.next_turn()
                    return True

                if self.turn_index == 0: # Ход человека
                    mx, my = pygame.mouse.get_pos()
                    
                    # 1. Проверка клика по колоде (взять карту)
                    center_x, center_y = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
                    deck_rect = pygame.Rect(center_x - CARD_WIDTH - 20, center_y - CARD_HEIGHT//2, CARD_WIDTH, CARD_HEIGHT)
                    if deck_rect.collidepoint(mx, my):
                        new_card = self.deck.draw_card()
                        if new_card:
                            self.players[0].append(new_card)
                            # Если взятая карта подходит, можно сразу сыграть (упрощение: просто берем и переход хода)
                            self.next_turn()
                    
                    # 2. Проверка клика по картам в руке
                    hand = self.players[0]
                    # Нужно пересчитать rect карт, так как они перерисовываются
                    start_x = (SCREEN_WIDTH - (len(hand) * (CARD_WIDTH + GAP))) // 2
                    for i, card in enumerate(hand):
                        card_rect = pygame.Rect(start_x + i * (CARD_WIDTH + GAP), SCREEN_HEIGHT - CARD_HEIGHT - 20, CARD_WIDTH, CARD_HEIGHT)
                        if card_rect.collidepoint(mx, my):
                            if self.is_valid_move(card):
                                played_card = hand.pop(i)
                                self.apply_card(played_card)
                                if played_card.is_wild:
                                    self.wild_color_selection = True # Ждем выбора цвета
                                else:
                                    self.next_turn()
                                return True
                            else:
                                self.message = "Нельзя сыграть эту карту!"

        return True

    def bot_logic(self):
        # Задержка 1.5 секунды перед ходом бота
        if pygame.time.get_ticks() - self.timer < 1500:
            return

        current_player_idx = self.turn_index
        hand = self.players[current_player_idx]
        
        valid_moves = [c for c in hand if self.is_valid_move(c)]
        
        if valid_moves:
            # Приоритет: обычные карты, потом Wild
            card_to_play = valid_moves[0]
            for c in valid_moves:
                if not c.is_wild:
                    card_to_play = c
                    break
            
            hand.remove(card_to_play)
            self.apply_card(card_to_play)
            self.message = f"Бот {current_player_idx} сыграл {card_to_play.rank}"
            self.next_turn()
        else:
            # Бот берет карту
            new_card = self.deck.draw_card()
            if new_card:
                hand.append(new_card)
                self.message = f"Бот {current_player_idx} взял карту"
            else:
                self.message = "Колода пуста!"
            self.next_turn()

    def run(self):
        running = True
        while running:
            running = self.handle_input()
            
            if self.turn_index != 0 and not self.wild_color_selection:
                self.bot_logic()
            
            # Проверка победы
            for i, p in enumerate(self.players):
                if len(p) == 0:
                    print(f"Игрок {i} победил!")
                    running = False # Можно сделать экран победы

            self.draw_ui()
            self.clock.tick(FPS)
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run()
