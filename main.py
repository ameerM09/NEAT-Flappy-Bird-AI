# Module imports
import pygame
import random
import neat
import time
import sys
import os

# Initializing pygame libraries
pygame.init()
pygame.font.init()

# Constant variables
WIN_WIDTH = 500
WIN_HEIGHT = 750
CAPTION = 'Flappy Bird AI'

BIRD_WIDTH = 59.5
BIRD_HEIGHT = 42

FPS = 45

GENERATION_COUNT = 0

WHITE = (255, 255, 255)
ORANGE = (215, 115, 40)

MAIN_FONT = pygame.font.SysFont('Comicsans', 30)
MENU_FONT = pygame.font.SysFont('Comicsans', 35)
END_SCREEN_FONT = pygame.font.SysFont('Comicsans', 35)

CITYSCAPE_BG = pygame.transform.scale(pygame.image.load(os.path.join('assets', 'bg.png')), (WIN_WIDTH, WIN_HEIGHT))

PLATFORM = pygame.transform.scale2x(pygame.image.load(os.path.join('assets', 'platform.png')))

OBSTACLE = pygame.transform.scale2x(pygame.image.load(os.path.join('assets', 'obstacle.png')))

# List of bird animations
BIRD_ASSETS = [
	pygame.transform.scale(pygame.image.load(os.path.join('assets', 'bird1.png')), (BIRD_WIDTH, BIRD_HEIGHT)),

	pygame.transform.scale(pygame.image.load(os.path.join('assets', 'bird2.png')), (BIRD_WIDTH, BIRD_HEIGHT)),

	pygame.transform.scale(pygame.image.load(os.path.join('assets', 'bird3.png')), (BIRD_WIDTH, BIRD_HEIGHT))
]

WIN = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
pygame.display.set_caption(CAPTION)

# Specific class for the bird
class Bird():
	ASSETS = BIRD_ASSETS
	MAX_TILT = 25
	ROTATION_VELOCITY = 20

# The speed at which bird animation occurs
	ANIMATION_TIME = 5

# Constructor
	def __init__(self, x, y):
		self.x = x 
		self.y = y

		self.tilt = 0
		self.flap_count = 0
		self.velocity = 0
		self.height = self.y 
		self.asset_count = 0
		self.asset = self.ASSETS[0]

# Method to have the bird 'flap' up the screen
	def flap(self):
		self.velocity = -10
		self.flap_count = 0
		self.height = self.y

# Method where the bird's animation style changes based on its type of movement
	def flap_movement(self):
		self.flap_count = self.flap_count + 1

# Displacement equation which moves the bird a certain number of pixels up the screen
# This is dependent on the number of times that the flap animation has appeared on screen
		displacement = (self.velocity * self.flap_count) + (1.5 * self.flap_count ** 2)

		if displacement >= 16:
			displacement = 16

		elif displacement < 0:
			displacement = displacement - 2

		self.y = self.y + displacement

		if displacement < 0 or self.y < self.height + 50:
			if self.tilt < self.MAX_TILT:
				self.tilt = self.MAX_TILT

		else:
			if self.tilt > -90:
				self.tilt = self.tilt - self.ROTATION_VELOCITY

# Renders bird on screen
	def draw_sprite(self, win):
		self.asset_count = self.asset_count + 1

		if self.asset_count <= self.ANIMATION_TIME:
			self.asset = self.ASSETS[0]

		elif self.asset_count <= self.ANIMATION_TIME * 2:
			self.asset = self.ASSETS[1]

		elif self.asset_count <= self.ANIMATION_TIME * 3:
			self.asset = self.ASSETS[2]

		elif self.asset_count <= self.ANIMATION_TIME * 4:
			self.asset = self.ASSETS[1]

		elif self.asset_count == self.ANIMATION_TIME * 4 + 1:
			self.asset = self.ASSETS[0]
			self.asset_count = 0

		if self.tilt <= -80:
			self.asset = self.ASSETS[1]
			self.asset_count = self.ANIMATION_TIME * 2

		flapped_asset = pygame.transform.rotate(self.asset, self.tilt)
		asset_center = flapped_asset.get_rect(center = self.asset.get_rect(topleft = (self.x, self.y)).center)

		win.blit(flapped_asset, (asset_center.topleft))

	def get_bird_mask(self):
		return pygame.mask.from_surface(self.asset)

	def get_width(self):
		return self.asset.get_width()

	def get_height(self):
		return self.asset.get_height()

class Obstacle():
	OBJ_SPACING = 175
	VELOCITY_SPEED = 5.5

	def __init__(self, x):
		self.x = x 

		self.height = 0
		self.spacing = 100

		self.top_obj = 0 
		self.bottom_obj = 0 

# Flip the top obstacle through the use of the initial asset
		self.TOP_OBSTACLE_ASSET = pygame.transform.rotate(OBSTACLE, 180)
		self.BOTTOM_OBSTACLE_ASSET = OBSTACLE

		self.passed = False 
		self.get_ycor()

# Sets the y-coordinate of the obstacle at a random value between a given range
	def get_ycor(self):
		self.height = random.randint(100, 350)

		self.top_obj = self.height - self.TOP_OBSTACLE_ASSET.get_height()
		self.bottom_obj = self.height + self.OBJ_SPACING

# Moves the obstacles towards the left of the screen to give the feel that the bird's x-position is moving when it truly is not
	def move_obstacle(self):
		self.x = self.x - self.VELOCITY_SPEED

# Creates a mask to handle collissions
	def obj_collision(self, bird):
		bird_mask = bird.get_bird_mask()

		top_obstacle_mask = pygame.mask.from_surface(self.TOP_OBSTACLE_ASSET)
		bottom_obstacle_mask = pygame.mask.from_surface(self.BOTTOM_OBSTACLE_ASSET)

		top_obstacle_offset = (self.x - bird.x, self.top_obj - round(bird.y))
		bottom_obstacle_offset = (self.x - bird.x, self.bottom_obj - round(bird.y))

		top_obstacle_overlap = bird_mask.overlap(top_obstacle_mask, top_obstacle_offset)
		bottom_obstacle_overlap = bird_mask.overlap(bottom_obstacle_mask, bottom_obstacle_offset)

		if top_obstacle_overlap or bottom_obstacle_overlap:
			return True

		return False

	def draw_obj(self, win):
		win.blit(self.TOP_OBSTACLE_ASSET, (self.x, self.top_obj))
		win.blit(self.BOTTOM_OBSTACLE_ASSET, (self.x, self.bottom_obj))

# Class for the platform
class Platform():
	MOVEMENT_VELOCITY = 5.5
	PLATFORM_ASSET = PLATFORM
	PLATFORM_WIDTH = PLATFORM.get_width()

	def __init__(self, y):
		self.y = y 
		self.x1 = 0 
		self.x2 = self.PLATFORM_WIDTH

# Moves the platform for the same feel that the player is actually moving
# Creates two assets of the platform and constantly has them move together
	def drag_movement(self):
		self.x1 = self.x1 - self.MOVEMENT_VELOCITY
		self.x2 = self.x2 - self.MOVEMENT_VELOCITY

		if self.x1 + self.PLATFORM_WIDTH < 0:
			self.x1 = self.x2 + self.PLATFORM_WIDTH

		elif self.x2 + self.PLATFORM_WIDTH < 0:
			self.x2 = self.x1 + self.PLATFORM_WIDTH

	def draw_element(self, win):
		win.blit(self.PLATFORM_ASSET, (self.x1, self.y))
		win.blit(self.PLATFORM_ASSET, (self.x2, self.y))

# Function to draw all elements onto screen
def render_elements(win, bird_score, gen, menu_bar, bird_players, obstacles, platform):
	win.blit(CITYSCAPE_BG, (0, 0))

	for obstacle in obstacles:
		obstacle.draw_obj(win)

	platform.draw_element(win)

	for bird_player in bird_players:
		bird_player.draw_sprite(win)

	pygame.draw.rect(win, ORANGE, menu_bar)

	RENDER_GENS = MAIN_FONT.render('Gen: ' + str(gen), 1, WHITE)
	win.blit(RENDER_GENS, (5, 0))

	RENDER_NUMBER_BIRDS = MAIN_FONT.render('Birds: ' + str(len(bird_players)), 1, WHITE)
	win.blit(RENDER_NUMBER_BIRDS, (WIN_WIDTH // 2 - (RENDER_NUMBER_BIRDS.get_width() // 2), 0))

	RENDER_SCORE = MAIN_FONT.render('Score: ' + str(bird_score), 1, WHITE)
	win.blit(RENDER_SCORE, (WIN_WIDTH - (RENDER_SCORE.get_width() + 5), 0))

# Creating the game loop to run between each generation of the birds
def main_game_loop(genomes, config):
	run = True
	clock = pygame.time.Clock()

	bird_players = []
	obstacles = [Obstacle(500)]
	platform = Platform(635)

	neural_nets = []
	gen = []

	global GENERATION_COUNT
	GENERATION_COUNT = GENERATION_COUNT + 1

	for _, genome in genomes:
		neural_net = neat.nn.FeedForwardNetwork.create(genome, config)
		neural_nets.append(neural_net)
		bird_players.append(Bird(WIN_WIDTH // 2 - (BIRD_ASSETS[0].get_width() // 2), WIN_HEIGHT // 2 - (BIRD_ASSETS[0].get_height() + 15)))

		genome.fitness = 0

		gen.append(genome)

	menu_bar = pygame.Rect(0, 0, WIN_WIDTH, 45)

	bird_score = 0
	bird_high_score = 0

	while run:
		clock.tick(FPS)

		removed_obstacles = []
		append_new_obstacle = False

		obstacle_index = 0 

		if len(bird_players) > 0:
			if len(obstacles) > 1 and bird_players[0].x > obstacles[0].x + obstacles[0].TOP_OBSTACLE_ASSET.get_width():
				obstacle_index = 1

		else:
			run = False
			break

		for i, bird_player in enumerate(bird_players):
			bird_player.flap_movement()
			gen[i].fitness = gen[i].fitness + 0.1

			output = neural_nets[i].activate((bird_player.y, abs(bird_player.y - obstacles[obstacle_index].height), abs(bird_player.y - obstacles[obstacle_index].bottom_obj)))

			if output[0] > 0.5:
				bird_player.flap()

		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				run = False
				sys.exit()

		for obstacle in obstacles:
			for i, bird_player in enumerate(bird_players):

				if obstacle.obj_collision(bird_player):
					gen[i].fitness = gen[i].fitness - 1
					bird_players.pop(i)
					neural_nets.pop(i)
					gen.pop(i)

				if not obstacle.passed and obstacle.x < bird_player.x:
					obstacle.passed = True 
					append_new_obstacle = True

			if obstacle.x + obstacle.TOP_OBSTACLE_ASSET.get_width() < 0:
				removed_obstacles.append(obstacle)

			obstacle.move_obstacle()

		if append_new_obstacle:
			bird_score = bird_score + 1

			for g in gen:
				g.fitness = g.fitness + 5

			obstacles.append(Obstacle(700))

		for removed_obstacle in removed_obstacles:
			obstacles.remove(removed_obstacle)

		for i, bird_player in enumerate(bird_players):
			if bird_player.y + BIRD_ASSETS[0].get_height() >= 730 or bird_player.y < 0:
				bird_players.pop(i)
				neural_nets.pop(i)
				gen.pop(i)

		platform.drag_movement()
		render_elements(WIN, bird_score, GENERATION_COUNT, menu_bar, bird_players, obstacles, platform)

		pygame.display.update()

def run(config_path):
	config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet, neat.DefaultStagnation, config_path)

	pop_size = neat.Population(config)
	pop_size.add_reporter(neat.StdOutReporter(True))

	game_stats = neat.StatisticsReporter()
	pop_size.add_reporter(game_stats)

	completion = pop_size.run(main_game_loop, 50)

if __name__ == '__main__':
	local_directory = os.path.dirname(__file__)
	config_path = os.path.join(local_directory, 'config.txt')	
	run(config_path)