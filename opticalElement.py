#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Nov 25 16:35:33 2018

@author: jaymz
"""

from abc import ABC, abstractmethod
import pygame
import numpy as np

# Define some colors
BLACK    = (   0,   0,   0)
WHITE    = ( 255, 255, 255)
GREEN    = (   0, 255,   0)
RED      = ( 255,   0,   0)
BLUE     = (   0,   0, 255)

class OpticalElement(ABC):
    
    def __init__(self, pos, orientation, boundaries, properties):
        self.pos = np.array(pos)
        self.orientation = orientation
        self.boundaries = boundaries
        self.properties = properties
        super().__init__()
        
    @abstractmethod
    def reflect(self,ray_pos, ray_dir):
        pass
    
    @abstractmethod
    def rayIntersection(self,ray_pos,ray_dir):
        pass
        
    @abstractmethod
    def draw(self,screen,screenPosFunc):
        pass
    
    @abstractmethod
    def drawSelected(self,screen,screenPosFunc):
        pass
    
    @abstractmethod
    def checkBoundaries(self,pos):
        pass
    
    def checkIfMouseNear(self,pos, screenPosFunc):
        x, y, _, _ = screenPosFunc(self.pos)
        return np.linalg.norm(pos - np.array([x,y])) < 20
    
    
    
    
    
class FlatMirror(OpticalElement): 
      
    def rayIntersection(self, ray_pos, ray_dir):
        #super.rayIntersection(ray_pos,ray_dir)
        oVect = [np.cos(self.orientation*np.pi/180), np.sin(self.orientation*np.pi/180)]
        det = ray_dir[0]*oVect[1] - ray_dir[1]*oVect[0]
        if(det == 0):
            return None
        delta = self.pos - np.array(ray_pos)
        tval = (oVect[1]*delta[0] - oVect[0]*delta[1])/det
        if(tval < 0):
            return None
        return ray_pos+ray_dir*tval
    
    def reflect(self, ray_pos, ray_dir):
        #super.reflect()
        vperp = np.array([-np.sin(np.pi*self.orientation/180), np.cos(np.pi*self.orientation/180)])
        vin = np.array(ray_dir)
        return vin - 2*np.dot(ray_dir,vperp)*vperp
    
    def checkBoundaries(self, pos):
        #super.checkBoundaries()
        p = np.array(pos)
        if(np.linalg.norm(p-self.pos) < self.boundaries):
            return True
        return False

    def draw(self,screen,screenPosFunc):
        #super.draw(None,None)
        color = BLUE
        screenX, screenY, scaleX, scaleY = screenPosFunc(self.pos)
        angleRad = self.orientation*np.pi/180
        if(isinstance(self.properties, dict)):
            color = self.properties['color']
        x1, y1 = self.boundaries*np.cos(angleRad)*scaleX + screenX, -self.boundaries*np.sin(angleRad)*scaleY + screenY
        x2, y2 = -self.boundaries*np.cos(angleRad)*scaleX + screenX, self.boundaries*np.sin(angleRad)*scaleY + screenY
        pygame.draw.line(screen, color, [x1,y1],[x2,y2],10)
        return
    
    def drawSelected(self, screen, screenPosFunc):
        color = BLUE
        screenX, screenY, scaleX, scaleY = screenPosFunc(self.pos)
        angleRad = self.orientation*np.pi/180
        if(isinstance(self.properties, dict)):
            color = self.properties['color']
        x1, y1 = self.boundaries*np.cos(angleRad)*scaleX + screenX, -self.boundaries*np.sin(angleRad)*scaleY + screenY
        x2, y2 = -self.boundaries*np.cos(angleRad)*scaleX + screenX, self.boundaries*np.sin(angleRad)*scaleY + screenY
        pygame.draw.line(screen, color, [x1,y1],[x2,y2],10)
        pygame.draw.circle(screen, color, [screenX, screenY], int(max(scaleX, scaleY)*25),0)
        return
    