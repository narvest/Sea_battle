from random import randint  # функция включающая игрока-компьютер

class Dot: # класс точек на поле
    def __init__(self, x, y): # метод задающий координаты по Х и У
        self.x = x
        self.y = y

    def __eq__(self, other): # метод отвечающий за сравнение двух объектов
        return self.x == other.x and self.y == other.y

    def __repr__(self): # вывод точек в консоль
        return f"({self.x}, {self.y})"

# классы исключений
class BoardException(Exception): # общий класс, содержащий в себе все классы исключений
    pass


class BoardOutException(BoardException): # выстрел за границы доски
    def __str__(self):
        return "Вы пытаетесь выстрелить за доску!"


class BoardUsedException(BoardException): # стрельба в ту же клетку
    def __str__(self):
        return "Вы уже стреляли в эту клетку"


class BoardWrongShipException(BoardException): # исключение для нормального размещения кораблей
    pass


class Ship: # класс корабля
    def __init__(self, bow, l, o): # координаты носа корабля, длина корабля, ориентация
        self.bow = bow
        self.l = l
        self.o = o
        self.lives = l

    @property
    def dots(self):
        ship_dots = []
        for i in range(self.l):
            cur_x = self.bow.x
            cur_y = self.bow.y

            if self.o == 0: # ориентация корабля по вертикали, а 1 по горизонтали
                cur_x += i

            elif self.o == 1:
                cur_y += i

            ship_dots.append(Dot(cur_x, cur_y))

        return ship_dots

    def shooten(self, shot): # метод показывающий попадания в корабль
        return shot in self.dots


class Board: # класс игровое поле
    def __init__(self, hid=False, size=6):
        self.size = size
        self.hid = hid

        self.count = 0  # количество пораженных кораблей

        self.field = [["O"] * size for _ in range(size)]  # содержащий в клетке 0

        self.busy = []  # хранит в себе занятые точки
        self.ships = []  # список кораблей на доске

    def add_ship(self, ship):  # метод для размещения корабля

        for d in ship.dots:
            if self.out(d) or d in self.busy: # показывает не выходит ли корабль за границы доски и не занята ли клетка
                raise BoardWrongShipException() # если это так то выходит исключение
        for d in ship.dots:  # проходим по точкам корабля и отмечаем квадратиком
            self.field[d.x][d.y] = "■"
            self.busy.append(d)

        self.ships.append(ship)  # добавление кораблей
        self.contour(ship)  # обвод кораблей по контуру

    def contour(self, ship, verb=False): # контур корабля на доске
        near = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 0), (0, 1),  # основная координата 0, 0 и окружающий ее контур
            (1, -1), (1, 0), (1, 1)
        ]
        for d in ship.dots:
            for dx, dy in near:  # передвижение по Х и У конструкции окруженной по контуру клетке
                cur = Dot(d.x + dx, d.y + dy)
                if not (self.out(cur)) and cur not in self.busy:
                    if verb:
                        self.field[cur.x][cur.y] = "."
                    self.busy.append(cur)  # занятые точки

    def __str__(self):  # вывод корабля на доску
        res = ""
        res += "  | 1 | 2 | 3 | 4 | 5 | 6 |"
        for i, row in enumerate(self.field):
            res += f"\n{i + 1} | " + " | ".join(row) + " |"

        if self.hid:
            res = res.replace("■", "O")
        return res

    def out(self, d):  # метод определяющий находится ли точка за пределами доски
        return not ((0 <= d.x < self.size) and (0 <= d.y < self.size))

    def shot(self, d):  # метод стрельбы
        if self.out(d):
            raise BoardOutException()  # выстрел за границы доски

        if d in self.busy:
            raise BoardUsedException()

        self.busy.append(d)  # указываем, что клетка занята, если она еще не занята

        for ship in self.ships:
            if d in ship.dots:
                ship.lives -= 1  # убавляется жизнь корабля
                self.field[d.x][d.y] = "X"  # ставится Х при попадание
                if ship.lives == 0:
                    self.count += 1  # прибавляем к уничтоженным кораблям
                    self.contour(ship, verb=True)  # обозначаем контур подбитого корабля точками
                    print("Корабль уничтожен!")
                    return False
                else:
                    print("Корабль ранен!")
                    return True

        self.field[d.x][d.y] = "."
        print("Мимо!")
        return False

    def begin(self):
        self.busy = []  # занятые клетки, куда стреляли


class Player: # класс игрока
    def __init__(self, board, enemy):  # передаются в качестве аргумента две доски
        self.board = board  # доска игрока
        self.enemy = enemy  # доска противника

    def ask(self):
        raise NotImplementedError()

    def move(self):  # даем команду выстрела
        while True:
            try:
                target = self.ask()
                repeat = self.enemy.shot(target)
                return repeat
            except BoardException as e:
                print(e)


class AI(Player):  # класс игрок-компьютер
    def ask(self):
        d = Dot(randint(0, 5), randint(0, 5))
        print(f"Ход компьютера: {d.x + 1} {d.y + 1}")
        return d


class User(Player):  # кдасс игрок-пользователь
    def ask(self):
        while True:
            cords = input("Ваш ход: ").split()

            if len(cords) != 2:
                print(" Введите 2 координаты! ")
                continue

            x, y = cords

            if not (x.isdigit()) or not (y.isdigit()):
                print(" Введите числа! ")
                continue

            x, y = int(x), int(y)

            return Dot(x - 1, y - 1)


class Game:
    def __init__(self, size=6):
        self.size = size
        pl = self.random_board()
        co = self.random_board()
        co.hid = True

        self.ai = AI(co, pl)
        self.us = User(pl, co)

    def random_board(self):
        board = None
        while board is None:
            board = self.random_place()
        return board

    def random_place(self):
        lens = [3, 2, 2, 1, 1, 1, 1]
        board = Board(size=self.size)
        attempts = 0
        for l in lens:
            while True:
                attempts += 1
                if attempts > 2000:
                    return None
                ship = Ship(Dot(randint(0, self.size), randint(0, self.size)), l, randint(0, 1))
                try:
                    board.add_ship(ship)
                    break
                except BoardWrongShipException:
                    pass
        board.begin()
        return board

    def greet(self):
        print("-------------------")
        print("  Приветсвуем вас  ")
        print("      в игре       ")
        print("    морской бой    ")
        print("-------------------")
        print(" формат ввода: x y ")
        print(" x - номер строки  ")
        print(" y - номер столбца ")

    def loop(self):
        num = 0
        while True:
            print("-" * 20)
            print("Доска пользователя:")
            print(self.us.board)
            print("-" * 20)
            print("Доска компьютера:")
            print(self.ai.board)
            if num % 2 == 0:
                print("-" * 20)
                print("Ходит пользователь!")
                repeat = self.us.move()
            else:
                print("-" * 20)
                print("Ходит компьютер!")
                repeat = self.ai.move()
            if repeat:
                num -= 1

            if self.ai.board.count == 7:
                print("-" * 20)
                print("Пользователь выиграл!")
                break

            if self.us.board.count == 7:
                print("-" * 20)
                print("Компьютер выиграл!")
                break
            num += 1

    def start(self):
        self.greet()
        self.loop()


g = Game()
g.start()
