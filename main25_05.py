
from tkinter import Button
from turtle import title, width
from kivy.config import Config

from matplotlib import use
from numpy import delete
from sklearn.linear_model import enet_path
from zmq import has
Config.set('graphics', 'fullscreen', 'auto')
from kivy.uix.label import Label 
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.properties import ObjectProperty, NumericProperty
from kivy.graphics import Color, Rectangle, Line, Ellipse, Rotate, PushMatrix, PopMatrix
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.vector import Vector
import math, time
from kivy.uix.boxlayout import BoxLayout
import random
from kivy.uix.screenmanager import ScreenManager, Screen, RiseInTransition
from kivy.uix.popup import Popup
from kivy.utils import get_color_from_hex
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from functools import partial



class Tank(Widget):
    cannon_angle = NumericProperty(0)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        
        with self.canvas: #type: ignore
            Color(1, 1, 1)
            self.rect = Rectangle(pos=self.pos, size=self.size, source = "spaceship.png" )
            self.cannon_length = 110
            self.cannon_width = 10
            Color(0.169, 0.169, 0.169)
            self.cannon = Line(points=(self.center_x, self.center_y, self.center_x + self.cannon_length, self.center_y + self.cannon_width), width=self.cannon_width)
            self.size = self.rect.size

        self.bind(pos=self.update_rect, size=self.update_rect) # type: ignore
        self.laser_shoot_cooldown = 2  # Set initial cooldown to 2 seconds
        self.last_shot_time = 0.0  # Track the time of the last shot
        self.num_col =0
        self.has_collided= False

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
        return self.cannon_angle
    
     
     


    def collide_with_rock(self, rock):
        return self.collide_widget(rock)
    
    def collide_with_bullet(self, bullet):
        if screen_manager.current == 'main_menu' or screen_manager.current == 'levels' or screen_manager.current == 'game_win' :  #type: ignore
            return False 
        else:
            self.has_collided = True 
            return self.collide_widget(bullet)


    def move_right(self):
        if self.right <= Window.width:
            self.x += 5

    def move_left(self):
        if self.x >= 0:
            self.x -= 5




    def shoot(self, game):
        self.bullet_shoot_cooldown = 0.3
        current_time = time.time()
        if current_time - self.last_shot_time >= self.bullet_shoot_cooldown:
            bullet = Bullet()
            bullet.angle = self.cannon_angle
            bullet.pos = [self.center_x + self.cannon_length * math.cos(bullet.angle) - bullet.size[0] / 2,
                          self.center_y + self.cannon_length * math.sin(bullet.angle) - bullet.size[1] / 2]
            game.bullets.add(bullet)
            game.add_widget(bullet)
            self.last_shot_time = current_time  # Update last shot time

    def shootLaser(self, game):
        #self.shoot_cooldown = 0.3
        current_time = time.time()
        if current_time - self.last_shot_time >= self.laser_shoot_cooldown:
            laser = Laser()
            laser.angle = math.degrees(self.cannon_angle)
            laser.pos = [self.center_x + self.cannon_length * math.cos(self.cannon_angle) - laser.size[0] / 2,
                          self.center_y + self.cannon_length * math.sin(self.cannon_angle) - laser.size[1] / 2]
            game.bullets.add(laser)
        
            game.add_widget(laser)
            self.last_shot_time = current_time  # Update last shot time
    def shootBombshell(self, game):
        self.shoot_cooldown = 1
        current_time = time.time()
        if current_time - self.last_shot_time >= self.shoot_cooldown:
            bombshell = Bombshell()
            bombshell.angle = self.cannon_angle
            bombshell.pos = [self.center_x + self.cannon_length * math.cos(bombshell.angle) - bombshell.size[0] / 2,  #type: ignore
                            self.center_y + self.cannon_length * math.sin(bombshell.angle) - bombshell.size[1] / 2]
            game.bullets.add(bombshell)
            game.add_widget(bombshell)
            self.last_shot_time = current_time  # Update last shot time

    



def counter(fn):
        def _counted(*largs, **kargs):
            _counted.invocations += 1
            fn(*largs, **kargs)
        _counted.invocations = 0
        return _counted  

class Enemy(Widget):
    cannon_angle = NumericProperty(0)
    direction = NumericProperty(1)  # 1 for right, -1 for left


    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        
        with self.canvas:
            Color(1, 1, 1)
            self.rect = Rectangle(pos=self.pos, size=self.size, source = "enemyship.png" )
            self.cannon_length = 70
            self.cannon_width = 10
            #Color(0.169, 0.1, 0.169)
            Color(0,0,0,0)
            self.cannon = Line(points=(self.center_x, self.center_y, self.center_x + self.cannon_length, self.center_y + self.cannon_width), width=self.cannon_width)
            

        self.bind(pos=self.update_rect, size=self.update_rect) # type: ignore
        self.shoot_cooldown = 2  # Set initial cooldown to 2 seconds
        self.last_shot_time = 0.0  # Track the time of the last shot
        self.last_angle_change_time = 0  # Initialize the time of the last angle change
        self.cooldown_duration = 1  # 5 seconds cooldown
        self.has_collided= False
        Clock.schedule_interval(self.move, 1 / 60.)  # 60 times per second
        Clock.schedule_interval(self.change_direction, 1)  # Change direction every second

    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size
        self.cannon.points = (self.center_x, self.center_y, self.center_x + self.cannon_length, self.center_y)
        

    def move(self, dt):
        # Move right or left based on the direction property
        self.x += self.direction * 5
        # Check for screen boundaries and reset position if necessary
        if self.x <= 0:
            self.x = 0
            self.direction = 1
        elif self.x + self.width >= self.parent.width:
            self.x = self.parent.width - self.width
            self.direction = -1

    def change_direction(self, dt):
        # Randomly change direction
        self.direction = random.choice([-1, 1])


            


    def set_cannon_angle(self):
            dx = -2.5
            dy = -172.5
            self.cannon_angle = math.atan2(dy, dx)

            self.cannon.points = (self.center_x, self.center_y,
                                  self.center_x + self.cannon_length * math.cos(self.cannon_angle),
                                  self.center_y + self.cannon_length * math.sin(self.cannon_angle)
                                  )

            return self.cannon_angle
    
     
     


    def collide_with_bullet(self, bullet):
        self.has_collided = True 
        return self.collide_widget(bullet)




    def shoot(self, game):
        current_time = time.time()
        if current_time - self.last_shot_time >= self.shoot_cooldown:
            bullet = Bullet()
            bullet.angle = self.cannon_angle
            bullet.pos = [self.center_x + self.cannon_length * math.cos(bullet.angle) - bullet.size[0] / 2,
                          self.center_y + self.cannon_length * math.sin(bullet.angle) - bullet.size[1] / 2]
            game.enemy_bullets.add(bullet)
            game.add_widget(bullet)
            self.last_shot_time = current_time  # Update last shot time

    def shootLaser(self, game):
        current_time = time.time()
        if current_time - self.last_shot_time >= self.shoot_cooldown:
            laser = Laser()
            laser.angle = math.degrees(self.cannon_angle)
            laser.pos = [self.center_x + self.cannon_length * math.cos(self.cannon_angle) - laser.size[0] / 2,
                          self.center_y + self.cannon_length * math.sin(self.cannon_angle) - laser.size[1] / 2]
            game.enemy_bullets.add(laser)
        
            game.add_widget(laser)
            self.last_shot_time = current_time  # Update last shot time

    def shootBombshell(self, game):
        self.shoot_cooldown = 1
        current_time = time.time()
        if current_time - self.last_shot_time >= self.shoot_cooldown:
            bombshell = Bombshell()
            bombshell.angle = self.cannon_angle
            bombshell.pos = [self.center_x + self.cannon_length * math.cos(bombshell.angle) - bombshell.size[0] / 2,
                            self.center_y + self.cannon_length * math.sin(bombshell.angle) - bombshell.size[1] / 2]
            game.bullets.add(bombshell)
            game.add_widget(bombshell)
            self.last_shot_time = current_time  # Update last shot time









class Bullet(Widget):
    mass = NumericProperty(0.5)
    speed = NumericProperty(0)
    time = NumericProperty(0)
    angle = NumericProperty(0)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size = (10, 10)
        with self.canvas:
            Color(1,0.6,0.4)
            self.bullet = Ellipse(pos=self.pos)

        self.bind(pos=self.update_bullet_pos) #type: ignore 

    def update_bullet_pos(self, *args):
        self.bullet.pos = self.pos
        self.bullet.size = self.size

    def trajectory(self):
        self.x += self.speed * math.cos(self.angle) 
        self.y += self.speed * math.sin(self.angle)  -  self.mass *( self.time + 1)
        self.time += 0.5
        return self.angle

    def gravitational_attraction(self, gravitonio):
        G = 6.67259 *10**(-2)
        M = 2000
        distance = (self.pos[0]-self.pos[0])**2 +((self.pos[1]+ self.size[1]/2) -self.pos[1])**2
        self.x -= (G*M *self.x)/(distance)**3
        self.y -= (G*M *self.y)/(distance)**3
        self.time += 0.5

def random_except(start, stop, exclude1, exclude2, exclude3):
    value = random.randrange(start, stop)
    if (value > (exclude1 + 180) or value < (exclude1 - 180)) and ( value > (exclude2 + 180) or value < (exclude2 - 180)) and ( value > (exclude3 + 280) or value < (exclude3 - 280)):
            return value
    else:
        return random_except(start, stop, exclude1, exclude2, exclude3)

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

    def move(self,start, finish, exclude1, exclude2, exclude3):
        self.pos[0] = random_except(start, finish, exclude1, exclude2, exclude3)
        #self.pos[1] = random.randrange(250, 500)
    
    
    
    

class Coin(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas:
            Color(255,255,0)
            self.rect = Ellipse(pos=self.pos, size=self.size)
            

        self.bind(pos=self.update_rect_pos, size=self.update_rect_size)

    def update_rect_pos(self, *args):
        self.rect.pos = self.pos
    
    def update_rect_size(self, *args):
        self.rect.size = self.size
    
    def collide_with_bullet(self, bullet):
        return self.collide_widget(bullet)

    def move(self, elem):
        self.pos[0] = random.randrange( 0, int( Window.width-self.size[0]), int(elem.pos[0]))
        self.pos[1] = random.randrange(int(Window.height/2),int( Window.height -self.size[0]*3), int(elem.pos[1]))
        
class Wormhole(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas:
            Color(1, 1, 1)  # Change color as needed
            self.circle = Ellipse(pos=self.pos, size=self.size, source = "wormho.png")

        self.bind(pos=self.update_circle_pos, size=self.update_circle_size)

    def update_circle_pos(self, *args):
        self.circle.pos = self.pos

    def update_circle_size(self, *args):
        self.circle.size = self.size

    def collide_with_bullet(self, bullet):
        return self.collide_widget(bullet)
    
    def collide_dir(self, obj2):
        left1 = self.x
        right1 = self.x + self.width

        left2 = obj2.x
        right2 = obj2.x + obj2.width

        top1 = self.y + self.height
        bottom1 = self.y

        top2 = obj2.y + obj2.height
        bottom2 = obj2.y

        
        # Check for collision
        if right1 == left2 or left1 == right2 or top1 == bottom2 or bottom1 == top2:
            # Determine collision direction
            if right1 == left2:
                return 'right'
            elif left1 == right2:
                return 'left'
            
        
    
class Enemylife(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Drawing the counter rectangle
        with self.canvas:
            Color(1, 1, 1)
            self.counter = Rectangle(pos=self.pos, size=self.size, source = "vita.png")
 
        # Initial score
        self.enemy_value = 20

        # Create a layout for label and counter
        self.layout = BoxLayout(orientation='vertical')

        # Adding label to display score
        self.label = Label(text=str(self.enemy_value))
        self.layout.add_widget(self.label)

        # Add the layout to Enemylife widget
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
        self.enemy_value += 1
        self.label.text = str(self.enemy_value)  # Update label text with new score

    def descore(self,value=1):
        self.enemy_value -= value
        self.label.text = str(self.enemy_value)

class CoinsCounter(Widget):
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

        # Add the layout to Enemylife widget
        self.add_widget(self.layout)

        # Binding position and size update methods
        self.bind(size=self.update_rect_size, pos = self.update_rect_pos) #type: ignore 

    def update_rect_size(self, *args):
        self.counter.size = self.size
        self.layout.size = self.size  # Update layout size with widget size

    def update_rect_pos(self, *args):
        self.counter.pos = self.pos
        self.layout.pos = self.pos

    def score(self):
        self.score_value += 1
        self.label.text = str(self.score_value)  # Update label text with new score

class LifeCounter(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Drawing the counter rectangle
        with self.canvas:
            Color(1, 1, 1)
            self.counter = Rectangle(pos=self.pos, size=self.size, source = "counter.png")

        # Initial score
        self.life_value = 5

        # Create a layout for label and counter
        self.layout = BoxLayout(orientation='vertical')

        # Adding label to display score
        self.label = Label(text=str(self.life_value))
        self.layout.add_widget(self.label)

        # Add the layout to Enemylife widget
        self.add_widget(self.layout)

        # Binding position and size update methods
        self.bind(size=self.update_rect_size, pos = self.update_rect_pos)

    def update_rect_size(self, *args):
        self.counter.size = self.size
        self.layout.size = self.size  # Update layout size with widget size

    def update_rect_pos(self, *args):
        self.counter.pos = self.pos
        self.layout.pos = self.pos

    def descore(self,value=1):
        self.life_value -= value
        self.label.text = str(self.life_value)  # Update label text with new score

    def score(self, num):
        self.life_value += num
        self.label.text = str(self.life_value)  # Update label text with new score

class PerpetuoPlatform(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas:
            Color(1, 1, 1)
            self.rect = Rectangle(pos=self.pos, size=self.size, source = "perpetuo.jpg")
            

        self.bind(pos=self.update_rect_pos, size=self.update_rect_size)

    def update_rect_pos(self, *args):
        self.rect.pos = self.pos
    
    def update_rect_size(self, *args):
        self.rect.size = self.size
    
    def collide_with_bullet(self, bullet):
        return self.collide_widget(bullet)

    def move(self,start, finish, exclude1, exclude2, exclude3):
        self.pos[0] = random_except(start, finish, exclude1, exclude2, exclude3)
        #self.pos[1] = random.randrange(250, 500)
    


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

class Bombshell(Widget):
    mass = NumericProperty(1)
    speed = NumericProperty(0)
    time = NumericProperty(0)
    angle = NumericProperty(0)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size = (30, 30)
        self.has_collided = False
        self.exploded = False
        with self.canvas:
            Color(1, 1, 1)
            self.bullet = Ellipse(pos=self.pos, source = "Cartoon-Bomb-Clipart.png")

        self.bind(pos=self.update_bombshell_pos) #type: ignore 

    def update_bombshell_pos(self, *args):
        self.bullet.pos = self.pos
        self.bullet.size = self.size

    def trajectory(self):
        self.x += self.speed * math.cos(self.angle) 
        self.y += self.speed * math.sin(self.angle)  -  self.mass *( self.time + 1)
        self.time += 0.5
    
    def explode(self,delay):
        self.exploded = True
        #self.speed = 0
         # Explode after 1 second
       # self.canvas.clear()
        self.mass = 999
        with self.canvas:
            Color(1, 1, 1)  # Example color
            Ellipse(pos=self.pos, size=(60, 60), source = "esplosione.png")
        self.pos = (50000, 50000)
        

    def clear_from_ground(self,dt):
        self.canvas.clear()
        
class Laser(Widget):
    mass = NumericProperty(0.5)
    speed = NumericProperty(0)
    time = NumericProperty(0)
    angle = NumericProperty(0)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size = (40, 10)
        
        
        with self.canvas:
            PushMatrix()
            Color(0,0.9,0)
            self.rotation = Rotate(angle=self.angle, origin=self.center)
            self.laser = Rectangle(pos=self.pos, size=self.size)
            PopMatrix()

        self.bind(pos=self.update_laser_pos)  

        

    def update_laser_pos(self, *args):
        self.rotation.origin = self.center
        self.rotation.angle = self.angle
        self.laser.pos = self.pos
        self.laser.size = self.size

    
    

    def trajectory(self):
        self.x += self.speed  *math.cos(math.radians(self.angle)) 
        self.y += self.speed  *math.sin(math.radians(self.angle)) 
        self.time += 0.5
       

class Mirror(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas:
            Color(0.68, 0.85, 0.9)
            PushMatrix()
            self.rotation = Rotate(angle= 0, origin=self.center)
            self.mir = Rectangle(pos=self.pos, size=(10,100))
            PopMatrix()
            self.size = self.mir.size
            

        self.bind(pos=self.update_mir_pos, size=self.update_mir_size)

    def update_mir_pos(self, *args):
        self.mir.pos = self.pos
        self.rotation.origin = self.center

    
    def update_mir_size(self, *args):
        self.mir.size = self.size
    
    def collide_with_bullet(self, bullet):
            #if bullet.pos[0] == self.pos[0] and bullet.y <= self.pos[1] <= self.size[1]:
                #return True 
            return self.collide_widget(bullet)
        
        

    def move(self):#should we call it "changepos" ?
        self.pos[0] = random.randrange(0,929)
        self.pos[1] = random.randrange(355,600)

class Gravitonio(Widget):
    mass =NumericProperty(2)
    #radius = NumericProperty(10000)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        with self.canvas:
            Color(1, 1, 1)  # Black color
            self.circle = Ellipse(pos=self.pos, size=self.size, source = "gravitonio.png")

        # Bind position and size updates to the update method
        self.bind(pos=self.update_ellipses, size=self.update_ellipses)

    def update_ellipses(self, *args):
        self.circle.pos = self.pos
        self.circle.size = self.size

    def collide_with_bullet(self, bullet):
        #bullet.center_x = bullet.size[0] /2
        #bullet.center_y = bullet.size[1] /2
        distance = math.sqrt((self.pos[0]-bullet.pos[0])**2 +((self.pos[1]+ self.size[1]/2) -bullet.pos[1])**2)
        if distance <= 150:
            return True     
        else:
            return False 
    
    #togliere l'ellisse grande e scrivere la proprità raggio, usare quella per definire l funzione collide + cercare equazione della traiettoria 



class Shield(Widget):
    alpha = NumericProperty(0)
    source = "shield.png"
    damaged_shield = "damaged.png"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        
        with self.canvas:
            self.color = Color(1, 1, 1, self.alpha)
            
            self.circle = Ellipse(pos=self.pos, size=self.size, source = self.source)

        # Bind position and size updates to the update method
        self.bind(pos=self.update_ellipses, size=self.update_ellipses, alpha=self.update_color)

    shield_power = 3
    
    def update_ellipses(self, *args):
        self.circle.pos = self.pos
        self.circle.size = self.size

    def update_color(self, *args):
        self.color.a = self.alpha

    def move_with(self, elem):
        self.pos = elem.pos

    def collide_with_bullet(self, bullet):
        if self.alpha == 0:
            return False  # Ignore collision if the shield is invisible
        return self.collide_widget(bullet)
    
 

class CannonGame(Widget):# properties of objects should be in class
    tank = ObjectProperty(None)
    rock = ObjectProperty(None)
    wormhole = ObjectProperty(None)
    fps = NumericProperty(60)
    level = 1
    
    

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        print("level", self.level)
        


        # Initialize canvas
        with self.canvas:
            Color(1, 1, 1)
            
            self.wallpaper = Rectangle(pos=(0, 0), size=(Window.width, Window.height), source = "sfondo2.jpg")
            #Color(1, 1, 1)
            #self.soil = Rectangle(pos=(0, 0), size=(Window.width, Window.height / 3), source = "ground.png")
        # Initialize tank
        self.tank = Tank()
        self.tank.size_hint = (None, None)
        self.tank.pos = (0, 150)
        self.tank.size = (150, 150)
        self.add_widget(self.tank)

        self.shield = Shield()
        self.shield.size_hint = (None, None)
        self.shield.pos = (0, 150)
        self.shield.size = (155, 155)
        self.add_widget(self.shield)
        



        self.enemy = Enemy()
        self.enemy.size_hint = (None, None)
        self.enemy.pos = (Window.width/2 - self.enemy.size[0]*2, Window.height / 1.5)
        self.enemy.size = (165, 160)
        self.enemy.set_cannon_angle()
        self.add_widget(self.enemy)


        self.keys_pressed = set()
        self.bullets = set()
        self.enemy_bullets = set()
        


        # Initialize rock
        self.rock = Rock()
        self.rock.size = (90, 90)
        self.add_widget(self.rock)

        self.perpetuo = PerpetuoPlatform()
        self.perpetuo.size = (200, 90)
        self.perpetuo.pos = (400,400)
        self.add_widget(self.perpetuo)

       



        # Initialize wormholes
        self.enter_wormhole = Wormhole()
        self.add_widget(self.enter_wormhole)
        self.enter_wormhole.pos = (Window.width / 2, 180)
        self.enter_wormhole.size= (100, 100)
        

        self.exit_wormhole = Wormhole()
        self.add_widget(self.exit_wormhole)
        self.exit_wormhole.pos = (Window.width / 2 + 280, Window.height / 2)
        self.exit_wormhole.size =  (100, 100)

        if self.level == 1:
            self.rock.pos = (Window.width/2 +100, 390)
            
        """"elif self.level == 2:
            
            self.add_widget(self.enter_wormhole)
            self.enter_wormhole.pos = (Window.width / 2, 180)
            self.enter_wormhole.size= (100, 100)
            

            self.add_widget(self.exit_wormhole)
            self.exit_wormhole.pos = (Window.width / 2 + 280, Window.height / 2)
            self.exit_wormhole.size =  (100, 100)"""


        self.counter = Enemylife()  
        self.add_widget(self.counter)
        self.counter.pos = (0,Window.height - self.counter.size[1])
        self.counter.size = (80, 80)

        self.coinscounter = CoinsCounter()  
        self.coinscounter.pos = (Window.width - self.coinscounter.size[0],Window.height - self.coinscounter.size[1])
        self.coinscounter.size = (80, 80)
        self.add_widget(self.coinscounter)
        
        self.lifecounter = LifeCounter()  
        self.lifecounter.pos = (Window.width/2 ,Window.height - self.lifecounter.size[1])
        self.lifecounter.size = (80, 80)
        self.add_widget(self.lifecounter)


        # Initialize Mirror
        self.mirror = Mirror()
        self.add_widget(self.mirror)
        self.mirror.pos= (Window.width -self.size[0],500)

        self.gravitonio = Gravitonio()  
        self.gravitonio.pos = (500,500)
        self.gravitonio.size = (90, 90)
        self.add_widget(self.gravitonio)

        self.coin = Coin()  
        self.coin.pos = (260,328)
        self.coin.size = (30, 30)
        self.add_widget(self.coin)
        
       

        self.power = Powerbar()
        self.power.pos = (self.counter.width + 5 ,Window.height - self.power.size[1])
        self.power.size = (150, 50)
        with self.canvas:
            Color(1, 1, 1)
            Rectangle(pos= self.power.pos, size=(500, 60), source = "energia.jpg")
        self.add_widget(self.power)
        

        #armory_button = Button(
        #    text='armory',
        #    size_hint=(0.2, 0.2),
        #    pos_hint={'center_x': 0.5, 'center_y': 0.8},
        #    font_size=37,
        #    background_color=(0,0,0)
        #)

        
        #armory_button.bind(on_release=self.ChooseWeapon())
        #self.add_widget(armory_button)

        # Bind keyboard and mouse events
        Window.bind(on_key_down=self.on_keyboard_down, on_key_up=self.on_keyboard_up)
        Window.bind(mouse_pos=self.on_mouse_move)
        self.mouse = Vector(Window.mouse_pos)

    def reinitialize(self):
        # Custom reinitialization method
        self.__init__()

    def initializeGame(self): #move almost everything from init here because init is called too early(before we choose the level)
        print( "level is", self.level)


    def on_enter(self): #we need to call it to change levels because it is initialized with level 0, but we want to initialize it with level according to variable
        #as an alternative we can write a class for each level but it is gonna be a mess
        # Called when the screen is displayed
        self.clear_widgets()
        self.add_widget(Label(text=f'Cannon Game Level: {self.level}'))
       

    def remove_with_delay(self, widget,*largs):
        if isinstance(widget, Bombshell) and not widget.exploded:
            widget.exploded = True
            self.remove_widget(widget)
        else: 
            self.remove_widget(widget)


    def update(self, dt):
        angle = self.tank.set_cannon_angle(self.mouse)
        Laser.angle = math.degrees(angle)
        
        self.enemy.set_cannon_angle()

        

        if 100 in self.keys_pressed:
            self.tank.move_right()
        if 97 in self.keys_pressed:
            self.tank.move_left()
        self.tank.set_cannon_angle(self.mouse)
        
        if 119 in self.keys_pressed:
            self.tank.shoot(self)
        if 112 in self.keys_pressed and self.power.size[0]<=522:   #if you press p
            self.power.increase_size()
        if 108 in self.keys_pressed and self.power.size[0] >= 140:   #if you press l
            self.power.decrease_size()
        if 32 in self.keys_pressed:
            self.tank.shootLaser(self)
        if 98 in self.keys_pressed: #shoot bombshell (b)
            self.tank.shootBombshell(self)
        if self.lifecounter.life_value == 0:
            global username
            self.SaveScore(username, self.counter.enemy_value)
            screen_manager.current = 'game_over'
        
        if self.counter.enemy_value <= 0:
            screen_manager.current = 'game_win'
        
        bullets_to_remove = set()
        
        #functions to dectect where the collision between the tank and wormhole took place, so to keep going in the same direction from the other wormhole
        enter_collide_dir = self.enter_wormhole.collide_dir(self.tank)
        exit_collide_dir = self.exit_wormhole.collide_dir(self.tank)


        #the more coins you have the more you can use the laser 
        if self.coinscounter.score_value >= 10 and self.coinscounter.score_value >= 19:
            self.tank.laser_shoot_cooldown = 1
        
        if self.coinscounter.score_value >= 20:
            self.tank.laser_shoot_cooldown = 0.3
         
        

        if self.coinscounter.score_value >= 2 and 101 in self.keys_pressed and self.shield.shield_power > 0:  #if you have more than 2 coins and E is pressed you get a shield 
            self.shield.alpha = 0.6   #the shield is always on the spaceship but it becomes visible only if the condition is satisfied
            if self.shield.shield_power == 2:
                self.shield.circle.source = "damaged2.png"    # when the shield is invisible the collision is not detected 
            if self.shield.shield_power == 1:
                self.shield.circle.source = "damaged1.png"
                
        else:
            self.shield.alpha = 0
                
        self.shield.move_with(self.tank) #makes the shield always stay on the spaceship 
        
        
        
        self.enemy.shoot(self)
        
    
        #sort of gravity
        if self.tank.y > 150:
            self.tank.y -= 2.5
        else:
            self.tank.y = 150
        
        

        
        for bullet in self.bullets:
            if not isinstance(bullet, Laser):
                bullet.speed = self.power.size[0]/30
            else: 
                bullet.speed = 20

            

            if self.shield.collide_with_bullet(bullet):
                self.shield.shield_power -= 1
                bullets_to_remove.add(bullet)
                bullet.pos = (0,500000)  #we must send the bullet away because it is removed graphically but apprently the hit box stays 
                

                

                
            
            if self.rock.collide_with_bullet(bullet):
                if isinstance(bullet, Bombshell):
                    bullet.mass = 0
                    bullet.speed = 0
                    bullet.pos = bullet.pos 
                    Clock.schedule_once(bullet.explode, 2)  
                    def code_to_execute(dt):
                        self.rock.move(0, Window.width - self.rock.size[0], self.tank.pos[0], self.enter_wormhole.pos[0], self.rock.size[0] )

                    if not bullet.has_collided:
                        Clock.schedule_once(code_to_execute, 2)
                        Clock.schedule_once(partial(self.remove_with_delay, bullet), 3)
                        bullet.has_collided = True
                else:
                    bullets_to_remove.add(bullet)
                    self.rock.move(0, Window.width - self.rock.size[0], self.tank.pos[0], self.enter_wormhole.pos[0], self.rock.size[0] )
                    


            if self.enemy.collide_with_bullet(bullet):
                if isinstance(bullet, Bombshell):
                    bullet.mass = 0
                    bullet.speed = 0
                    bullet.pos = bullet.pos 
                    Clock.schedule_once(bullet.explode, 2)  
                    def code_to_execute(dt):
                        self.counter.descore(3)
                        

                    if not bullet.has_collided:
                        Clock.schedule_once(code_to_execute, 2)
                        Clock.schedule_once(partial(self.remove_with_delay, bullet), 3)
                        bullet.has_collided = True
                else:
                    bullets_to_remove.add(bullet)
                    if isinstance(bullet, Laser):
                        self.counter.descore(2)
                    else:
                        self.counter.descore()

                    self.remove_widget(bullet)
                    bullet.pos = (0,500000)

                

            if bullet.pos[1] <= 150:
                if isinstance(bullet, Bombshell):
                    bullet.mass = 0
                    bullet.speed = 0
                    bullet.pos = bullet.pos
                    Clock.schedule_once(bullet.explode, 2)
                    Clock.schedule_once(bullet.clear_from_ground,2.1)
                    Clock.schedule_once(partial(self.remove_with_delay, bullet), 3 )
                    #self.remove_widget(bullet)

                else:
                    bullets_to_remove.add(bullet)
                    

            if self.mirror.collide_with_bullet(bullet): #if bullet is laser change angle if bullet destroy
                if isinstance(bullet, Laser):
                    bullet.angle = bullet.angle +180 - 2* bullet.angle
                elif isinstance(bullet, Bombshell):
                    bullet.mass = 0
                    bullet.speed = 0
                    bullet.pos = bullet.pos #later we can just call the explode function and write this shit there
                    def code_to_execute(dt):
                        self.counter.score()
                        self.mirror.move()
                    
                    Clock.schedule_once(bullet.explode, 2) 
                    if not bullet.has_collided:
                        Clock.schedule_once(code_to_execute, 2)
                        Clock.schedule_once(partial(self.remove_with_delay, bullet), 3)
                        bullet.has_collided = True 
                elif isinstance(bullet, Bullet):
                    self.remove_widget(bullet)

                #elif isinstance(bullet, Bullet):
                    #bullets_to_remove.add(bullet)
                    #self.mirror.move()
                    
            if self.perpetuo.collide_with_bullet(bullet):
                if isinstance(bullet, Bombshell):
                    bullet.mass = 0
                    bullet.speed = 0
                    bullet.pos = bullet.pos 
                    Clock.schedule_once(bullet.explode, 2) 
                else:
                    self.remove_widget(bullet)

            if self.enter_wormhole.collide_with_bullet(bullet):
                bullet.pos = self.exit_wormhole.center
            
            if isinstance(bullet, Bullet):
                if self.gravitonio.collide_with_bullet(bullet):

                    bullet.gravitational_attraction(self.gravitonio)
            
            if self.coin.collide_with_bullet(bullet):
                self.coin.move(self.enemy)
                self.coinscounter.score()


        if self.enter_wormhole.collide_with_bullet(self.tank): 
            if enter_collide_dir == 'left':
                self.tank.pos = (self.exit_wormhole.center_x + 200, self.exit_wormhole.center_y )
            else:
                self.tank.pos = (self.exit_wormhole.center_x - 250, self.exit_wormhole.center_y )


        
        if self.exit_wormhole.collide_with_bullet(self.tank): 
            if exit_collide_dir == 'right':
                self.tank.pos = (self.enter_wormhole.center_x - 200, self.enter_wormhole.y )
            else:
                self.tank.pos = (self.enter_wormhole.center_x + 200, self.enter_wormhole.y )
        
       
        
        #enemy's bullets are different from ours, the enemy's one do not detroy neither the rock nor the mirror, the laser is still reflected. 
        #Also the relation between the size of thhe power bar and the velocity of the bullet is preserved.
        for bullet in self.enemy_bullets:
            bullet.speed = self.power.size[0]/30
            bullet.trajectory()
            
            if self.perpetuo.collide_with_bullet(bullet): #if enemy bullet collides with perpetuo, bullet gets destroyed
                self.remove_widget(bullet)

            if self.shield.collide_with_bullet(bullet):
                self.shield.shield_power -= 1
                bullets_to_remove.add(bullet)
                bullet.pos = (0,500000)


            if self.tank.collide_with_bullet(bullet):
                self.lifecounter.descore()
                self.remove_widget(bullet)
                bullet.pos = (0,500000)
            
            


            if self.mirror.collide_with_bullet(bullet): #if bullet is laser change angle if bullet destroy
                if isinstance(bullet, Laser):
                    bullet.angle = bullet.angle +180 - 2* bullet.angle
                    
            
            if self.enter_wormhole.collide_with_bullet(bullet):
                bullet.pos = self.exit_wormhole.center
            
            if isinstance(bullet, Bullet):
                if self.gravitonio.collide_with_bullet(bullet):

                    bullet.gravitational_attraction(self.gravitonio)

            if self.enter_wormhole.collide_with_bullet(self.tank): 
                self.tank.pos = (self.exit_wormhole.center_x - 250, self.exit_wormhole.center_y )
        
            if self.exit_wormhole.collide_with_bullet(self.tank): 
                self.tank.pos = (self.enter_wormhole.center_x - 250, self.enter_wormhole.y )
                    
        
        
       
            
        for bullet in self.bullets:
            bullet.trajectory()

            if self.tank.collide_with_bullet(bullet):
                self.lifecounter.descore()
                self.remove_widget(bullet)
                bullet.pos = (0,500000)



        # Remove collided bullets
        for bullet in bullets_to_remove:
            self.remove_widget(bullet)

        
        
      
        
    def SaveScore(self, username, score):
        import os
        filename = "scores.txt" 
        curr_path = os.path.dirname(os.path.realpath(__file__))
        with open(os.path.join(curr_path, filename), 'a+') as file:
            file.write(username + ";" + str(score) )  

    def LoadTop(self):
        import os
        results = []
        usernames = []
        filename = "scores.txt"
        curr_path = os.path.dirname(os.path.realpath(__file__))
        with open(os.path.join(curr_path, filename), 'r') as file:
            line = file.readlines()
            for i in line: 
                #spezza ogni linea in username e score
                stats = i.split(";")
                results.append(int(stats[1]))
                usernames.append(stats[0])
            
        sorted_res = results.copy()
        sorted_res.sort(reverse=True)
        sorted_res = sorted_res[0:5]
        username_res = []
        for i in range(len(sorted_res)):
            el = sorted_res[i]
            index = results.index(el)

            username_res.append(usernames[index])
        return usernames[0:5], sorted_res

    def on_keyboard_down(self, keyboard, keycode, *args):
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
            self.rect = Rectangle(source="back2.jpg", pos=self.pos, size=self.size)

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
    
    def stop(self, instance):
        CannonApp().stop()

    def GoToLevels(self, instance):
        self.manager.current = 'levels'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.add_widget(MainMenuBackground())

        button_color = (0,0,0,0.8)

        welcome_button = Button(
            text='Welcome',
            size_hint=(0.2, 0.2),
            pos_hint={'center_x': 0.5, 'center_y': 0.8},
            font_size=37,
            background_color=button_color
        )

        welcome_button.bind(on_release=self.show_welcome)
        self.add_widget(welcome_button)

        play_button = Button(
            text='Play',
            size_hint=(0.2, 0.2),
            pos_hint={'center_x': 0.5, 'center_y': 0.6},
            font_size=37,
            background_color=button_color
        )

        play_button.bind(on_release=self.play)
        self.add_widget(play_button)

        levels_button = Button(
            text='Levels',
            size_hint=(0.2, 0.2),
            pos_hint={'center_x': 0.5, 'center_y': 0.4},
            font_size=37,
            background_color=button_color
        )

        levels_button.bind(on_release=self.GoToLevels)
        self.add_widget(levels_button)


        exit_button = Button(
            text='Exit',
            size_hint=(0.2, 0.2),
            pos_hint={'center_x': 0.5, 'center_y': 0.2},
            font_size=37,
            background_color=button_color
        )

        exit_button.bind(on_release=self.stop)
        self.add_widget(exit_button)

class Levels(Screen):
    level_defined = False 
    def play(self, instance,level):
        self.level_defined = True
        CannonGame.level = level 
        screen_manager.current= "get_username"

        
        
        
        

    def GoMainMENU(self, instance):
        self.manager.current = 'main_menu'
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(pos=self.update_rect, size=self.update_rect)
        with self.canvas:
            self.rect = Rectangle(source="levels.jpg", pos=self.pos, size=self.size)

        button_color = (0,0,0,0.8)

        first_level = Button(
            text='1',
            size_hint=(0.3, 0.2),
            pos_hint={'center_x': 0.2, 'center_y': 0.7},
            font_size=37,
            background_color=button_color
        )
        first_level.bind(on_release=lambda instance: self.play(instance, 1))
        self.add_widget(first_level)


        second_level = Button(
                    text='2',
                    size_hint=(0.3, 0.2),
                    pos_hint={'center_x': 0.5, 'center_y': 0.7},
                    font_size=37,
                    background_color=button_color
                )
        second_level.bind(on_release=lambda instance: self.play(instance, 2))
        self.add_widget(second_level)

        back_button = Button(
            text='Back',
            size_hint=(0.3, 0.2),
            pos_hint={'center_x': 0.8, 'center_y': 0.7},
            font_size=37,
            background_color=button_color
        )

        back_button.bind(on_release=self.GoMainMENU)
        self.add_widget(back_button)

    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size


class Armory(Screen):
    
    def play(self, instance):
        self.manager.current = 'cannon_game'

    def ChooseWeapon(self):
        self.manager.current = 'Armory'
   
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(pos=self.update_rect, size=self.update_rect)
        with self.canvas:
            self.rect = Rectangle(source="levels.jpg", pos=self.pos, size=self.size)

        button_color = (0,0,0,0.8)

        bullet_button = Button(
            text='Bullet',
            size_hint=(0.3, 0.2),
            pos_hint={'center_x': 0.2, 'center_y': 0.7},
            font_size=37,
            background_color=button_color
        )

        bullet_button.bind(on_release=self.play)
        self.add_widget(bullet_button)

        laser_button = Button(
            text='Laser',
            size_hint=(0.3, 0.2),
            pos_hint={'center_x': 0.5, 'center_y': 0.7},
            font_size=37,
            background_color=button_color
        )

        laser_button.bind(on_release=self.play)
        self.add_widget(laser_button)





    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size


class Game_over(Screen):
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(pos=self.update_rect, size=self.update_rect)
        with self.canvas:
            self.rect = Rectangle(source= "fine.jpg", pos=self.pos, size=self.size)


        button_color = (0,0,0,0.8)

        PlayAgain = Button(
            text='Play again',
            size_hint=(0.25, 0.2),
            pos={50,  30},
            font_size=37,
            background_color=button_color
        )
        PlayAgain.bind(on_release=self.play)
        self.add_widget(PlayAgain)

    

    def play(self,instance):
        app.cannon_game.reinitialize()
        screen_manager.current = 'cannon_game' # type: ignore
    
    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size
    

class Game_win(Screen):
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(pos=self.update_rect, size=self.update_rect)
        with self.canvas:
            self.rect = Rectangle(source= "winn.jpg", pos=self.pos, size=self.size)


        button_color = (0,0,0,0.8)

        PlayAgain = Button(
            text='Play again',
            size_hint=(0.25, 0.2),
            pos={50,  30},
            font_size=37,
            background_color=button_color
        )
        PlayAgain.bind(on_release=self.play)
        self.add_widget(PlayAgain)

    

    def play(self,instance):
        app.cannon_game.reinitialize()
        screen_manager.current = 'cannon_game' # type: ignore
    
    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size


username = ""
class UsernameLayout(BoxLayout):
    def __init__(self, **kwargs):
        super(UsernameLayout, self).__init__(**kwargs)
        self.orientation = 'horizontal'

        # Create a Label
        self.label = Label(text='Enter username:')
        self.add_widget(self.label)

        # Create a TextInput
        self.input = TextInput()
        self.add_widget(self.input)

        # Create a Button
        self.button = Button(text='press to enter username')
        self.button.bind(on_press=self.GetUsername)
        self.add_widget(self.button)

    def GetUsername(self, instance):
        global username
        username = self.input.text
        screen_manager.current = 'cannon_game'
        app.cannon_game.clear_widgets()
        app.cannon_game.reinitialize()

class WriteUsername(Screen): 
    def __init__(self, **kwargs):
        super(WriteUsername, self).__init__(**kwargs)
        self.add_widget(UsernameLayout()) 



screen_manager = None
class CannonApp(App):
    def build(self):
        self.screen_manager = ScreenManager(transition=RiseInTransition(duration = 0.3))
        global screen_manager
        screen_manager = self.screen_manager

        main_menu = MainMenu(name='main_menu')
        game_screen = Screen(name='cannon_game')
        self.cannon_game = CannonGame()
        levels = Levels(name = 'levels')
        armory = Armory(name = 'armory')
        game_over = Game_over(name='game_over')
        game_win = Game_win(name='game_win')
        get_username = WriteUsername(name="get_username")

        game_screen.add_widget(self.cannon_game)
        self.screen_manager.add_widget(main_menu)
        self.screen_manager.add_widget(levels)
        self.screen_manager.add_widget(game_screen)
        self.screen_manager.add_widget(armory)
        self.screen_manager.add_widget(game_over)
        self.screen_manager.add_widget(game_win)
        self.screen_manager.add_widget(get_username)

        # Schedule the update method of the CannonGame instance added to the game_screen
        Clock.schedule_interval(self.cannon_game.update, 1 / self.cannon_game.fps)

        return self.screen_manager

    


if __name__ == '__main__':
    app = CannonApp()
    app.run()
    
