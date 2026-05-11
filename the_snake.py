import random
import sys
from typing import List, Tuple

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
DEFAULT_BODY_COLOR = BOARD_BACKGROUND_COLOR

DEFAULT_POSITION = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
SCORE_POSITION = (10, 10)
FPS = 10

pg.init()
screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pg.time.Clock()


class GameObject:
    """Базовый класс для игровых объектов."""

    def __init__(
        self,
        position: Tuple[int, int] = DEFAULT_POSITION,
        body_color: Tuple[int, int, int] = DEFAULT_BODY_COLOR
    ):
        self.position = position
        self.body_color = body_color

    def draw(self) -> None:
        """Отрисовка объекта."""
        raise NotImplementedError(
            f'Метод draw не переопределён в {self.__class__.__name__}'
        )

    def draw_rect(
        self,
        position: Tuple[int, int],
        color: Tuple[int, int, int],
        width: int = 0
    ) -> None:
        """Отрисовывает прямоугольник."""
        pg.draw.rect(
            screen,
            color,
            pg.Rect(position, (GRID_SIZE, GRID_SIZE)),
            width
        )


class Apple(GameObject):
    """Класс яблока."""

    def __init__(
        self,
        taken_position: List[Tuple[int, int]] | None = None,
        color: Tuple[int, int, int] = APPLE_COLOR
    ):
        super().__init__(body_color=color)

        if taken_position is None:
            taken_position = []

        self.randomize_position(taken_position)

    def randomize_position(
        self,
        taken_position: List[Tuple[int, int]]
    ) -> None:
        """Случайная позиция яблока."""
        while True:
            self.position = (
                random.randint(0, GRID_WIDTH - 1) * GRID_SIZE,
                random.randint(0, GRID_HEIGHT - 1) * GRID_SIZE
            )
            if self.position not in taken_position:
                break

    def draw(self) -> None:
        """Отрисовывает яблоко."""
        self.draw_rect(self.position, self.body_color)


class Snake(GameObject):
    """Класс змейки."""

    def __init__(
        self,
        position: Tuple[int, int] = DEFAULT_POSITION,
        body_color: Tuple[int, int, int] = SNAKE_HEAD_COLOR
    ):
        super().__init__(position, body_color)
        self.length = 1
        self.positions: List[Tuple[int, int]] = [self.position]
        self.direction = RIGHT

    def get_head_position(self) -> Tuple[int, int]:
        """Позиция головы."""
        return self.positions[0]

    def get_segment_color(self, index: int) -> Tuple[int, int, int]:
        """Цвет сегмента змейки."""
        t = index / max(1, self.length - 1)

        r = int(SNAKE_HEAD_COLOR[0] * (1 - t) + DARK_GREEN[0] * t)
        g = int(SNAKE_HEAD_COLOR[1] * (1 - t) + DARK_GREEN[1] * t)
        b = int(SNAKE_HEAD_COLOR[2] * (1 - t) + DARK_GREEN[2] * t)

        return r, g, b

    def update_direction(self, new_direction: Tuple[int, int]) -> None:
        """Меняет направление."""
        if (
            new_direction[0] * -1 != self.direction[0]
            or new_direction[1] * -1 != self.direction[1]
        ):
            self.direction = new_direction

    def move(self) -> None:
        """Двигает змейку."""
        head = self.get_head_position()

        new_head = (
            (head[0] + self.direction[0] * GRID_SIZE) % SCREEN_WIDTH,
            (head[1] + self.direction[1] * GRID_SIZE) % SCREEN_HEIGHT
        )

        self.positions.insert(0, new_head)

        if len(self.positions) > self.length:
            self.positions.pop()

    def draw(self) -> None:
        """Отрисовывает змейку."""
        for i, position in enumerate(self.positions):
            self.draw_rect(position, self.get_segment_color(i))

    def reset(self) -> None:
        """Сбрасывает змейку."""
        self.length = 1
        self.positions = [self.position]
        self.direction = RIGHT

    def grow(self) -> None:
        """Увеличивает длину."""
        self.length += 1


def handle_keys(snake: Snake) -> None:
    """Обрабатывает клавиши."""
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            sys.exit()

        if event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                pg.quit()
                sys.exit()
            if event.key == pg.K_UP:
                snake.update_direction(UP)
            elif event.key == pg.K_DOWN:
                snake.update_direction(DOWN)
            elif event.key == pg.K_LEFT:
                snake.update_direction(LEFT)
            elif event.key == pg.K_RIGHT:
                snake.update_direction(RIGHT)


def main() -> None:
    """Главный цикл игры."""
    font = pg.font.SysFont(None, 30)
    pg.display.set_caption('Змейка - Изгиб Питона')

    snake = Snake()
    apple = Apple(snake.positions)
    score = 0

    while True:
        handle_keys(snake)

        snake.move()
        head = snake.get_head_position()

        if head in snake.positions[4:]:
            snake.reset()
            score = 0
            apple.randomize_position(snake.positions)

        elif head == apple.position:
            snake.grow()
            apple.randomize_position(snake.positions)
            score += 1

        screen.fill(BOARD_BACKGROUND_COLOR)
        snake.draw()
        apple.draw()

        score_text = font.render(f'Счёт: {score}', True, GREEN)
        screen.blit(score_text, SCORE_POSITION)

        pg.display.update()
        clock.tick(FPS)


if __name__ == '__main__':
    main()
    