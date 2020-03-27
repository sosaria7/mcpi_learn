#-*- coding: utf-8 -*-

from mcpi.minecraft import Minecraft
from mcpi import block

import time
import random



class Cell:
    class ConstError(TypeError): pass

    def __setattr__(self,name,value):
        if name.startswith("STATE_") or name.startswith("WALL_"):
            raise self.ConstError, "Can't rebind const(%s)"%name
        self.__dict__[name]=value

    STATE_NONE = 0
    STATE_DONE = 1
    STATE_MOVE_UP = 2
    STATE_MOVE_DOWN = 3
    STATE_MOVE_LEFT = 4
    STATE_MOVE_RIGHT = 5

    WALL_BLOCKED = 0
    WALL_OPENED = 1

    state = STATE_NONE
    left = WALL_OPENED
    up = WALL_BLOCKED

    def __init__(self):
        self.clear()

    def clear(self):
        self.state = Cell.STATE_NONE
        self.left = Cell.WALL_BLOCKED
        self.up = Cell.WALL_BLOCKED


class Maze:
    width = 1
    height = 1
    maze = None
    restCount = 1

    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.restCount = width * height
        # maze[x][y]
        self.maze = [[Cell() for x in range(height)] for y in range(width)]
        self.makeMaze()

    def makeMaze(self):
        for x in range(0, self.width):
            for y in range(0, self.height):
                self.maze[x][y].clear()

        first_x = random.randint(0, self.width - 1)
        first_y = random.randint(0, self.height - 1)

        #처음 하나를 done으로 변경
        self.maze[first_x][first_y].state = Cell.STATE_DONE
        self.restCount -= 1

        #path 만들기
        while self.restCount > 0:
            self.makePath()

        self.maze[0][0].left = Cell.WALL_OPENED


    def makePath(self):
        x = 0
        y = 0

        startIndex = random.randint(0, self.restCount - 1)

        index = 0

        #시작 좌표 찾으면서 이전의 자국 지우기
        for xx in range(self.width):
            for yy in range(self.height):
                if self.maze[xx][yy].state == Cell.STATE_NONE:
                    if index == startIndex:
                        x = xx
                        y = yy
                    index += 1
                elif self.maze[xx][yy].state != Cell.STATE_DONE:
                    self.maze[xx][yy].state = Cell.STATE_NONE

        startX = x
        startY = y

        # 통로를 찾을 때 까지 이동하기
        while self.maze[x][y].state != Cell.STATE_DONE:
            while True:
                direction = random.randint(0, 3)
                if direction == 0:      # up
                    if y == 0: continue
                    self.maze[x][y].state = Cell.STATE_MOVE_UP
                    y -= 1
                elif direction == 1:    # down
                    if y == self.height - 1: continue
                    self.maze[x][y].state = Cell.STATE_MOVE_DOWN
                    y += 1
                elif direction == 2:    # left
                    if x == 0: continue
                    self.maze[x][y].state = Cell.STATE_MOVE_LEFT
                    x -= 1
                else:                   # right
                    if x == self.width - 1: continue;
                    self.maze[x][y].state = Cell.STATE_MOVE_RIGHT
                    x += 1
                break

        # 시작 위치부터 목적지까지 경로 생성
        x = startX
        y = startY
        while self.maze[x][y].state != Cell.STATE_DONE:
            state = self.maze[x][y].state
            self.restCount -= 1

            self.maze[x][y].state = Cell.STATE_DONE
            if state == Cell.STATE_MOVE_UP:
                self.maze[x][y].up = Cell.WALL_OPENED
                y -= 1
            elif state == Cell.STATE_MOVE_DOWN:
                self.maze[x][y+1].up = Cell.WALL_OPENED
                y += 1
            elif state == Cell.STATE_MOVE_LEFT:
                self.maze[x][y].left = Cell.WALL_OPENED
                x -= 1
            else:
                self.maze[x+1][y].left = Cell.WALL_OPENED
                x += 1

    # 출력하기
    def printMaze(self):

        for y in range(self.height):
            line =''
            for x in range(self.width):
                if self.maze[x][y].up == Cell.WALL_OPENED:
                    char = ' '
                else:
                    char = '*'
                line += '*' + char
            #마지막 오른쪽 벽
            line += '*'
            print( line )

            line = ''
            for x in range(self.width):
                if self.maze[x][y].left == Cell.WALL_OPENED:
                    char = ' '
                else:
                    char = '*'
                line += char
                line += ' '

            #마지막 오른쪽 벽, 마지막 라인의 마지막 오른쪽은 출력하지 않는다.
            if y != self.height - 1:
                line += '*'
            print( line )

        #마지막 아랫쪽 벽
        line = ''
        for x in range(self.width * 2 + 1):
            line += '*'
        print( line )

    # 마인크래프트에 미로 건축
    def build(self, mc, pos):
        wallId = block.BRICK_BLOCK
        #wallId = block.BEDROCK

        pos.x -= 1
        pos.z -= 1
        # width = self.width * 3 + 1
        # height = self.height * 3 + 1

        # 공간
        mc.setBlocks( pos.x, pos.y, pos.z, pos.x + self.width * 3, pos.y + 100, pos.z + self.height * 3, block.AIR )

        # 바닥
        mc.setBlocks( pos.x, pos.y - 1, pos.z, pos.x + self.width * 3, pos.y - 1, pos.z + self.height * 3, 169 )    #바다랜턴

        # 밑바닥
        mc.setBlocks( pos.x, pos.y - 2, pos.z, pos.x + self.width * 3, pos.y - 2, pos.z + self.height * 3, block.BEDROCK )    #바다랜턴

        # 천정
        #mc.setBlocks( pos.x, pos.y + 4, pos.z, pos.x + self.width * 3, pos.y + 4, pos.z + self.height * 3, block.GLASS )

        for y in range(self.height):
            # 윗쪽 벽
            for x in range(self.width):
                mc.setBlocks( pos.x + x * 3, pos.y, pos.z + y * 3, pos.x + x * 3, pos.y + 3, pos.z + y * 3, wallId)
                if self.maze[x][y].up == Cell.WALL_BLOCKED:
                    mc.setBlocks( pos.x + x * 3 + 1, pos.y, pos.z + y * 3, pos.x + x * 3 + 2, pos.y + 3, pos.z + y * 3, wallId)

            # 마지막 오른쪽 벽
            mc.setBlocks(pos.x + self.width * 3, pos.y, pos.z + y * 3, pos.x + self.width * 3, pos.y + 3, pos.z + y * 3, wallId)

            # 통로 왼쪽 벽
            for x in range(self.width):
                if self.maze[x][y].left == Cell.WALL_BLOCKED:
                    mc.setBlocks(pos.x + x * 3, pos.y, pos.z + y * 3 + 1,
                                 pos.x + x * 3, pos.y + 3, pos.z + y * 3 + 2, wallId)

            #마지막 오른쪽 벽, 마지막 라인의 마지막 오른쪽은 출력하지 않는다.
            if y != self.height - 1:
                mc.setBlocks(pos.x + self.width * 3, pos.y, pos.z + y * 3 + 1,
                             pos.x + self.width * 3, pos.y + 3, pos.z + y * 3 + 2, wallId)

        # 맨 위 벽
        mc.setBlocks(pos.x, pos.y, pos.z, pos.x + self.width * 3, pos.y + 3, pos.z, 95, 4 )

        # 맨 아래 벽
        mc.setBlocks(pos.x, pos.y, pos.z + self.height * 3, pos.x + self.width * 3, pos.y + 3, pos.z + self.height * 3, 95, 5 )

        # 시작위치 천정
        mc.setBlocks(pos.x, pos.y + 4, pos.z + 1, pos.x + 1, pos.y + 4, pos.z + 2, 95, 4)

        # 끝 위치 천정
        mc.setBlocks(pos.x + self.width * 3 - 1, pos.y + 4, pos.z + self.height * 3 - 2, pos.x + self.width * 3, pos.y + 4, pos.z + self.height * 3 - 1, 95, 5)


if __name__ == '__main__':
    mc = Minecraft.create()
    while True:
        event = mc.events.pollChatPosts()
        for e in event:
            if e.message == 'maze':
                maze = Maze(30, 30)
                id = e.entityId
                pos = mc.entity.getTilePos(id)
                maze.build(mc, pos)
        time.sleep(0.1)




