import random
from typing import List, Optional, Tuple

import pygame

SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

BOARD_BACKGROUND_COLOR = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
DARK_GREEN = (0, 150, 0)

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()


class GameObject:
    """Базовый класс для всех игровых объектов."""

    def __init__(self, position: Tuple[int, int] = (0, 0)):
        """Инициализирует базовый игровой объект."""
        self.position = position
        self.body_color = BOARD_BACKGROUND_COLOR

    def draw(self, surface: pygame.Surface) -> None:
        """Отрисовывает объект на игровой поверхности."""
        raise NotImplementedError(
            'Метод draw должен быть переопределён в дочернем классе'
        )


class Apple(GameObject):
    """Яблоко в игре."""

    def __init__(self):
        """Инициализирует яблоко со случайной позицией и красным цветом."""
        super().__init__()
        self.body_color = RED
        self.randomize_position()

    def randomize_position(self) -> None:
        """Устанавливает случайную позицию яблока на игровом поле."""
        self.position = (
            random.randint(0, GRID_WIDTH - 1) * GRID_SIZE,
            random.randint(0, GRID_HEIGHT - 1) * GRID_SIZE
        )

    def draw(self, surface: pygame.Surface) -> None:
        """Отрисовывает яблоко на игровой поверхности."""
        pygame.draw.rect(
            surface,
            self.body_color,
            (self.position[0], self.position[1], GRID_SIZE, GRID_SIZE)
        )


class Snake(GameObject):
    """Класс, представляющий змейку в игре."""

    def __init__(self) -> None:
        """Инициализирует змейку."""
        super().__init__()
        self.length = 1
        self.positions: List[Tuple[int, int]] = [
            (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        ]
        self.direction = RIGHT
        self.next_direction: Optional[Tuple[int, int]] = None
        self.body_color = GREEN

    def get_head_position(self) -> Tuple[int, int]:
        """Возвращает позицию головы змейки."""
        return self.positions[0]

    def update_direction(self) -> None:
        """Обновляет направление движения змейки."""
        if self.next_direction:
            if self.next_direction[0] * -1 != self.direction[0] or \
               self.next_direction[1] * -1 != self.direction[1]:
                self.direction = self.next_direction
            self.next_direction = None

    def move(self) -> None:
        """Обновляет позицию змейки."""
        head = self.get_head_position()
        new_head = (
            (head[0] + self.direction[0] * GRID_SIZE) % SCREEN_WIDTH,
            (head[1] + self.direction[1] * GRID_SIZE) % SCREEN_HEIGHT
        )

        self.positions.insert(0, new_head)

        if len(self.positions) > self.length:
            self.positions.pop()

    def draw(self, surface: pygame.Surface) -> None:
        """Отрисовывает змейку на игровой поверхности."""
        for position in self.positions:
            pygame.draw.rect(
                surface,
                self.body_color,
                (position[0], position[1], GRID_SIZE, GRID_SIZE)
            )

            pygame.draw.rect(
                surface,
                DARK_GREEN,
                (position[0], position[1], GRID_SIZE, GRID_SIZE),
                1
            )  # для лучшей видимости змейки

    def reset(self) -> None:
        """Сбрасывает змейку в начальное состояние."""
        self.length = 1
        self.positions = [(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)]
        self.direction = RIGHT
        self.next_direction = None

    def grow(self) -> None:
        """Увеличивает длину змейки на одну клетку."""
        self.length += 1


def handle_keys(snake: Snake) -> bool:
    """Обрабатывает нажатия клавиш для изменения направления змейки."""
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                snake.next_direction = UP
            elif event.key == pygame.K_DOWN:
                snake.next_direction = DOWN
            elif event.key == pygame.K_LEFT:
                snake.next_direction = LEFT
            elif event.key == pygame.K_RIGHT:
                snake.next_direction = RIGHT
    return True


def main() -> None:
    """Главный игровой цикл."""
    pygame.display.set_caption('Змейка - Изгиб Питона')

    snake = Snake()
    apple = Apple()

    running = True
    score = 0

    while running:
        running = handle_keys(snake)
        if not running:
            break

        snake.update_direction()
        snake.move()

        head = snake.get_head_position()
        if head in snake.positions[1:]:
            snake.reset()
            score = 0
            continue

        if head == apple.position:
            snake.grow()
            apple.randomize_position()
            score += 1

        screen.fill(BOARD_BACKGROUND_COLOR)
        snake.draw(screen)
        apple.draw(screen)

        pygame.display.update()

        clock.tick(10)

    pygame.quit()


if __name__ == '__main__':
    main()
