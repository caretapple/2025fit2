import pyxel
import random

W, H = 256, 256
GROUND_Y = H - 28

# player catch area (arms)
CATCH_W, CATCH_H = 44, 14

# fruit base size
FRUIT_W, FRUIT_H = 10, 10

# fruits: (score, color)
FRUITS = [
    (10, pyxel.COLOR_RED),
    (12, pyxel.COLOR_YELLOW),
    (15, pyxel.COLOR_GREEN),
]

# bonus (gold fruit)
GOLD_SCORE = 40
GOLD_COLOR = pyxel.COLOR_ORANGE
GOLD_SIZE = 14


def rect_hit(ax, ay, aw, ah, bx, by, bw, bh):
    return (ax < bx + bw and ax + aw > bx and ay < by + bh and ay + ah > by)


class Fruit:
    def __init__(self, level, is_gold=False):
        self.is_gold = is_gold

        if is_gold:
            self.score = GOLD_SCORE
            self.color = GOLD_COLOR
            self.w = GOLD_SIZE
            self.h = GOLD_SIZE
            base_v = 1.1
        else:
            self.score, self.color = random.choice(FRUITS)
            self.w = FRUIT_W
            self.h = FRUIT_H
            base_v = 1.2

        self.x = random.randint(0, W - self.w)
        self.y = random.randint(-90, -16)

        # speed up by level
        self.vy = random.uniform(base_v, base_v + 0.4) + level * 0.08


        # small horizontal drift (harder at higher level)
        self.vx = random.uniform(-0.25, 0.25) * (1 + level * 0.15)

    def update(self):
        self.y += self.vy
        self.x += self.vx

        # bounce at edges
        if self.x < 0:
            self.x = 0
            self.vx *= -1
        if self.x > W - self.w:
            self.x = W - self.w
            self.vx *= -1

    def draw(self):
        if self.is_gold:
            cx = self.x + self.w // 2
            cy = int(self.y) + self.h // 2
            pyxel.circ(cx, cy, self.w // 2, self.color)
            pyxel.pset(cx, int(self.y) + 1, pyxel.COLOR_WHITE)
        else:
            pyxel.rect(self.x, int(self.y), self.w, self.h, self.color)


class App:
    def __init__(self):
        pyxel.init(W, H, title="Fruit Catcher", fps=30)
        self.reset()
        pyxel.run(self.update, self.draw)

    def reset(self):
        # player (top-left)
        self.px = (W - CATCH_W) // 2
        self.py = GROUND_Y - 42

        self.score = 0
        self.life = 3
        self.time_left = 60 * 30
        self.frame = 0
        self.level = 1
        self.fruits = []
        self.state = "TITLE"  # TITLE / PLAY / GAMEOVER

        # combo system
        self.combo = 0
        self.combo_timer = 0
        self.best_combo = 0

        # clouds for background
        self.clouds = []
        for _ in range(6):
            self.clouds.append(
                [random.randint(0, W), random.randint(18, 90), random.uniform(0.2, 0.6)]
            )

    def spawn(self):
        gold_prob = min(0.03 + self.level * 0.01, 0.12)
        is_gold = (random.random() < gold_prob)
        self.fruits.append(Fruit(self.level, is_gold=is_gold))

    def update(self):
        # TITLE
        if self.state == "TITLE":
            if pyxel.btnp(pyxel.KEY_RETURN) or pyxel.btnp(pyxel.KEY_SPACE):
                self.state = "PLAY"
            return

        # GAMEOVER
        if self.state == "GAMEOVER":
            if pyxel.btnp(pyxel.KEY_R):
                self.reset()
            return

        # PLAY
        if pyxel.btnp(pyxel.KEY_R):
            self.reset()
            return

        # timer
        self.time_left -= 1
        if self.time_left <= 0:
            self.time_left = 0
            self.state = "GAMEOVER"
            return

        # level up every 15 seconds
        sec = self.time_left // 30
        self.level = 1 + (60 - sec) // 15

        # move
        speed = 4
        if pyxel.btn(pyxel.KEY_LEFT) or pyxel.btn(pyxel.KEY_A):
            self.px -= speed
        if pyxel.btn(pyxel.KEY_RIGHT) or pyxel.btn(pyxel.KEY_D):
            self.px += speed
        self.px = max(0, min(W - CATCH_W, self.px))

        # combo timer (about 0.8 sec at 30fps)
        if self.combo_timer > 0:
            self.combo_timer -= 1
        else:
            self.combo = 0

        # spawn
        self.frame += 1
        interval = max(8, 28 - self.level * 3)
        if self.frame % interval == 0:
            self.spawn()

        # update fruits and collisions
        alive = []
        catch_x = self.px
        catch_y = self.py + 18

        for f in self.fruits:
            f.update()

            if rect_hit(catch_x, catch_y, CATCH_W, CATCH_H, f.x, f.y, f.w, f.h):
                self.combo += 1
                self.best_combo = max(self.best_combo, self.combo)
                self.combo_timer = 24

                bonus = 1.0 + min(self.combo, 10) * 0.1
                gained = int(f.score * bonus)
                self.score += gained
                continue

            if f.y > GROUND_Y:
                self.life -= 1
                self.combo = 0
                self.combo_timer = 0
                if self.life <= 0:
                    self.life = 0
                    self.state = "GAMEOVER"
                continue

            alive.append(f)

        self.fruits = alive

        # move clouds
        for c in self.clouds:
            c[0] += c[2]
            if c[0] > W + 20:
                c[0] = -20
                c[1] = random.randint(18, 90)
                c[2] = random.uniform(0.2, 0.6)

    def draw_background(self):
        # sky
        pyxel.cls(12)
        pyxel.rect(0, 0, W, 90, 6)

        # mountains
        pyxel.tri(20, 110, 60, 70, 100, 110, 5)
        pyxel.tri(90, 120, 140, 80, 190, 120, 5)
        pyxel.tri(160, 115, 200, 75, 240, 115, 5)

        # clouds
        for x, y, _v in self.clouds:
            xi = int(x)
            pyxel.circ(xi, y, 8, 7)
            pyxel.circ(xi + 10, y + 2, 10, 7)
            pyxel.circ(xi + 20, y, 8, 7)

        # ground
        pyxel.rect(0, GROUND_Y, W, H - GROUND_Y, 11)
        pyxel.line(0, GROUND_Y, W, GROUND_Y, 3)

        # grass dots
        for i in range(0, W, 12):
            pyxel.pset(i + (self.frame % 12), GROUND_Y + 6, 3)

    def draw_player_human(self):
        # simple pixel human
        head_x = self.px + CATCH_W // 2

        # head
        pyxel.circ(head_x, self.py + 10, 6, 15)
        pyxel.pset(head_x - 2, self.py + 9, 0)
        pyxel.pset(head_x + 2, self.py + 9, 0)

        # body
        pyxel.rect(self.px + 16, self.py + 18, 12, 16, 8)

        # arms (catch area)
        arm_y = self.py + 18
        pyxel.rect(self.px, arm_y, CATCH_W, CATCH_H, 8)
        pyxel.line(self.px, arm_y, self.px + CATCH_W, arm_y, 0)

        # hands
        pyxel.rect(self.px - 2, arm_y + 2, 2, 6, 15)
        pyxel.rect(self.px + CATCH_W, arm_y + 2, 2, 6, 15)

        # legs
        pyxel.rect(self.px + 18, self.py + 34, 4, 10, 0)
        pyxel.rect(self.px + 24, self.py + 34, 4, 10, 0)

    def draw(self):
        self.draw_background()

        if self.state == "TITLE":
            pyxel.rect(0, 0, W, H, 0)
            pyxel.text(W // 2 - 40, H // 2 - 25, "FRUIT CATCHER", 7)
            pyxel.text(W // 2 - 58, H // 2 - 5, "ENTER or SPACE to START", 7)
            pyxel.text(W // 2 - 54, H // 2 + 15, "A/D or <- -> to MOVE", 7)
            return

        # UI
        pyxel.text(5, 5, f"SCORE: {self.score}", 0)
        pyxel.text(5, 15, f"LIFE : {self.life}", 0)
        pyxel.text(5, 25, f"TIME : {self.time_left // 30}", 0)
        pyxel.text(160, 5, f"LV:{self.level}", 0)

        if self.combo >= 2 and self.combo_timer > 0:
            pyxel.text(160, 15, f"COMBO x{self.combo}", 2)

        pyxel.text(160, 25, "R: RESET", 0)

        # fruits
        for f in self.fruits:
            f.draw()

        # player
        self.draw_player_human()

        if self.state == "GAMEOVER":
            pyxel.rect(0, 0, W, H, 0)
            pyxel.text(W // 2 - 40, H // 2 - 18, "GAME OVER", 7)
            pyxel.text(W // 2 - 52, H // 2, f"SCORE: {self.score}", 7)
            pyxel.text(W // 2 - 52, H // 2 + 12, f"BEST COMBO: {self.best_combo}", 7)
            pyxel.text(W // 2 - 60, H // 2 + 26, "PRESS R TO RESTART", 7)


App()
