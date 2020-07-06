import pygame, sys, time, random, keyboard, neat, math, os

# Pygame stuff
SCREEN_RES = (800, 624)
pygame.init()
pygame.mixer.pre_init()
SCREEN = pygame.display.set_mode(SCREEN_RES)
pygame.display.set_caption("A game that doesn't work")
CLOCK = pygame.time.Clock()

# Defining colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
PURPLE = (255, 0, 255)
YELLOW = (255, 255, 0)
GREY = (171, 173, 189)
COLORS = [BLACK, WHITE, BLUE, GREEN, RED, PURPLE, YELLOW, GREEN]

# Globals
GRAVITY = 9.8
HorizantalSpeed = 10
VerticalSpeed = -GRAVITY
generation = 0

class Bird(pygame.sprite.Sprite):
	def __init__(self, x, y):
		pygame.sprite.Sprite.__init__(self)

		self.PrevX = x
		self.PrevY = y

		self.image1 = pygame.image.load('Resources/bird1.png') 
		self.image2 = pygame.image.load('Resources/bird2.png')
		self.image3 = pygame.image.load('Resources/bird3.png')

		# This var changes the image accoriding to the stage of the animation 
		self.image = self.image2 

		self.rect = self.image.get_rect()
		self.rect.center = (x, y)

	def jump(self, pipes):
		self.CurrentX = self.rect.left
		self.CurrentY = self.rect.top

		# Changing the positions and making a backup of the coordinates
		NewX = self.CurrentX
		NewY = self.CurrentY + VerticalSpeed

		# Check for collision
		xCollision = pygame.sprite.spritecollide(self, pipes, False)

		self.rect.left = NewX

		if xCollision:
			# reset the x value
			self.rect.left = self.currentX
		else:
			self.rect.top = NewY
			yCollision = pygame.sprite.spritecollide(self, pipes, False)

			if yCollision:
				# reset value
				self.rect.top = self.currentY
				print('collision')

	def fall(self, pipes):
		self.CurrentX = self.rect.left
		self.CurrentY = self.rect.top

		# Changing the positions and making a backup of the coordinates
		NewX = self.CurrentX
		NewY = self.CurrentY - VerticalSpeed

		# Check for collision
		xCollision = pygame.sprite.spritecollide(self, pipes, False)

		self.rect.left = NewX

		if xCollision:
			# reset the x value
			self.rect.left = self.currentX
		else:
			self.rect.top = NewY
			yCollision = pygame.sprite.spritecollide(self, pipes, False)

			if yCollision:
				# reset value
				self.rect.top = self.currentY

	def animate(self, frame):
		if frame >= 0 and frame <=2:
			self.image = self.image1
		elif frame >= 3 and frame <=4:
			self.image = self.image2
		elif frame >= 5 and frame <=6:
			self.image = self.image3
			if frame == 6:
				frame = 0 

		
		return frame
		
class Base(pygame.sprite.Sprite):
	def __init__(self, x, y):
		pygame.sprite.Sprite.__init__(self)

		self.image = pygame.image.load('Resources/NewBase.jpg')
		self.x = x
		self.y = y

		self.rect = self.image.get_rect()
		self.rect.top = self.y
		self.rect.left = self.x

		self.VEL = 5
		self.WIDTH = self.image.get_width()
		self.y = y
		self.x1 = 0
		self.x2 = self.WIDTH

	def move(self):
		"""
		move floor so it looks like its scrolling
		:return: None
		"""
		self.x1 -= self.VEL
		self.x2 -= self.VEL
		if self.x1 + self.WIDTH < 0:
			self.x1 = self.x2 + self.WIDTH

		if self.x2 + self.WIDTH < 0:
			self.x2 = self.x1 + self.WIDTH

	def draw(self, win):
		"""
		Draw the floor. This is two images that move together.
		:param win: the pygame surface/window
		:return: None
		"""
		win.blit(self.image, (self.x1, self.y))
		win.blit(self.image, (self.x2, self.y))

class Background(pygame.sprite.Sprite):
	def __init__(self, x, y):
		pygame.sprite.Sprite.__init__(self)

		self.image = pygame.image.load('Resources/NewBg.jpg')
		self.x = x
		self.y = y

		self.rect = self.image.get_rect()
		self.rect.top = self.y
		self.rect.left = self.x


class Pipe(pygame.sprite.Sprite):
	
	# The rotation var is used to switch between the upper and lower pipe
	def __init__(self, x, y, height):
		pygame.sprite.Sprite.__init__(self)

		self.x = x
		self.y = y 
		self.VEL = 5

		self.image = pygame.image.load('Resources/pipe.png')
		self.LowerX1 = x
		self.LowerY1 = y

		self.rect = self.image.get_rect()

		self.UpperImage = self.image
		self.UpperImage = pygame.transform.rotate(self.UpperImage, 180)
		self.UpperX1 = x
		self.UpperY1 = self.LowerY1 - height - 320
		self.rect2 = self.UpperImage.get_rect()

	def move(self):
		self.LowerX1 -= self.VEL
		self.UpperX1 -= self.VEL

	def draw(self, win):
		win.blit(self.image, (self.LowerX1, self.LowerY1))
		win.blit(self.UpperImage, (self.UpperX1, self.UpperY1))

def GeneratePipe(x, PipeSprite, AllSprites):
	xCoord = x 
	height = 100
	yCoord = random.randint(204, 420)
	pipe = Pipe(xCoord, yCoord, height)
	PipeSprite.add(pipe)
	#AllSprites.add(pipe)
	return pipe, PipeSprite

def CheckCollision(Bird, CurrentPipe, Base):
	birdX = Bird.rect.center[0]
	birdY = Bird.rect.center[1]

	baseY = 512 

	LowerPipeX = CurrentPipe.LowerX1
	LowerPipeY = CurrentPipe.LowerY1

	UpperPipeX = CurrentPipe.UpperX1
	UpperPipeY = CurrentPipe.UpperY1 + 320

	# Checking the base collision
	PipeCollision, BaseCollision = False, False
	if birdY >= baseY:
		BaseCollision = True
	# Checking if the bird went off screen i.e. higher than pipes
	elif birdY <=0:
		BaseCollision = True

	# Checking the pipe collision
	if birdY >= LowerPipeY:
		# Checkign if they touch the pipe from the beginning to the end
		if birdX >= LowerPipeX and birdX <= LowerPipeX + 52:
			PipeCollision = True
	elif birdY <= UpperPipeY:
		if birdX >= UpperPipeX and birdX <= UpperPipeX + 52:
			PipeCollision = True

	return PipeCollision, BaseCollision

def CheckIfBirdPassedPipe(BirdX, PipeX):
	if PipeX < BirdX - 52:
		return True
	else:
		return False

def CalcDistanceTillPipe(BirdX, BirdY, PipeX, PipeY):
	# Use the distance formula
	LowerPipeX = PipeX
	LowerPipeY = PipeY

	UpperPipeX = PipeX
	UpperPipeY = PipeY - 100
	# For the lower pipe
	DistLower = math.sqrt((LowerPipeX-BirdX)**2+(LowerPipeY-BirdY)**2)

	# For the upper pipe
	DistUpper = math.sqrt((UpperPipeX-BirdX)**2+(UpperPipeY-BirdY)**2)
	drawDistance(SCREEN, BirdY, UpperPipeX, UpperPipeY, LowerPipeX, LowerPipeY)
	return DistLower, DistUpper

def drawDistance(win, birdY, UpperX, UpperY, LowerX, LowerY):
	color = random.choice(COLORS)
	pygame.draw.line(win, color, (250, birdY), (UpperX, UpperY), 3)
	pygame.draw.line(win, color, (250, birdY), (LowerX, LowerY), 3)
	pygame.display.flip()

def main(genomesInput, config):
	global generation
	generation += 1
	AllSprites = pygame.sprite.RenderPlain()
	PlayerSprite = pygame.sprite.RenderPlain()

	ge = []
	nets = []
	players = []
	for id_, gene in genomesInput:
		gene.fitness = 0 
		network = neat.nn.FeedForwardNetwork.create(gene, config)
		nets.append(network)
		player = Bird(250, 312)
		players.append(player)
		ge.append(gene)
		PlayerSprite.add(player)
		AllSprites.add(player)

	BaseSprite = pygame.sprite.RenderPlain()
	base1 = Base(0, 512)
	base1.draw(SCREEN)
	BaseSprite.add(base1)

	BackgroundSprite = pygame.sprite.RenderPlain()
	background1 = Background(0, 0)
	BackgroundSprite.add(background1)

	PipeSprite = pygame.sprite.RenderPlain()

	AllSprites.add(background1)

	running = True
	# Initial pipe
	CurrentPipe, PipeSprite = GeneratePipe(500, PipeSprite, AllSprites)
	Pipes = []
	Pipes.append(CurrentPipe)

	frames = [0]*len(players)
	score = 0
	scoreSTR = 'Score: ' + str(score)

	myfont = pygame.font.SysFont('Consolas', 20)
	textsurface = myfont.render(scoreSTR, False, (0, 0, 0))
	SCREEN.blit(textsurface, (650, 0))

	while running:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				running = False
				sys.exit()
				pygame.quit()
				quit()
				break

		for position, player in enumerate(players):
			ge[position].fitness += 0.2

			LowerDist, UpperDist = CalcDistanceTillPipe(250, player.rect.center[1], CurrentPipe.LowerX1, CurrentPipe.LowerY1)
			output = nets[position].activate((player.rect.center[1], LowerDist, UpperDist))

			if output[0] > 0.5:
				players[position].jump(PipeSprite)
			else:
				players[position].fall(PipeSprite)

		for position, player in enumerate(players):
			PipeCollision, BaseCollision = CheckCollision(player, CurrentPipe, BaseSprite)
			if PipeCollision:
				ge[position].fitness -= 1
				PlayerSprite.remove(players[position])
				players.pop(position)
				ge.pop(position)
				nets.pop(position)
				frames.pop(position)
			elif BaseCollision:
				PlayerSprite.remove(players[position])
				players.pop(position)
				ge.pop(position)
				nets.pop(position)
				frames.pop(position)
			else:
				for gene in ge:
					gene.fitness += 0.2


			passed = CheckIfBirdPassedPipe(player.PrevX, CurrentPipe.LowerX1)
			if passed:
				CurrentPipe, PipeSprite = GeneratePipe(350, PipeSprite, AllSprites)
				Pipes.append(CurrentPipe)
				score  += 10
		if len(players) == 0:
			break
		# Animation
		for i in range(len(frames)):
			frames[i] += 1
			frames[i] = players[i].animate(frames[i])

		# Drawing & Updating
		SCREEN.fill(BLACK)
		AllSprites.draw(SCREEN)
		for i in Pipes:
			i.move()
			i.draw(SCREEN)
		base1.move()
		base1.draw(SCREEN)
		scoreSTR = 'Score: ' + str(score)
		textsurface = myfont.render(scoreSTR, False, (0, 0, 0))
		SCREEN.blit(textsurface, (650, 0))
		genSTR = 'Generation: ' + str(generation)
		textsurface = myfont.render(genSTR, False, (0, 0, 0))
		SCREEN.blit(textsurface, (0, 0))
		PlayerSprite.draw(SCREEN)
		pygame.display.flip()
		CLOCK.tick(10)

def run(config_file):
    """
    runs the NEAT algorithm to train a neural network to play flappy bird.
    :param config_file: location of config file
    :return: None
    """
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         config_file)

    # Create the population, which is the top-level object for a NEAT run.
    p = neat.population.Population(config)

    # Add a stdout reporter to show progress in the terminal.
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)
    #p.add_reporter(neat.Checkpointer(5))

    # Run for up to 25 generations.
    winner = p.run(main, 300)

    # show final stats
    print('\nBest genome:\n{!s}'.format(winner))


if __name__ == '__main__':
	CurrentDir = os.path.dirname(__file__)
	ConfigPath = os.path.join(CurrentDir, 'config-feedforward.txt')
	run(ConfigPath)