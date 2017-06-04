# myTeam.py
# ---------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
# 
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).


from captureAgents import CaptureAgent
import random, time, util
from game import Directions
import game

#################
# Team creation #
#################

def createTeam(indexes, num, isRed, names=['TDAgent','TDAgent']):
    """
    This function should return a list of agents that will form the
    team, initialized using firstIndex and secondIndex as their agent
    index numbers.    isRed is True if the red team is being created, and
    will be False if the blue team is being created.

    As a potentially helpful development aid, this function can take
    additional string-valued keyword arguments, which will come from
    the --redOpts and --blueOpts command-line arguments to capture.py.
    For the nightly contest, however, your team will be created without
    any extra arguments, so you should make sure that the default
    behavior is what you want for the nightly contest.
    """

    # The following line is an example only; feel free to change it.
    return [eval(name)(index) for name, index in zip(names, indexes)]

##########
# Agents #
##########

class alphaBetaTDAgent(CaptureAgent):
    def registerInitialState(self, gameState):
        CaptureAgent.registerInitialState(self, gameState)

        self.alpha = 0.0001
        self.features = ['dot', 'big', 'cap']
        self.used = {}
        self.weight = {}
        fi = open('weight' + str(self.index[0]), 'r')
        for feature in self.features:
            self.used[feature] = []
            self.weight[feature] = []
            '''
            for i in range(10):
                n = fi.readline()
                self.weight[feature].append(float(n))
            '''
            self.weight[feature] = [random.random() for i in range(10, 0, -1)]
        fi.close()
        self.preScore = None
        self.preGameState = None
        self.count = 1800

    def chooseAction(self, gameState):
        self.learnEvaluateion(gameState)

        legalMoves = gameState.getLegalActions(self.index[0])
        agents = [self.index[0], (self.index[0] + 1) % 4, (self.index[0] + 3) % 4]
        scores = []
        a = -float('inf')

        for action in legalMoves:
            successor = gameState.generateSuccessor(self.index[0], action)
            successor = successor.generateSuccessor(self.index[1], action)
            v = self.alphabeta(successor, gameState, 1, a, float('inf'), agents[1:]+agents[:1])
            a = max(a, v)
            scores.append(v)

        bestScore = max(scores)
        bestIndices = [index for index in range(len(scores)) if scores[index] == bestScore]
        chosenIndex = random.choice(bestIndices)

        if self.count <= 4:
            fo = open('weight' + str(self.index[0]), 'w')
            for feature in self.features:
                for weight in self.weight[feature]:
                    fo.write(str(weight) + '\n')
            fo.close()
        else:
            self.count -= 4

        self.preScore = gameState.getScore()
        self.preGameState = gameState
        return legalMoves[chosenIndex]
        # return random.choice(legalMoves)

    def alphabeta(self, gameState, preGameState, depth, a, b, agents):
        if depth == 0:
            return self.evaluate(gameState, preGameState)

        legalMoves = gameState.getLegalActions(agents[0])
        nextAgent = agents[1]
        nextDepth = depth - 1 if nextAgent == self.index[0] else depth
        
        if agents[0] == self.index[0]:
            v = -float('inf')
            for action in legalMoves:
                successor = gameState.generateSuccessor(self.index[0], action)
                successor = successor.generateSuccessor(self.index[1], action)
                v = max(v, self.alphabeta(successor, gameState, nextDepth, a, b, agents[1:]+agents[:1]))
                a = max(a, v)
                if a > b:
                    break
            return v
        else:
            v = float('inf')
            for action in legalMoves:
                successor = gameState.generateSuccessor(agents[0], action)
                successor = successor.generateSuccessor((agents[0] + 4) % 8, action)
                v = min(v, self.alphabeta(successor, gameState, nextDepth, a, b, agents[1:]+agents[:1]))
                a = min(a, v)
                if a > b:
                    break
            return v
    
    def learnEvaluateion(self, gameState):
        if self.preScore == None:
            return
        reward = gameState.getScore() - self.preScore
        value = self.value(gameState)
        preValue = self.value(self.preGameState)
        if value == -float('inf') or preValue == -float('inf'):
            return 
        delta = self.alpha * (reward + value - preValue)
        for feature in self.features:
            for i, used in enumerate(self.used[feature]):
                self.weight[feature][i] += delta if used else 0

    def evaluate(self, successor, gameState):
        r = 0

        pacman = successor.getAgentState(self.index[0])
        ghost = successor.getAgentState(self.index[1])
        pos = pacman.getPosition()
        r += self.getFood(gameState)[int(pos[0])][int(pos[1])]

        opponents = self.getOpponents(gameState)
        opponents = [gameState.getAgentState(opponent) for opponent in opponents]
        for opponent in opponents:
            if opponent.isPacman and opponent.getPosition() == ghost.getPosition():
                if ghost.scaredTimer == 0:
                    r += 150
                else:
                    r -= 150
            if not opponent.isPacman and opponent.getPosition() == pacman.getPosition():
                if opponent.scaredTimer == 0:
                    r -= 150
                else:
                    r += 150

        return r + self.value(successor)


    def value(self, gameState):
        pacman = gameState.getAgentState(self.index[0]).getPosition()

        opponents = self.getOpponents(gameState)
        opponents = [gameState.getAgentState(opponent) for opponent in opponents]
        opponents_distance = [self.getMazeDistance(pacman, opponent.getPosition()) for opponent in opponents if not opponent.isPacman]

        dots = self.getFood(gameState).asList(key=10)
        dots_distance = [self.getMazeDistance(pacman, dot) for dot in dots]

        bigs = self.getFood(gameState).asList(key=50)
        bigs_distance = [self.getMazeDistance(pacman, big) for big in bigs]

        caps = self.getCapsules(gameState)
        caps_distance = [self.getMazeDistance(pacman, cap) for cap in caps]


        for i in range(0, 2):
            if i in opponents_distance:
                return -float('inf')

        self.used['dot'] = []
        for i in range(1, 11):
            self.used['dot'].append(True if i in dots_distance else False)

        self.used['big'] = []
        for i in range(1, 11):
            self.used['big'].append(True if i in bigs_distance else False)

        self.used['cap'] = []
        for i in range(1, 11):
            self.used['cap'].append(True if i in caps_distance else False)

        value = 0
        for feature in self.features:
            for i, used in enumerate(self.used[feature]):
                value += self.weight[feature][i] if used else 0

        return value


class TDAgent(CaptureAgent):
    def registerInitialState(self, gameState):
        CaptureAgent.registerInitialState(self, gameState)

        self.alpha = 0.001
        self.features = ['big', 'cap', 'deadend', 'dot', 'open', 'scared']
        self.used = {}
        self.weight = {}
        for feature in self.features:
            self.used[feature] = []
            self.weight[feature] = []

        '''
        for feature in self.features:
            self.weight[feature] = [random.random() for i in range(10, 0, -1)]
        self.weight['deadend'] = [random.random()]
        self.weight['open'] = [random.random()]
        self.weight['scared'] = [random.random() for i in range(2)]
        '''
        fi = open('weight' + str(self.index[0]), 'r')
        for i in range(10):
            self.weight['big'].append(float(fi.readline()))
        for i in range(10):
            self.weight['cap'].append(float(fi.readline()))
        self.weight['deadend'] = [float(fi.readline())]
        for i in range(10):
            self.weight['dot'].append(float(fi.readline()))
        self.weight['open'] = [float(fi.readline())]
        for i in range(2):
            self.weight['scared'].append(bool(fi.readline()))
        fi.close()

        self.preScore = None
        self.preGameState = None
        self.count = 1800

    def chooseAction(self, gameState):
        self.learnEvaluateion(gameState)

        legalMoves = gameState.getLegalActions(self.index[0])
        scores = [self.evaluate(gameState, action) for action in legalMoves]
        bestScore = max(scores)
        bestIndices = [index for index in range(len(scores)) if scores[index] == bestScore]
        chosenIndex = random.choice(bestIndices)

        if self.count <= 4:
            fo = open('weight' + str(self.index[0]), 'w')
            for i in range(10):
                fo.write(str(self.weight['big'][i]) + '\n')
            for i in range(10):
                fo.write(str(self.weight['cap'][i]) + '\n')
            fo.write(str(self.weight['deadend'][0]) + '\n')
            for i in range(10):
                fo.write(str(self.weight['dot'][i]) + '\n')
            fo.write(str(self.weight['open'][0]) + '\n')
            for i in range(2):
                fo.write(str(self.weight['scared'][i]) + '\n')
            fo.close()
        else:
            self.count -= 4

        self.preScore = gameState.getScore()
        self.preGameState = gameState
        return legalMoves[chosenIndex]
        # return random.choice(legalMoves)
    
    def learnEvaluateion(self, gameState):
        if self.preScore == None:
            return
        reward = gameState.getScore() - self.preScore
        value = self.value(gameState)
        preValue = self.value(self.preGameState)
        if value == -float('inf') or preValue == -float('inf'):
            return 
        delta = self.alpha * (reward + value - preValue)
        for feature in self.features:
            for i, used in enumerate(self.used[feature]):
                self.weight[feature][i] += delta if used else 0


    def evaluate(self, gameState, action):
        successor = gameState.generateSuccessor(self.index[0], action)
        successor = successor.generateSuccessor(self.index[1], action)

        r = 0

        pacman = successor.getAgentState(self.index[0])
        ghost = successor.getAgentState(self.index[1])
        pos = pacman.getPosition()
        r += self.getFood(gameState)[int(pos[0])][int(pos[1])]
        
        if (int(pos[0]), int(pos[1])) in self.getCapsules(gameState):
            r += 150

        opponents = self.getOpponents(gameState)
        opponents = [gameState.getAgentState(opponent) for opponent in opponents]
        for opponent in opponents:
            if opponent.isPacman and opponent.getPosition() == ghost.getPosition():
                if ghost.scaredTimer == 0:
                    r += 150
                else:
                    r -= 150
            if not opponent.isPacman and opponent.getPosition() == pacman.getPosition():
                if opponent.scaredTimer == 0:
                    r -= 150
                else:
                    r += 150

        return r + self.value(successor)


    def value(self, gameState):
        pacman = gameState.getAgentState(self.index[0]).getPosition()

        opponents = self.getOpponents(gameState)
        opponents = [gameState.getAgentState(opponent) for opponent in opponents]
        opponents_distance = [self.getMazeDistance(pacman, opponent.getPosition()) for opponent in opponents if not opponent.isPacman and opponent.scaredTimer == 0]

        dots = self.getFood(gameState).asList(key=10)
        dots_distance = [self.getMazeDistance(pacman, dot) for dot in dots]

        bigs = self.getFood(gameState).asList(key=50)
        bigs_distance = [self.getMazeDistance(pacman, big) for big in bigs]

        caps = self.getCapsules(gameState)
        caps_distance = [self.getMazeDistance(pacman, cap) for cap in caps]


        for i in range(0, 2):
            if i in opponents_distance:
                return -float('inf')

        self.used['scared'] = []
        for opponent in opponents:
            if not opponent.isPacman:
                self.used['scared'].append(True if opponent.scaredTimer != 0 else False)

        self.used['dot'] = []
        for i in range(1, 11):
            self.used['dot'].append(True if i in dots_distance else False)

        self.used['big'] = []
        for i in range(1, 11):
            self.used['big'].append(True if i in bigs_distance else False)

        self.used['cap'] = []
        for i in range(1, 11):
            self.used['cap'].append(True if i in caps_distance else False)

        self.used['deadend'] = [True if gameState.getLegalActions(self.index[0]) <= 2 else False]
        self.used['deadend'] = [True if gameState.getLegalActions(self.index[0]) >= 4 else False]
        
        value = 0
        for feature in self.features:
            for i, used in enumerate(self.used[feature]):
                value += self.weight[feature][i] if used else 0

        return value

class attackAgent(CaptureAgent):
    def registerInitialState(self, gameState):
        CaptureAgent.registerInitialState(self, gameState)

    def chooseAction(self, gameState):
        legalMoves = gameState.getLegalActions(self.index[1])
        opponents =  self.getOpponents(gameState)
        pos = gameState.getAgentPosition(self.index[1])
        
        distances = []
        for action in legalMoves:
            distances.append(min([self.getMazeDistance(pos, gameState.getAgentPosition(opponent)) for opponent in opponents if opponent < 4]))
        print distances

        if gameState.getAgentState(self.index[1]).scaredTimer != 0:
            minDistance = max(distances)
            bestIndices = [index for index in range(len(distances)) if distances[index] == minDistance]
        else:
            minDistance = min(distances)
            bestIndices = [index for index in range(len(distances)) if distances[index] == minDistance]
        chosenIndex = random.choice(bestIndices)

        return legalMoves[chosenIndex]
        # return random.choice(legalMoves)


class alphaBetaAgent(CaptureAgent):
    def registerInitialState(self, gameState):
        CaptureAgent.registerInitialState(self, gameState)

    def chooseAction(self, gameState):
        legalMoves = gameState.getLegalActions(self.index[0])
        agents = [self.index[0], (self.index[0] + 1) % 4, (self.index[0] + 3) % 4]
        scores = []
        a = -float('inf')

        for action in legalMoves:
            successor = gameState.generateSuccessor(self.index[0], action)
            successor = successor.generateSuccessor(self.index[1], action)
            v = self.alphabeta(successor, 1, a, float('inf'), agents[1:]+agents[:1])
            a = max(a, v)
            scores.append(v)

        bestScore = max(scores)
        bestIndices = [index for index in range(len(scores)) if scores[index] == bestScore]
        chosenIndex = random.choice(bestIndices)

        return legalMoves[chosenIndex]
        # return random.choice(actions)

    def alphabeta(self, gameState, depth, a, b, agents):
        if depth == 0:
            return self.evalFn(gameState, agents[1:])

        legalMoves = gameState.getLegalActions(agents[0])
        nextAgent = agents[1]
        nextDepth = depth - 1 if nextAgent == self.index[0] else depth
        
        if agents[0] == self.index[0]:
            v = -float('inf')
            for action in legalMoves:
                successor = gameState.generateSuccessor(self.index[0], action)
                successor = successor.generateSuccessor(self.index[1], action)
                v = max(v, self.alphabeta(successor, nextDepth, a, b, agents[1:]+agents[:1]))
                a = max(a, v)
                if a > b:
                    break
            return v
        else:
            v = float('inf')
            for action in legalMoves:
                successor = gameState.generateSuccessor(agents[0], action)
                successor = successor.generateSuccessor((agents[0] + 4) % 8, action)
                v = min(v, self.alphabeta(successor, nextDepth, a, b, agents[1:]+agents[:1]))
                a = min(a, v)
                if a > b:
                    break
            return v
            
    def evalFn(self, gameState, ghosts):
        pos = gameState.getAgentPosition(self.index[0])
        food = self.getFood(gameState).asList(key=50)
        dot = self.getFood(gameState).asList(key=10)
        capsules = self.getCapsules(gameState)
        scaredTimes = [gameState.getAgentState(ghost).scaredTimer for ghost in ghosts]

        ghostDist = 0
        for i in range(len(ghosts)):
            d = self.getMazeDistance(pos, gameState.getAgentPosition(ghosts[i]))
            if scaredTimes[i] != 0:
                ghostDist += (100 / d)
            elif d <= 1:
                ghostDist = -float('inf')
                break
        capDist = min([self.getMazeDistance(pos, capPos) for capPos in capsules]) if len(capsules) else 0
        foodDist = min([self.getMazeDistance(pos, foodPos) for foodPos in food]) if len(food) else 0
        dotDist = min([self.getMazeDistance(pos, dotPos) for dotPos in dot]) if len(dot) else 0

        # return gameState.getScore() + ghostDist - 5 * capDist - foodDist - 10 * dotDist - 2 * (len(food) + len(dot))
        return gameState.getScore() + ghostDist - dotDist - foodDist - 50 * capDist - 25 * (len(food) + len(dot))



class DummyAgent(CaptureAgent):
    """
    A Dummy agent to serve as an example of the necessary agent structure.
    You should look at baselineTeam.py for more details about how to
    create an agent as this is the bare minimum.
    """

    def registerInitialState(self, gameState):
        """
        This method handles the initial setup of the
        agent to populate useful fields (such as what team
        we're on).

        A distanceCalculator instance caches the maze distances
        between each pair of positions, so your agents can use:
        self.distancer.getDistance(p1, p2)

        IMPORTANT: This method may run for at most 15 seconds.
        """
        
        
        """
    	you can have your own distanceCalculator. (you can even have multiple distanceCalculators, if you need.)
    	reference the registerInitialState function in captureAgents.py and baselineTeam.py to understand more about the distanceCalculator. 
    	"""

        """
        Each agent has two indexes, one for pacman and the other for ghost.
        self.index[0]: pacman
        self.index[1]: ghost
        """

        '''
        Make sure you do not delete the following line. If you would like to
        use Manhattan distances instead of maze distances in order to save
        on initialization time, please take a look at
        CaptureAgent.registerInitialState in captureAgents.py.
        '''
        CaptureAgent.registerInitialState(self, gameState)

        '''
        Your initialization code goes here, if you need any.
        '''


    def chooseAction(self, gameState):
        """
        Picks among actions randomly.
        """
        actions = gameState.getLegalActions(self.index[0])

        values = [self.eval(gameState, a) for a in actions]
        maxValue = max(values)
        bestActions = [a for a, v in zip(actions, values) if v == maxValue]
        
        act =  random.choice(bestActions)
        return act
        '''
        You should change this in your own agent.
        '''


    def getOppoPos(self, gameState):
        AgentExistIdx = self.getOpponents(gameState)
        GhostPos = []
        AgentPos = []
        for idx in AgentExistIdx:
            if idx >= 4:
                GhostPos.append(gameState.getAgentPosition(idx))
            else:
                AgentPos.append(gameState.getAgentPosition(idx))
        return (AgentPos, GhostPos)
    
    def getScaredTimer(self, gameState):
        AgentExistIdx = self.getOpponents(gameState)
        ScaredTimer = []
        for idx in AgentExistIdx:
            if idx >= 4:
                ScaredTimer.append(gameState.getAgentState(idx).scaredTimer)
        return ScaredTimer
    
    def getSuccessor(self, gameState, action, index):
        return gameState.generateSuccessor(index, action)
    
    def eval(self, gameState, action):
        OppoAgentPos, OppoGhostPos = self.getOppoPos(gameState)
        # Pacmans' Viewpoint
        successorGameState = self.getSuccessor(gameState, action, self.index[0])
        PacPos = successorGameState.getAgentState(self.index[0]).getPosition()
        ScaredTimer = self.getScaredTimer(gameState)
        Food = self.getFood(successorGameState).asListNot()
        Capsules = self.getCapsules(successorGameState)
#print("ScaredTimer: ", ScaredTimer)
#print("PacmanPosition: ", PacPos)
#print("Food: ", Food)
#print("Capsules: ", Capsules)
        ghostDist = 0
        # Avoid meeting the ghosts
        for i in range(len(OppoGhostPos)):
            d = self.getMazeDistance(OppoGhostPos[i], PacPos)
            if d <= 1:
                if ScaredTimer[i] != 0:
                    ghostDist = float('inf')
                else:
                    ghostDist = -float('inf')
                break
            if ScaredTimer[i] != 0:
                ghostDist += (100 / d)
        capDist = min([self.getMazeDistance(PacPos, capPos) for capPos in Capsules]) if len(Capsules) else 0
        foodDist = min([self.getMazeDistance(PacPos, foodPos) for foodPos in Food]) if len(Food) else 0
        score = (successorGameState.getScore() - gameState.getScore())
        Pac_score = ghostDist - 50 * capDist - foodDist - 25 * len(Food)
        # Ghosts' Viewpoint
        successorGameState = self.getSuccessor(gameState, action, self.index[1])
        GhostPos = successorGameState.getAgentState(self.index[1]).getPosition()
        ScaredTime = successorGameState.getAgentState(self.index[1]).scaredTimer
        pacDist = min([self.getMazeDistance(GhostPos, pacPos) for pacPos in OppoAgentPos]) if len(OppoAgentPos) else 0
        Gho_score = 0
        if ScaredTime != 0:
            if len(OppoAgentPos) != 0 and min([self.getMazeDistance(GhostPos, pacPos) for pacPos in OppoAgentPos]) <= 1:
                Gho_score = -float('inf')
            else:
                Gho_score = 100 * pacDist
        if gameState.isOnRedTeam(self.index[0]):
            return Gho_score + Pac_score + score * 10
        else:
            return Gho_score + Pac_score - score * 10

