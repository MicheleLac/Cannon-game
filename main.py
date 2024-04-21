from kivy.app import App
from kivy.uix.widget import Widget
from kivy.properties import ObjectProperty, NumericProperty
from kivy.graphics import Color, Rectangle, Line, Ellipse
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.vector import Vector
import math


class Tank(Widget):
    cannon_angle = NumericProperty(0)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas:
            Color(0.2, 0.2, 0.9)
            self.rect = Rectangle(pos=self.pos, size=self.size, source="base_cannolone.png")
            self.cannon_length = 70
            self.cannon_width = 10
            Color(0.3, 0.2, 0)
            self.cannon = Line(points=(self.center_x, self.center_y, self.center_x + self.cannon_length, self.center_y + self.cannon_width), width=self.cannon_width)

        self.bind(pos=self.update_rect, size=self.update_rect)

    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size
        self.cannon.points = (self.center_x, self.center_y, self.center_x + self.cannon_length, self.center_y)

    def set_cannon_angle(self, mouse_pos):
        dx = mouse_pos[0] - self.center_x
        dy = mouse_pos[1] - self.center_y
        self.cannon_angle = math.atan2(dy, dx)

        self.cannon.points = (self.center_x, self.center_y,
                              self.center_x + self.cannon_length * math.cos(self.cannon_angle),
                              self.center_y + self.cannon_length * math.sin(self.cannon_angle)
                              )

    def collide_with_rock(self, rock):
        return self.collide_widget(rock)

    def move_right(self):
        if not self.collide_with_rock(self.parent.rock):
            self.x += 5

    def move_left(self):
            self.x -= 5


    def shoot(self, game):
        bullet = Bullet()
        bullet.angle = self.cannon_angle
        bullet.pos = [self.center_x + self.cannon_length * math.cos(bullet.angle) - bullet.size[0] / 2,
                      self.center_y + self.cannon_length * math.sin(bullet.angle) - bullet.size[1] / 2]
        game.bullets.add(bullet)
        game.add_widget(bullet)


class Bullet(Widget):
    mass = NumericProperty(0.5)
    speed = NumericProperty(10)
    time = NumericProperty(0)
    angle = NumericProperty(0)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size = (10, 10)
        with self.canvas:
            Color(0.2, 0.2, 0.9)
            self.bullet = Ellipse(pos=self.pos)

        self.bind(pos=self.update_bullet_pos)

    def update_bullet_pos(self, *args):
        self.bullet.pos = self.pos
        self.bullet.size = self.size

    def trajectory(self):
        self.x += self.speed * math.cos(self.angle)
        self.y += self.speed * math.sin(self.angle) - self.mass * self.time
        self.time += 0.5


class Rock(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas:
            Color(0.2, 0.2, 0.9)
            self.rect = Rectangle(pos=self.pos, size=self.size)
            

        self.bind(pos=self.update_rect_pos, size=self.update_rect_size)

    def update_rect_pos(self, *args):
        self.rect.pos = self.pos
    
    def update_rect_size(self, *args):
        self.rect.size = self.size


class CannonGame(Widget):
    tank = ObjectProperty(None)
    rock = ObjectProperty(None)
    fps = NumericProperty(60)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas:
            Color(0.5, 0.8, 0.9)
            self.wallpaper = Rectangle(pos=(0, 0), size=(Window.width, Window.height))
            Color(0, 1, 0)
            self.soil = Rectangle(pos=(0, 0), size=(Window.width, Window.height / 3))
        self.tank = Tank()
        self.tank.size_hint = (None, None)
        self.tank.pos = (0, Window.height / 3)
        self.tank.size = (100, 50)
        self.add_widget(self.tank)

        self.keys_pressed = set()
        self.bullets = set()

        self.rock = Rock()
        self.rock.size = (70, 70)
        self.add_widget(self.rock)
        self.rock.pos = (Window.width - self.rock.size[0], Window.height / 3)

        Window.bind(on_key_down=self.on_keyboard_down, on_key_up=self.on_keyboard_up)

        Window.bind(mouse_pos=self.on_mouse_move)
        self.mouse = Vector(Window.mouse_pos)

    def update(self, dt):
        if 275 in self.keys_pressed:
            self.tank.move_right()
        if 276 in self.keys_pressed:
            self.tank.move_left()
        self.tank.set_cannon_angle(self.mouse)
        for bullet in self.bullets:
            bullet.trajectory()
        if 115 in self.keys_pressed:
            self.tank.shoot(self)

    def on_keyboard_down(self, keyboard, keycode, *args):
        self.keys_pressed.add(keycode)

    def on_keyboard_up(self, keyboard, keycode, *args):
        self.keys_pressed.remove(keycode)

    def on_mouse_move(self, window, pos):
        self.mouse = Vector(pos)


class CannonApp(App):
    def build(self):
        game = CannonGame()
        Clock.schedule_interval(game.update, 1 / game.fps)
        return game


if __name__ == '__main__':
    CannonApp().run()
