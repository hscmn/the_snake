import random
from typing import List, Optional, Tuple

import pygame as pg

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

APPLE_COLOR = RED
SNAKE_HEAD_COLOR = GREEN
SNAKE_BODY_COLOR = DARK_GREEN
BACKGROUND_COLOR = BOARD_BACKGROUND_COLOR

DEFAULT_POSITION = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
DEFAULT_BODY_COLOR = BACKGROUND_COLOR
DEFAULT_SNAKE_COLOUR = SNAKE_HEAD_COLOR
FPS = 10


class GameObject:
    """Базовый класс для всех игровых объектов."""

    def __init__(
        self,
        position: Tuple[int, int] = DEFAULT_POSITION,
        body_color: Tuple[int, int, int] = DEFAULT_BODY_COLOR
    ):
        """Инициализирует базовый игровой объект."""
        self.position = position
        self.body_color = body_color

    def draw(self, screen: pg.Surface) -> None:
        raise NotImplementedError(
            f'Метод draw не переопределён в классе {self.__class__.__name__}'
        )

    def draw_rect(
        self,
        screen: pg.Surface,
        position: Tuple[int, int],
        color: Tuple[int, int, int],
        width: int = 0
    ) -> None:
        pg.draw.rect(
            screen,
            color,
            pg.Rect(position, (GRID_SIZE, GRID_SIZE)),
            width
        )


class Apple(GameObject):
    """Яблоко в игре."""

    def __init__(
        self,
        taken_position: List[Tuple[int, int]],
        color: Tuple[int, int, int] = APPLE_COLOR
    ):
        """Инициализирует яблоко со случайной позицией и яблочным цветом."""
        super().__init__(body_color=color)
        self.randomize_position(taken_position)

    def randomize_position(
        self,
        taken_position: List[Tuple[int, int]]
    ) -> None:
        """Устанавливает случайную позицию яблока на игровом поле."""
        while True:
            new_position = (
                random.randint(0, GRID_WIDTH - 1) * GRID_SIZE,
                random.randint(0, GRID_HEIGHT - 1) * GRID_SIZE
            )
            if new_position not in taken_position:
                self.position = new_position
                break

    def draw(self, screen: pg.Surface) -> None:
        """Отрисовывает яблоко на игровой поверхности."""
        self.draw_rect(screen, self.position, self.body_color)


class Snake(GameObject):
    """Класс, представляющий змейку в игре."""

    def __init__(self) -> None:
        super().__init__(body_color=SNAKE_HEAD_COLOR)
        self.length = 1
        self.positions: List[Tuple[int, int]]
        self.positions = [self.position]
        self.direction = RIGHT
        self.next_direction: Optional[Tuple[int, int]] = None

    def get_head_position(self) -> Tuple[int, int]:
        return self.positions[0]

    def get_segment_color(self, index: int) -> Tuple[int, int, int]:
        """Змея теперь градиентная :)."""
        t = index / max(1, self.length - 1)

        r = int(SNAKE_HEAD_COLOR[0] * (1 - t) + DARK_GREEN[0] * t)
        g = int(SNAKE_HEAD_COLOR[1] * (1 - t) + DARK_GREEN[1] * t)
        b = int(SNAKE_HEAD_COLOR[2] * (1 - t) + DARK_GREEN[2] * t)

        return (r, g, b)

    def update_direction(self, new_direction):
        if (
            new_direction[0] * -1 != self.direction[0]
            or new_direction[1] * -1 != self.direction[1]
        ):
            self.direction = new_direction

    def move(self) -> None:
        head = self.get_head_position()
        new_head = (
            (head[0] + self.direction[0] * GRID_SIZE) % SCREEN_WIDTH,
            (head[1] + self.direction[1] * GRID_SIZE) % SCREEN_HEIGHT
        )
        self.positions.insert(0, new_head)
        if len(self.positions) > self.length:
            self.positions.pop()

    def draw(self, screen: pg.Surface) -> None:
        for i, position in enumerate(self.positions):
            color = self.get_segment_color(i)
            self.draw_rect(screen, position, color)

    def reset(self) -> None:
        self.length = 1
        self.positions = [DEFAULT_POSITION]
        self.direction = RIGHT
        self.next_direction = None

    def grow(self) -> None:
        self.length += 1


def handle_keys(snake: Snake) -> bool:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            return False
        elif event.type == pg.KEYDOWN:
            if event.key == pg.K_UP:
                snake.next_direction = UP
            elif event.key == pg.K_DOWN:
                snake.next_direction = DOWN
            elif event.key == pg.K_LEFT:
                snake.next_direction = LEFT
            elif event.key == pg.K_RIGHT:
                snake.next_direction = RIGHT
            if event.key == pg.K_ESCAPE:
                return False
    return True


def main() -> None:
    pg.init()
    screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pg.time.Clock()
    font = pg.font.SysFont(None, 30)
    pg.display.set_caption('Змейка - Изгиб Питона')

    snake = Snake()
    apple = Apple(snake.positions)

    running = True
    score = 0

    while running:
        if not handle_keys(snake):
            break
        pg.quit()

        if snake.next_direction is not None:
            snake.update_direction(snake.next_direction)
        snake.move()

        head = snake.get_head_position()

        if head in snake.positions[1:]:
            snake.reset()
            score = 0
            apple.randomize_position(snake.positions)
            continue

        if head == apple.position:
            snake.grow()
            apple.randomize_position(snake.positions)
            score += 1

        screen.fill(BOARD_BACKGROUND_COLOR)
        snake.draw(screen)
        apple.draw(screen)
        score_text = font.render(f'Счёт: {score}', True, GREEN)
        screen.blit(score_text, (10, 10))

        pg.display.update()
        clock.tick(FPS)


if __name__ == '__main__':
    main()
