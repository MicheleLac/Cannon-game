import kivy

import GameCannon
import cannon

kivy.require("2.3.0")
from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition, NoTransition
from kivy.core.window import Window
from kivy.graphics import Color,Rectangle



class MainMenu(Widget):
    def exit(self): #function for quiting the game
        CannonGame().stop()
    def changeScreen(self): #function for changing the screen to levels
        cannonGame.screen_manager.transition = NoTransition()
        cannonGame.screen_manager.current = "Levels"




class Levels(Widget):
    def changeScreen(self): #going back to main menu
        cannonGame.screen_manager.current = "Main Menu"
    def startGame(self): #goint to the game screen
        cannonGame.screen_manager.current = "GameScreen"
        #in case of levels we should assign the same funtion to all buttons but then using the if statement change stuff in the levels
        #i.e.: if level = 2 add rock in such pos, if level = 3 add mirror, etc

"""def collide(rect1,rect2): #function for collision
    r1x = rect1[0][0]
    r1y = rect1[0][1]
    r1width = rect1[1][0]
    r1height = rect1[1][1]
    r2x = rect2[0][0]
    r2y = rect2[0][1]
    r2width = rect2[1][0]
    r2height = rect2[1][1]

    if (r1x < r2x + r2width and r1x + r1width > r2x and r1y < r2y + r2height and r1y + r1height ):
        return True
    else:
        return False"""
"""class GameScreen(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._keyboard = Window.request_keyboard(self._on_keyboard_closed, self)
        self._keyboard.bind(on_key_down=self.on_key_down)
        self.player = Cannon()
        self.add_widget(self.player)
        self.enemy = Target()
        self.add_widget(self.enemy)

    def _on_keyboard_closed(self):
        self._keyboard.unbind(on_key_down=self.on_key_down)
        self._keyboard = None

    def on_key_down(self, keyboard, keycode, text, modifiers):
        currentx = self.player.pos[0]
        currenty = self.player.pos[1]
        #currentx, currenty = self.player.pos

        if text == "d": #maybe it will make sense to change the type of movement as in tutorial
            self.player.x +=2
        if text == "a":
            self.player.x -=2
        self.player.update_position()
        #self.player.canvas.ask_update()
        if collide((self.player.pos, self.player.size),(self.enemy.pos,self.enemy.size)) == True:
            print("Collision")
        else:
            print("No Col")

class Cannon(Widget):
    def __init__(self, **kwargs):
        super(Cannon, self).__init__(**kwargs)


        #self.size = (50, 50)
        #self.pos = (100, 200)
        with self.canvas: #for image source = "image.png"
            Color(0, 1, 0, 1)  # Red color
            self.rect = Rectangle(pos=(0,100), size=(50, 50))

    def update_position(self): #works only when you update pos like this in the class of cannon
        self.rect.pos = (self.pos[0],100)

class Target(Widget):
    def __init__(self, **kwargs):
        super(Target, self).__init__(**kwargs)


        #self.size = (50, 50)
        #self.pos = (100, 200)
        with self.canvas:
            Color(1, 0, 0, 1)  # Red color
            self.rect = Rectangle(pos=(400,100), size=(50, 50))"""
class CannonGame(App):
    def build(self):


       self.screen_manager = ScreenManager()
       self.firstpage = MainMenu()
       screen = Screen(name = "Main Menu")
       screen.add_widget(self.firstpage)
       self.screen_manager.add_widget(screen)

       self.secondpage = Levels()
       screen = Screen(name="Levels")
       screen.add_widget(self.secondpage)
       self.screen_manager.add_widget(screen)


       self.thirdpage = GameCannon.GameScreen()
       screen = Screen(name="GameScreen")
       screen.add_widget(self.thirdpage)
       self.screen_manager.add_widget(screen)
       return self.screen_manager



cannonGame = CannonGame()
cannonGame.run()