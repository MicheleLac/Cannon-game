from cgitb import text
from tkinter import Button
from turtle import title, width
from webbrowser import BackgroundBrowser
from kivy.config import Config
import os
from matplotlib import use
from numpy import delete, savez_compressed, source
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
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout



class Tank(Widget):
    cannon_angle = NumericProperty(0) # Property to store the angle of the cannon

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        with self.canvas: # Set up the graphical representation of the tank and its cannon
            Color(1, 1, 1)
            self.rect = Rectangle(pos=self.pos, size=self.size, source = "spaceship.png" )
            self.cannon_length = 115
            self.cannon_width = 10
            Color(0.169, 0.169, 0.169)
            self.cannon = Line(points=(self.center_x, self.center_y, self.center_x + self.cannon_length, self.center_y + self.cannon_width), width=self.cannon_width)
            self.size = self.rect.size

        self.bind(pos=self.update_rect, size=self.update_rect)  # Update rect on position and size change
        self.laser_shoot_cooldown = 2  # Set initial cooldown to 2 seconds
        self.last_shot_time = 0.0  # Track the time of the last shot
        self.num_col =0
        self.has_collided= False

    # Update the rectangle's position and size
    def update_rect(self, *args): 
        self.rect.pos = self.pos
        self.rect.size = self.size
        self.cannon.points = (self.center_x, self.center_y, self.center_x + self.cannon_length, self.center_y)

    # Set the angle of the cannon based on mouse position
    def set_cannon_angle(self, mouse_pos):
        dx = mouse_pos[0] - self.center_x #compute the horizontal distance between the mouse position and the center of the tank.
        dy = mouse_pos[1] - self.center_y #compute the vertical distance between the mouse position and the center of the tank.
        self.cannon_angle = math.atan2(dy, dx)
        
        self.cannon.points = (self.center_x, self.center_y,
                              self.center_x + self.cannon_length * math.cos(self.cannon_angle),
                              self.center_y + self.cannon_length * math.sin(self.cannon_angle)
                              )
        return self.cannon_angle

    # Check collision with a rock
    def collide_with_rock(self, rock):
        return self.collide_widget(rock)
    
    # Check collision with a rock
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

    #shoot bullet after a cooldown period set to 0.3s
    def shoot(self, game):
        self.bullet_shoot_cooldown = 0.3
        current_time = time.time()
        if current_time - self.last_shot_time >= self.bullet_shoot_cooldown:
            bullet = Bullet() 
            bullet.angle = self.cannon_angle
            bullet.pos = [self.center_x + self.cannon_length * math.cos(bullet.angle) - bullet.size[0] / 2,
                          self.center_y + self.cannon_length * math.sin(bullet.angle) - bullet.size[1] / 2]
            game.bullets.add(bullet)  #add bullet to the set of bullets
            game.add_widget(bullet) #add widget to the screen
            self.last_shot_time = current_time  # Update last shot time

    #shoot laser from cannon 
    def shootLaser(self, game):
        current_time = time.time()
        if current_time - self.last_shot_time >= self.laser_shoot_cooldown:
            laser = Laser()
            laser.angle = math.degrees(self.cannon_angle)
            laser.pos = [self.center_x + self.cannon_length * math.cos(self.cannon_angle) - laser.size[0] / 2,
                          self.center_y + self.cannon_length * math.sin(self.cannon_angle) - laser.size[1] / 2]
            game.bullets.add(laser) #add laser to the set of bullets
        
            game.add_widget(laser)
            self.last_shot_time = current_time  # Update last shot time

    #shoot bobshell after a cooldown set to 1s
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
    cannon_angle = NumericProperty(0) #property to store the cannon angle 
    direction = NumericProperty(1)  # 1 for right, -1 for left


    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Set up the graphical representation of the enemy spaceship and its cannon
        with self.canvas:
            Color(1, 1, 1)
            self.rect = Rectangle(pos=self.pos, size=self.size, source = "enemyship.png" )
            self.cannon_length = 70
            self.cannon_width = 10
            Color(0,0,0,0)
            self.cannon = Line(points=(self.center_x, self.center_y, self.center_x + self.cannon_length, self.center_y + self.cannon_width), width=self.cannon_width)
            

        self.bind(pos=self.update_rect, size=self.update_rect) # type: ignore
        self.shoot_cooldown = 2  # Set initial cooldown to 2 seconds
        self.last_shot_time = 0.0  # Track the time of the last shot
        self.last_angle_change_time = 0  # Initialize the time of the last angle change
        self.cooldown_duration = 1  
        self.has_collided= False
        Clock.schedule_interval(self.move, 1 / 60.)  # 60 times per second
        Clock.schedule_interval(self.change_direction, 1)  # Change direction every second

    # Update the rectangle's position, size and cannon points position
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
        elif self.x + self.width >= Window.width:
            self.x = Window.width - self.width
            self.direction = -1

    def change_direction(self, dt):
        # Randomly change direction
        self.direction = random.choice([-1, 1])
    
    #cannon angle is set to point downwards
    def set_cannon_angle(self):
            dx = -2.5
            dy = -172.5
            self.cannon_angle = math.atan2(dy, dx)

            self.cannon.points = (self.center_x, self.center_y,
                                  self.center_x + self.cannon_length * math.cos(self.cannon_angle),
                                  self.center_y + self.cannon_length * math.sin(self.cannon_angle)
                                  )

            return self.cannon_angle
    
    #detect collision between enemy spaceship and bullet
    def collide_with_bullet(self, bullet):
        self.has_collided = True 
        return self.collide_widget(bullet)

    #shoot bullet every time shoot_cooldown has elapsed 
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

    #shoot laser every time shoot_cooldown has elapsed 
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

    #shoot bombshel once every sencond 
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
    mass = NumericProperty(0.5) #property to store the mass of the bullet
    speed = NumericProperty(0) #property to store the speed of the bullet
    time = NumericProperty(0) #property to store the flight time of the bullet
    angle = NumericProperty(0) #property to store the angle of the trajectory 

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size = (10, 10)
        #set the grapichal component
        with self.canvas:
            Color(1,0.6,0.4)
            self.bullet = Ellipse(pos=self.pos)

        self.bind(pos=self.update_bullet_pos) 

    #update the bullet position and size
    def update_bullet_pos(self, *args):
        self.bullet.pos = self.pos
        self.bullet.size = self.size

    #compute the trajectory followed by the bullet during flight time 
    def trajectory(self):
        self.x += self.speed * math.cos(self.angle) #implement the actual motion equation
        self.y += self.speed * math.sin(self.angle)  -  self.mass *( self.time + 1) #adapted equation of motion in the y direction according 
        self.time += 0.5
        return self.angle

    #compute the gravitational distortion on the bullet trajectory operated by the gravitonio
    def gravitational_attraction(self, gravitonio):
        G = 6.67259 *10**(-2)
        M = 2000
        distance = (self.pos[0]-self.pos[0])**2 +((self.pos[1]+ self.size[1]/2) -self.pos[1])**2
        self.x -= (G*M *self.x)/(distance)**3
        self.y -= (G*M *self.y)/(distance)**3
        self.time += 0.5


#custom random number generator, used to generate random positions of objects exluding the area around other objects, so that they don't overlap
def random_except(start, stop, exclude1, exclude2, exclude3):
    value = random.randrange(start, stop)
    if (value > (exclude1 + 180) or value < (exclude1 - 180)) and ( value > (exclude2 + 180) or value < (exclude2 - 180)) and ( value > (exclude3 + 280) or value < (exclude3 - 280)):
            return value
    else:
        return random_except(start, stop, exclude1, exclude2, exclude3)

class Rock(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        #graphical component
        with self.canvas:
            Color(1, 1, 1)
            self.rect = Rectangle(pos=self.pos, size=self.size, source= "rock.png")
            

        self.bind(pos=self.update_rect_pos, size=self.update_rect_size)

    #update rect position and size
    def update_rect_pos(self, *args):
        self.rect.pos = self.pos
    
    def update_rect_size(self, *args):
        self.rect.size = self.size
    
    #detect collision between rock and bullet 
    def collide_with_bullet(self, bullet):
        return self.collide_widget(bullet)

    #move the rock to another position, excluding the area around specified objets already present
    def move(self,start, finish, exclude1, exclude2, exclude3):
        self.pos[0] = random_except(start, finish, exclude1, exclude2, exclude3)

class Coin(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        #graphical component
        with self.canvas:
            Color(255,255,0)
            self.rect = Ellipse(pos=self.pos, size=self.size)
            

        self.bind(pos=self.update_rect_pos, size=self.update_rect_size)

    #update the coin position
    def update_rect_pos(self, *args):
        self.rect.pos = self.pos
    
    #update the coin size
    def update_rect_size(self, *args):
        self.rect.size = self.size
    
    #detect collision with bullet
    def collide_with_bullet(self, bullet):
        return self.collide_widget(bullet)

    #move the coing in a random range 
    def move(self, elem):
        self.pos[0] = random.randrange( 0, int( Window.width-self.size[0]), int(elem.pos[0]))
        self.pos[1] = random.randrange(int(Window.height/2),int( Window.height -self.size[0]*3), int(elem.pos[1]))
        
class Wormhole(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        #graphical component
        with self.canvas:
            Color(1, 1, 1)  # Change color as needed
            self.circle = Ellipse(pos=self.pos, size=self.size, source = "wormho.png")

        self.bind(pos=self.update_circle_pos, size=self.update_circle_size)

    #update wormhole postion
    def update_circle_pos(self, *args):
        self.circle.pos = self.pos

    #update wormhole size
    def update_circle_size(self, *args):
        self.circle.size = self.size

    #detect collision with bullet
    def collide_with_bullet(self, bullet):
        return self.collide_widget(bullet)
    
    #detect the direction of collision between an object and the wormhole
    #used in the game to detect the side where the collision between the spaceship and the wormhole takes place, so as to continue 
    #from the other wormhole in the right direction. 
    #So if the collision is detected from the right of the wormhole, the spaceship will move from the other wormhole to the left
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
    #enemy life counter 

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Drawing the counter rectangle
        with self.canvas:
            Color(0.5, 0.5, 0.5)
            self.counter = Rectangle(pos=self.pos, size=self.size, source = "vita.png")
 
        # Initial enemy score
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

    #increase the life of 1 point
    def score(self):
        self.enemy_value += 1
        self.label.text = str(self.enemy_value)  # Update label text with new score

    #decrease the life of 1 point
    def descore(self,value=1):
        self.enemy_value -= value
        self.label.text = str(self.enemy_value)  # Update label text with new score

class CoinsCounter(Widget):
    #coins number counter

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Drawing the counter rectangle
        with self.canvas:
            Color(0.8, 0.8, 0.8)
            self.counter = Rectangle(pos=self.pos, size=self.size, source = "coin.png")

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
        self.bind(size=self.update_rect_size, pos = self.update_rect_pos) 

    def update_rect_size(self, *args):
        self.counter.size = self.size
        self.layout.size = self.size  # Update layout size with widget size

    def update_rect_pos(self, *args):
        self.counter.pos = self.pos
        self.layout.pos = self.pos

    #increase the counter value of 1 coin
    def score(self):
        self.score_value += 1
        self.label.text = str(self.score_value)  # Update label text with new score

class LifeCounter(Widget):
    #player life counter

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Drawing the counter rectangle
        with self.canvas:
            Color(1, 1, 1)
            self.counter = Rectangle(pos=self.pos, size=self.size, source = "vita.png")

        # Initial player life score
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

class PerpetuoPlatform(Widget):  #perpetio indestructible rock
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas:
            Color(1, 1, 1)
            self.rect = Rectangle(pos=self.pos, size=self.size, source = "perpetuo.png")
            

        self.bind(pos=self.update_rect_pos, size=self.update_rect_size)

    def update_rect_pos(self, *args):
        self.rect.pos = self.pos
    
    def update_rect_size(self, *args):
        self.rect.size = self.size
    
    #detect collision with bullet
    def collide_with_bullet(self, bullet):
        return self.collide_widget(bullet)

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

    #increase the power bar size, used to increase the speed of the bullet and to the range 
    def increase_size(self):
        self.size[0] = self.size[0] + 8

    def decrease_size(self):
        self.size[0] = self.size[0] - 8

class Bombshell(Widget):
    mass = NumericProperty(1) #property to store the mass 
    speed = NumericProperty(0) #property to store the speed 
    time = NumericProperty(0) #property to store the time 
    angle = NumericProperty(0) #property to store the angle of trajectory  
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size = (30, 30) #set size
        self.has_collided = False #check if collision is detected
        self.exploded = False #check if explosion is detected
        with self.canvas:
            Color(1, 1, 1)
            self.bullet = Ellipse(pos=self.pos, source = "Cartoon-Bomb-Clipart.png")

        self.bind(pos=self.update_bombshell_pos) #type: ignore 

    def update_bombshell_pos(self, *args):
        self.bullet.pos = self.pos
        self.bullet.size = self.size

    #compute bombshell trajectory
    def trajectory(self):
        self.x += self.speed * math.cos(self.angle) 
        self.y += self.speed * math.sin(self.angle)  -  self.mass *( self.time + 1)
        self.time += 0.5
    
    #creates an explosion on the place of the bomb 
    def explode(self,delay):
        self.exploded = True
    
        self.mass = 999
        with self.canvas:
            Color(1, 1, 1)  # Example color
            Ellipse(pos=self.pos, size=(60, 60), source = "esplosione.png")
        self.pos = (50000, 50000)
        
    #delete the bomb 
    def clear_from_ground(self,dt):
        self.canvas.clear()
        
class Laser(Widget):
    mass = NumericProperty(0.5) #property to store the laser mass
    speed = NumericProperty(0) #property to store the laser speed
    time = NumericProperty(0) #property to store the laser flight time 
    angle = NumericProperty(0) #property to store the laser trajectory angle
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size = (40, 10)
        
        
        with self.canvas:
            PushMatrix()
            Color(0,0.9,0)
            self.rotation = Rotate(angle=self.angle, origin=self.center) #set origin as pivot point of rotation
            self.laser = Rectangle(pos=self.pos, size=self.size)
            PopMatrix()

        self.bind(pos=self.update_laser_pos)  

        
    #update the laser origin of rotation, angle, size and position 
    def update_laser_pos(self, *args):
        self.rotation.origin = self.center
        self.rotation.angle = self.angle
        self.laser.pos = self.pos
        self.laser.size = self.size

    #compute the laser trajecotry 
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
            self.rotation = Rotate(angle= 0, origin=self.center) #the the rotation angle and origin of rotation
            self.mir = Rectangle(pos=self.pos, size=(10,100))
            PopMatrix()
            self.size = self.mir.size
            

        self.bind(pos=self.update_mir_pos, size=self.update_mir_size)

    #updates mirror position and rotation origin
    def update_mir_pos(self, *args):
        self.mir.pos = self.pos
        self.rotation.origin = self.center

    #update mirror size
    def update_mir_size(self, *args):
        self.mir.size = self.size
    
    #detect collision with bullet
    def collide_with_bullet(self, bullet):
            return self.collide_widget(bullet)
        
    #move the mirror in a random range 
    def move(self):
        self.pos[0] = random.randrange(0,929)
        self.pos[1] = random.randrange(355,600)

class Gravitonio(Widget):
    mass =NumericProperty(2) #property to store the mass of gravitonio
   

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        with self.canvas:
            Color(1, 1, 1) 
            self.circle = Ellipse(pos=self.pos, size=self.size, source = "gravitonio.png")

        # Bind position and size updates to the update method
        self.bind(pos=self.update_ellipses, size=self.update_ellipses)

    def update_ellipses(self, *args):
        self.circle.pos = self.pos
        self.circle.size = self.size

    #detect the collision with the bullet in a radius called "distance"
    def collide_with_bullet(self, bullet):

        # Calculate the distance between the object and the bullet using the Euclidean distance formula
        distance = math.sqrt((self.pos[0]-bullet.pos[0])**2 +((self.pos[1]+ self.size[1]/2) -bullet.pos[1])**2)
        
        # If the calculated distance is less than or equal to 150, a collision is detected
        if distance <= 150:
            return True     #collision detected 
        else:
            return False  #no collision detected 
    

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
    
class CannonGame(Widget):
    tank = ObjectProperty(None)
    rock = ObjectProperty(None)
    wormhole = ObjectProperty(None)
    fps = NumericProperty(60)
    level = 1
    Enemy_counter = NumericProperty(0)
    

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        print("level", self.level)
        


        # Initialize canvas
        with self.canvas:
            Color(1, 1, 1)
            
            self.wallpaper = Rectangle(pos=(0, 0), size=(Window.width, Window.height), source = "sfondo2.jpg")
            

        # Initialize tank
        self.tank = Tank()
        self.tank.size_hint = (None, None)
        self.tank.pos = (0, 150)
        self.tank.size = (150, 150)
        self.add_widget(self.tank)

        # Initialize shield
        self.shield = Shield()
        self.shield.size_hint = (None, None)
        self.shield.pos = (0, 150)
        self.shield.size = (155, 155)
        self.add_widget(self.shield)
        
        # Initialize enemy
        self.enemy = Enemy()
        self.enemy.size_hint = (None, None)
        self.enemy.pos = (Window.width/2 - self.enemy.size[0]*2, Window.height / 1.5)
        self.enemy.size = (165, 160)
        self.enemy.set_cannon_angle()
        self.add_widget(self.enemy)

        # Initialize keys and bullets sets
        self.keys_pressed = set()
        self.bullets = set()
        self.enemy_bullets = set()
        


        # Initialize rock
        self.rock = Rock()
        self.rock.size = (90, 90)
        self.add_widget(self.rock)

        # Initialize perpetuo platform
        self.perpetuo = PerpetuoPlatform()
        

        self.enter_wormhole = Wormhole()
        self.exit_wormhole = Wormhole()


        #set levels 
        if self.level == 1:
            self.rock.pos = (Window.width/2 +250, 390)
            self.perpetuo.size = (200, 90)
            self.perpetuo.pos = (900,400)
            self.add_widget(self.perpetuo)
            
        elif self.level == 2:
            
        # Initialize wormholes
            #self.enter_wormhole = Wormhole()
            self.enter_wormhole.pos = (Window.width / 2, 180)
            self.enter_wormhole.size= (100, 100)
            self.add_widget(self.enter_wormhole)

            #self.exit_wormhole = Wormhole()
            self.exit_wormhole.pos = (Window.width / 2 + 280, Window.height / 2)
            self.exit_wormhole.size =  (100, 100)
            self.add_widget(self.exit_wormhole)

        # Initialize enemy life counter
        self.counter = Enemylife() 
        self.add_widget(self.counter)
        self.counter.pos = (0,Window.height - self.counter.size[1])
        self.counter.size = (80, 80)

         # Initialize coins counter
        self.coinscounter = CoinsCounter()  
        self.coinscounter.pos = (Window.width - self.coinscounter.size[0],Window.height - self.coinscounter.size[1])
        self.coinscounter.size = (80, 80)
        self.add_widget(self.coinscounter)
        
        # Initialize life counter
        self.lifecounter = LifeCounter()  
        self.lifecounter.pos = (Window.width/2 ,Window.height - self.lifecounter.size[1])
        self.lifecounter.size = (80, 80)
        self.add_widget(self.lifecounter)


        # Initialize Mirror
        self.mirror = Mirror()
        self.add_widget(self.mirror)
        self.mirror.pos= (Window.width -self.size[0],500)

        # Initialize gravitonio
        self.gravitonio = Gravitonio()  
        self.gravitonio.pos = (500,500)
        self.gravitonio.size = (90, 90)
        self.add_widget(self.gravitonio)

        # Initialize coin
        self.coin = Coin()  
        self.coin.pos = (260,328)
        self.coin.size = (30, 30)
        self.add_widget(self.coin)
        
       
        # Initialize power bar
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

    def reinitialize(self):
        # Custom reinitialization method
        self.__init__()

    def initializeGame(self): 
        print( "level is", self.level)


    def on_enter(self): 
        # Called when the screen is displayed
        self.clear_widgets()
        self.add_widget(Label(text=f'Cannon Game Level: {self.level}'))
       

    # Remove widget with a delay if it's a Bombshell and hasn't exploded
    def remove_with_delay(self, widget,*largs):
        if isinstance(widget, Bombshell) and not widget.exploded:
            widget.exploded = True
            self.remove_widget(widget)
        else: 
            self.remove_widget(widget)

    
    # Update game state
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
        if self.lifecounter.life_value <= 0: #if pler life is less or equal to zero go to game over page and save ememy life left
            Game_over.EnemyLF= self.counter.enemy_value   #set enemy life left to the current Enemy life counter value 
            screen_manager.current = 'game_over'
        
        #If enemy life counter is smaller or equal to zero go to win screen
        if self.counter.enemy_value <= 0:
            screen_manager.current = 'game_win'
        
        #initialize set of bullets to remove
        bullets_to_remove = set()
        
        #functions to dectect where the collision between the tank and wormhole took place, so to keep going in the same direction from the other wormhole
        enter_collide_dir = self.enter_wormhole.collide_dir(self.tank)
        exit_collide_dir = self.exit_wormhole.collide_dir(self.tank)

        # Laser cooldown based on coins
        # The more coins the use have the more he can use the laser 
        if self.coinscounter.score_value >= 10 and self.coinscounter.score_value >= 19:
            self.tank.laser_shoot_cooldown = 1
        
        if self.coinscounter.score_value >= 20:
            self.tank.laser_shoot_cooldown = 0.3
         
        
        # Shield activation based on coins and key press
        if self.coinscounter.score_value >= 2 and 101 in self.keys_pressed and self.shield.shield_power > 0:  #if you have more than 2 coins and E is pressed you get a shield 
            self.shield.alpha = 0.6   #the shield is always on the spaceship but it becomes visible only if the condition is satisfied
            if self.shield.shield_power == 2:
                self.shield.circle.source = "damaged2.png"    # when the shield is invisible the collision is not detected 
            if self.shield.shield_power == 1:
                self.shield.circle.source = "damaged1.png"
                
        else:
            self.shield.alpha = 0
                
        #makes the shield always stay on the spaceship 
        self.shield.move_with(self.tank) 
        
        
        
        self.enemy.shoot(self)
        
    
        #Gravity effect on spaceship 
        if self.tank.y > 150:
            self.tank.y -= 2.5
        else:
            self.tank.y = 150
        
        

        # Process each bullet in the self.bullets set
        for bullet in self.bullets:

            # Set the bullet's speed based on its type
            if not isinstance(bullet, Laser):
                bullet.speed = self.power.size[0]/30
            else: 
                bullet.speed = 20

            
            # Check if the bullet collides with the shield
            if self.shield.collide_with_bullet(bullet):
                self.shield.shield_power -= 1
                bullets_to_remove.add(bullet)
                bullet.pos = (0,500000)  #we must send the bullet away because it is removed graphically but apprently the hit box stays 
                

                

                
            # Check if the bullet collides with the rock
            if self.rock.collide_with_bullet(bullet):
                if isinstance(bullet, Bombshell):
                    bullet.mass = 0
                    bullet.speed = 0
                    bullet.pos = bullet.pos  #make the bombshell stay on the place of collision
                    Clock.schedule_once(bullet.explode, 2)  # Schedule the explosion
                    def code_to_execute(dt):
                        self.rock.move(0, Window.width - self.rock.size[0], self.tank.pos[0], self.enter_wormhole.pos[0], self.rock.size[0] )

                    if not bullet.has_collided:
                        Clock.schedule_once(code_to_execute, 2)
                        Clock.schedule_once(partial(self.remove_with_delay, bullet), 3)
                        bullet.has_collided = True
                else:
                    bullets_to_remove.add(bullet) # Mark the bullet for removal
                    self.rock.move(0, Window.width - self.rock.size[0], self.tank.pos[0], self.enter_wormhole.pos[0], self.rock.size[0] )
                    

            # Check if the bullet collides with the enemy
            if self.enemy.collide_with_bullet(bullet):
                if isinstance(bullet, Bombshell):
                    bullet.mass = 0
                    bullet.speed = 0
                    bullet.pos = bullet.pos  # Keep the bullet's position
                    Clock.schedule_once(bullet.explode, 2)   # Schedule the explosion
                    def code_to_execute(dt):
                        self.counter.descore(3)  # Decrease the enemy's score
                        
                    #remove collided bullets
                    if not bullet.has_collided:
                        Clock.schedule_once(code_to_execute, 2)
                        Clock.schedule_once(partial(self.remove_with_delay, bullet), 3)
                        bullet.has_collided = True
                else:
                    bullets_to_remove.add(bullet)
                    if isinstance(bullet, Laser):
                        self.counter.descore(2) #descore two points if enemy collides with laset
                    else:
                        self.counter.descore() 

                    self.remove_widget(bullet)
                    bullet.pos = (0,500000) #move the hitbox 

                
            # Check if the bullet is on the ground
            if bullet.pos[1] <= 150:
                if isinstance(bullet, Bombshell):
                    bullet.mass = 0
                    bullet.speed = 0
                    bullet.pos = bullet.pos
                    Clock.schedule_once(bullet.explode, 2)
                    Clock.schedule_once(bullet.clear_from_ground,2.1)
                    Clock.schedule_once(partial(self.remove_with_delay, bullet), 3 )
                    

                else:
                    bullets_to_remove.add(bullet)
                    

            if self.mirror.collide_with_bullet(bullet): #if bullet is laser change angle if bullet destroy
                if isinstance(bullet, Laser):
                    bullet.angle = bullet.angle +180 - 2* bullet.angle #reflect the laser
                elif isinstance(bullet, Bombshell):
                    bullet.mass = 0
                    bullet.speed = 0
                    bullet.pos = bullet.pos 
                    def code_to_execute(dt):
                        self.counter.score() 
                        self.mirror.move() #move mirror in another position
                    
                    Clock.schedule_once(bullet.explode, 2) 
                    if not bullet.has_collided:
                        Clock.schedule_once(code_to_execute, 2)
                        Clock.schedule_once(partial(self.remove_with_delay, bullet), 3)
                        bullet.has_collided = True 
                elif isinstance(bullet, Bullet):
                    self.remove_widget(bullet) #remove the bullet widget

                
            # Check if the bullet collides with the perpetuo platform
            if self.perpetuo.collide_with_bullet(bullet):
                if isinstance(bullet, Bombshell):
                    bullet.mass = 0
                    bullet.speed = 0
                    bullet.pos = bullet.pos 
                    Clock.schedule_once(bullet.explode, 2) 
                else:
                    self.remove_widget(bullet)

            # Check if the bullet collides with the entry wormhole
            if self.enter_wormhole.collide_with_bullet(bullet):
                bullet.pos = self.exit_wormhole.center
            
            # Apply gravitational attraction if bullet collides with gravitonio
            if isinstance(bullet, Bullet):
                if self.gravitonio.collide_with_bullet(bullet):

                    bullet.gravitational_attraction(self.gravitonio)
            
            # Check if the bullet collides with the coin
            if self.coin.collide_with_bullet(bullet):
                self.coin.move(self.enemy)
                self.coinscounter.score()

        # Handle collision with the tank and the wormhole
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
        
       
        
        #enemy's bullets are different from player's, the enemy's one do not detroy neither the rock nor the mirror, the laser is still reflected. 
        #Also the relation between the size of thhe power bar and the velocity of the bullet is preserved.
        for bullet in self.enemy_bullets:
            bullet.speed = self.power.size[0]/30
            bullet.trajectory()
            
            if self.perpetuo.collide_with_bullet(bullet): #if enemy bullet collides with perpetuo, bullet gets destroyed
                self.remove_widget(bullet)

            #Shield is damed of one point when hit by a bullet of any kind 
            if self.shield.collide_with_bullet(bullet):
                self.shield.shield_power -= 1
                bullets_to_remove.add(bullet)
                bullet.pos = (0,500000)

            #if tank collides with bullet loses one point 
            if self.tank.collide_with_bullet(bullet):
                self.lifecounter.descore()
                self.remove_widget(bullet)
                bullet.pos = (0,500000) #hitbox is move away
            
            


            if self.mirror.collide_with_bullet(bullet): #if bullet is laser change angle if bullet destroy
                if isinstance(bullet, Laser):
                    bullet.angle = bullet.angle +180 - 2* bullet.angle
                    
            #if bullet collides with enter wormhole the bullet is moved to the center of the exitwormhole
            if self.enter_wormhole.collide_with_bullet(bullet):
                bullet.pos = self.exit_wormhole.center
            
            #if a bullet collides with gravitonio or is in its radius then the trajectory changes accordingly 
            if isinstance(bullet, Bullet):
                if self.gravitonio.collide_with_bullet(bullet):
                    bullet.gravitational_attraction(self.gravitonio)

            #if tank collides with the enterwormhole it is moved to a position close to the exit wormhole
            if self.enter_wormhole.collide_with_bullet(self.tank): 
                self.tank.pos = (self.exit_wormhole.center_x - 250, self.exit_wormhole.center_y )
        
            #if tank collides with the exit wormhole it is moved to a position close to the enter wormhole
            if self.exit_wormhole.collide_with_bullet(self.tank): 
                self.tank.pos = (self.enter_wormhole.center_x - 250, self.enter_wormhole.y )
                    
        
        
       
        #apply trajectory function on each bullet
        for bullet in self.bullets:
            bullet.trajectory()

            #if tank collides with bulle tthe tank loses one life point and the hit box of the bullet is moved to prevent other collision 
            if self.tank.collide_with_bullet(bullet):
                self.lifecounter.descore()
                self.remove_widget(bullet)
                bullet.pos = (0,500000)


        # Remove collided bullets
        for bullet in bullets_to_remove:
            self.remove_widget(bullet)

    # Keyboard and mouse event handlers
    def on_keyboard_down(self, keyboard, keycode, *args):
        self.keys_pressed.add(keycode)


    def on_keyboard_up(self, keyboard, keycode, *args):
        self.keys_pressed.remove(keycode)

    def on_mouse_move(self, window, pos):
        self.mouse = Vector(pos)

class HallOfFame(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(pos=self.update_rect, size=self.update_rect)
        with self.canvas:
            self.rect = Rectangle(source="cutbill.jpg", pos=self.pos, size=self.size)

        button_color = (0, 0, 0, 0.8)

        #add buttons
        self.back_button = Button(
            text='Back',
            size_hint=(0.3, 0.2),
            pos= (500,30),
            font_size=37,
            background_color=button_color
        )
        self.back_button.bind(on_release=self.GoMainMENU) 
        self.add_widget(self.back_button)

        self.scores_button = Button(
            text='Hall of Fame',
            size_hint=(0.25, 0.2),
            pos=(10, 30),
            font_size=37,
            background_color=button_color
        )
        self.scores_button.bind(on_release=self.get_scores)
        self.add_widget(self.scores_button)

        # Create a BoxLayout for the scores label and add it to the screen
        self.scores_layout = BoxLayout(orientation='vertical')
        self.add_widget(self.scores_layout)

    def GoMainMENU(self, instance):
        app.cannon_game.reinitialize() #reinizialize the game to the intial condition
        self.manager.current = 'main_menu'

    # Method to retrieve and display scores
    def get_scores(self, instance):
        filename = "scores.txt" # Define the filename where scores are stored
        curr_path = os.path.dirname(os.path.realpath(__file__)) # Get the current file's directory
        file_path = os.path.join(curr_path, filename) # Construct the full path to the scores file
        
        # Check if the scores file exists
        if not os.path.exists(file_path):
            scores_text = "No scores available."
        else:
            # Open the scores file and read its contents
            with open(file_path, 'r') as file:
                scores_text = file.read()

        # Clear the previous scores (if any) but keep the back button and other elements
        self.scores_layout.clear_widgets()
        
        # Create a label with the scores text
        score_label = Label(
            text=scores_text,
            color=(1, 1, 1, 1),
            font_size=35
        )
        self.scores_layout.add_widget(score_label) # Add the label to the scores layout

    # Method to start the game
    def play(self, instance):
        app.cannon_game.reinitialize()
        self.manager.current = 'cannon_game'

    # Method to update the position and size of a rectangle
    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

class MainMenuBackground(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Bind the position and size of the widget to the update_rect method
        self.bind(pos=self.update_rect, size=self.update_rect)
        with self.canvas:
            # Draw a rectangle with the background image
            self.rect = Rectangle(source="back2.jpg", pos=self.pos, size=self.size)

    # Method to update the position and size of the rectangle
    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

# MainMenu class inherits from Screen and represents the main menu of the game
class MainMenu(Screen):
    # Method to show a welcome message with instructions
    def show_welcome(self, instance):
        welcome_text = (
            'Welcome, here are some instructions to play this game:\n'
            '- Press "a" and "d" to move left and right,\n'
            '- Press "w" to shoot bullets, spacebar for laser, and "b" for bombshell,\n'
            '- After collecting two or more coins, activate the shield with "e",\n'
            '- Press "p" and "l" to increase or decrease the power,\n'
            '- Use the mouse to move the cannon'
        )  
        # Create and open a popup with the welcome text
        popup = Popup(title="Welcome!", content=Label(text=welcome_text), size_hint=(None, None), size=(750, 300))
        popup.open()

    # Method to start the game
    def play(self, instance):
        self.manager.current = 'cannon_game'  # Switch to the game screen
    
    # Method to stop the application
    def stop(self, instance):
        CannonApp().stop()  # Stop the application

    # Method to go to the levels screen
    def GoToLevels(self, instance):
        self.manager.current = 'levels'  # Switch to the levels screen

    # Constructor method for the MainMenu class
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.add_widget(MainMenuBackground())  # Add the background widget to the screen

        button_color = (0,0,0,0.8) # Define a common button background color

        # Create and configure the welcome button
        welcome_button = Button(
            text="Welcome center",
            size_hint=(0.2, 0.2),
            pos_hint={'center_x': 0.5, 'center_y': 0.8},
            font_size=37,
            background_color=button_color
        )

        welcome_button.bind(on_release=self.show_welcome)  # Bind the button to the show_welcome method
        self.add_widget(welcome_button)  # Add the button to the screen

        # Create and configure the play button
        play_button = Button(
            text='Arcade',
            size_hint=(0.2, 0.2),
            pos_hint={'center_x': 0.5, 'center_y': 0.6},
            font_size=37,
            background_color=button_color
        )

        play_button.bind(on_release=self.play)  # Bind the button to the play method
        self.add_widget(play_button)  # Add the button to the screen

        # Create and configure the levels button
        levels_button = Button(
            text='Levels',
            size_hint=(0.2, 0.2),
            pos_hint={'center_x': 0.5, 'center_y': 0.4},
            font_size=37,
            background_color=button_color
        )

        levels_button.bind(on_release=self.GoToLevels)
        self.add_widget(levels_button)


        # Create and configure the exit button
        exit_button = Button(
            text='Exit',
            size_hint=(0.2, 0.2),
            pos_hint={'center_x': 0.8, 'center_y': 0.2},
            font_size=37,
            background_color=button_color
        )
        exit_button.bind(on_release=self.stop)  # Bind the button to the stop method
        self.add_widget(exit_button)  # Add the button to the screen

        # Create and configure the hall of fame button
        fame_button = Button(
            text='Hall of Fame',
            size_hint=(0.2, 0.2),
            pos_hint={'center_x': 0.5, 'center_y': 0.2},
            font_size=37,
            background_color=button_color
        )
        fame_button.bind(on_release=self.show_score)  # Bind the button to the show_score method
        self.add_widget(fame_button)  # Add the button to the screen

    # Method to show the hall of fame screen
    def show_score(self, instance):
        self.manager.current = 'hall_of_fame'  # Switch to the hall of fame screen

# Levels class inherits from Screen and represents the levels selection screen
class Levels(Screen):
    level_defined = False  # Class attribute to track if a level has been selected

    # Method to start the game at the selected level
    def play(self, instance, level):
        self.level_defined = True  # Set the level_defined attribute to True
        CannonGame.level = level  # Set the selected level in the CannonGame class
        screen_manager.current = "get_username"  # Switch to the username input screen

    # Method to go back to the main menu
    def GoMainMENU(self, instance):
        self.manager.current = 'main_menu'  # Switch to the main menu screen

    # Constructor method for the Levels class
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Bind the position and size of the widget to the update_rect method
        self.bind(pos=self.update_rect, size=self.update_rect)
        with self.canvas:
            # Draw a rectangle with the background image for the levels screen
            self.rect = Rectangle(source="levels.jpg", pos=self.pos, size=self.size)

        button_color = (0, 0, 0, 0.8)  # Define a common button background color

        # Create and configure the button for the first level
        first_level = Button(
            text='1',
            size_hint=(0.3, 0.2),
            pos_hint={'center_x': 0.2, 'center_y': 0.7},
            font_size=37,
            background_color=button_color
        )
        # Bind the button to the play method with level 1
        first_level.bind(on_release=lambda instance: self.play(instance, 1))
        self.add_widget(first_level)  # Add the button to the screen

        # Create and configure the button for the second level
        second_level = Button(
            text='2',
            size_hint=(0.3, 0.2),
            pos_hint={'center_x': 0.5, 'center_y': 0.7},
            font_size=37,
            background_color=button_color
        )
        # Bind the button to the play method with level 2
        second_level.bind(on_release=lambda instance: self.play(instance, 2))
        self.add_widget(second_level)  # Add the button to the screen

        # Create and configure the back button
        back_button = Button(
            text='Back',
            size_hint=(0.3, 0.2),
            pos_hint={'center_x': 0.8, 'center_y': 0.7},
            font_size=37,
            background_color=button_color
        )
        # Bind the button to the GoMainMENU method
        back_button.bind(on_release=self.GoMainMENU)
        self.add_widget(back_button)  # Add the button to the screen

    # Method to update the position and size of the rectangle
    def update_rect(self, *args):
        self.rect.pos = self.pos  # Update rectangle position to match widget's position
        self.rect.size = self.size  # Update rectangle size to match widget's size



# Game_over class inherits from Screen and represents the game over screen
class Game_over(Screen):
    EnemyLF = 0  # Class attribute to store the enemy's life points

    # Constructor method for the Game_over class
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Bind the position and size of the widget to the update_rect method
        self.bind(pos=self.update_rect, size=self.update_rect)
        with self.canvas:
            # Draw a rectangle with the background image for the game over screen
            self.rect = Rectangle(source="fine.jpg", pos=self.pos, size=self.size)

        button_color = (0, 0, 0, 0.8)  # Define a common button background color

        # Create and configure the "Play again" button
        PlayAgain = Button(
            text='Play again',
            size_hint=(0.25, 0.2),
            pos={1300, 30},
            font_size=37,
            background_color=button_color
        )
        # Bind the button to the play method
        PlayAgain.bind(on_release=self.play)
        self.add_widget(PlayAgain)  # Add the button to the screen

        # Create and configure the "Save" button to save the previous game score
        Saveprevious = Button(
            text='Save',
            size_hint=(0.25, 0.2),
            pos={100, 30},
            font_size=37,
            background_color=button_color
        )
        # Bind the button to the save method
        Saveprevious.bind(on_release=self.save)
        self.add_widget(Saveprevious)  # Add the button to the screen

        # Create and configure the "Back" button to go back to the main menu
        back_button = Button(
            text='Back',
            size_hint=(0.25, 0.2),
            pos={700, 30},
            font_size=37,
            background_color=button_color
        )
        # Bind the button to the GoMainMENU method
        back_button.bind(on_release=self.GoMainMENU)
        self.add_widget(back_button)  # Add the button to the screen

    # Method to go back to the main menu and reinitialize the game
    def GoMainMENU(self, instance):
        app.cannon_game.reinitialize()  # Reinitialize the game
        self.manager.current = 'main_menu'  # Switch to the main menu screen

    # Method to save the game score
    def save(self, instance):
        global username
        score = self.EnemyLF  # Get the enemy's life points
        # Save the score as the maximum life points (20) minus the enemy's remaining life
        self.SaveScore(username, (20 - score))
        app.cannon_game.reinitialize()  # Reinitialize the game
        self.manager.current = 'hall_of_fame'  # Switch to the hall of fame screen

    # Method to save the score to a file
    def SaveScore(self, username, score):
        import os
        filename = "scores.txt"  # Define the scores file name
        curr_path = os.path.dirname(os.path.realpath(__file__))  # Get the current path
        with open(os.path.join(curr_path, filename), 'a+') as file:
            # Append the username and score to the file
            file.write(username + ":" + str(score) + "\n")

    # Method to load the top scores from the file
    def LoadTop(self):
        results = []
        usernames = []
        filename = "scores.txt"  # Define the scores file name
        curr_path = os.path.dirname(os.path.realpath(__file__))  # Get the current path
        with open(os.path.join(curr_path, filename), 'r') as file:
            lines = file.readlines()  # Read all lines from the file
            for line in lines:
                # Split each line into username and score
                stats = line.split(";")
                results.append(int(stats[1]))
                usernames.append(stats[0])
        
        sorted_res = results.copy()
        sorted_res.sort(reverse=True)  # Sort the scores in descending order
        sorted_res = sorted_res[:5]  # Get the top 5 scores
        username_res = []
        for el in sorted_res:
            index = results.index(el)
            username_res.append(usernames[index])
        return username_res[:5], sorted_res  # Return the top 5 usernames and scores

    # Method to get and display the scores
    def get_scores(self):
        filename = "scores.txt"  # Define the scores file name
        layout = BoxLayout(orientation='vertical')
        curr_path = os.path.dirname(os.path.realpath(__file__))  # Get the current path
        file_path = os.path.join(curr_path, filename)

        if not os.path.exists(file_path):
            return "No scores available."  # Return message if no scores file exists

        with open(file_path, 'r') as file:
            scores_text = file.read()  # Read the scores from the file
        score_label = Label(text=scores_text)
        layout.add_widget(score_label)  # Add the scores to the layout
        return layout  # Return the layout with scores

    # Method to start a new game
    def play(self, instance):
        app.cannon_game.reinitialize()  # Reinitialize the game
        screen_manager.current = 'cannon_game'  # Switch to the cannon game screen
    
    # Method to update the position and size of the rectangle
    def update_rect(self, *args):
        self.rect.pos = self.pos  # Update rectangle position to match widget's position
        self.rect.size = self.size  # Update rectangle size to match widget's size

    
# Game_win class inherits from Screen and represents the game win screen
class Game_win(Screen):
    EnemyLF = 0  # Class attribute to store the enemy's life points

    # Constructor method for the Game_win class
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Bind the position and size of the widget to the update_rect method
        self.bind(pos=self.update_rect, size=self.update_rect)
        with self.canvas:
            # Draw a rectangle with the background image for the game win screen
            self.rect = Rectangle(source="winn.jpg", pos=self.pos, size=self.size)

        button_color = (0, 0, 0, 0.8)  # Define a common button background color

        # Create and configure the "Play again" button
        PlayAgain = Button(
            text='Play again',
            size_hint=(0.25, 0.2),
            pos=(50, 300),
            font_size=37,
            background_color=button_color
        )
        # Bind the button to the play method
        PlayAgain.bind(on_release=self.play)
        self.add_widget(PlayAgain)  # Add the button to the screen

        # Create and configure the "Save" button to save the previous game score
        Saveprevious = Button(
            text='Save',
            size_hint=(0.25, 0.2),
            pos=(600, 300),
            font_size=37,
            background_color=button_color
        )
        # Bind the button to the save method
        Saveprevious.bind(on_release=self.save)
        self.add_widget(Saveprevious)  # Add the button to the screen

        # Create and configure the "Back" button to go back to the main menu
        back_button = Button(
            text='Back',
            size_hint=(0.25, 0.2),
            pos=(1200, 300),
            font_size=37,
            background_color=button_color
        )
        # Bind the button to the GoMainMENU method
        back_button.bind(on_release=self.GoMainMENU)
        self.add_widget(back_button)  # Add the button to the screen

    # Method to go back to the main menu and reinitialize the game
    def GoMainMENU(self, instance):
        app.cannon_game.reinitialize()  # Reinitialize the game
        self.manager.current = 'main_menu'  # Switch to the main menu screen

    # Method to save the game score
    def save(self, instance):
        global username
        score = self.EnemyLF  # Get the enemy's life points
        # Save the score as the maximum life points (20) minus the enemy's remaining life
        self.SaveScore(username, (20 - score))
        app.cannon_game.reinitialize()  # Reinitialize the game
        self.manager.current = 'hall_of_fame'  # Switch to the hall of fame screen

    # Method to save the score to a file
    def SaveScore(self, username, score):
        import os
        filename = "scores.txt"  # Define the scores file name
        curr_path = os.path.dirname(os.path.realpath(__file__))  # Get the current path
        with open(os.path.join(curr_path, filename), 'a+') as file:
            # Append the username and score to the file
            file.write(username + ":" + str(score) + "\n")

    # Method to load the top scores from the file
    def LoadTop(self):
        results = []
        usernames = []
        filename = "scores.txt"  # Define the scores file name
        curr_path = os.path.dirname(os.path.realpath(__file__))  # Get the current path
        with open(os.path.join(curr_path, filename), 'r') as file:
            lines = file.readlines()  # Read all lines from the file
            for line in lines:
                # Split each line into username and score
                stats = line.split(";")
                results.append(int(stats[1]))
                usernames.append(stats[0])

        sorted_res = results.copy()
        sorted_res.sort(reverse=True)  # Sort the scores in descending order
        sorted_res = sorted_res[:5]  # Get the top 5 scores
        username_res = []
        for el in sorted_res:
            index = results.index(el)
            username_res.append(usernames[index])
        return username_res[:5], sorted_res  # Return the top 5 usernames and scores

    # Method to get and display the scores
    def get_scores(self):
        filename = "scores.txt"  # Define the scores file name
        layout = BoxLayout(orientation='vertical')
        curr_path = os.path.dirname(os.path.realpath(__file__))  # Get the current path
        file_path = os.path.join(curr_path, filename)

        if not os.path.exists(file_path):
            return "No scores available."  # Return message if no scores file exists

        with open(file_path, 'r') as file:
            scores_text = file.read()  # Read the scores from the file
        score_label = Label(text=scores_text)
        layout.add_widget(score_label)  # Add the scores to the layout
        return layout  # Return the layout with scores

    # Method to start a new game
    def play(self, instance):
        app.cannon_game.reinitialize()  # Reinitialize the game
        screen_manager.current = 'cannon_game'  # Switch to the cannon game screen

    # Method to update the position and size of the rectangle
    def update_rect(self, *args):
        self.rect.pos = self.pos  # Update rectangle position to match widget's position
        self.rect.size = self.size  # Update rectangle size to match widget's size


username = ""
# UsernameLayout class inherits from BoxLayout and is used to create the layout for entering the username
class UsernameLayout(BoxLayout):
    def __init__(self, **kwargs):
        super(UsernameLayout, self).__init__(**kwargs)
        self.orientation = 'horizontal'  # Set the layout orientation to horizontal

        # Create a Label to prompt the user to enter a username
        self.label = Label(text='Enter username:', color=(0.9, 0.9, 1, 0.9), font_size=50, size=(50, 70))
        self.add_widget(self.label)  # Add the label to the layout

        # Create a TextInput for the user to enter the username
        self.input = TextInput()
        self.add_widget(self.input)  # Add the TextInput to the layout

        # Create a Button for submitting the username
        self.button = Button(text='Press to enter username', background_normal="sfondo2.jpg", color=(0.9, 0.9, 1, 0.9), font_size=50)
        self.button.bind(on_press=self.GetUsername)  # Bind the button to the GetUsername method
        self.add_widget(self.button)  # Add the button to the layout

    # Method to handle the button press and save the username
    def GetUsername(self, instance):
        global username
        username = self.input.text  # Get the text from the TextInput
        screen_manager.current = 'cannon_game'  # Switch to the cannon game screen
        app.cannon_game.clear_widgets()  # Clear the current widgets in the cannon game screen
        app.cannon_game.reinitialize()  # Reinitialize the cannon game

# WriteUsername class inherits from Screen and represents the screen for entering the username
class WriteUsername(Screen):
    def __init__(self, **kwargs):
        super(WriteUsername, self).__init__(**kwargs)
        # Bind the position and size of the widget to the update_rect method
        self.bind(pos=self.update_rect, size=self.update_rect)

        with self.canvas:
            # Draw a rectangle with the background image for the username screen
            self.rect = Rectangle(source="sfondo2.jpg", pos=self.pos, size=self.size)

        self.add_widget(UsernameLayout())  # Add the UsernameLayout to the screen

    # Method to update the position and size of the rectangle
    def update_rect(self, *args):
        self.rect.pos = self.pos  # Update rectangle position to match widget's position
        self.rect.size = self.size  # Update rectangle size to match widget's size

screen_manager = None  # Global variable for the screen manager

# CannonApp class inherits from App and represents the main application
class CannonApp(App):
    def build(self):
        # Create a ScreenManager with a transition effect
        self.screen_manager = ScreenManager(transition=RiseInTransition(duration=0.3))
        global screen_manager
        screen_manager = self.screen_manager

        # Create instances of the different screens
        main_menu = MainMenu(name='main_menu')
        game_screen = Screen(name='cannon_game')
        self.cannon_game = CannonGame()
        levels = Levels(name='levels')
        game_over = Game_over(name='game_over')
        game_win = Game_win(name='game_win')
        get_username = WriteUsername(name="get_username")
        halloffame = HallOfFame(name="hall_of_fame")

        # Add the CannonGame widget to the game_screen
        game_screen.add_widget(self.cannon_game)

        # Add all the screens to the screen manager
        self.screen_manager.add_widget(main_menu)
        self.screen_manager.add_widget(levels)
        self.screen_manager.add_widget(game_screen)
        self.screen_manager.add_widget(game_over)
        self.screen_manager.add_widget(game_win)
        self.screen_manager.add_widget(get_username)
        self.screen_manager.add_widget(halloffame)

        # Schedule the update method of the CannonGame instance to be called at the specified FPS
        Clock.schedule_interval(self.cannon_game.update, 1 / self.cannon_game.fps)

        return self.screen_manager  # Return the screen manager as the root widget

# Main entry point for the application
if __name__ == '__main__':
    app = CannonApp()  # Create an instance of the CannonApp
    app.run()  # Run the application

