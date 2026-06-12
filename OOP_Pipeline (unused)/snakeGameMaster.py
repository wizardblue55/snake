import snakePlayer as sp
import snakeGameGrid as sg
import food as sf

class snakeGameMaster:
    def __init__(self, playerName, gridSizeX, gridSizeY):
        self.player = sp.snakePlayer(playerName)
        self.grid = sg.snakeGameGrid(gridSizeX, gridSizeY)
    def movePlayer(self):
        if self.player.direction == "right":
            self.player.loc.x += 1
        elif self.player.direction == "left":
            self.player.loc.x -= 1
        elif self.player.direction == "up":
            self.player.loc.y -= 1
        elif self.player.direction == "down":
            self.player.loc.y += 1
    def changePlayerDirection(self, newDirection):
        self.player.direction = newDirection
    def placeFood(self, foodLoc):
        self.food = sf.snakeFood(foodLoc)
    def checkFoodCollision(self):
        if self.player.loc.x == self.food.loc.x and self.player.loc.y == self.food.loc.y:
            self.player.length += 1
            return True
        return False
    def checkWallCollision(self):
        if self.player.loc.x < 0 or self.player.loc.x >= self.grid.sizeX or self.player.loc.y < 0 or self.player.loc.y >= self.grid.sizeY:
            return True
        return False
    