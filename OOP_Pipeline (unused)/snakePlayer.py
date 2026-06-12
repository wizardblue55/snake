import loc

class snakePlayer:
    def __init__(self, name):
        self.name = name
        self.length = 1
        self.loc = loc.gridLoc(0, 0)
        self.direction = "right"
        
    def getLength(self):
        return self.length
    
    