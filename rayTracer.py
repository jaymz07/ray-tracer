#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Nov 25 16:15:36 2018

@author: jaymz
"""

import pygame
import numpy as np
import opticalElement
from rayList import Ray, Trace
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
BG_COLOR = ( 30,   30,  30)

PI = np.pi

size = (900, 900)
screen = pygame.display.set_mode(size)

coord_lims_default = np.array([[-2000.0,2000.0],[-2000.0,2000.0]])
coord_lims = coord_lims_default

MAX_BOUNCE = 200

ZOOMFACTOR = 1.3


# Mapping from program coordinates to screen coordinates
def screenMapFunction(pos):
    rangeX = abs(coord_lims[0][0] - coord_lims[0][1])
    rangeY = abs(coord_lims[1][0] - coord_lims[1][1])
    scaleX = float(size[0])/rangeX
    scaleY = float(size[1])/rangeY
    return (int((pos[0]-coord_lims[0][0])/rangeX*size[0]), int((-pos[1]-coord_lims[1][0])/rangeY*size[1]), scaleX, scaleY )

# Screen coordinates to program coordinates
def screenMapInv(posScreen):
    rangeX = abs(coord_lims[0][0] - coord_lims[0][1])
    rangeY = abs(coord_lims[1][0] - coord_lims[1][1])
    scaleX = float(size[0])/rangeX
    scaleY = float(size[1])/rangeY
    return (int((posScreen[0]/size[0]*rangeX+coord_lims[0][0])), int(-posScreen[1]*rangeY/size[1]-coord_lims[1][0]), scaleX, scaleY )

pygame.display.set_caption("Ray Tracer")

# Loop until the user clicks the close button.
done = False

#-------------Optical configuration-----------------------------
# Configuration of mirrors and lenses and stuff
elements = []
elements.append(opticalElement.FlatMirror( [100,710], # Position
                                          -45,        # Angle
                                          100,        # Size
                                          {'color' : BLUE}))
elements.append(opticalElement.Lens([120,270],        # Position
                                    245,              # Angle
                                    [130,40],         # Radius, Thickness
                                    {'color' : BLUE}))


# Initial Rays
traces = []
for theta in np.linspace(-2,2,10):
    ray_i = Ray( np.array([-1000, 710]), \
                np.array([np.cos(np.pi*theta/180), np.sin(np.pi*theta/180)]) )
    traces.append( Trace(ray_i) )

#------------Right Click Menu Functions-----------------------
menuEntries = ['Flat Mirror', 'Curved Mirror', 'Lens']
rightClickMenu = Menu([0,0], menuEntries, rightClick=True,activated=False)

def addFlatMirror():
    x, y, _, _ = screenMapInv(mousePos)
    elements.append(opticalElement.FlatMirror([x,y],45,100,{'color' : BLUE}))

def addCurvedMirror():
    x, y, _, _ = screenMapInv(mousePos)
    elements.append(opticalElement.CurvedMirror([x,y],45,[100,1000],{'color' : BLUE}))

def addLens():
    x, y, _, _ = screenMapInv(mousePos)
    elements.append(opticalElement.Lens([x,y],45,[130,40],{'color' : BLUE}))

rightClickMenu.assignFunction(0,addFlatMirror)
rightClickMenu.assignFunction(1,addCurvedMirror)
rightClickMenu.assignFunction(2,addLens)


# -------- Ray Tracing ---------------
def rayTrace():
    traces_out = []
    for t in traces:
        traces_out.append(copy.deepcopy(t))
    for i in range(MAX_BOUNCE):
        for t in traces_out:
            t.trace_next(elements)
    return traces_out


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
                elements.append(opticalElement.FlatMirror(np.array([x,y]),-45,100,{'color' : BLUE}))
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
            if(event.button == 1):    # Left Click
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

            elif(event.button == 4):  # Wheel
                x, y, scaleX, scaleY = screenMapInv(mousePos)
                coord_lims[0][0] = (coord_lims[0][0] - x) * ZOOMFACTOR + x
                coord_lims[0][1] = (coord_lims[0][1] - x) * ZOOMFACTOR + x
                coord_lims[1][0] = (coord_lims[1][0] + y) * ZOOMFACTOR - y
                coord_lims[1][1] = (coord_lims[1][1] + y) * ZOOMFACTOR - y
            elif(event.button == 5):  # Wheel
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
                #print("Dragging element %d to pos " % mouseSelection_elementIndex + str(newPos))
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
                elif(elements[scaling_elementIndex].elementType() == 'Lens'):
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

    outputTraces = rayTrace()
    lines = []
    for t in outputTraces:
        for l in t.get_lines():
            lines.append(l)
    exitRays = []
    for t in outputTraces:
        for r in t.get_last_rays():
            exitRays.append(r)


    #----------------Drawing code should go here------------

    #Clear screen, fill with background color
    screen.fill(BG_COLOR)

    #Draw the rays
    for l in lines:
        x1, y1, _,_ = screenMapFunction(l[0])
        x2, y2, _,_ = screenMapFunction(l[1])
        try:
            pygame.draw.line(screen, RED, [x1,y1],[x2,y2],1)
        except TypeError:
            print("Invalid ray!")
    for r in exitRays:
        x1, y1, _,_ = screenMapFunction(r.pos)
        x2, y2, _,_ = screenMapFunction(r.pos + r.direc*(np.max(coord_lims)-np.min(coord_lims)))
        try:
            pygame.draw.line(screen, RED, [x1,y1],[x2,y2],1)
        except TypeError:
            print("Invalid ray!")

    #Draw the optical elements
    for i in range(0,len(elements)):
        if(mouseNear_elementIndex is not None and mouseNear_elementIndex == i):
            elements[i].drawSelected(screen,screenMapFunction)
        else:
            elements[i].draw(screen,screenMapFunction)

    rightClickMenu.draw(screen)
    #Go ahead and update the screen with what we've drawn.
    pygame.display.flip()

    #Limit to 60 frames per second
    clock.tick(60)

#Exit thread after loop has been exited
pygame.quit()
