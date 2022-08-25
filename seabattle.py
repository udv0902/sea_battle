from random import randint, choice


class Ship:
	def __init__(self, bow, lenth, pos):
		self.bow = bow
		self.lenth = lenth
		self.pos = pos
		self.lives = lenth

	@property
	def dots(self):
		dots = []
		for i in range(self.lenth):
			if self.pos == 0:
				dots.append((self.bow[0] + i, self.bow[1]))
			elif self.pos == 1:
				dots.append((self.bow[0], self.bow[1] + i))
		return dots

	@property
	def around(self):
		dots = []
		near = [(i, j) for i in range(-1, 2) for j in range(-1, 2)]
		for i, j in near:
			for dot in self.dots:
				if (dot[0] + i, dot[1] + j) not in dots:
					dots.append((dot[0] + i, dot[1] + j))
		return dots

	@staticmethod
	def rand(lenth, size=6):
		return Ship((randint(0, size - lenth), randint(0, size - lenth)), lenth, randint(0, 1))


class BoardException(Exception):
	pass


class WrongShipException(BoardException):
	pass


class OutBoardException(BoardException):
	def __str__(self):
		return 'Выстрел за пределы поля'


class UsedBoardException(BoardException):
	def __str__(self):
		return 'Вы уже стреляли в это место'


class Board:
	def __init__(self, size=6, lst=None, is_comp=False):
		if lst is None:
			lst = [3, 2, 2, 1, 1, 1, 1]
		self.size = size
		self.field = [['O'] * size for _ in range(size)]
		self.busy = []
		self.ships = []
		self.is_comp = is_comp
		self.lst = lst

	def __str__(self):
		return self.print_field

	@property
	def print_field(self):
		res = '  | 1 |'
		for i in range(1, self.size):
			res += f' {i + 1} |'
		for i, row in enumerate(self.field):
			res += f'\n{i + 1} | {" | ".join(row)} |'
		if self.is_comp:
			return res.replace('■', 'O')
		return res

	@staticmethod
	def print(f_comp, f_user):
		print('\tКомпьютер\t\t\t\t\t     Игрок')
		comp = f_comp.print_field.split('\n')
		user = f_user.print_field.split('\n')
		for i in range(len(comp)):
			print(f'{comp[i]}\t\t\t{user[i]}')

	def out(self, dot):
		return not (0 <= dot[0] < self.size and 0 <= dot[1] < self.size)

	def add_ship(self, ship):
		for dot in ship.dots:
			if dot in self.busy or self.out(dot):
				raise WrongShipException
		for dot in ship.dots:
			self.field[dot[0]][dot[1]] = '■'
		for dot in ship.around:
			if not self.out(dot) and dot not in self.busy:
				self.busy.append(dot)
		self.ships.append(ship)

	def ship_killed(self, ship):
		for dot in ship.around:
			if not self.out(dot) and self.field[dot[0]][dot[1]] == 'O':
				self.field[dot[0]][dot[1]] = '.'
			if dot not in self.busy:
				self.busy.append(dot)
		self.ships.remove(ship)
		if self.is_comp == True:
			print('Убит')

	def shoot(self, dot):
		if self.out(dot):
			raise OutBoardException
		if dot in self.busy:
			raise UsedBoardException
		self.busy.append(dot)
		for ship in self.ships:
			if dot in ship.dots:
				self.field[dot[0]][dot[1]] = 'X'
				ship.lives -= 1
				if ship.lives == 0:
					self.ship_killed(ship)
				else:
					if self.is_comp == True:
						print('Ранен')
				return True
		self.field[dot[0]][dot[1]] = '.'
		if self.is_comp == True:
			print('Мимо')
		return False

	def begin(self):
		self.busy = []

	@staticmethod
	def rand(size=6, lst=None, is_comp=False):
		if lst is None:
			lst = [3, 2, 2, 1, 1, 1, 1]
		b = Board(size=size, lst=lst, is_comp=is_comp)
		for l in lst:
			count = 0
			while True:
				count += 1
				if count > 400:
					return None
				try:
					b.add_ship(Ship.rand(l))
					break
				except WrongShipException:
					continue
		return b


class Player:
	def __init__(self, enemy):
		self.enemy = enemy

	def ask(self):
		pass

	def move(self):
		while True:
			try:
				rep = self.enemy.shoot(self.ask())
				return rep
			except BoardException as e:
				print(e)


class Comp(Player):
	def __init__(self, enemy):
		super().__init__(enemy)
		self.shoot_list = [(i, j) for i in range(enemy.size) for j in range(enemy.size)]

	def ask(self):
		dot = choice(self.shoot_list)
		self.shoot_list.remove(dot)
		return dot


class User(Player):
	def ask(self):
		print('Ваш ход ', end='')
		while True:
			try:
				x, y = map(int, input().split())
				break
			except:
				print('Должно быть 2 целых числа')
				continue
		return (x - 1, y - 1)


class Game:
	def __init__(self, size=6, lst=None):
		if lst is None:
			lst = [3, 2, 2, 1, 1, 1, 1]
		self.size = size
		self.lst = lst
		self.comp_board = self.random_board(is_comp=True)
		self.user_board = self.random_board()
		self.user = User(self.comp_board)
		self.comp = Comp(self.user_board)

	def random_board(self, is_comp=False):
		while True:
			b = Board.rand(size=self.size, lst=self.lst, is_comp=is_comp)
			if b == None:
				continue
			b.busy = []
			return b

	def hello(self):
		print('Игра "Морской бой"')
		print('Введите номер строки и номер столбца через пробел')
		print()

	def loop(self):
		count = 0
		while True:
			if count % 2 == 0:
				Board.print(self.comp_board, self.user_board)
				rep = self.user.move()
			else:
				rep = self.comp.move()
			if rep:
				count -= 1
			if not self.comp_board.ships:
				print('Вы выирали')
				Board.print(self.comp_board, self.user_board)
				break
			if not self.user_board.ships:
				print('Победил компьтер')
				Board.print(self.comp_board, self.user_board)
				break
			count += 1

	def start(self):
		self.hello()
		self.loop()


g = Game()
g.start()
