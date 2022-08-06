from . import *

BIRD_WIDTH = 59.5
BIRD_HEIGHT = 42

# List of bird animations
BIRD_ASSETS = [
	pygame.transform.scale(pygame.image.load(os.path.join('assets', 'bird1.png')), (BIRD_WIDTH, BIRD_HEIGHT)),

	pygame.transform.scale(pygame.image.load(os.path.join('assets', 'bird2.png')), (BIRD_WIDTH, BIRD_HEIGHT)),

	pygame.transform.scale(pygame.image.load(os.path.join('assets', 'bird3.png')), (BIRD_WIDTH, BIRD_HEIGHT))
]

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