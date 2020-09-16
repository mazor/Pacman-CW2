# mdpAgents.py
# parsons/20-nov-2017
#
# Version 1
#
# The starting point for CW2.
#
# Intended to work with the PacMan AI projects from:
#
# http://ai.berkeley.edu/
#
# These use a simple API that allow us to control Pacman's interaction with
# the environment adding a layer on top of the AI Berkeley code.
#
# As required by the licensing agreement for the PacMan AI we have:
#
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

# The agent here is was written by Simon Parsons, based on the code in
# pacmanAgents.py

from pacman import Directions
from game import Agent
import api
import random
import game
import util

# Disclaimer: This is code that Professor Simon Parsons wrote
#(code segment from Professor Simon Parsons starts)
#
# A class that creates a grid that can be used as a map
#
# The map itself is implemented as a nested list, and the interface
# allows it to be accessed by specifying x, y locations.
class Grid:
         
    # Constructor
    #
    # Note that it creates variables:
    #
    # grid:   an array that has one position for each element in the grid.
    # width:  the width of the grid
    # height: the height of the grid
    #
    # Grid elements are not restricted, so you can place whatever you
    # like at each location. You just have to be careful how you
    # handle the elements when you use them.
    def __init__(self, width, height):
        self.width = width
        self.height = height
        subgrid = []
        for i in range(self.height):
            row=[]
            for j in range(self.width):
                row.append(0)
            subgrid.append(row)

        self.grid = subgrid

    # Print the grid out.
    def display(self):       
        for i in range(self.height):
            for j in range(self.width):
                # print grid elements with no newline
                print self.grid[i][j],
            # A new line after each line of the grid
            print 
        # A line after the grid
        print

    # The display function prints the grid out upside down. This
    # prints the grid out so that it matches the view we see when we
    # look at Pacman.
    def prettyDisplay(self):       
        for i in range(self.height):
            for j in range(self.width):
                # print grid elements with no newline
                print self.grid[self.height - (i + 1)][j],
            # A new line after each line of the grid
            print 
        # A line after the grid
        print
        
    # Set and get the values of specific elements in the grid.
    # Here x and y are indices.
    def setValue(self, x, y, value):
        self.grid[y][x] = value

    def getValue(self, x, y):
        return self.grid[y][x]

    # Return width and height to support functions that manipulate the
    # values stored in the grid.
    def getHeight(self):
        return self.height

    def getWidth(self):
        return self.width

#(code segment from Professor Simon Parsons ends)

class MDPAgent(Agent):

    def __init__(self):
        name = "Pacman"

    # Gets run after an MDPAgent object is created and once there is
    # game state to access.
    def registerInitialState(self, state):
        # Make maps of the right size
        self.makeMaps(state)
        
        #add walls, set rewards and update utilities
        self.addWallsToMap(state)
        self.updateFoodInMaps(state)
        self.updateGhostsInMaps(state)
        self.updateUtilities(state)
        
    # This is what gets run in between multiple games
    def final(self, state):
       name = "Pacman"
      
    # Make two maps by creating a grid of the right size. Modified from code taken from Professor Simon Parsons 
    def makeMaps(self,state):
        corners = api.corners(state)
        height = self.getLayoutHeight(corners)
        width = self.getLayoutWidth(corners)
        self.map = Grid(width, height) #map to hold utilities
        self.rewardsMap = Grid(width, height) #map to hold rewards

    # Functions to get the height and the width of the grid.
    #
    # We add one to the value returned by corners to switch from the
    # index (returned by corners) to the size of the grid (that damn
    # "start counting at zero" thing again).
    # Disclaimer: This is code that Professor Simon Parsons wrote
    #(code segment from Professor Simon Parsons starts)
    def getLayoutHeight(self, corners):
        height = -1
        for i in range(len(corners)):
            if corners[i][1] > height:
                height = corners[i][1]
        return height + 1

    def getLayoutWidth(self, corners):
        width = -1
        for i in range(len(corners)):
            if corners[i][0] > width:
                width = corners[i][0]
        return width + 1

    # Functions to manipulate the map.
    #
    # Put every element in the list of wall elements into the map
    def addWallsToMap(self, state):
        walls = api.walls(state)
        for i in range(len(walls)):
            self.map.setValue(walls[i][0], walls[i][1], '%')
    #(code segment from Professor Simon Parsons ends)
    
    # Update the maps with the food that exists.
    # Code in this unrelated to setting rewards is modified from code Professor Simon Parsons supplied
    def updateFoodInMaps(self, state):
        # Make all grid elements that aren't walls blank.
        for i in range(self.map.getWidth()):
            for j in range(self.map.getHeight()):
                if self.map.getValue(i, j) != '%':
                    self.map.setValue(i, j, 0) #initialise utilities to 0
                    self.rewardsMap.setValue(i, j, -1)  #initialise rewards to -1, the score you get when moving in this pacman
        
        food = api.food(state)
        for i in range(len(food)):
            self.rewardsMap.setValue(food[i][0], food[i][1], 10)#set rewards of food to 10, as it is worth more than a blank space

    #Add the positions of the ghosts to the maps
    def updateGhostsInMaps(self, state):
        ghosts = api.ghostStatesWithTimes(state) #Get the positions of the ghosts, along with the time they are safe to eat for
        
        #for every ghost, check how long it is safe for and update reward accordingly
        for i in range(len(ghosts)):
	  
	  currentGhostLoc = ghosts[i][0] #the position of the ghost
	  ghostX = int(currentGhostLoc[0]) #the ghost's x coordinate
	  ghostY = int(currentGhostLoc[1]) #the ghost's y coordinate
	  timeSafe = ghosts[i][1] #how long the ghost will be safe to eat for the pacman
	  
	  if (timeSafe == 0):  #if the time left is 0 it means the ghost can attack the pacman
	    
            self.map.setValue(ghostX, ghostY, -1000) #a bad terminal state, so utility is made to be really low (-1000)
            self.rewardsMap.setValue(ghostX, ghostY, -1000) #location of the ghost which is extremely bad so reward is made to be extremely low
            self.rewardsMap.setValue(ghostX, ghostY-1, -500) #quite near to the ghost which is very bad so reward is made to be very low
            self.rewardsMap.setValue(ghostX+1, ghostY, -500) #quite near to the ghost which is very bad so reward is made to be very low
            self.rewardsMap.setValue(ghostX, ghostY+1, -500) #quite near to the ghost which is very bad so reward is made to be very low
            self.rewardsMap.setValue(ghostX-1, ghostY, -500) #quite near to the ghost which is very bad so reward is made to be very low

	  elif (timeSafe<5): #if there is still time left for the ghost to be safe but it is under 5 time units, then
	     self.rewardsMap.setValue(ghostX, ghostY, 1) #it is good to catch it but not better than food since there is a risk it will become a bad ghost
	     #so reward is made bigger than a blank space (or an unsafe ghost) but still made much lower than food
	  else: #if there is still time left for the ghost to be safe and it is larger than 5 time units, then
	     self.rewardsMap.setValue(ghostX, ghostY, 9) #it is good to catch it but not better than food since there is a risk it will become a bad ghost
	     #so reward is made bigger than a blank space (or an unsafe ghost) but still made a little lower than food, as food is still a priority
	     
    #Update the utilities in the utilities map based on value iteration and the Bellman equation
    def updateUtilities(self,state):
      
	  tempMap = self.map # used to make sure all changes to utilities are done 'simultaneously'
	  width = self.map.getWidth()
	  height = self.map.getHeight()
	  
	  for p in range(25): #iterate through this 25 times 

	    for pacmanX in range(width):

	      for pacmanY in range(height):
		
		if self.map.getValue(pacmanX,pacmanY) != '%':# '%' indicates a wall. You do not update utilities of walls
		    current = self.map.getValue(pacmanX,pacmanY) #current utility of the current place being looked at -NOT the current position of the pacman
		    north = self.map.getValue(pacmanX,pacmanY+1) #utility of the north of current
		    east = self.map.getValue(pacmanX+1,pacmanY) #utility of the east of current 
		    south = self.map.getValue(pacmanX,pacmanY-1) #utility of the south of current 
		    west = self.map.getValue(pacmanX-1,pacmanY) #utility of the west of current 

		    gamma = 1 #the letter gamma in the Bellman equation is not compilable so it is written out for the sake of the variable name
		  
		    #up, down, left and right are the expected utilities for moving in that direction
		    #Initially set to 0 because they will be incremented in the if statements below
		    up = 0 #For the sake of this, trying to go up == trying to go north
		    down = 0 #For the sake of this, trying to go down == trying to go south
		    left = 0 #For the sake of this, trying to go left == trying to go west
		    right = 0 #For the sake of this, trying to go right == trying to go east
		    rs = self.rewardsMap.getValue(pacmanX,pacmanY) #R(S) in the Bellman equation - the reward of the state
		    
		    #If the east utility is equal to '%' it means there is a wall there and so the move is not valid so the pacman will stay in its current location
		    if (east == "%"): 
		      up = up+0.1*current #trying to go up has a 0.1 probability of trying to go east
		      down = down+0.1*current #trying to go down has a 0.1 probability of trying to go east
		      right = right+0.8*current #trying to go right has a 0.8 probability of trying to go east
		    else: #east is valid
		      up = up+0.1*east #trying to go up has a 0.1 probability of trying to go east
		      down = down+0.1*east #trying to go down has a 0.1 probability of trying to go east
		      right = right+0.8*east #trying to go right has a 0.1 probability of trying to go east

		    #If the west utility is equal to '%' it means there is a wall there and so the move is not valid so the pacman will stay in its current location
		    if (west == "%"): 
		      up = up+0.1*current #trying to go up has a 0.1 probability of trying to go west
		      down = down+0.1*current #trying to go down has a 0.1 probability of trying to go west
		      left = left+0.8*current #trying to go left has a 0.8 probability of trying to go west
		    else: #west is valid
		      up = up+0.1*west #trying to go up has a 0.1 probability of trying to go west
		      down = down+0.1*west #trying to go down has a 0.1 probability of trying to go west
		      left = left+0.8*west #trying to go left has a 0.8 probability of trying to go west
		    
		    #If the north utility is equal to '%' it means there is a wall there and so the move is not valid so the pacman will stay in its current location
		    if (north == "%"): 
		      up = up+0.8*current #trying to go up has a 0.8 probability of trying to go north
		      left = left+0.1*current #trying to go left has a 0.1 probability of trying to go north
		      right = right+0.1*current #trying to go right has a 0.1 probability of trying to go north
		    else: #north is valid
		      up = up+0.8*north #trying to go up has a 0.8 probability of trying to go north
		      left = left+0.1*north #trying to go left has a 0.1 probability of trying to go north
		      right = right+0.1*north #trying to go right has a 0.1 probability of trying to go north
		    
		    #If the south utility is equal to '%' it means there is a wall there and so the move is not valid so the pacman will stay in its current location
		    if (south == "%"): 
		      down = down+0.8*current  #trying to go down has a 0.8 probability of trying to go south
		      left = left+0.1*current  #trying to go left has a 0.1 probability of trying to go south
		      right = right+0.1*current #trying to go right has a 0.1 probability of trying to go south
		    else: #south is valid
		      down = down+0.8*south #trying to go down has a 0.8 probability of trying to go south
		      left = left+0.1*south #trying to go left has a 0.1 probability of trying to go south
		      right = right+0.1*south #trying to go right has a 0.1 probability of trying to go south

		    maxValue = max(up,left,down,right) #getting the max utility of the four possible moves attempted

		    newUtility = rs+ (gamma * maxValue) #using the Bellman utility to calculate the updated utility
		    
		    tempMap.setValue(pacmanX,pacmanY, newUtility) 
		    #all done 'simultaneously' so actual map should only be changed once an iteration is done
	    self.map = tempMap 


    #Method used to choose what move the pacman will make
    def getAction(self, state):
	  
	  legal = api.legalActions(state)
	  if Directions.STOP in legal:
              legal.remove(Directions.STOP)
	  self.updateFoodInMaps(state)
	  self.updateGhostsInMaps(state)
	  self.updateUtilities(state)
       
	  currentLoc = api.whereAmI(state) #get the current position of pacman
	  pacmanX = currentLoc[0] #x coordinate of the pacman
	  pacmanY = currentLoc[1] #y coordinate of the pacman
	  
	  #get the utilities of the nearby locations
	  north = self.map.getValue(pacmanX,pacmanY+1)
	  east = self.map.getValue(pacmanX+1,pacmanY)
	  south = self.map.getValue(pacmanX,pacmanY-1)
	  west = self.map.getValue(pacmanX-1,pacmanY)
	  
	  #an array of all possible utilities to attempt to move to
	  possible = [north, east, south, west]
	  
	  #utility should not be in the array if the place the utility belongs to is a wall
	  if (north == "%"):
	    possible.remove(north)
	  
	  if (east == "%"):
	    possible.remove(east)
	  
	  if (south == "%"):
	    possible.remove(south)
	  
	  if (west == "%"):
	    possible.remove(west)
	 
	  maxValue=max(possible) #the max utility that can be reached legally

	  #Attempt to go in the direction of the max utility
	  if (south == maxValue):
	    if Directions.SOUTH in legal:
		return api.makeMove(Directions.SOUTH, legal)
	      
	  if (west == maxValue):
	    if Directions.WEST in legal: 
		return api.makeMove(Directions.WEST, legal)
	  
	  if (north == maxValue):
	    if Directions.NORTH in legal: 
		return api.makeMove(Directions.NORTH, legal)
	  
	  if (east == maxValue):
	    if Directions.EAST in legal: 
		return api.makeMove(Directions.EAST, legal) 

	  if (len(legal) == 0): #if there are no legal methods left re-add the stop move to legal
	    legal.append(Directions.STOP)
	  
          return api.makeMove(random.choice(legal), legal) #if all else (everything above) fails just make a random move
