import time
from main_gui import *
from AIs import *
from Heuristic import *


def ai(n, SoLanTron, heuristic):
    
    m = Cube(n)
    ai = A_Star(m, heuristic)
    
    scramble = m.trueScramble(SoLanTron)
    print('Scramble moves: ' + str(scramble))
    input('Type enter to continue.')

    start_time = time.time() # Thời gian bắt đầu của thuật toán
    path = ai.solve()
    gui_path = [] # Được sử dụng để lưu trữ các bộ dữ liệu di chuyển, trạng thái
    print('AI took: ' + str(time.time()-start_time) + ' seconds')
    print('Original scramble: ' + str(scramble))
    for i in range(len(path)):
        print('Move #' + str(i+1) + '[ ' + str(Cube.translateMove(path[i][0])) + ', ' + str(path[i][1].state))
        gui_path.append((path[i][0], path[i][1].state))

    new_cube = Cube(n)
    g = GUI(cube=new_cube, width=800, height=600, threeD=True)
    g.moveList(gui_path)
    while True:
        g.update()


if __name__ == '__main__':

    heuristic = Heuristic.manhattanDistance
    ai(2, 5, heuristic)
