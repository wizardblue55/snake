from playerAi import snakeEnv, train

# --- Settings ---
RENDER      = False     # set to False for faster headless training
GRID_X      = 10
GRID_Y      = 10
OUTPUT_FILE = "trainingData.json"  # file to save training data to

# --- Run ---
if __name__ == "__main__":
    print("=== Snake AI Training ===")
    print(f"Grid:     {GRID_X}x{GRID_Y}")
    print(f"Render:   {RENDER}")
    print(f"Output:   {OUTPUT_FILE}")
    print("=========================\n")

    train(snakeEnv, render=RENDER, outputFile=OUTPUT_FILE)