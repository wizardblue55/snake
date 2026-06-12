import gymnasium as gym
import numpy as np
import random
import json
import os
import time
import pygame
from stable_baselines3 import PPO


class snakeEnv(gym.Env):
    metadata = {'render_modes': ['human', 'rgb_array'], 'render_fps': 10}

    def __init__(self, sizeX, sizeY, renderMode=None):
        self.sizeX = sizeX
        self.sizeY = sizeY
        self.renderMode = renderMode
        self.cellSize = 40

        self.action_space = gym.spaces.Discrete(4)  # 0: up, 1: right, 2: down, 3: left
        self.observation_space = gym.spaces.Box(
            low=0, high=255, shape=(sizeX, sizeY, 3), dtype=np.uint8
        )

        self.window = None
        self.clock = None

        self.reset()

    def initPygame(self):
        if self.renderMode == 'human' and self.window is None:
            pygame.init()
            pygame.display.init()
            self.headerHeight = 44
            self.cellSize = 48
            self.window = pygame.display.set_mode((
                self.sizeY * self.cellSize,
                self.sizeX * self.cellSize + self.headerHeight
            ))
            pygame.display.set_caption("Snake AI")
            self.font = pygame.font.SysFont("monospace", 16, bold=True)
        if self.clock is None:
            self.clock = pygame.time.Clock()

    def reset(self, seed=None):
        super().reset(seed=seed)
        self.snake = [
            (self.sizeX // 2, self.sizeY // 2),      # head
            (self.sizeX // 2, self.sizeY // 2 - 1),  # body
            (self.sizeX // 2, self.sizeY // 2 - 2),  # tail
        ]
        self.direction = (0, 1)
        self.food = self._place_food()
        self.deathReason = None
        
        if self.renderMode == 'human':
            self.initPygame()

        return self._get_observation(), {}

    def render(self):
        if self.renderMode != 'human':
            return

        self.initPygame()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.close()
                return

        # background
        self.window.fill((12, 12, 20))

        # header bar
        pygame.draw.rect(self.window, (22, 22, 35),
            pygame.Rect(0, 0, self.sizeY * self.cellSize, self.headerHeight))
        pygame.draw.line(self.window, (50, 50, 80),
            (0, self.headerHeight - 1), (self.sizeY * self.cellSize, self.headerHeight - 1))

        length_surf = self.font.render(f"LENGTH  {len(self.snake)}", True, (100, 220, 100))
        steps_surf  = self.font.render(f"FOOD  {len(self.snake) - 3}", True, (220, 100, 100))
        self.window.blit(length_surf, (14, 13))
        self.window.blit(steps_surf, (self.sizeY * self.cellSize - steps_surf.get_width() - 14, 13))

        # grid lines
        for col in range(self.sizeY + 1):
            pygame.draw.line(self.window, (22, 22, 35),
                (col * self.cellSize, self.headerHeight),
                (col * self.cellSize, self.sizeX * self.cellSize + self.headerHeight))
        for row in range(self.sizeX + 1):
            pygame.draw.line(self.window, (22, 22, 35),
                (0, row * self.cellSize + self.headerHeight),
                (self.sizeY * self.cellSize, row * self.cellSize + self.headerHeight))

        # snake body — gradient from head to tail
        for i, segment in enumerate(self.snake):
            x = segment[1] * self.cellSize
            y = segment[0] * self.cellSize + self.headerHeight
            pad = 3

            if i == 0:
                color = (80, 230, 80)
            elif i == len(self.snake) - 1:
                color = (30, 120, 30)
            else:
                ratio = i / max(len(self.snake) - 1, 1)
                g = int(190 - ratio * 80)
                color = (30, g, 40)

            pygame.draw.rect(self.window, color,
                pygame.Rect(x + pad, y + pad, self.cellSize - pad * 2, self.cellSize - pad * 2),
                border_radius=8)

        # eyes on head — face the direction of travel
        head = self.snake[0]
        hx = head[1] * self.cellSize
        hy = head[0] * self.cellSize + self.headerHeight
        d = self.direction

        if d == (0, 1):    # right
            eye1, eye2 = (hx + 36, hy + 13), (hx + 36, hy + 31)
        elif d == (0, -1): # left
            eye1, eye2 = (hx + 12, hy + 13), (hx + 12, hy + 31)
        elif d == (-1, 0): # up
            eye1, eye2 = (hx + 13, hy + 12), (hx + 31, hy + 12)
        else:              # down
            eye1, eye2 = (hx + 13, hy + 36), (hx + 31, hy + 36)

        for eye in (eye1, eye2):
            pygame.draw.circle(self.window, (255, 255, 255), eye, 5)
            pygame.draw.circle(self.window, (0, 0, 0), eye, 2)

        # food — circle with highlight
        fx = self.food[1] * self.cellSize + self.cellSize // 2
        fy = self.food[0] * self.cellSize + self.cellSize // 2 + self.headerHeight
        pygame.draw.circle(self.window, (200, 40, 40), (fx, fy), self.cellSize // 2 - 5)
        pygame.draw.circle(self.window, (255, 130, 130), (fx - 5, fy - 5), 5)

        pygame.display.flip()
        self.clock.tick(self.metadata['render_fps'])

    def step(self, action):
        if action == 0:
            self.direction = (-1, 0)
        elif action == 1:
            self.direction = (0, 1)
        elif action == 2:
            self.direction = (1, 0)
        elif action == 3:
            self.direction = (0, -1)

        # distance to food before moving
        oldDist = abs(self.snake[0][0] - self.food[0]) + abs(self.snake[0][1] - self.food[1])

        newHead = (
            self.snake[0][0] + self.direction[0],
            self.snake[0][1] + self.direction[1]
        )

        reward = 0
        done = False

        if newHead in self.snake:
            done = True
            reward = -10
            self.deathReason = "tail"
        elif not (0 <= newHead[0] < self.sizeX) or not (0 <= newHead[1] < self.sizeY):
            done = True
            reward = -10
            self.deathReason = "wall"
        else:
            self.snake.insert(0, newHead)
            if newHead == self.food:
                reward = 15                     # ate food
                self.food = self._place_food()
            else:
                self.snake.pop()
                new_dist = abs(newHead[0] - self.food[0]) + abs(newHead[1] - self.food[1])
                reward = 1 if new_dist < oldDist else -1   # closer = good, further = bad

        if self.renderMode == 'human':
            self.render()

        return self._get_observation(), reward, done, False, {}

    def _place_food(self):
        while True:
            food = (random.randint(0, self.sizeX - 1), random.randint(0, self.sizeY - 1))
            if food not in self.snake:
                return food

    def _get_observation(self):
        obs = np.zeros((self.sizeX, self.sizeY, 3), dtype=np.uint8)
        for segment in self.snake:
            obs[segment[0], segment[1]] = [0, 255, 0]
        obs[self.food[0], self.food[1]] = [255, 0, 0]
        return obs

    def close(self):
        if self.window is not None:
            pygame.display.quit()
            pygame.quit()
            self.window = None
            self.clock = None


def train(snakeEnviroment, render, outputFile):
    if os.path.exists(outputFile):
        with open(outputFile, 'r') as f:
            data = json.load(f)
    else:
        data = {
            "totalSteps": 0,
            "totalTrainingSeconds": 0,
            "runs": []
        }

    sessionStart = time.time()
    episodeNumber = len(data['runs']) + 1  # pick up episode count where we left off

    renderMode = 'human' if render else None
    evn = snakeEnviroment(10, 10, renderMode=renderMode)

    modelFile = "snake_model.zip"
    if os.path.exists(modelFile):
        model = PPO.load(modelFile, env=evn)
        print("Continuing from saved model...")
    else:
        model = PPO("MlpPolicy", evn, verbose=0, n_steps=200)
        print("Starting fresh model...")

    print(f"\n--- Training ---")
    eps = 0
    while True:
        eps += 1
        # train a little
        model.learn(total_timesteps=200, reset_num_timesteps=False)

        # run one episode to log
        obs, _ = evn.reset()
        done = False
        steps = 0
        totalReward = 0
        while not done:
            action, _ = model.predict(obs)
            obs, reward, done, _, _ = evn.step(int(action))
            steps += 1
            totalReward += reward
        endLength = len(evn.snake)
        data['totalSteps'] += steps

        data['runs'].append({
            "life": episodeNumber,
            "steps": steps,
            "rewards": totalReward,
            "lengthAtDeath": len(evn.snake),
            "deathReason": evn.deathReason,
            "totalTrainingSeconds": round(data['totalTrainingSeconds'] + (time.time() - sessionStart), 2)
        })

        print(f"Ep {episodeNumber:>4} | End length: {endLength} | Steps: {steps}")
        episodeNumber += 1
        with open(outputFile, 'w') as f:
            json.dump(data, f, indent=2)
            
        model.save(modelFile)
        evn.close()

        sessionTime = time.time() - sessionStart
        data['totalTrainingSeconds'] = round(data['totalTrainingSeconds'] + sessionTime, 2)



        print(f"\nDone | Total steps: {data['totalSteps']} | Total time: {data['totalTrainingSeconds']}s")