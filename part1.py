# Group#: B24
# Student Names: Jesse Tam, Eric Yoon

"""
    This program implements a variety of the snake 
    game (https://en.wikipedia.org/wiki/Snake_(video_game_genre))
"""

import threading
import queue        #the thread-safe queue from Python standard library

from tkinter import Tk, Canvas, Button
import random, time

class Gui(): 
    """
        This class takes care of the game's graphic user interface (gui)
        creation and termination.
    """
    def __init__(self) -> None:
        """        
            The initializer instantiates the main window and 
            creates the starting icons for the snake and the prey,
            and displays the initial gamer score.
        """
        #some GUI constants
        scoreTextXLocation = 60
        scoreTextYLocation = 15
        textColour = "white"
        #instantiate and create gui
        self.root = Tk()
        self.canvas = Canvas(self.root, width = WINDOW_WIDTH, 
            height = WINDOW_HEIGHT, bg = BACKGROUND_COLOUR)
        self.canvas.pack()
        #create starting game icons for snake and the prey
        self.snakeIcon = self.canvas.create_line(
            (0, 0), (0, 0), fill=SNAKE_COLOUR, width=SNAKE_ICON_WIDTH)
        self.preyIcon = self.canvas.create_rectangle(
            0, 0, 0, 0, fill=PREY_COLOUR, outline=PREY_COLOUR, width=PREY_ICON_WIDTH)
        #display starting score of 0
        self.score = self.canvas.create_text(
            scoreTextXLocation, scoreTextYLocation, fill=textColour, 
            text='Your Score: 0', font=("Helvetica","11","bold"))
        #binding the arrow keys to be able to control the snake
        for key in ("Left", "Right", "Up", "Down"):
            self.root.bind(f"<Key-{key}>", game.whenAnArrowKeyIsPressed)

    def gameOver(self) -> None:
        """
            This method is used at the end to display a
            game over button.
        """
        gameOverButton = Button(self.canvas, text="Game Over!", 
            height = 3, width = 10, font=("Helvetica","14","bold"), 
            command=self.root.destroy)
        self.canvas.create_window(200, 100, anchor="nw", window=gameOverButton)
    

class QueueHandler():
    """
        This class implements the queue handler for the game.
    """
    def __init__(self):
        self.queue = gameQueue
        self.gui = gui
        self.queueHandler()
    
    def queueHandler(self) -> None:
        '''
            This method handles the queue by constantly retrieving
            tasks from it and accordingly taking the corresponding
            action.
            A task could be: game_over, move, prey, score.
            Each item in the queue is a dictionary whose key is
            the task type (for example, "move") and its value is
            the corresponding task value.
            If the queue.empty exception happens, it schedules 
            to call itself after a short delay.
        '''
        try:
            while True:
                task = self.queue.get_nowait()
                if "game_over" in task:
                    gui.gameOver()
                elif "move" in task:
                    points = [x for point in task["move"] for x in point]
                    gui.canvas.coords(gui.snakeIcon, *points)
                elif "prey" in task:
                    gui.canvas.coords(gui.preyIcon, *task["prey"])
                elif "score" in task:
                    gui.canvas.itemconfigure(
                        gui.score, text=f"Your Score: {task['score']}")
                self.queue.task_done()
        except queue.Empty:
            gui.root.after(100, self.queueHandler)


class Game():
    '''
        This class implements most of the game functionalities.
    '''
    def __init__(self):
        """
           This initializer sets the initial snake coordinate list, movement
           direction, and arranges for the first prey to be created.
        """
        self.queue = gameQueue
        self.score = 0
        #starting length and location of the snake
        #note that it is a list of tuples, each being an
        # (x, y) tuple. Initially its size is 5 tuples.       
        self.snakeCoordinates = [(495, 55), (485, 55), (475, 55),
                                 (465, 55), (455, 55)]
        #initial direction of the snake
        self.direction = "Left"
        self.gameNotOver = True
        self.createNewPrey()

    def superloop(self) -> None:
        """
            This method implements a main loop
            of the game. It constantly generates "move" 
            tasks to cause the constant movement of the snake.
            Use the SPEED constant to set how often the move tasks
            are generated.
        """
        SPEED: float = 0.15   #speed of snake updates (sec)
        while self.gameNotOver:

            self.move() # this handles the logic of it, so the code knows the coordinates of the snake

            self.queue.put({"move": self.snakeCoordinates}) # this puts the "move" action into the queue to be updated by the GUI

            time.sleep(SPEED) # waits for SPEED seconds

    def whenAnArrowKeyIsPressed(self, e) -> None:
        """ 
            This method is bound to the arrow keys
            and is called when one of those is clicked.
            It sets the movement direction based on 
            the key that was pressed by the gamer.
            Use as is.
        """
        currentDirection = self.direction
        #ignore invalid keys
        if (currentDirection == "Left" and e.keysym == "Right" or 
            currentDirection == "Right" and e.keysym == "Left" or
            currentDirection == "Up" and e.keysym == "Down" or
            currentDirection == "Down" and e.keysym == "Up"):
            return
        self.direction = e.keysym

    def move(self) -> None:
        """ 
            This method implements what is needed to be done
            for the movement of the snake.
            It generates a new snake coordinate. 
            If based on this new movement, the prey has been 
            captured, it adds a task to the queue for the updated
            score and also creates a new prey.
            It also calls a corresponding method to check if 
            the game should be over. 
            The snake coordinates list (representing its length 
            and position) should be correctly updated.
        """
        # computing new coordinate and appending
        NewSnakeCoordinates = self.calculateNewCoordinates()
        self.snakeCoordinates.append(NewSnakeCoordinates)
        
        # finding where the prey is
        x1: int
        y1: int
        x2: int
        y2: int

        x1, y1, x2, y2 = self.preyCoords # defining the bottom left and top right of prey square

        preyX: float = (x1+x2) / 2 # finding the middle point (x,y) of the prey
        preyY: float = (y1+y2) / 2

        preyMiddle: tuple = preyX, preyY

        distance: float = ((NewSnakeCoordinates[0] - preyX)**2 + (NewSnakeCoordinates[1] - preyY)**2)**(1/2) # distance from head to prey according to pythagoreas theorem

        # arbituary distance threshold obtained from testing
        distanceThreshold: int = 10

        # if the actual distance from the head of the snake is less than the threshold value, then the snake ate the prey and it increments score by 1
        if distance <= distanceThreshold:
            self.score += 1
            self.queue.put({"score": self.score})
            self.createNewPrey()

        # if it has not eaten a prey, then it removes the tail it added in the beginning
        else: 
            self.snakeCoordinates.pop(0)
        # every iteration checks if the snake ate itself or hit the wall
        self.isGameOver(NewSnakeCoordinates)
       
    def calculateNewCoordinates(self) -> tuple:
        """
            This method calculates and returns the new 
            coordinates to be added to the snake
            coordinates list based on the movement
            direction and the current coordinate of 
            head of the snake.
            It is used by the move() method.    
        """
        lastX, lastY = self.snakeCoordinates[-1]

        newHead: tuple

        if self.direction == "Left": 
            newHead = (lastX - SNAKE_ICON_WIDTH, lastY) # if the user inputs left, the coordinates would be the previous X coordinate - the width of the snake icon as it is moving in neg X
        
        elif self.direction == "Right":
            newHead = (lastX + SNAKE_ICON_WIDTH, lastY) # if the user inputs right, the coordinates would be the previous X coordinate + the width of the snake icon as it is moving in pos X
        
        # the origin for the game board is set to top-left, so up is neg Y and down is pos Y (read documentation file)
        elif self.direction == "Up":
            newHead = (lastX, lastY - SNAKE_ICON_WIDTH) # if the user inputs up, the coordinates would be the previous Y coordinate - the width of the snake icon as it is moving in neg Y
        else:
            newHead = (lastX, lastY + SNAKE_ICON_WIDTH) # if the user inputs down, the coordinates would be the previous Y coordinate + the width of the snake icon as it is moving in pos Y

        return newHead
       


    def isGameOver(self, snakeCoordinates) -> None:
        """
            This method checks if the game is over by 
            checking if now the snake has passed any wall
            or if it has bit itself.
            If that is the case, it updates the gameNotOver 
            field and also adds a "game_over" task to the queue. 
        """
        x: int
        y: int

        x, y = snakeCoordinates
        
        if x < 0 or x > WINDOW_WIDTH or y < 0 or y > WINDOW_HEIGHT: # checks if the snake has passed any walls
            self.gameNotOver = False
            self.queue.put({"game_over": True})
        
        if snakeCoordinates in self.snakeCoordinates[:-1]: # checks if the snake bit itself
            self.gameNotOver = False
            self.queue.put({"game_over": True})


    def createNewPrey(self) -> None:
        """ 
            This methods picks an x and a y randomly as the coordinate 
            of the new prey and uses that to calculate the 
            coordinates (x - 5, y - 5, x + 5, y + 5). [you need to replace 5 with a constant]
            It then adds a "prey" task to the queue with the calculated
            rectangle coordinates as its value. This is used by the 
            queue handler to represent the new prey.                    
            To make playing the game easier, set the x and y to be THRESHOLD
            away from the walls. 
        """
        THRESHOLD: int = 15 #sets how close prey can be to borders
        
        x: int
        y: int

        x = random.randint(THRESHOLD, WINDOW_WIDTH - THRESHOLD) # randomly creates x and y values that are THRESHOLD away from the walls
        y = random.randint(THRESHOLD, WINDOW_HEIGHT - THRESHOLD)

        self.preyCoords = (x - PREY_ICON_WIDTH, y - PREY_ICON_WIDTH, x + PREY_ICON_WIDTH, y + PREY_ICON_WIDTH) # creates the prey coordinates

        self.queue.put({"prey": self.preyCoords}) # adds the prey task to the queue

if __name__ == "__main__":
    #some constants for our GUI
    WINDOW_WIDTH = 500           
    WINDOW_HEIGHT = 300 
    SNAKE_ICON_WIDTH = 15
    PREY_ICON_WIDTH = 4
    #add the specified constant PREY_ICON_WIDTH here     

    BACKGROUND_COLOUR = "black"   #you may change this colour if you wish
    SNAKE_COLOUR = "yellow"        #you may change this colour if you wish
    PREY_COLOUR = "red"
    gameQueue = queue.Queue()     #instantiate a queue object using python's queue class

    game = Game()        #instantiate the game object

    gui = Gui()    #instantiate the game user interface
    
    QueueHandler()  #instantiate the queue handler    
    
    #start a thread with the main loop of the game
    threading.Thread(target = game.superloop, daemon=True).start()

    #start the GUI's own event loop
    gui.root.mainloop()