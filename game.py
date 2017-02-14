import tkinter as tk
from time import sleep
import sys
from random import randint, choice


class App:
    """The main class
        Args:
            width (int): display width
            height (int): display height
            size (int): size of the cells
    """
    def __init__(self, width=1200, height=1000, size=20):
        self.screen_width = width
        self.screen_height = height
        self._running = True
        self._paused = False
        self.cellsize = size
        self.maxcols = self.screen_width // self.cellsize
        self.maxrows = self.screen_height // self.cellsize

    def initialize(self):
        global root
        root = tk.Tk()
        root.wm_title("Snek")

        # binding keys
        root.bind('<Escape>', self.close)
        root.protocol('WM_DELETE_WINDOW', self.close)
        root.bind('<w>', self.up)
        root.bind('<Up>', self.up)
        root.bind('<a>', self.left)
        root.bind('<Left>', self.left)
        root.bind('<s>', self.down)
        root.bind('<Down>', self.down)
        root.bind('<d>', self.right)
        root.bind('<Right>', self.right)
        root.bind('<Return>', self.restart)

        self.cv = tk.Canvas(root, height=self.screen_height,
                            width=self.screen_width, background='black')
        self.init_board()

    def init_board(self):
        """Constructs the game board.
        """
        # the cell ids are represented by tuples containing the coords in the
        # form of (x, y)
        self.cellids = [(i, n) for i in range(self.maxrows+1)
                        for n in range(self.maxcols+1)]

        # Create snek
        self.midcol, self.midrow = self.maxcols // 2, self.maxrows // 2
        self.snek = Snek(self.cv, (self.midrow, self.midcol), self.cellsize)
        self.cv.pack()
        self.mainloop()

    def mainloop(self):
        """Application Mainloop
        """
        while self._running:
            sleep(0.1)
            try:
                self.snek.update()
            except GameOver as e:
                gomessage = self.cv.create_text(((self.midcol-2)*self.cellsize,
                                                 self.midrow*self.cellsize),
                                                anchor=tk.CENTER, fill='red',
                                                text="  GAME\n  OVER\n\nSCORE %s" % e,
                                                font=("Fixedsys", 52, "bold"))
                self._gameover = True
                while self._gameover:
                    self.cv.update()
                self.snek.kill_snek()
                self.cv.delete(gomessage)
                self.init_board()
            self.cv.update()

    def up(self, *ignore):
        if self.snek.ori != (+1, 0):
            self.snek.ori = (-1, 0)

    def left(self, *ignore):
        if self.snek.ori != (0, +1):
            self.snek.ori = (0, -1)

    def down(self, *ignore):
        if self.snek.ori != (-1, 0):
            self.snek.ori = (+1, 0)

    def right(self, *ignore):
        if self.snek.ori != (0, -1):
            self.snek.ori = (0, +1)

    def restart(self, *ignore):
        if self._gameover:
            self._gameover = False

    def close(self, *ignore):
        """Close Application
        """
        self._running = False
        root.destroy()


class GameOver(Exception):
    pass


class Cell(App):
    """A cell. Can be alive or dead.
    Args:
        cv (canvas): the canvas on which to draw on
        row (int): the row of the Cell
        column (int): the column of the Cell
    """
    def __init__(self, cv, loc, size, color):
        super().__init__()
        self.cv = cv
        self.color = color
        self.width = size
        self.height = size
        self.row, self.col = loc
        self.x = self.col * self.width
        self.y = self.row * self.height
        self.corn = [self.x, self.y, self.x + self.width, self.y + self.height]
        self.cid = self.cv.create_rectangle(self.corn[0], self.corn[1],
                                            self.corn[2], self.corn[3],
                                            fill=self.color)

    def update(self, newcords):
        self.row, self.col = newcords
        self.x = self.col * self.width
        self.y = self.row * self.height
        self.corn = [self.x, self.y, self.x + self.width, self.y + self.height]
        self.cv.coords(self.cid, (self.corn[0], self.corn[1],
                                  self.corn[2], self.corn[3]))

    def kill(self):
        self.cv.delete(self.cid)


class Snek(App):
    def __init__(self, cv, loc, size):
        super().__init__()
        self.cv = cv
        self.size = size
        self.row, self.col = loc
        self.fodder = Cell(self.cv, (randint(1, self.maxrows-1),
                           randint(1, self.maxcols-1)), self.size,
                           choice(['red', 'white', 'blue', 'yellow', 'cyan']))
        self.ori = (0, +1)
        self.head = Cell(self.cv, (self.row, self.col), self.size, 'green')
        self.tailcoords = [(self.row, self.col-1), (self.row, self.col-2)]
        self.score = len(self.tailcoords)
        self.tail = [Cell(self.cv, self.tailcoords[0], self.size, 'green'),
                     Cell(self.cv, self.tailcoords[1], self.size, 'green')]

    def update(self):
        dr, dc = self.ori
        nr, nc = self.row+dr, self.col+dc
        if (nr, nc) in self.tailcoords:
            raise GameOver(str(self.score))
        elif nr > self.maxrows or nc > self.maxcols:
            raise GameOver(str(self.score))
        elif nr < 0 or nc < 0:
            raise GameOver(str(self.score))
        self.head.update((nr, nc))
        if (nr, nc) == (self.fodder.row, self.fodder.col):
            self.tailcoords.append(self.tailcoords[-1])
            self.tail.append(self.tail[-1])
            self.score = len(self.tail)
        for i in reversed(self.tailcoords):
            ind = self.tailcoords.index(i)
            if ind == 0:
                self.tail[ind].update((self.row, self.col))
                self.tailcoords[ind] = (self.row, self.col)
                break
            self.tail[ind].update(self.tailcoords[ind-1])
            self.tailcoords[ind] = self.tailcoords[ind-1]
        self.row += dr
        self.col += dc

    def kill_snek(self):
        self.head.kill()
        for i in self.tail:
            i.kill()


def main():
    try:
        app = App(int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]))
    except IndexError:
        app = App()
    app.initialize()


if __name__ == '__main__':
    main()
