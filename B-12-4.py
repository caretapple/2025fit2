import pyxel

# 定数
W, H = 200, 200


# ---------- Pad クラス ----------
class Pad:
    def __init__(self, w=40, h=5, y=H - 5):
        self.w = w
        self.h = h
        self.x = W // 2
        self.y = y

    def update(self):
        # マウスで左右移動（はみ出し防止）
        self.x = max(self.w // 2, min(pyxel.mouse_x, W - self.w // 2))

    def draw(self):
        pyxel.rect(self.x - self.w // 2, self.y - self.h // 2, self.w, self.h, 14)

    def catch(self, ball):
        # パドルとボールの位置が重なっていれば True
        in_y = (self.y - self.h // 2) <= ball.y <= (self.y + self.h // 2)
        in_x = (self.x - self.w // 2) <= ball.x <= (self.x + self.w // 2)
        return in_y and in_x


# ---------- Ball クラス ----------
class Ball:
    def __init__(self):
        self.reset()
        self.speed = 1.2

    def reset(self):
        self.x = pyxel.rndi(10, W - 10)
        self.y = 20
        ang = pyxel.rndi(30, 150)
        self.vx = pyxel.cos(ang)
        self.vy = pyxel.sin(ang)

    def update(self):
        self.x += self.vx * self.speed
        self.y += self.vy * self.speed

        # 壁反射
        if self.x < 0 or self.x > W - 1:
            self.vx = -self.vx
        if self.y < 0:
            self.vy = -self.vy
        # 下に抜けたらリセット
        if self.y > H:
            self.reset()

    def draw(self):
        pyxel.circ(int(self.x), int(self.y), 2, 10)


# ---------- App クラス ----------
class App:
    def __init__(self):
        pyxel.init(W, H, title="PadとBall (クラス版)")
        pyxel.mouse(True)

        self.pad = Pad()
        self.ball = Ball()

        pyxel.run(self.update, self.draw)

    def update(self):
        self.pad.update()
        self.ball.update()

        # パドルに当たったら反射
        if self.ball.vy > 0 and self.pad.catch(self.ball):
            self.ball.vy = -self.ball.vy

    def draw(self):
        pyxel.cls(0)
        self.pad.draw()
        self.ball.draw()


# 実行
App()
