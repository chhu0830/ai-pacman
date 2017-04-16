all:

p1-1:
	python pacman.py -p CleanerAgent -l P1-1

p1-2:
	python pacman.py -p FroggerAgent -l P1-2 -g StraightRandomGhost

p1-3:
	# python pacman.py -l P1-3 -g StraightRandomGhost
	python pacman.py -p SnakeAgent -l P1-3 -g StraightRandomGhost

p1-4:
	python pacman.py -p DodgeAgent -l P1-4
