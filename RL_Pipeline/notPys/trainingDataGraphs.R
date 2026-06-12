library(jsonlite)
library(ggplot2)

data <- fromJSON("trainingData.json")
runs <- data$runs

# Rolling average helper
roll_mean <- function(x, n = 50) {
  stats::filter(x, rep(1/n, n), sides = 2)
}

runs$lengthSmooth <- roll_mean(runs$lengthAtDeath, n = 50)
runs$rewardsSmooth <- roll_mean(runs$rewards, n = 50)

# --- Plot 1: Life vs Length at Death ---
ggplot(runs, aes(x = life, y = lengthAtDeath)) +
  geom_point(alpha = 0.08, size = 0.6, color = "steelblue") +
  geom_line(aes(y = lengthSmooth), color = "firebrick", linewidth = 1.1, na.rm = TRUE) +
  geom_smooth(method = "loess", span = 0.3, se = TRUE,
              color = "darkgreen", fill = "darkgreen", alpha = 0.15,
              linewidth = 0.8, na.rm = TRUE) +
  labs(
    title = "Life vs Length at Death",
    subtitle = "Points = individual runs | Red = 50-run rolling avg | Green = LOESS trend",
    x = "Life",
    y = "Length at Death"
  ) +
  theme_minimal()

ggsave("plot_length.png", width = 12, height = 6, dpi = 150)

# --- Plot 2: Life vs Rewards ---
ggplot(runs, aes(x = life, y = rewards)) +
  geom_point(alpha = 0.08, size = 0.6, color = "steelblue") +
  geom_line(aes(y = rewardsSmooth), color = "firebrick", linewidth = 1.1, na.rm = TRUE) +
  geom_smooth(method = "loess", span = 0.3, se = TRUE,
              color = "blue", fill = "blue", alpha = 0.15,
              linewidth = 0.8, na.rm = TRUE) +
  labs(
    title = "Life vs Rewards",
    subtitle = "Points = individual runs | Red = 50-run rolling avg | Blue = LOESS trend",
    x = "Life",
    y = "Rewards"
  ) +
  theme_minimal()

ggsave("plot_rewards.png", width = 12, height = 6, dpi = 150)

library(jsonlite)
library(ggplot2)
library(dplyr)

data <- fromJSON("trainingData.json")
runs <- data$runs

bin_size <- 50

runs <- runs %>%
  mutate(bin = (row_number() - 1) %/% bin_size)

summary_df <- runs %>%
  group_by(bin) %>%
  summarise(
    life_center = mean(life),
    wall_deaths = sum(deathReason == "wall"),
    tail_deaths = sum(deathReason == "tail")
  )

# Reshape to long format for two lines
plot_df <- summary_df %>%
  select(life_center, wall_deaths, tail_deaths) %>%
  tidyr::pivot_longer(
    cols = c(wall_deaths, tail_deaths),
    names_to = "deathType",
    values_to = "count"
  )

ggplot(plot_df, aes(x = life_center, y = count, color = deathType)) +
  geom_line(linewidth = 1) +
  geom_point(size = 0.8) +
  scale_color_manual(
    values = c("wall_deaths" = "firebrick", "tail_deaths" = "steelblue"),
    labels = c("wall_deaths" = "Wall deaths", "tail_deaths" = "Self (tail) deaths")
  ) +
  labs(
    title = paste0("Death Cause Over Training (per ", bin_size, "-life bins)"),
    x = "Life",
    y = paste0("Count out of ", bin_size),
    color = "Death type"
  ) +
  theme_minimal()

ggsave("death_cause_over_training.png", width = 12, height = 6, dpi = 150)