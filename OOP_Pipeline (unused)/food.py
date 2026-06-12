import loc
import random

class snakeFood:
    def __init__(self, loc):
        self.loc = loc
    def placeFood(self, gridSizeX, gridSizeY):
        newLoc = loc.gridLoc(random.randint(0, gridSizeX - 1), random.randint(0, gridSizeY - 1))
        self.loc = newLoc