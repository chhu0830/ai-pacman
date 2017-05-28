all:

# Lab 1
q1-1:
	python pacman.py -p CleanerAgent -l P1-1
q1-2:
	python pacman.py -p FroggerAgent -l P1-2 -g StraightRandomGhost
q1-3:
	python pacman.py -p SnakeAgent -l P1-3 -g StraightRandomGhost
q1-4:
	python pacman.py -p DodgeAgent -l P1-4

q2-1:
	python pacman.py -l mediumMaze -p SearchAgent -a fn=dfs
q2-2:
	python pacman.py -l mediumMaze -p SearchAgent -a fn=bfs
q2-3:
	python pacman.py -l mediumMaze -p SearchAgent -a fn=astar,heuristic=manhattanHeuristic

# Lab2
q3-1:
	python pacman.py -l openClassic -p ReflexAgent
q3-2:
	python pacman.py -l minimaxClassic -p MinimaxAgent -a depth=4
q3-3:
	python pacman.py -l smallClassic -p AlphaBetaAgent -a depth=3
q3-4:
	python pacman.py -l smallClassic -p AlphaBetaAgent -a depth=3,evalFn=better
test:
	python autograder.py -q q1 --no-graphics
	python autograder.py -q q2 --no-graphics
	python autograder.py -q q3 --no-graphics
	python autograder.py -q q5 --no-graphics
