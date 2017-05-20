all:

# Lab 1
p1-1:
	python pacman.py -p CleanerAgent -l P1-1
p1-2:
	python pacman.py -p FroggerAgent -l P1-2 -g StraightRandomGhost
p1-3:
	python pacman.py -p SnakeAgent -l P1-3 -g StraightRandomGhost
p1-4:
	python pacman.py -p DodgeAgent -l P1-4

p2-1:
	python pacman.py -l mediumMaze -p SearchAgent -a fn=dfs
p2-2:
	python pacman.py -l mediumMaze -p SearchAgent -a fn=bfs
p2-3:
	python pacman.py -l mediumMaze -p SearchAgent -a fn=astar,heuristic=manhattanHeuristic

p3-1:
	python pacman.py -l openClassic -p ReflexAgent
p3-2:
	python pacman.py -l minimaxClassic -p MinimaxAgent -a depth=4
p3-3:
	python pacman.py -l smallClassic -p AlphaBetaAgent -a depth=3
p3-4:
	python pacman.py -l smallClassic -p AlphaBetaAgent -a depth=3,evalFn=better
