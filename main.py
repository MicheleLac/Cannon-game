from turtle import window_width
from kivy.uix.label import Label 
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.properties import ObjectProperty, NumericProperty
from kivy.graphics import Color, Rectangle, Line, Ellipse
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.vector import Vector
import math, time
from kivy.properties import ListProperty
from random import randint
from kivy.uix.boxlayout import BoxLayout
import random

class Tank(Widget):
    cannon_angle = NumericProperty(0)


    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas:
            Color(0.2, 0.2, 0.9)
            self.rect = Rectangle(pos=self.pos, size=self.size)
            self.cannon_length = 70
            self.cannon_width = 10
            Color(0.2, 0.1, 1)
            self.cannon = Line(points=(self.center_x, self.center_y, self.center_x + self.cannon_length, self.center_y + self.cannon_width), width=self.cannon_width, source="testa_cannolone.png")
            

        self.bind(pos=self.update_rect, size=self.update_rect) # type: ignore
        self.shoot_cooldown = 0.3  # Set initial cooldown to 2 seconds
        self.last_shot_time = 0.0  # Track the time of the last shot


    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size
        self.cannon.points = (self.center_x, self.center_y, self.center_x + self.cannon_length, self.center_y)

    def set_cannon_angle(self, mouse_pos):
        dx = mouse_pos[0] - self.center_x #This line calculates the horizontal distance between the mouse position and the center of the tank.
        dy = mouse_pos[1] - self.center_y #This line calculates the vertical distance between the mouse position and the center of the tank.
        self.cannon_angle = math.atan2(dy, dx)

        self.cannon.points = (self.center_x, self.center_y,
                              self.center_x + self.cannon_length * math.cos(self.cannon_angle),
                              self.center_y + self.cannon_length * math.sin(self.cannon_angle)
                              )

    def collide_with_rock(self, rock):
        return self.collide_widget(rock)
    

    def move_right(self):
        if not self.collide_with_rock(self.parent.rock) and self.right <= Window.width:
            self.x += 5

    def move_left(self):
        if self.x >= 0:
            self.x -= 5



    def shoot(self, game):
        current_time = time.time()
        if current_time - self.last_shot_time >= self.shoot_cooldown:
            bullet = Bullet()
            bullet.angle = self.cannon_angle
            bullet.pos = [self.center_x + self.cannon_length * math.cos(bullet.angle) - bullet.size[0] / 2,
                          self.center_y + self.cannon_length * math.sin(bullet.angle) - bullet.size[1] / 2]
            game.bullets.add(bullet)
            game.add_widget(bullet)
            self.last_shot_time = current_time  # Update last shot time

    
    

class Bullet(Widget):
    mass = NumericProperty(0.5)
    speed = NumericProperty(5)
    time = NumericProperty(0)
    angle = NumericProperty(0)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size = (10, 10)
        with self.canvas:
            Color(0.2, 0.2, 0.9)
            self.bullet = Ellipse(pos=self.pos)

        self.bind(pos=self.update_bullet_pos) #type: ignore 

    def update_bullet_pos(self, *args):
        self.bullet.pos = self.pos
        self.bullet.size = self.size

    def trajectory(self):
        self.x += self.speed * math.cos(self.angle) 
        self.y += self.speed * math.sin(self.angle)  -  self.mass *( self.time + 1)
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
    
    def collide_with_bullet(self, bullet):
        return self.collide_widget(bullet)

    def move(self):
        self.pos[0] = random.randrange(0,929)
        self.pos[1] = random.randrange(0,300)
        


class Wormhole(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas:
            Color(0, 0, 0)  # Change color as needed
            self.circle = Ellipse(pos=self.pos, size=self.size)

        self.bind(pos=self.update_circle_pos, size=self.update_circle_size)

    def update_circle_pos(self, *args):
        self.circle.pos = self.pos

    def update_circle_size(self, *args):
        self.circle.size = self.size

    def collide_with_bullet(self, bullet):
        return self.collide_widget(bullet)
    
class PointsCounter(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Drawing the counter rectangle
        with self.canvas:
            Color(0, 0, 0)
            self.counter = Rectangle(pos=self.pos, size=self.size)

        # Initial score
        self.score_value = 0

        # Create a layout for label and counter
        self.layout = BoxLayout(orientation='vertical')

        # Adding label to display score
        self.label = Label(text=str(self.score_value))
        self.layout.add_widget(self.label)

        # Add the layout to PointsCounter widget
        self.add_widget(self.layout)

        # Binding position and size update methods
        self.bind(size=self.update_rect_size, pos = self.update_rect_pos)

    def update_rect_size(self, *args):
        self.counter.size = self.size
        self.layout.size = self.size  # Update layout size with widget size

    def update_rect_pos(self, *args):
        self.counter.pos = self.pos
        self.layout.pos = self.pos

    def score(self):
        self.score_value += 1
        self.label.text = str(self.score_value)  # Update label text with new score


class CannonGame(Widget):
    tank = ObjectProperty(None)
    rock = ObjectProperty(None)
    wormhole = ObjectProperty(None)
    fps = NumericProperty(60)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Initialize canvas
        with self.canvas:
            Color(0.5, 0.8, 0.9)
            self.wallpaper = Rectangle(pos=(0, 0), size=(Window.width, Window.height))
            Color(0, 1, 0)
            self.soil = Rectangle(pos=(0, 0), size=(Window.width, Window.height / 3))

        # Initialize tank
        self.tank = Tank()
        self.tank.size_hint = (None, None)
        self.tank.pos = (0, Window.height / 3)
        self.tank.size = (150, 60)
        self.add_widget(self.tank)

        self.keys_pressed = set()
        self.bullets = set()

        # Initialize rock
        self.rock = Rock()
        self.rock.size = (70, 70)
        self.add_widget(self.rock)
        self.rock.pos = (Window.width - self.rock.size[0], Window.height / 3)


        # Initialize wormholes
        self.enter_wormhole = Wormhole()
        self.add_widget(self.enter_wormhole)
        self.enter_wormhole.pos = (Window.width / 2.5, Window.height / 3)
        self.enter_wormhole.size = (80, 80)

        self.exit_wormhole = Wormhole()
        self.add_widget(self.exit_wormhole)
        self.exit_wormhole.pos = (Window.width / 2 + 280, Window.height / 2)
        self.exit_wormhole.size = (80, 80)
        
        self.counter = PointsCounter()  
        self.add_widget(self.counter)
        self.counter.pos = (0,Window.height - self.counter.size[1])
        self.counter.size = (80, 80)
        
        # Bind keyboard and mouse events
        Window.bind(on_key_down=self.on_keyboard_down, on_key_up=self.on_keyboard_up)
        Window.bind(mouse_pos=self.on_mouse_move)
        self.mouse = Vector(Window.mouse_pos)

    def update(self, dt):
        if 275 in self.keys_pressed:
            self.tank.move_right()
        if 276 in self.keys_pressed:
            self.tank.move_left()
        self.tank.set_cannon_angle(self.mouse)
        if 115 in self.keys_pressed:
            self.tank.shoot(self)

        if self.tank.y > Window.height / 3:
            self.tank.y -= 2.5
        else:
            self.tank.y = Window.height / 3
        
        # Check collision between the rock and the bullets
        bullets_to_remove = set()
        
        for bullet in self.bullets:
            if self.rock.collide_with_bullet(bullet):
                bullets_to_remove.add(bullet)
                self.rock.move()
                self.counter.score()
                
                    
            
            if self.enter_wormhole.collide_with_bullet(bullet):
                bullet.pos = self.exit_wormhole.center
            
        
        if self.enter_wormhole.collide_with_bullet(self.tank): 
            self.tank.pos = (self.exit_wormhole.center_x - 250, self.exit_wormhole.center_y )
        
        if self.exit_wormhole.collide_with_bullet(self.tank): 
            self.tank.pos = (self.enter_wormhole.center_x - 250, self.enter_wormhole.y )
       
        
                    
        for bullet in self.bullets:
            bullet.trajectory()


        # Remove collided bullets
        for bullet in bullets_to_remove:
            self.remove_widget(bullet)

        

        
            


        


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
