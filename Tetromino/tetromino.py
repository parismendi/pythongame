#!venv/bin/python
import pygame, sys, time, random
from GameObjects import *
from pygame.locals import *

WINDOWWIDTH = 800
WINDOWHEIGHT = 1024
WINDOWX = 10
WINDOWY = 10

class Tetrominos(Enum):
	LINE = ([[False,False,True,False]]*4,Colors.CYAN)
	SQUARE = ([[False]*4,[False,True,True,False],[False,True,True,False],[False]*4],Colors.YELLOW)
	L_1 = ([[False,False,True,False]]*3 + [[False,True,True,False]],Colors.BLUE)
	L_2 = ([[False,True,False,False]]*3 + [[False,True,True,False]],Colors.ORANGE)
	S_1 = ([[False]*4] + [[False,False,True,True],[False,True,True,False]] + [[False]*4],Colors.GREEN)
	S_2 = ([[False]*4] + [[True,True,False,False],[False,True,True,False]] + [[False]*4],Colors.RED)
	FORK = ([[False]*4] + [[False,False,True,False],[False,True,True,True]] + [[False]*4],Colors.PURPLE)
	ACTIONSQUARE = ([[True]*4]*4,Colors.RED)

def random_tetromino():
	return Tetrominos.LINE
	#return getattr(Tetrominos, random.choice(['LINE','SQUARE','L_1','L_2','S_1','S_2','FORK']))

def displaygameover(surface,score):
	ax = 200
	ay = 80
	display = GameRect(surface,(WINDOWWIDTH/2) - ax/2,(WINDOWHEIGHT/2) - ay/2,ax,ay,forecolor=Colors.WHITE,legend='Score: {0}'.format(score))
	display.draw()

class Grid(GameRect):
	def __init__(self,surface,x,y,square_x,square_y,square_size=10,forecolor=Colors.WHITE,bgcolor=Colors.BLACK,rectwidth=5):
		GameRect.__init__(self,surface,x,y,rectwidth+3+square_x*square_size,rectwidth+3+square_y*square_size,forecolor=forecolor,bgcolor=bgcolor,rectwidth=rectwidth)
		self.__matrix = [[Block(self._surface,self.x+rectwidth-1+i*square_size,self.y-1+rectwidth+j*square_size,length=square_size,color=bgcolor,bgcolor=bgcolor) for i in range(square_x)] for j in range(square_y)]
		self.tetromino = None
	def drawblocks(self):
		for obj in itertools.chain.from_iterable(zip(*self.__matrix)):
			obj.redraw()
	def dropblocks(self):
		if self.tetromino:
			self.erase_tetromino()
			self.move_tetromino(K_DOWN)
			if not self.tetromino.check_collision(self.__matrix):
				self.draw_tetromino()
			else:
				self.move_tetromino(K_UP)
				self.draw_tetromino()
				self.__freeze()
				self.tetromino = None
		else:
			for line, prev_line in zip(self.__matrix[:0:-1],self.__matrix[::-1][1:]):
				for obj, prev_obj in zip(line,prev_line):
					if not obj.empty():
						break
				else:
					for obj, prev_obj in zip(line,prev_line):
						obj.changecolor(prev_obj.getcolor())
						obj.falling = False
	def __freeze(self):
		for obj in itertools.chain.from_iterable(zip(*self.__matrix)):
			obj.falling = False
	def draw_tetromino(self):
		assert self.tetromino, 'There is no Tetromino.'
		self.tetromino > self.__matrix
	def move_tetromino(self,direction):
		assert self.tetromino, 'There is no Tetromino.'
		if direction == K_LEFT:
			self.tetromino.j -= 1
		elif direction == K_DOWN:
			self.tetromino.i += 1
		elif direction == K_UP:
			self.tetromino.i -= 1
		elif direction == K_RIGHT:
			self.tetromino.j += 1
	def erase_tetromino(self):
		assert self.tetromino, 'There is no Tetromino.'
		for i,j in itertools.product([self.tetromino.i+x for x in range(4)],[self.tetromino.j+x for x in range(4)]):
			try:
				if self.__matrix[i][j].falling:
					self.__matrix[i][j].changecolor(self._bgcolor)
			except IndexError:
				pass
	def tetromino_at_the_border(self,border):
		return self.tetromino.at_the_border(self.__matrix,border)
	def rotate_tetromino(self,direction):
		self.tetromino.rotate(direction)
		if self.tetromino_at_the_border(K_RIGHT) or self.tetromino_at_the_border(K_LEFT):
			self.tetromino.rotate(K_UP if direction == K_DOWN else K_DOWN)
	def paintsquare(self,i,j):
		self.__matrix[j][i].changecolor(Colors.CYAN)
	def __flashline(self,line):
		for t in range(2):
			for obj in line:
				obj.changecolor(Colors.WHITE)
			self.drawblocks()
			time.sleep(0.3)
			for obj in line:
				obj.changecolor(self._bgcolor)
			self.drawblocks()
			time.sleep(0.3)
	def check_lines(self):
		for line in self.__matrix:
			for obj in line:
				if obj.empty():
					break
			else:
				self.__flashline(line)
				self.dropblocks()

class Tetromino(object):
	def __init__(self,i,j,figure):
		self.__figure = figure[0]
		self.i = i
		self.j = j
		self.color = figure[1]
	def __gt__(self,otherobj):
		assert not self.check_collision(otherobj), 'There is another block here!'
		for i,j in itertools.product([self.i+x for x in range(4)],[self.j+x for x in range(4)]):
			if self.__figure[i-self.i][j-self.j]:
				otherobj[i][j].changecolor(self.color)
		return otherobj
	def check_collision(self,matrix):
		for i,j in itertools.product([self.i+x for x in range(4)],[self.j+x for x in range(4)]):
			if self.__figure[i-self.i][j-self.j]:
				if i >= len(matrix):
					return True
				try:
					if not matrix[i][j].empty():
						return True
				except IndexError:
					pass
		else:
			return False
	def at_the_border(self,matrix,border):
		border_limit = 0
		if border == K_LEFT:
			border_limit = 0
		elif border == K_RIGHT:
			border_limit = (len(matrix[0]) - 1)
		for i,j in itertools.product([self.i+x for x in range(4)],[self.j+x for x in range(4)]):
			if self.__figure[i-self.i][j-self.j]:
				try:
					if j == border_limit:
						return True
					elif (not matrix[i][j+(1 if border == K_RIGHT else -1)].empty() and not matrix[i][j+(1 if border == K_RIGHT else -1)].falling):
						return True
				except IndexError:
					pass
		else:
			return False
	def rotate(self,direction):
		if direction == K_UP:
			self.__figure = zip(*self.__figure[::-1])
		elif direction == K_DOWN:
			self.__figure = zip(*self.__figure)[::-1]

def main():
	pygame.init()
	DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH,WINDOWHEIGHT))
	BLOCKSIZE = 30
	FPS = 30
	pygame.display.set_caption('Tetromino')
	FPSCLOCK = pygame.time.Clock()
	BLOCKCLOCK = 1
	#pygame.mixer.music.load('music/level1.mp3')
	#pygame.mixer.music.play(-1, 0.0)

	#Generate containers
	main_grid = Grid(DISPLAYSURF,10,10,square_x=17,square_y=33,square_size=BLOCKSIZE,forecolor=Colors.PURPLE)
	next_grid = Grid(DISPLAYSURF,10+17*BLOCKSIZE+50,700,square_x=6,square_y=6,square_size=BLOCKSIZE,forecolor=Colors.SALMON)
	score_grid = Score(DISPLAYSURF,550,50,fontcolor=Colors.WHITE,bgcolor=Colors.BLACK)
	main_grid.draw()
	next_grid.draw()
	score_grid.draw()
	score = 0

	main_grid.tetromino = Tetromino(0,7,random_tetromino())
	main_grid.draw_tetromino()
	main_grid.drawblocks()
	fps = 0
	blockclock = 0
	next_tetromino = random_tetromino()

	next_grid.tetromino = Tetromino(1,1,next_tetromino)
	next_grid.draw_tetromino()
	next_grid.drawblocks()
	while True:
		if fps == FPS/10:
			blockclock += 1
			fps = 0
		for event in pygame.event.get():
			if event.type == QUIT:
				pygame.mixer.music.stop()
				pygame.quit()
				sys.exit()
			elif event.type == KEYDOWN:
				if event.key in [K_LEFT, K_RIGHT]:
					if 	not (event.key == K_LEFT and main_grid.tetromino_at_the_border(K_LEFT) or \
											event.key == K_RIGHT and main_grid.tetromino_at_the_border(K_RIGHT)):
						main_grid.erase_tetromino()
						main_grid.move_tetromino(event.key)
						main_grid.draw_tetromino()
				elif event.key in [K_UP,K_DOWN]:
					main_grid.erase_tetromino()
					main_grid.rotate_tetromino(event.key)
					main_grid.draw_tetromino()
		if blockclock == BLOCKCLOCK:
			main_grid.dropblocks()
			blockclock = 0
		if not main_grid.tetromino:
			main_grid.check_lines()
			main_grid.tetromino = Tetromino(0,7,next_tetromino)
			main_grid.draw_tetromino()
			next_tetromino = random_tetromino()
			next_grid.tetromino = Tetromino(1,1,next_tetromino)
			next_grid.erase_tetromino()
			next_grid.draw_tetromino()
			next_grid.drawblocks()
		main_grid.drawblocks()
		FPSCLOCK.tick(FPS)
		fps += 1

if __name__ == '__main__':
	main()