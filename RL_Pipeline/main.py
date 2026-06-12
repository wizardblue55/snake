import os

try:
    from playerAi import snakeEnv, train
except ModuleNotFoundError:
    from RL_Pipeline.playerAi import snakeEnv, train

# --- Settings ---
RENDER      = False     # set to False for faster headless training
GRID_X      = 8         #This is from the orgianl snake game on the nokia phone
GRID_Y      = 14
OUTPUT_FILE = os.path.join(os.path.dirname(__file__), "notPys", "trainingData.json")

# --- Run ---
def main():
    print("=== Snake AI Training ===")
    print(f"Grid:     {GRID_X}x{GRID_Y}")
    print(f"Render:   {RENDER}")
    print(f"Output:   {OUTPUT_FILE}")
    print("=========================\n")

    train(snakeEnv, render=RENDER, outputFile=OUTPUT_FILE, sizeX=GRID_X, sizeY=GRID_Y)


if __name__ == "__main__":
    main()
