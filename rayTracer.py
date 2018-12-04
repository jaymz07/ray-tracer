#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Nov 25 16:15:36 2018

@author: jaymz
"""

import pygame
import numpy as np
import opticalElement
import copy

from menu import Menu

pygame.init()

# Used to manage how fast the screen updates
clock = pygame.time.Clock()

# Define some colors
BLACK    = (   0,   0,   0)
WHITE    = ( 255, 255, 255)
GREEN    = (   0, 255,   0)
RED      = ( 255,   0,   0)
BLUE     = (   0,   0, 255)

PI = np.pi

size = (700, 700)
screen = pygame.display.set_mode(size)

coord_lims_default = np.array([[-1000.0,1000.0],[-1000.0,1000.0]])
coord_lims = coord_lims_default

MAX_BOUNCE = 100

ZOOMFACTOR = 1.3

def screenMapFunction(pos):
    rangeX = abs(coord_lims[0][0] - coord_lims[0][1])
    rangeY = abs(coord_lims[1][0] - coord_lims[1][1])
    scaleX = float(size[0])/rangeX
    scaleY = float(size[1])/rangeY
    return (int((pos[0]-coord_lims[0][0])/rangeX*size[0]), int((-pos[1]-coord_lims[1][0])/rangeY*size[1]), scaleX, scaleY )

def screenMapInv(posScreen):
    rangeX = abs(coord_lims[0][0] - coord_lims[0][1])
    rangeY = abs(coord_lims[1][0] - coord_lims[1][1])
    scaleX = float(size[0])/rangeX
    scaleY = float(size[1])/rangeY
    return (int((posScreen[0]/size[0]*rangeX+coord_lims[0][0])), int(-posScreen[1]*rangeY/size[1]-coord_lims[1][0]), scaleX, scaleY )

pygame.display.set_caption("Ray Tracer")

# Loop until the user clicks the close button.
done = False

elements = []
rays = []
 
#-------------Optical configuration-----------------------------

##>>>>>Retroreflector array----------
#sep = 200
#L = sep * np.sqrt(2)/2
#for i in range(0,7):
#    elements.append(opticalElement.FlatMirror([500,700-sep*i],-(1-2*(i%2))*45,L,{'color' : BLACK}))
#    elements.append(opticalElement.FlatMirror([-500,700-sep*i-sep],(1-2*(i%2))*45,L,{'color' : BLACK}))
#    
#disp = 10
#elements.append(opticalElement.FlatMirror([500+disp,-700],45,L,{'color' : BLUE}))
#elements.append(opticalElement.FlatMirror([500+disp,-700],-45,L,{'color' : BLUE}))
#
#theta = 0; rays.append({'pos' : np.array([-1000,710]), 'dir' : np.array([np.cos(np.pi*theta/180),np.sin(np.pi*theta/180)]), 'color' : RED})
#theta = 0.2; rays.append({'pos' : np.array([-1000,710]), 'dir' : np.array([np.cos(np.pi*theta/180),np.sin(np.pi*theta/180)]), 'color' : GREEN})
#theta = -0.2; rays.append({'pos' : np.array([-1000,710]), 'dir' : np.array([np.cos(np.pi*theta/180),np.sin(np.pi*theta/180)]), 'color' : BLUE})

#>>>>Vernier slicer---------
#N = 24
#count = 0
#for theta in np.linspace(-5,3,N):
#    rays.append({'pos' : np.array([-1000,690]), 'dir' : np.array([np.cos(np.pi*theta/180),np.sin(np.pi*theta/180)]), 'color' : [int(255*count/N),0,255-int(255*count/N)]})
#    count += 1
#
#elements.append(opticalElement.FlatMirror([100,775],-43.5,100,{'color' : BLACK}))
#elements.append(opticalElement.FlatMirror([420,720],-44.8,100,{'color' : BLACK}))
#elements.append(opticalElement.FlatMirror([740,640],-46.0,100,{'color' : BLACK}))

#>>>>>Import saved configuration--------
import pickle
elements = pickle.load(open('cateyeDelayStage.pkl','rb'))

theta = 0; rays.append({'pos' : np.array([-1000,710]), 'dir' : np.array([np.cos(np.pi*theta/180),np.sin(np.pi*theta/180)]), 'color' : RED})
theta = 0.2; rays.append({'pos' : np.array([-1000,710]), 'dir' : np.array([np.cos(np.pi*theta/180),np.sin(np.pi*theta/180)]), 'color' : GREEN})
theta = -0.2; rays.append({'pos' : np.array([-1000,710]), 'dir' : np.array([np.cos(np.pi*theta/180),np.sin(np.pi*theta/180)]), 'color' : BLUE})

#------------Right Click Menu Functions-----------------------

menuEntries = ['Flat Mirror', 'Curved Mirror']
rightClickMenu = Menu([0,0], menuEntries, rightClick=True,activated=False)

def addFlatMirror():
    x, y, _, _ = screenMapInv(mousePos)
    elements.append(opticalElement.FlatMirror([x,y],45,100,{'color' : BLACK}))
    
def addCurvedMirror():
    x, y, _, _ = screenMapInv(mousePos)
    elements.append(opticalElement.CurvedMirror([x,y],45,[100,1000],{'color' : BLACK}))
    
rightClickMenu.assignFunction(0,addFlatMirror)
rightClickMenu.assignFunction(1,addCurvedMirror)


# -------- Ray Tracing ---------------

def rayTrace():
    outputRays = [rays]

    for i in range(0,MAX_BOUNCE):
        newRays = []
        #print("i = %d" % i)
        for r in outputRays[-1]:
            minDist = np.inf
            closestElem = None
            closestIntersect = None
            for elem in elements:
                intersect = elem.rayIntersection(r['pos'], r['dir'])
                #print(intersect)
                if(intersect is None):
                    continue
                dist = np.linalg.norm(intersect-r['pos'])
                if(dist < .0001):
                    continue
#                if(closestElem is not None and elem == closestElem):
#                    continue
                if(minDist > dist):
                    minDist = dist
                    closestElem = elem
                    closestIntersect = intersect
            if(closestElem is not None):    
                dir_new = closestElem.reflect(r['pos'],r['dir'],closestIntersect)
                dir_new = dir_new / np.linalg.norm(dir_new)
                r['intersect'] = closestIntersect
                if('color' in r):
                    newRays.append({'pos' : closestIntersect, 'dir' : dir_new, 'color' : r['color']})
                else:
                    newRays.append({'pos' : closestIntersect, 'dir' : dir_new, 'color' : r['color']})
            else:
                r['intersect'] = None
        if(len(newRays) != 0):
            outputRays.append(newRays)
    return outputRays

                
    
# -------- Main program loop---------------
    
#Keep track of mouse manipulations
mouseSelection_elementIndex = None
mouseNear_elementIndex = None

rotating_elementIndex = None
scaling_elementIndex = None

viewDrag_mouseStart = None
viewDrag_cstart = None
    
while not done:
    
    for event in pygame.event.get():                    #Handle events
        rightClickMenu.processMouseInput(event)
        if event.type == pygame.QUIT:
            print("User asked to quit.")
            
    #--------Keyboard Events---------------
        elif event.type == pygame.KEYDOWN:
            print(event)
            x, y, _, _ = screenMapInv(mousePos)
            if(event.unicode == 'n'):
                elements.append(opticalElement.FlatMirror(np.array([x,y]),-45,100,{'color' : BLACK}))
            elif event.unicode == '\x08': #Backspace
                if(len(elements) > 0):
                    del elements[-1]
            elif event.unicode == 'r':    #Rotate
                rotating_elementIndex = mouseNear_elementIndex
            elif event.unicode == 's':    #Scale
                scaling_elementIndex = mouseNear_elementIndex
            elif event.unicode == '0':   #Reset View
                coord_lims = coord_lims_default
            elif event.unicode == 'd':
                if(mouseNear_elementIndex is not None):
                    del elements[mouseNear_elementIndex]
                    mouseNear_elementIndex = None
            elif event.key == 282:
                coord_lims = np.array(coord_lims) * 2
            elif event.key == 283:
                coord_lims = np.array(coord_lims) / 2
            elif event.key == 276:  #Left Arrow
                coord_lims = np.array(coord_lims) - (coord_lims[0][1]-coord_lims[0][0])/10*np.array([[1.0,1.0],[0.0,0.0]])
            elif event.key == 275:  #Right Arrow
                coord_lims = np.array(coord_lims) + (coord_lims[0][1]-coord_lims[0][0])/10*np.array([[1.0,1.0],[0.0,0.0]])
            elif event.key == 273:  #Up Arrow
                coord_lims = np.array(coord_lims) - (coord_lims[1][1]-coord_lims[1][0])/10*np.array([[0.0,0.0],[1.0,1.0]])
            elif event.key == 274:  #Down Arrow
                coord_lims = np.array(coord_lims) + (coord_lims[1][1]-coord_lims[1][0])/10*np.array([[0.0,0.0],[1.0,1.0]])
        elif event.type == pygame.KEYUP:
            print("User let go of a key.")
            
    #-------Mouse Events--------
        elif event.type == pygame.MOUSEBUTTONDOWN:     #Mouse click events
            print(event)
            mousePos = np.array(pygame.mouse.get_pos())
            if(event.button == 1):
                for i in range(0,len(elements)):
                    if(elements[i].checkIfMouseNear(mousePos, screenMapFunction)):
                        print("Grabbed element %d" % i)
                        mouseSelection_elementIndex = i
                if(mouseSelection_elementIndex is None):
                    x, y, scaleX, scaleY = screenMapInv(mousePos)
                    viewDrag_mouseStart = np.array([x,y])
                    viewDrag_cstart = copy.deepcopy(coord_lims)
            elif(event.button == 3):
                continue
                
            elif(event.button == 4):
                x, y, scaleX, scaleY = screenMapInv(mousePos)
                coord_lims[0][0] = (coord_lims[0][0] - x) * ZOOMFACTOR + x
                coord_lims[0][1] = (coord_lims[0][1] - x) * ZOOMFACTOR + x
                coord_lims[1][0] = (coord_lims[1][0] + y) * ZOOMFACTOR - y
                coord_lims[1][1] = (coord_lims[1][1] + y) * ZOOMFACTOR - y
            elif(event.button == 5):
                x, y, scaleX, scaleY = screenMapInv(mousePos)
                coord_lims[0][0] = (coord_lims[0][0] - x) / ZOOMFACTOR + x
                coord_lims[0][1] = (coord_lims[0][1] - x) / ZOOMFACTOR + x
                coord_lims[1][0] = (coord_lims[1][0] + y) / ZOOMFACTOR - y
                coord_lims[1][1] = (coord_lims[1][1] + y) / ZOOMFACTOR - y
            rotating_elementIndex = None
            scaling_elementIndex = None
        
        elif event.type == pygame.MOUSEMOTION:          #Mouse movement events
            mousePos = np.array(pygame.mouse.get_pos())
            #print(mousePos)
            #print(mouseSelection_elementIndex)
            x, y, scaleX, scaleY = screenMapInv(mousePos)
            if(mouseSelection_elementIndex is not None):
                newPos = np.array([x,y])
                print("Dragging element %d to pos " % mouseSelection_elementIndex + str(newPos))
                elements[mouseSelection_elementIndex].pos = newPos
            elif(rotating_elementIndex is not None):
                relVect = np.array([x,y]) - elements[rotating_elementIndex].pos
                newAngle = np.arctan2(relVect[1],relVect[0])
                elements[rotating_elementIndex].setOrientation(180*newAngle/np.pi)
            elif(scaling_elementIndex is not None):
                relVect = np.array([x,y]) - elements[scaling_elementIndex].pos
                newScale = np.linalg.norm([relVect[1],relVect[0]])
                if(elements[scaling_elementIndex].elementType() == 'FlatMirror'):
                    elements[scaling_elementIndex].boundaries = newScale
                elif(elements[scaling_elementIndex].elementType() == 'CurvedMirror'):
                    elements[scaling_elementIndex].boundaries[0] = newScale
                    
            elif(viewDrag_mouseStart is not None):
                dragVect = np.array([x,y]) - viewDrag_mouseStart
                coord_lims = viewDrag_cstart + np.array([[-dragVect[0]]*2,[dragVect[1]]*2])/1.2
                
            else:
                mouseNear_elementIndex = None
                for i in range(0,len(elements)):
                    mousePos = np.array(pygame.mouse.get_pos())
                    if(elements[i].checkIfMouseNear(mousePos, screenMapFunction)):
                        mouseNear_elementIndex = i
                
        elif event.type == pygame.MOUSEBUTTONUP:        #Mouse release event
            mousePos = np.array(pygame.mouse.get_pos())
            print(mousePos)
            print(mouseSelection_elementIndex)
            if(mouseSelection_elementIndex is not None):
                x, y, _, _ = screenMapInv(mousePos)
                print("Moved element %d from " % mouseSelection_elementIndex + str(elements[mouseSelection_elementIndex].pos) + " to pos " + str(mousePos))
                elements[mouseSelection_elementIndex].pos = np.array([x,y])
            mouseSelection_elementIndex = None
            viewDrag_mouseStart = None
        
                                                        #Handle window close
        if event.type == pygame.QUIT: # If user clicked close
            done = True # Flag that we are done so we exit this loop
 
    outputRays = rayTrace()
    
    #----------------Drawing code should go here------------
    
    #Clear screen
    screen.fill(WHITE)
    
    #Draw the optical elements
    for i in range(0,len(elements)):
        if(mouseNear_elementIndex is not None and mouseNear_elementIndex == i):
            elements[i].drawSelected(screen,screenMapFunction)
        else:
            elements[i].draw(screen,screenMapFunction)
    
    #Draw the rays
    for i in range(0,len(outputRays)):
        for j in range(0,len(outputRays[i])):
            x1, y1, _,_ = screenMapFunction(outputRays[i][j]['pos'])
            if('intersect' in outputRays[i][j] and outputRays[i][j]['intersect'] is not None):
                x2, y2, _,_ = screenMapFunction(outputRays[i][j]['intersect'])
            else:
                x2, y2, _,_ = screenMapFunction(outputRays[i][j]['pos'] + outputRays[i][j]['dir']*(np.max(coord_lims)-np.min(coord_lims)))
            if('color' in outputRays[i][j]):
                pygame.draw.line(screen, outputRays[i][j]['color'], [x1,y1],[x2,y2],2)
            else:
                pygame.draw.line(screen, RED, [x1,y1],[x2,y2],2)
 
    rightClickMenu.draw(screen)
    #Go ahead and update the screen with what we've drawn.
    pygame.display.flip()
 
    #Limit to 60 frames per second
    clock.tick(60)

#Exit thread after loop has been exited
pygame.quit()