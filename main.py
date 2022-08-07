from settings import *

# Constant variables
WIN_WIDTH = 500
WIN_HEIGHT = 750
CAPTION = 'Flappy Bird AI'

FPS = 45

GENERATION_COUNT = 0

WHITE = (255, 255, 255)
ORANGE = (215, 115, 40)

MAIN_FONT = pygame.font.SysFont('Comicsans', 30)
MENU_FONT = pygame.font.SysFont('Comicsans', 35)

END_SCREEN_FONT = pygame.font.SysFont('Comicsans', 35)

CITYSCAPE_BG = pygame.transform.scale(pygame.image.load(os.path.join('assets/bg.png')), (WIN_WIDTH, WIN_HEIGHT))

WIN = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
pygame.display.set_caption(CAPTION)

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
