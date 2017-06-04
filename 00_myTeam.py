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

def createTeam(indexes, num, isRed, names=['DummyAgent','DummyAgent']):
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

