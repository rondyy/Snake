import pygame, time
from random import randint
import numpy as np

class GridPoint:
    def __init__(self, x, y):
        self.x = x
        self.y = y

AREA = GridPoint(640, 480)
SPEED_DELAY = 0.1
STEP_SIZE = 20  # Needs to be the same as sprite size
BG_COLOR = (0, 0, 0)

UP = "U"
DOWN = "D"
LEFT = "L"
RIGHT = "R"

ACTIONS = [UP, DOWN, LEFT, RIGHT]  # Действия, которые может предпринимать змея

pygame.init()
game_screen = pygame.display.set_mode((AREA.x, AREA.y))
continue_game = True

snake_head = pygame.sprite.Sprite()
snake_head.tail = []
snake_head.image = pygame.image.load("images/snake_seg.gif")
snake_head.rect = snake_head.image.get_rect()
snake_group = pygame.sprite.GroupSingle(snake_head)

apple = pygame.sprite.Sprite()
apple.live = False
apple.image = pygame.image.load("images/apple.gif")
apple.rect = apple.image.get_rect()
apple_group = pygame.sprite.GroupSingle(apple)

# Q-Learning параметры
Q_table = {}  # Храним Q-значения для каждого состояния
learning_rate = 0.1  # Коэффициент обучения
discount_factor = 0.9  # Коэффициент дисконтирования
epsilon = 0.1  # Вероятность выбора случайного действия

def get_state(snake, apple):
    """Возвращаем состояние как кортеж из положения головы змеи и положения яблока"""
    return (snake.rect.left // STEP_SIZE, snake.rect.top // STEP_SIZE, apple.rect.left // STEP_SIZE, apple.rect.top // STEP_SIZE)

def initialize_Q(state):
    """Инициализируем Q-таблицу для нового состояния"""
    if state not in Q_table:
        Q_table[state] = {action: 0.0 for action in ACTIONS}

def choose_action(state):
    """Выбор действия на основе ε-жадности"""
    if np.random.rand() < epsilon:
        return np.random.choice(ACTIONS)  # Случайное действие
    else:
        return max(Q_table[state], key=Q_table[state].get)  # Действие с наибольшим Q-значением

def update_Q(state, action, reward, next_state):
    """Обновляем Q-таблицу по формуле Q-learning"""
    next_max = max(Q_table[next_state].values()) if next_state in Q_table else 0
    Q_table[state][action] += learning_rate * (reward + discount_factor * next_max - Q_table[state][action])

def isExitGameEvent(event):
    return event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE)

def moveSprite(sprite):
    if sprite.direction == UP:
        sprite.rect.top -= STEP_SIZE
    elif sprite.direction == DOWN:
        sprite.rect.top += STEP_SIZE
    elif sprite.direction == LEFT:
        sprite.rect.left -= STEP_SIZE
    elif sprite.direction == RIGHT:
        sprite.rect.left += STEP_SIZE

    if sprite.rect.left < 0:
        sprite.rect.left = 0
    if sprite.rect.top < 0:
        sprite.rect.top = 0
    if sprite.rect.bottom > AREA.y:
        sprite.rect.bottom = AREA.y
    if sprite.rect.right > AREA.x:
        sprite.rect.right = AREA.x

def handleEvents():
    for event in pygame.event.get():
        if isExitGameEvent(event):
            return False
        elif event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_UP, pygame.K_w):  # Вверх
                if snake_head.direction != DOWN:  # Исключение обратного хода
                    snake_head.direction = UP
            elif event.key in (pygame.K_DOWN, pygame.K_s):  # Вниз
                if snake_head.direction != UP:
                    snake_head.direction = DOWN
            elif event.key in (pygame.K_LEFT, pygame.K_a):  # Влево
                if snake_head.direction != RIGHT:
                    snake_head.direction = LEFT
            elif event.key in (pygame.K_RIGHT, pygame.K_d):  # Вправо
                if snake_head.direction != LEFT:
                    snake_head.direction = RIGHT
        elif event.type == pygame.KEYUP:
            pass
    return True

def createApples():
    if not apple.live:
        apple.rect.top = randint(0, AREA.y - STEP_SIZE) 
        apple.rect.top -= apple.rect.top % STEP_SIZE
        apple.rect.left = randint(0, AREA.x - STEP_SIZE) 
        apple.rect.left -= apple.rect.left % STEP_SIZE
        apple.live = True

def clearApples():
    apple.live = False

def eatAvailiableApples(eater):
    if (eater.rect.left == apple.rect.left) & (eater.rect.top == apple.rect.top):
        return True
    else:
        return False

def snakeIsTangled(snake):
    y = snake.rect.top
    x = snake.rect.left
    for tailSeg in snake.tail:
        if y == tailSeg.y and x == tailSeg.x:
            return True
    return False

def updateSnake():
    """Обновление змеи с использованием Q-learning"""
    state = get_state(snake_head, apple)
    initialize_Q(state)  # Инициализация Q-таблицы для текущего состояния
    action = choose_action(state)  # Выбор действия с использованием Q-learning
    snake_head.direction = action  # Выполнение выбранного действия
    
    snake_head.tail.append(GridPoint(snake_head.rect.left, snake_head.rect.top))
    moveSprite(snake_head)
    
    reward = 0  # Начальная награда
    
    if eatAvailiableApples(snake_head):
        clearApples()
        reward = 10  # Награда за поедание яблока
    elif snakeIsTangled(snake_head):
        reward = -10  # Штраф за столкновение с собой
        return False
    else:
        snake_head.tail.pop(0)

    next_state = get_state(snake_head, apple)
    initialize_Q(next_state)
    update_Q(state, action, reward, next_state)  # Обновление Q-таблицы

    return True

def drawSnake():
    halfStep = STEP_SIZE / 2
    snake_group.draw(game_screen)
    for tailSeg in snake_head.tail:
        pygame.draw.circle(game_screen, (10, 200, 10), (tailSeg.x + halfStep, tailSeg.y + halfStep), STEP_SIZE / 3, 2)

def printText(game_screen, text, yLoc, size, color=(255, 255, 255)):
    gameFont = pygame.font.Font(None, size)
    label = gameFont.render(text, 1, color)
    lblHeight = label.get_rect().bottom - label.get_rect().top
    lblWidth = label.get_rect().right - label.get_rect().left
    game_screen.blit(label, (AREA.x / 2 - lblWidth / 2, yLoc))  # Centered

def printEndOfGameSummary(game_screen, score):
    game_screen.fill(BG_COLOR)
    time.sleep(1)
    printText(game_screen, "Game Over", 150, 35)
    printText(game_screen, "Score: {}".format(score), 200, 30)
    pygame.display.update()
    waitForKeyPress()

def waitForKeyPress():
    while True:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                return

def run_game(player_mode=True):
    snake_head.direction = DOWN
    game_speed_modifier = SPEED_DELAY
    while continue_game:
        game_speed_modifier = SPEED_DELAY  # Keep the speed constant
        time.sleep(game_speed_modifier)
        if player_mode:
            continue_game = handleEvents()  # Режим игрока
        else:
            continue_game = updateSnake()  # Режим бота

        game_screen.fill(BG_COLOR)
        printText(game_screen, "{}".format(len(snake_head.tail)), 10, 30, (100, 100, 100))

        drawSnake()

        createApples()
        apple_group.draw(game_screen)

        pygame.display.update()

    print("Score: {}".format(len(snake_head.tail)))
    printEndOfGameSummary(game_screen, len(snake_head.tail) - 1)

# Выбираем режим игры
mode = input("Выберите режим (игрок/бот): ").strip().lower()
if mode == "бот":
    run_game(player_mode=False)  # Режим бота
else:
    run_game(player_mode=True)  # Режим игрока

pygame.quit()
