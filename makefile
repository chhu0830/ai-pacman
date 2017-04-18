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
