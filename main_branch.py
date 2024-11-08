from tkinter import Button
from turtle import title
from kivy.config import Config
Config.set('graphics', 'fullscreen', 'auto')
from kivy.uix.label import Label 
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.properties import ObjectProperty, NumericProperty
from kivy.graphics import Color, Rectangle, Line, Ellipse, Rotate
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.vector import Vector
import math, time
from kivy.uix.boxlayout import BoxLayout
import random
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.popup import Popup
from kivy.utils import get_color_from_hex
from kivy.uix.button import Button
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen

class Tank(Widget):
    cannon_angle = NumericProperty(0)


    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas:
            Color(1, 1, 1)
            self.rect = Rectangle(pos=self.pos, size=self.size, source = "base_cannolone.png" )
            self.cannon_length = 70
            self.cannon_width = 10
            Color(0, 0, 0)
            self.cannon = Line(points=(self.center_x, self.center_y, self.center_x + self.cannon_length, self.center_y + self.cannon_width), width=self.cannon_width)
            

        self.bind(pos=self.update_rect, size=self.update_rect) # type: ignore
        self.shoot_cooldown = 0.3  # Set initial cooldown to 2 seconds
        self.last_shot_time = 0.0  # Track the time of the last shot
        self.laser_cooldown = 0.5 # added laser cooldown
        self.laser_last_shot_time = 0.0  # Track the time of the last shot of laser



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

    def collide_with_rock(self, rock): #change collision logic
        return self.collide_widget(rock)
    

    def move_right(self):
        if not self.collide_with_rock(self.parent.rock) and self.right <= Window.width:
            self.x += 5

    def move_left(self):
        if self.x >= 0 and not self.collide_with_rock(self.parent.rock) and self.right <= Window.width :
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

    def shootLaser(self, game): #finish: WE NEED TO ROTATE LASER WITH CANNON 
        current_time = time.time()
        if current_time - self.laser_last_shot_time >= self.laser_cooldown:
            laser = Laser(angle = self.cannon_angle)
            #laser.velocity = Vector(1, 0).rotate(45)
            #laser.set_rotation(self.cannon_angle)
            laser.angle = self.cannon_angle 
            laser.pos = [self.center_x + self.cannon_length * math.cos(laser.angle) - laser.size[0] / 2,
                        self.center_y + self.cannon_length * math.sin(laser.angle) - laser.size[1] / 2]
            game.bullets.add(laser)
            game.add_widget(laser)
            self.laser_last_shot_time = current_time  # Update last shot time

    
    

class Bullet(Widget):
    mass = NumericProperty(0.5)
    speed = NumericProperty(0)
    time = NumericProperty(0)
    angle = NumericProperty(0)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size = (10, 10)
        with self.canvas:
            Color(0, 0, 0)
            self.bullet = Ellipse(pos=self.pos)

        self.bind(pos=self.update_bullet_pos) #type: ignore 

    def update_bullet_pos(self, *args):
        self.bullet.pos = self.pos
        self.bullet.size = self.size

    def trajectory(self):
        self.x += self.speed * math.cos(self.angle) 
        self.y += self.speed * math.sin(self.angle)  -  self.mass *( self.time + 1)
        self.time += 0.5

    """def increase_power(self, coefficent):
        self.speed += coefficent"""

class Laser(Widget): #do 
    mass = NumericProperty(0.5)
    speed = NumericProperty(1)
    time = NumericProperty(0)
    angle = NumericProperty(0)

    def __init__(self,angle = 0, **kwargs):
        super().__init__(**kwargs)
        self.size = (40,10)


        #self.angle = 90
        with self.canvas:
            Color(1, 0, 0) 
            self.rotation = Rotate(angle=self.angle, origin=self.center)
            self.angle = angle
            self.laser = Rectangle(pos=self.pos)
            

        self.bind(pos=self.update_laser_pos)
    
    #def rotate(self, angle):
    #    Rotate(angle = angle)

    def update_laser_pos(self, *args):
        self.laser.pos = self.pos
        self.laser.size = self.size        

    def trajectory(self):
        self.x += self.speed * math.cos(self.angle)
        self.y += self.speed * math.sin(self.angle)
        self.time += 0.5
    def set_rotation(self, angle):
        self.rotation.angle = angle


def random_except(start, stop, exclude1, exclude2 ):
    value = random.randrange(start, stop)
    if (value > (exclude1 + 180) or value < (exclude1 - 180)) and ( value > (exclude2 + 180) or value < (exclude2 - 180)) :
            return value
    else:
        return random_except(start, stop, exclude1, exclude2)

class Rock(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas:
            Color(1, 1, 1)
            self.rect = Rectangle(pos=self.pos, size=self.size, source= "rock.png")
            

        self.bind(pos=self.update_rect_pos, size=self.update_rect_size)

    def update_rect_pos(self, *args):
        self.rect.pos = self.pos
    
    def update_rect_size(self, *args):
        self.rect.size = self.size
    
    def collide_with_bullet(self, bullet):
        return self.collide_widget(bullet)

    def move(self,start, finish, exclude1, exclude2):
        self.pos[0] = random_except(start, finish, exclude1, exclude2)
        #self.pos[1] = random.randrange(250, 500)
        
class Mirror(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas:
            Color(0.68, 0.85, 0.9)
            self.rect = Rectangle(pos=self.pos, size=(10,100))
            self.rotation = Rotate(45)
            

        self.bind(pos=self.update_rect_pos, size=self.update_rect_size)

    def update_rect_pos(self, *args):
        self.rect.pos = self.pos

    
    def update_rect_size(self, *args):
        self.rect.size = self.size
    
    def collide_with_bullet(self, bullet):
        return self.collide_widget(bullet)

    def move(self):#should we call it "changepos" ?
        self.pos[0] = random.randrange(0,929)
        self.pos[1] = random.randrange(355,600)
        

class Wormhole(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas:
            Color(1, 1, 1)  # Change color as needed
            self.circle = Ellipse(pos=self.pos, size=self.size, source = "wormhole.png")

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
            Color(1, 1, 1)
            self.counter = Rectangle(pos=self.pos, size=self.size, source = "counter.png")

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


class Powerbar(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Drawing the counter rectangle
        with self.canvas:
            Color(1, 1, 1)
            self.power = Rectangle(pos=self.pos, size=self.size, source = "Freccia.png")
        
        
        self.bind(size=self.update_power_size, pos= self.update_power_pos)
    
    def update_power_size(self, *args):
        self.power.size = self.size
    
    def update_power_pos(self, *args):
        self.power.pos = self.pos

    def increase_size(self):
        self.size[0] = self.size[0] + 8

    def decrease_size(self):
        self.size[0] = self.size[0] - 8


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
            self.wallpaper = Rectangle(pos=(0, 0), size=(Window.width, Window.height), source = "sky.png")
            Color(0, 0.8, 0)
            self.soil = Rectangle(pos=(0, 0), size=(Window.width, Window.height / 3), source = "ground.png")

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

        # Initialize Mirror
        self.mirror = Mirror()
        self.add_widget(self.mirror)
        self.mirror.pos= (400,400)

        # Initialize wormholes
        self.enter_wormhole = Wormhole()
        self.add_widget(self.enter_wormhole)
        self.enter_wormhole.pos = (Window.width / 2.5, Window.height / 3)
        self.enter_wormhole.size= (80, 80)
        

        self.exit_wormhole = Wormhole()
        self.add_widget(self.exit_wormhole)
        self.exit_wormhole.pos = (Window.width / 2 + 280, Window.height / 2)
        self.exit_wormhole.size = (80, 80)
        
        self.counter = PointsCounter()  
        self.add_widget(self.counter)
        self.counter.pos = (0,Window.height - self.counter.size[1])
        self.counter.size = (80, 80)
        
        
        self.power = Powerbar()
        self.power.pos = (self.counter.width + 5 ,Window.height - self.power.size[1])
        self.power.size = (150, 50)
        with self.canvas:
            Color(1, 1, 1)
            Rectangle(pos= self.power.pos, size=(500, 60), source = "energia.jpg")
        self.add_widget(self.power)
        
        
        # Bind keyboard and mouse events
        Window.bind(on_key_down=self.on_keyboard_down, on_key_up=self.on_keyboard_up)
        Window.bind(mouse_pos=self.on_mouse_move)
        self.mouse = Vector(Window.mouse_pos)

    def update(self, dt):
        if 275 in self.keys_pressed: #97
            self.tank.move_right()
        if 276 in self.keys_pressed: #100
            self.tank.move_left()
        self.tank.set_cannon_angle(self.mouse)
        if 115 in self.keys_pressed:
            self.tank.shoot(self)
        if 112 in self.keys_pressed and self.power.size[0]<=522:   #if you press p
            self.power.increase_size()
        if 108 in self.keys_pressed and self.power.size[0] >= 140:   #if you press l
            self.power.decrease_size()
        if 32 in self.keys_pressed: #shoot laser (space)
            self.tank.shootLaser(self)

        
        

        if self.tank.y > Window.height / 3:
            self.tank.y -= 2.5
        else:
            self.tank.y = Window.height / 3
        
        # Check collision between the rock and the bullets
        bullets_to_remove = set()
        
        for bullet in self.bullets:
            bullet.speed = self.power.size[0]/30
            if self.rock.collide_with_bullet(bullet):
                bullets_to_remove.add(bullet)
                self.rock.move(0, Window.width - self.rock.size[0], self.tank.pos[0], self.enter_wormhole.pos[0])
                self.counter.score()
                
            if self.mirror.collide_with_bullet(bullet): #if bullet is laser change angle if bullet destroy
                if isinstance(bullet, Laser):
                    bullet.angle = bullet.angle +180 
                elif isinstance(bullet, Bullet):
                    bullets_to_remove.add(bullet)
                    self.mirror.move()
                    
            
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
        print(keycode)
        self.keys_pressed.add(keycode)


    def on_keyboard_up(self, keyboard, keycode, *args):
        self.keys_pressed.remove(keycode)

    def on_mouse_move(self, window, pos):
        self.mouse = Vector(pos)


class MainMenuBackground(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(pos=self.update_rect, size=self.update_rect)
        with self.canvas:
            self.rect = Rectangle(source="sfondo.jpg", pos=self.pos, size=self.size)

    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size


class MainMenu(Screen):
    def show_welcome(self, instance):
        welcome_text = 'Hope you have fun'
        popup = Popup(title="Welcome", content=Label(text=welcome_text), size_hint=(None, None), size=(500, 250))
        popup.open()

    def play(self, instance):
        self.manager.current = 'cannon_game'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.add_widget(MainMenuBackground())

        button_color = get_color_from_hex("#ff0000")

        welcome_button = Button(
            text='Welcome to Cannon Game',
            size_hint=(0.2, 0.2),
            pos_hint={'center_x': 0.5, 'center_y': 0.8},
            font_size=37,
            background_color=button_color
        )

        welcome_button.bind(on_release=self.show_welcome)
        self.add_widget(welcome_button)

        play_button = Button(
            text='Play',
            size_hint=(0.5, 0.2),
            pos_hint={'center_x': 0.5, 'center_y': 0.6},
            font_size=37,
            background_color=button_color
        )

        play_button.bind(on_release=self.play)
        self.add_widget(play_button)

class Game(Screen):
     def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        self.add_widget(CannonGame())

class CannonApp(App):
    def build(self):
        self.screen_manager = ScreenManager()

        main_menu = MainMenu(name='main_menu')
        cannon_game = Game(name='cannon_game')

        self.screen_manager.add_widget(main_menu)
        self.screen_manager.add_widget(cannon_game)
       
        
        game = CannonGame()
        Clock.schedule_interval(game.update, 1 / game.fps)

        return game


if __name__ == '__main__':
    CannonApp().run()
    
