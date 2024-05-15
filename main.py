from ast import Num
from tkinter import Button
from turtle import title, width
from kivy.config import Config
from numpy import delete
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

    def shootLaser(self, game):
        current_time = time.time()
        if current_time - self.last_shot_time >= self.shoot_cooldown:
            laser = Laser()
            laser.angle = math.degrees(self.cannon_angle)
            laser.pos = [self.center_x + self.cannon_length * math.cos(self.cannon_angle) - laser.size[0] / 2,
                          self.center_y + self.cannon_length * math.sin(self.cannon_angle) - laser.size[1] / 2]
            game.bullets.add(laser)
        
            game.add_widget(laser)
            self.last_shot_time = current_time  # Update last shot time

    

class Enemy(Widget):
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
        self.last_angle_change_time = 0  # Initialize the time of the last angle change
        self.cooldown_duration = 3.5  # 5 seconds cooldown


    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size
        self.cannon.points = (self.center_x, self.center_y, self.center_x + self.cannon_length, self.center_y)

    
    

    def set_cannon_angle(self):
        current_time = time.time()
        if current_time - self.last_angle_change_time >= self.cooldown_duration:
            dx = random.randrange(-5000, 1000, 80) - self.center_x
            dy = random.randrange(-5000, 1000, 80) - self.center_y
            self.cannon_angle = math.atan2(dy, dx)

            self.last_angle_change_time = current_time  # Update the time of the last angle change

            self.cannon.points = (self.center_x, self.center_y,
                                  self.center_x + self.cannon_length * math.cos(self.cannon_angle),
                                  self.center_y + self.cannon_length * math.sin(self.cannon_angle)
                                  )

            return self.cannon_angle
    
     
     


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

    def shootLaser(self, game):
        current_time = time.time()
        if current_time - self.last_shot_time >= self.shoot_cooldown:
            laser = Laser()
            laser.angle = math.degrees(self.cannon_angle)
            laser.pos = [self.center_x + self.cannon_length * math.cos(self.cannon_angle) - laser.size[0] / 2,
                          self.center_y + self.cannon_length * math.sin(self.cannon_angle) - laser.size[1] / 2]
            game.bullets.add(laser)
        
            game.add_widget(laser)
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
        return self.angle

    """def increase_power(self, coefficent):
        self.speed += coefficent"""

def random_except(start, stop, exclude1, exclude2, exclude3):
    value = random.randrange(start, stop)
    if (value > (exclude1 + 180) or value < (exclude1 - 180)) and ( value > (exclude2 + 180) or value < (exclude2 - 180)) and ( value > (exclude3 + 180) or value < (exclude3 - 180)):
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
    
    
    def pieces(self):
        
        with self.canvas:
            Color(1, 1, 1)
            self.piece1 = Rectangle(pos=self.pos, size=(20,20), source= "rock.png")
        

        with self.canvas:
            Color(1, 1, 1)
            self.piece2 = Rectangle(pos=(self.pos[0]+20, self.pos[1]), size=(20,20), source= "rock.png")
        

        with self.canvas:
            Color(1, 1, 1)
            self.piece3 = Rectangle(pos=(self.pos[0]-20, self.pos[1]), size=(20,20), source= "rock.png")
        
        
        Clock.schedule_interval(self.remove_pieces, 3)
        # Schedule the removal of smaller rocks after 5 seconds
        
            
    def remove_pieces(self, dt):
        self.piece1.pos = (50000,50000)
        self.piece2.pos = (50000,50000)
        self.piece3.pos = (50000,50000)





            
        
        

    

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
            self.rotation = Rotate(angle=0, origin=self.center)
            self.mir = Rectangle(pos=self.pos, size=(10,100))
            PopMatrix()
            

        self.bind(pos=self.update_mir_pos, size=self.update_mir_size)

    def update_mir_pos(self, *args):
        self.mir.pos = self.pos
        self.rotation.origin = self.center

    
    def update_mir_size(self, *args):
        self.mir.size = self.size
    
    def collide_with_bullet(self, bullet):
            return self.collide_widget(bullet)
        
        
        
        
        
        
        
        


    def move(self):#should we call it "changepos" ?
        self.pos[0] = random.randrange(0,929)
        self.pos[1] = random.randrange(355,600)





class CannonGame(Widget):
    tank = ObjectProperty(None)
    rock = ObjectProperty(None)
    wormhole = ObjectProperty(None)
    fps = NumericProperty(60)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        


        # Initialize canvas
        with self.canvas:
            Color(1, 1, 1)
            self.wallpaper = Rectangle(pos=(0, 0), size=(Window.width, Window.height), source = "gioco2.jpg")
            #Color(1, 1, 1)
            #self.soil = Rectangle(pos=(0, 0), size=(Window.width, Window.height / 3), source = "ground.png")

        # Initialize tank
        self.tank = Tank()
        self.tank.size_hint = (None, None)
        self.tank.pos = (0, 0)
        self.tank.size = (190, 80)
        self.add_widget(self.tank)

        self.enemy = Enemy()
        self.enemy.size_hint = (None, None)
        self.enemy.pos = (Window.width - self.enemy.size[0]*2, Window.height / 3)
        self.enemy.size = (190, 80)
        self.add_widget(self.enemy)


        self.keys_pressed = set()
        self.bullets = set()
        self.lasers = set()
        self.pezzi = set()


        # Initialize rock
        self.rock = Rock()
        self.rock.size = (70, 70)
        self.add_widget(self.rock)
        self.rock.pos = (Window.width - self.rock.size[0], Window.height / 3)


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
        
        # Initialize Mirror
        self.mirror = Mirror()
        self.add_widget(self.mirror)
        self.mirror.pos= (800,500)

       

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
        
        angle = self.tank.set_cannon_angle(self.mouse)
        Laser.angle = math.degrees(angle)
        
        if 275 in self.keys_pressed:
            self.tank.move_right()
        if 276 in self.keys_pressed:
            self.tank.move_left()
        self.tank.set_cannon_angle(self.mouse)
        
        if 115 in self.keys_pressed:
            self.tank.shoot(self)
        if 112 in self.keys_pressed and self.power.size[0]<=522:   #if you press p
            self.power.increase_size()
        if 108 in self.keys_pressed and self.power.size[0] >= 140:   #if you press l
            self.power.decrease_size()
        if 32 in self.keys_pressed:
            
            self.tank.shootLaser(self)

        
        #kind of gravity
        if self.tank.y > 0:
            self.tank.y -= 2.5
        else:
            self.tank.y = 0

        """if self.tank.y > Window.height / 3:
            self.tank.y -= 2.5
        else:
            self.tank.y = Window.height / 3"""
        
        # Check collision between the rock and the bullets
        bullets_to_remove = set()
        
        
        self.enemy.set_cannon_angle()
        
        #Clock.schedule_interval(self.enemy.shoot, 5)


        for bullet in self.bullets:
            bullet.speed = self.power.size[0]/30
            if self.rock.collide_with_bullet(bullet):
                bullets_to_remove.add(bullet)
                self.rock.pieces()
                
                self.rock.move(0, Window.width - self.rock.size[0], self.tank.pos[0], self.enter_wormhole.pos[0], self.rock.size[0] )
                self.counter.score()

            

            if self.mirror.collide_with_bullet(bullet): #if bullet is laser change angle if bullet destroy
                if isinstance(bullet, Laser):
                    bullet.angle = bullet.angle +180 - 2* bullet.angle
                    

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
            self.rect = Rectangle(source="sfond.jpg", pos=self.pos, size=self.size)

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
    
    def play(self, instance):
        self.manager.current = 'cannon_game'

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

        first_level.bind(on_release=self.play)
        self.add_widget(first_level)

        back_button = Button(
            text='Back',
            size_hint=(0.3, 0.2),
            pos_hint={'center_x': 0.5, 'center_y': 0.7},
            font_size=37,
            background_color=button_color
        )

        back_button.bind(on_release=self.GoMainMENU)
        self.add_widget(back_button)

    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size



class CannonApp(App):
    def build(self):
        self.screen_manager = ScreenManager()

        main_menu = MainMenu(name='main_menu')
        game_screen = Screen(name='cannon_game')
        cannon_game = CannonGame()
        levels = Levels(name = 'levels')

        game_screen.add_widget(cannon_game)
        self.screen_manager.add_widget(main_menu)
        self.screen_manager.add_widget(levels)
        self.screen_manager.add_widget(game_screen)

        # Schedule the update method of the CannonGame instance added to the game_screen
        Clock.schedule_interval(cannon_game.update, 1 / cannon_game.fps)

        return self.screen_manager

    


if __name__ == '__main__':
    CannonApp().run()
    
