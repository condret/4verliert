#! /usr/bin/env python3

import sys, tty, termios, subprocess, random, time
#import simpleaudio as sa

def getchar():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    tty.setraw(sys.stdin.fileno())
    ch = sys.stdin.read(1)
    termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch

def gotoxy(x, y):
    if x > 0:
        x = x + 1
    if y > 0:
        y = y + 1
    print ("\x1b[%d;%dH" % (y , x), end="")

class ConsoleUser:

    def __init__(self, x, y, w):
        self.x = x
        self.y = y
        self.w = w

    def move_x(self, color, direction):
        if direction == 0:
            gotoxy(self.x * 2, self.y)
            print (color, end="")
            gotoxy(self.x * 2, self.y + 1)
            print ("V", end="", flush=True)
            return self.x
    
        gotoxy(self.x * 2, self.y)
        print (" ", end="")
        gotoxy(self.x * 2, self.y + 1)
        print (" ", end="")
        self.x = (self.x + direction) % self.w
        gotoxy(self.x * 2, self.y)
        print (color, end="")
        gotoxy(self.x * 2, self.y + 1)
        print ("V", end="", flush=True)
    
        return self.x

class PlayField:
    
    def __init__(self, xsize, ysize):
        if xsize < 4 or ysize < 4:
            return None
        self.xsize = xsize
        self.ysize = ysize
        self.field = {}
 #       self.thunder_wav = sa.WaveObject.from_wave_file("thunder.wav")
        for x in range(xsize):
            for y in range(ysize):
                self.field.update({(x, y): 0})

    def expose (self, next_element, next_row, user):
        if not next_element:
            return
        for y in range(self.ysize):
            for x in range(self.xsize):
                next_element (user, x, y, self.field[(x, y)])
            if next_row:
                next_row (user)

    def sink_in(self, x, color):
        if x >= self.xsize:
            return (False, 0)

        if x < 0:
            return (False, 0)

        for y in range(self.ysize - 1, -1, -1):
            if self.field[(x, y)] == 0:
#                print ("\a",end ="", flush=True)
                self.field.update({(x, y) : color})
#                time.sleep(0.1)
#                self.thunder_wav.play()
                return (True, y)

        return (False, 0)

    def get_coin (self, x, y):
        return self.field.get((x, y), None)


class Game:
    def check_win(self, x, y):
        color = self.field.get_coin(x, y)
        if color == None or color == 0:
            return False

        con_coins = 0
        for n in range(-3, 4):
            if self.field.get_coin (x + n, y) == color:
                con_coins = con_coins + 1
            else:
                con_coins = 0
            if con_coins > 3:
                return True

        con_coins = 0
        for n in range (-3, 4):
            if self.field.get_coin (x + n, y + n) == color:
                con_coins = con_coins + 1
            else:
                con_coins = 0
            if con_coins > 3:
                return True

        con_coins = 0
        for n in range (-3, 4):
            if self.field.get_coin (x + n, y - n) == color:
                con_coins = con_coins + 1
            else:
                con_coins = 0
            if con_coins > 3:
                return True

        for n in range (1, 4):
            if not self.field.get_coin(x, y + n) == color:
                return False

        return True


    def check_remi(self):
        return self.coins == self.field.xsize * self.field.ysize


    def __init__(self, xs, ys, p0, p1):
        if p0.color == 0:
            return None
        if p1.color == 0:
            return None
        if p0.color == p1.color:
            return None
        field = PlayField(xs, ys)
        if field is None:
            return None
        self.field = field
        self.players = [p0, p1]
        self.current = random.randint(0, 1)
        self.coins = 0

    #player has won, when it returns true
    def play(self, user):
        next_color = self.players[self.current].color
        self.current = (self.current + 1) % 2
        player = self.players[self.current]
        suc = False
        x, y = 0, 0

        while not suc:
            x = player.play(user)
            suc, y = self.field.sink_in(x, player.color)

        user.move_x (next_color, 0)
        self.coins = self.coins + 1

        return self.check_win(x, y)


class DumbHumanPlayer:
    def __init__ (self, color, right, left, down, get_input):
        if color == None or color == 0:
            return None
        if get_input == None:
            return None

        self.color = color
        self.right = right
        self.left = left
        self.down = down
        self.get_input = get_input

    def play(self, user):

        ch = None
        while ch != self.down:
            ch = self.get_input()
            if ch == self.right:
                user.move_x(self.color, -1)
            if ch == self.left:
                user.move_x(self.color, 1)

        return user.move_x(self.color, 0)


class SmartRandomPlayer:
    def __init__ (self, color, width):
        if color == None or color == 0:
            return None

        self.color = color
        self.width = width

    def play(self, user):
        rel_dst = random.randint(0, self.width-1) - (self.width / 2)
        while (rel_dst < 0):
            rel_dst = rel_dst + 1
            user.move_x(self.color, -1)
            time.sleep(.100)

        while (rel_dst > 0):
            rel_dst = rel_dst - 1
            user.move_x(self.color, 1)
            time.sleep(.100)

        return user.move_x(self.color, 0)

#class DumbBotPlayer:
#    def __init__(self, color):
#        if color == None or color == 0:
#            return None
#        self.color = color
#
#    def play(self, field):  # returns x-coordinate 



def next_column_in_line(user, x, y, color):
    print (color, end=" ")


def next_line(user):
    print ("", end="\n")


#p0 = DumbHumanPlayer("\x1b[31m0\x1b[37m", 'a', 'd', 's', getchar)    #red
p0 = SmartRandomPlayer("\x1b[31m0\x1b[37m", 64)    #cyan
p1 = SmartRandomPlayer("\x1b[36m0\x1b[37m", 64)    #cyan
g = Game(64, 8, p0, p1)

cons_user = ConsoleUser(0, 0, 64);

gotoxy (0, 2)
g.field.expose(next_column_in_line, next_line, None)
gotoxy (0, 0)
print ("V", end="", flush=True)

while not g.play(cons_user):
    gotoxy (0, 2)
    g.field.expose(next_column_in_line, next_line, None)
    if g.check_remi():
        print ("Y'\aa\al\al\a \af\au\ac\ak\ai\an\ag \al\ao\ao\as\ae\ar\as\aG\aT\aF\aO")
        sys.exit(0)

gotoxy (0, 2)
g.field.expose(next_column_in_line, next_line, None)

print (g.players[g.current].color, end=" wins\n")
