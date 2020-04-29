library(ggplot2)
library(rstudioapi)
library(tidyverse) # ggplot2, dplyr, tidyr, readr, purrr, tibble
library(magrittr) # pipes
library(lintr) # code linting
library(sf) # spatial data handling
library(viridis) # viridis color scale
library(cowplot) # stack ggplots
library(magick) # gif

# Load data
infected = st_read('~/data_covid.shp')

infected$Population <- as.integer(as.character(infected$Population))


names(infected) <- gsub("X", "", names(infected), fixed = TRUE)
names(infected) <- gsub(".", "-", names(infected), fixed = TRUE)

# Get list of days
days <- names(infected)[2:34]

# create 3 buckets for population
quantiles_pop <- infected %>%
  pull(Population) %>%
  quantile(probs = seq(0, 1, length.out = 5))

# create 3 buckets for infected people
quantiles_inf <- infected %>%
  pull(days[length(days)]) %>%
  quantile(probs = seq(0, 1, length.out = 5))

for (day in days){
  # create color scale that encodes two variables
  # red for population and blue for infected people
  bivariate_color_scale <- tibble(
    "4 - 4" = "#4f3655", # high infected, high population
    "3 - 4" = "#545574",
    "2 - 4" = "#587191",
    "1 - 4" = "#5c8cae", # high infected, low population
    "4 - 3" = "#71405b", 
    "3 - 3" = "#78637d",
    "2 - 3" = "#7e849c",
    "1 - 3" = "#84a4bb", 
    "4 - 2" = "#934961",
    "3 - 2" = "#9c7185",
    "2 - 2" = "#a397a6", 
    "1 - 2" = "#abbbc6",
    "4 - 1" = "#b55267", # low infected, high population
    "3 - 1" = "#c07f8d", 
    "2 - 1" = "#c9aab1",
    "1 - 1" = "#d3d3d3" # low infected, low population
  ) %>%
    gather("group", "fill")

  # cut into groups defined above and join fill
  inf <- infected
  inf %<>%
    mutate(
      pop_quantiles = cut(
        Population,
        breaks = unique(quantiles_pop),
        include.lowest = TRUE
      ),
      inf_quantiles = cut(
        inf[[day]],
        breaks = unique(quantiles_inf),
        include.lowest = TRUE
      ),
      group = paste(
        as.numeric(pop_quantiles), "-",
        as.numeric(inf_quantiles)
      )
    ) %>%
    # join the actual hex values per "group"
    left_join(bivariate_color_scale, by = "group")
  
  
  # separate the groups
  bivariate_color_scale %<>%
    separate(group, into = c("population", "infected"), sep = " - ") %>%
    mutate(population = as.integer(population),
           infected = as.integer(infected))
  
  
  #options(repr.plot.width = 10, repr.plot.height = 15)
  map <- ggplot(data = inf) +
    scale_alpha(name = "",
                range = c(0.6, 0),
                guide = F) + # suppress legend
    # color municipalities according to their poppulation / infected people combination
    geom_sf(
      aes(fill = fill),
      # use thin gray stroke for municipalities
      color = "gray",
      size = 0.1) +
    scale_fill_identity() +
    labs(x = NULL,
         y = NULL,
         title = "Relationship between the nr of infected and the population of each county",
         subtitle = as.name(day)) +
    theme_map()+
    theme(plot.title = element_text(hjust = 0.5),
          plot.subtitle = element_text(hjust = 0.5))
  
  
  legend <- ggplot() +
    geom_tile(
      data = bivariate_color_scale,
      mapping = aes(
        x = population,
        y = infected,
        fill = fill)
    ) +
    scale_fill_identity() +
    labs(x = "Population -->",
         y = "Infected -->")+
    theme_map() +
    theme(
      axis.title = element_text(size = 9)
    ) +
    theme_update(axis.title.y = element_text(angle=90, vjust=-1),
                 panel.border = element_blank(), 
                 panel.grid.major = element_blank(),
                 panel.grid.minor = element_blank(), 
                 axis.line = element_blank(),
                 axis.ticks = element_blank(),
                 axis.text = element_blank(),
                 panel.background = element_blank(),
                 plot.margin=unit(c(1,1,1,1),"mm")
                 )+
    # quadratic tiles
    coord_fixed()
  
  
  ggdraw() +
    draw_plot(map, 0, 0, 1, 1) +
    draw_plot(legend, 0.55, 0.075, 0.5, 0.2)
  
  
  ggsave(paste0('~/', day,'.png'), last_plot(), width = 9, height = 10, units = "in")
  
  dev.off
}

list.files(path='~/', pattern = '*.png', full.names = TRUE) %>% 
  image_read() %>% # reads each path file
  image_join() %>% # joins image
  image_animate(fps=1) %>% # animates, can opt for number of loops
  image_write("~/Infected_Population.gif") # write to current dir


# Foz Côa - 7900/6569
# Porto - 112000/214936


