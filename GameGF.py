import pygame
import random
import math
from pygame import Rect

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)


class Quadtree:
    def __init__(self, boundary, capacity=4):
        self.boundary = boundary
        self.capacity = capacity
        self.points = []
        self.divided = False
        self.northeast = None
        self.northwest = None
        self.southeast = None
        self.southwest = None

    def insert(self, point):
        if not self.boundary.contains(point):
            return False

        if len(self.points) < self.capacity:
            self.points.append(point)
            return True
        else:
            if not self.divided:
                self.subdivide()

            if self.northeast.insert(point):
                return True
            elif self.northwest.insert(point):
                return True
            elif self.southeast.insert(point):
                return True
            elif self.southwest.insert(point):
                return True

    def subdivide(self):
        x = self.boundary.x
        y = self.boundary.y
        w = self.boundary.width / 2
        h = self.boundary.height / 2

        ne = Rect(x + w, y, w, h)
        nw = Rect(x, y, w, h)
        se = Rect(x + w, y + h, w, h)
        sw = Rect(x, y + h, w, h)

        self.northeast = Quadtree(ne, self.capacity)
        self.northwest = Quadtree(nw, self.capacity)
        self.southeast = Quadtree(se, self.capacity)
        self.southwest = Quadtree(sw, self.capacity)

        self.divided = True

    def query(self, range):
        points = []

        if not self.boundary.colliderect(range):
            return points

        for point in self.points:
            if range.collidepoint(point.rect.center):
                points.append(point)

        if self.divided:
            points += self.northeast.query(range)
            points += self.northwest.query(range)
            points += self.southeast.query(range)
            points += self.southwest.query(range)

        return points

    def update(self, points):
        self.clear()
        for point in points:
            self.insert(point)

    def clear(self):
        self.points.clear()
        self.divided = False
        self.northeast = None
        self.northwest = None
        self.southeast = None
        self.southwest = None


class Point:
    def __init__(self, rect):
        self.rect = rect

    def __repr__(self):
        return f"Point({self.rect})"


class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((50, 50))
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.speed = 5
        self.velocity = pygame.Vector2(0, 0)
        self.input_state = {
            pygame.K_LEFT: False,
            pygame.K_RIGHT: False,
            pygame.K_UP: False,
            pygame.K_DOWN: False
        }

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key in self.input_state:
                self.input_state[event.key] = True
        elif event.type == pygame.KEYUP:
            if event.key in self.input_state:
                self.input_state[event.key] = False

    def update(self):
        self.velocity = pygame.Vector2(0, 0)

        if self.input_state[pygame.K_LEFT]:
            self.velocity.x -= self.speed
        if self.input_state[pygame.K_RIGHT]:
            self.velocity.x += self.speed
        if self.input_state[pygame.K_UP]:
            self.velocity.y -= self.speed
        if self.input_state[pygame.K_DOWN]:
            self.velocity.y += self.speed

        self.rect.move_ip(self.velocity.x, self.velocity.y)
        self.rect.clamp_ip(pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT))


class Enemy(pygame.sprite.Sprite):
    def __init__(self, speed, color):
        super().__init__()
        self.image = pygame.Surface((30, 30))
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, SCREEN_WIDTH - self.rect.width)
        self.rect.y = random.randint(0, SCREEN_HEIGHT - self.rect.height)
        self.speed = speed
        self.angle = random.uniform(0, 2 * math.pi)

    def update(self):
        direction = pygame.math.Vector2(
            math.cos(self.angle), math.sin(self.angle))
        velocity = direction * self.speed
        self.rect.move_ip(velocity.x, velocity.y)

        if self.rect.left < 0 or self.rect.right > SCREEN_WIDTH:
            self.angle = math.pi - self.angle

        if self.rect.top < 0 or self.rect.bottom > SCREEN_HEIGHT:
            self.angle = -self.angle


class PowerUp(pygame.sprite.Sprite):
    def __init__(self, player):
        super().__init__()
        self.image = pygame.Surface((20, 20))
        self.image.fill(GREEN)  # Green for power-up
        self.rect = self.image.get_rect()
        self.rect.center = (random.randint(0, SCREEN_WIDTH),
                            random.randint(0, SCREEN_HEIGHT))
        self.player = player

    def update(self):
        if pygame.sprite.collide_rect(self, self.player):
            self.apply_power_up()

    def apply_power_up(self):
        self.player.speed += 2  # Increase player speed temporarily


class EnemyType1(Enemy):
    def __init__(self, speed):
        super().__init__(speed, BLUE)

    def update(self):
        direction = pygame.math.Vector2(
            math.cos(self.angle), math.sin(self.angle))
        velocity = direction * self.speed
        speed_factor = random.uniform(0.9, 1.1)
        velocity *= speed_factor
        self.rect.move_ip(velocity.x, velocity.y)

        if self.rect.left < 0 or self.rect.right > SCREEN_WIDTH:
            self.angle = math.pi - self.angle

        if self.rect.top < 0 or self.rect.bottom > SCREEN_HEIGHT:
            self.angle = -self.angle


class BicycleGame:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Bicycle Game")
        self.clock = pygame.time.Clock()
        self.all_sprites = pygame.sprite.Group()
        self.player = Player()
        self.enemies = pygame.sprite.Group()
        self.power_ups = pygame.sprite.Group()
        self.all_sprites.add(self.player)

        self.level = 1  # Current game level
        self.score = 0
        self.font = pygame.font.Font(None, 36)

        bounds = Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)
        self.quadtree = Quadtree(bounds)

        self.dirty_rects = []  # Tracks the rects that need to be updated each frame

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            self.player.handle_event(event)
        return True

    def update_score(self):
        self.score += 1

    def draw_score(self):
        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        self.screen.blit(score_text, (10, 10))
        self.dirty_rects.append(score_text.get_rect())

    def create_enemies(self):
        for _ in range(self.level + 4):
            if random.random() < 0.5:
                enemy = Enemy(self.level + 1, WHITE)
            else:
                enemy = EnemyType1(self.level + 1)
            self.enemies.add(enemy)
            self.all_sprites.add(enemy)
            self.quadtree.insert(Point(enemy.rect))

    def create_power_up(self):
        if random.random() < 0.1:  # 10% chance of creating a power-up
            power_up = PowerUp(self.player)
            self.power_ups.add(power_up)
            self.all_sprites.add(power_up)

    def check_collision(self):
        range = Rect(self.player.rect.x - 50,
                     self.player.rect.y - 50, 100, 100)
        collided_enemies = self.quadtree.query(range)
        if collided_enemies:
            return True
        return False

    def show_game_over(self):
        game_over_text = self.font.render("Game Over", True, WHITE)
        game_over_rect = game_over_text.get_rect(
            center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.screen.fill(BLACK)
        self.screen.blit(game_over_text, game_over_rect)
        pygame.display.flip()
        pygame.time.wait(2000)

    def increase_level(self):
        self.level += 1
        self.create_enemies()

    def update(self):
        self.player.update()
        self.enemies.update()
        self.power_ups.update()

        self.dirty_rects.append(self.player.rect)

        self.dirty_rects.extend(self.enemies.sprites())
        self.dirty_rects.extend(self.power_ups.sprites())

        if self.check_collision():
            self.show_game_over()
            return False  # Stop the game loop

        if self.score % 50 == 0:  # Increase level every 50 score
            self.increase_level()

        self.create_power_up()

        self.quadtree.update(self.enemies)

        return True

    def draw(self):
        for dirty_rect in self.dirty_rects:
            self.screen.fill(BLACK, dirty_rect)
        self.dirty_rects.clear()

        self.all_sprites.draw(self.screen)
        self.draw_score()

        pygame.display.flip()

    def run(self):
        running = True
        while running:
            self.dirty_rects.append(pygame.Rect(
                0, 0, SCREEN_WIDTH, SCREEN_HEIGHT))

            self.clock.tick(FPS)
            running = self.handle_events()
            if not running:
                break

            running = self.update()
            if not running:
                break

            self.draw()

        pygame.quit()


if __name__ == "__main__":
    game = BicycleGame()
    game.run()
