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
        self.orientation = orientation  #Angle in degrees
        self.boundaries = boundaries    #Size properties
        self.properties = properties    #Focal length, etc

        self.last_element = None        #Last element that we bounced off of
        
        super().__init__()
        
    @abstractmethod
    def reflect(self,ray_pos, ray_dir, intersect):
        pass

    @abstractmethod
    def refract(self, ray_pos, ray_dir, intersect):
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
    
    @abstractmethod
    def setOrientation(self, angleDeg):
        pass
    
    @abstractmethod
    def elementType(self):
        pass
    
    def checkIfMouseNear(self,pos, screenPosFunc):
        x, y, _, _ = screenPosFunc(self.pos)
        return np.linalg.norm(pos - np.array([x,y])) < 20

    #def __eq__(self, other):
        #poseq = (self.pos[0] == other.pos[0]) and (self.pos[1] == other.pos[1])
        #oreq  = self.orientation == other.orientation
        #boundeq = True
        #for i,b in enumerate(self.boundaries):
            #boundeq = boundeq and (b == other.boundaries[i])
        #return poseq and oreq and boundeq
    
    
    
    
    
class FlatMirror(OpticalElement): 
    #self.boundaries = Length of mirror
    #self.orientation = angle of rotation
    
    def elementType(self):
        return 'FlatMirror'
        
    #Vector behavior      
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
        intersect = ray_pos+ray_dir*tval
        if(self.checkBoundaries(intersect)):
            return intersect
        return None
    
    def reflect(self, ray_pos, ray_dir, intersect):
        #super.reflect()
        vperp = np.array([-np.sin(np.pi*self.orientation/180), np.cos(np.pi*self.orientation/180)])
        vin = np.array(ray_dir)
        return vin - 2*np.dot(ray_dir,vperp)*vperp

    def refract(self):
        pass
    
    def checkBoundaries(self, pos):
        #super.checkBoundaries()
        p = np.array(pos)
        if(np.linalg.norm(p-self.pos) < self.boundaries):
            return True
        return False
    
    def setOrientation(self, angleDeg):
        self.orientation = angleDeg

    #Graphical Representation
    def draw(self,screen,screenPosFunc):
        #super.draw(None,None)
        color = BLUE
        screenX, screenY, scaleX, scaleY = screenPosFunc(self.pos)
        angleRad = self.orientation*np.pi/180
        if(isinstance(self.properties, dict)):
            color = self.properties['color']
        x1, y1 = self.boundaries*np.cos(angleRad)*scaleX + screenX, -self.boundaries*np.sin(angleRad)*scaleY + screenY
        x2, y2 = -self.boundaries*np.cos(angleRad)*scaleX + screenX, self.boundaries*np.sin(angleRad)*scaleY + screenY
        pygame.draw.line(screen, color, [x1,y1],[x2,y2],7)
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
        pygame.draw.circle(screen, color, [screenX, screenY], 10,0)
        return
    
class CurvedMirror(OpticalElement):

    def elementType(self):
        return 'CurvedMirror'
        
    #self.boundaries = [angularSize, radius]
    #self.orientation = direction
    
    def getCenterPoint(self):
        angleCent = self.orientation*np.pi/180
        return np.array([self.pos[0] - self.boundaries[1] * np.cos(angleCent), self.pos[1] - self.boundaries[1] * np.sin(angleCent)])
    
    def rayIntersection(self, ray_pos, ray_dir):
        center = self.getCenterPoint()
        rx, ry, vx, vy, R = ray_pos[0] - center[0], ray_pos[1] - center[1], ray_dir[0], ray_dir[1], self.boundaries[1]
        angExtent = np.arctan(self.boundaries[0]/R)*180/np.pi
        if((2*rx*vx + 2*ry*vy)**2 - 4*(-R**2 + rx**2 + ry**2)*(vx**2 + vy**2) < 0):
            return None
        tval1 = (-2*rx*vx - 2*ry*vy - np.sqrt((2*rx*vx + 2*ry*vy)**2 - 4*(-R**2 + rx**2 + ry**2)*(vx**2 + vy**2)))/(2*(vx**2 + vy**2))
        tval2 = (-2*rx*vx - 2*ry*vy + np.sqrt((2*rx*vx + 2*ry*vy)**2 - 4*(-R**2 + rx**2 + ry**2)*(vx**2 + vy**2)))/(2*(vx**2 + vy**2))
        
        intersect1 = np.array(ray_pos) + tval1*ray_dir
        intersect2 = np.array(ray_pos) + tval2*ray_dir
        
        angle1 = np.arctan2(intersect1[1]-center[1],intersect1[0]-center[0])*180/np.pi%360
        angle2 = np.arctan2(intersect2[1]-center[1],intersect2[0]-center[0])*180/np.pi%360
        
        b1, b2 = (self.orientation - angExtent)%360, (self.orientation + angExtent)%360
                
        if(self.angleBetween(angle1, b1, b2)):
            if(self.angleBetween(angle2, b1, b2)):
                dist1=np.linalg.norm(ray_pos - intersect1)
                dist2=np.linalg.norm(ray_pos - intersect2)
                if(dist1 < dist2):
                    return intersect1
                return intersect2
            else:
                return intersect1
        
        elif(self.angleBetween(angle2, b1, b2)):
                return intersect2
        else:
            return None
        
    def reflect(self, ray_pos, ray_dir, intersect):
        center = self.getCenterPoint()
        vperp = np.array([intersect[0] - center[0], intersect[1] - center[1]])
        vperp = vperp/np.linalg.norm(vperp)
        vin = np.array(ray_dir)
        return vin - 2*np.dot(ray_dir,vperp)*vperp

    def refract(self):
        pass
    
    def checkBoundaries(self,pos):
        return False
    
    def angleBetween(self, angle, b1, b2):
        diff1, diff2 = abs(angle%360 - b1%360), abs(angle%360 - b2%360)
        width = abs(b1-b2)
        if(width > 180):
            width = 360-width
        if(diff1 > 180):
            diff1 = 360-diff1
        if(diff2 > 180):
            diff2 = 360-diff2
        return (diff1 < width) and (diff2 < width)
    
    def setOrientation(self,angleDeg):
        self.orientation = angleDeg%360
        
    def draw(self, screen, screenPosFunction):
        center = self.getCenterPoint()
        screenX, screenY, scaleX, scaleY = screenPosFunction(center)
        R = self.boundaries[1]
        angExtent = np.arctan(self.boundaries[0]/R)*180/np.pi
        color = BLUE
        if(isinstance(self.properties, dict)):
            color = self.properties['color']
            
        b1, b2 = ((self.orientation - angExtent)%360)*np.pi/180, ((self.orientation + angExtent)%360)*np.pi/180
        
        pygame.draw.arc(screen,color,[screenX-R*scaleX,screenY-R*scaleY,R*scaleX*2,R*scaleY*2],b1,b2,2)
        
    def drawSelected(self,screen,screenPosFunc):
        self.draw(screen,screenPosFunc)
        screenX, screenY, scaleX, scaleY = screenPosFunc(self.pos)
        pygame.draw.circle(screen, BLACK, [screenX, screenY], 10,0)

class Lens(OpticalElement):

    def elementType(self):
        return 'Lens'

    #Return the center of curvature
    def getCenterPoint(self):
        angleCent = self.orientation*np.pi/180
        return np.array([self.pos[0] - self.boundaries[0] * np.cos(angleCent), self.pos[1] - self.boundaries[0] * np.sin(angleCent)])

    #self.boundaries = [angularSize, radius, thickness]
    #self.orientation = direction

    def rayIntersection(self, ray_pos, ray_dir):
        ret = self.rayIntersection_which(ray_pos, ray_dir)
        if(ret is not None):
            _, output = ret
            return output
        return ret

    def rayIntersection_which(self, ray_pos, ray_dir):
        c = self.getCenterPoint()
        p = np.array(ray_pos)
        d = np.array(ray_dir) / np.linalg.norm(ray_dir)
        rs = p-c
        ang = self.orientation*np.pi/180
        o = np.array([np.cos(ang),np.sin(ang)])

        r = self.boundaries[0]
        t = self.boundaries[1]

        #if(abs(np.linalg.norm(rs) - r) < 1):
        #    return None

        discrim = np.dot(-rs,d)**2 - np.linalg.norm(rs)**2 + r**2
        if(discrim < 0):
            return None

        # Circle has two intersections
        alpha1 = np.dot(-rs,d) - np.sqrt(discrim)
        alpha2 = np.dot(-rs,d) + np.sqrt(discrim)
        alphaMin = min(alpha1,alpha2)
        alphaMax = max(alpha1,alpha2)

        p1 = p + alphaMin*d #Closest intersection
        p2 = p + alphaMax*d

        # Flat surface has intersection
        alpha_flat = (r - t - np.dot(rs,o))/np.dot(d,o)
        pf = p + alpha_flat*d

        if(alphaMin <  0 and alphaMax < 0 and alpha_flat < 0):
            return None

        flat_cond = alpha_flat**2 + 2*alpha_flat * np.dot(d,rs) + np.linalg.norm(rs)**2
        if(flat_cond < r**2):
            if(   alphaMin > 0 and np.dot(p1 - c, -o) + r < t): #Check closest interesection first
                return "Curved", p1
            if( alpha_flat > 0):
                return 'Flat', p + alpha_flat*d #Flat surface is closest
        if(   alphaMin > 0 and np.dot(p1 - c, -o) + r < t): #Check closest interesection first
            return "Curved", p1
        elif( alphaMax > 0 and np.dot(p2 - c, -o) + r < t):
            return "Curved", p2
        return None

    def reflect(self, ray_pos, ray_dir, intersect):
        pass

    def refract(self, ray_pos, ray_dir, intersect):
        REF_IND = 1.3
        c = self.getCenterPoint()
        surf, p = self.rayIntersection_which(ray_pos, ray_dir)
        di = ray_dir / np.linalg.norm(ray_dir)
        rs = p-c
        ang = self.orientation*np.pi/180
        o = np.array([np.cos(ang),np.sin(ang)])
        ot = np.array([np.cos(ang+np.pi/2),np.sin(ang+np.pi/2)])

        r = self.boundaries[0]
        t = self.boundaries[1]

        pos_out, dir_out = [], []

        if(surf == "Curved"):
            #print("Curved")
            d = self.snells_law(-di, REF_IND, rs/np.linalg.norm(rs))
            d = d/np.linalg.norm(d)

            pos_out.append( p )
            dir_out.append( d )
            #alpha = (-np.dot(rs,d) + t - r)/np.dot(d,-o)
            alpha = (-t + (r-np.dot(rs,o)))/np.dot(d,o)
            #print(alpha)
            p2 = p + alpha*d

            snell_dir = self.snells_law(-d, 1/REF_IND, -o)

            if(snell_dir is not None):
                dir_out.append( snell_dir )
                pos_out.append( p2 )

            return pos_out, dir_out
        else:
            #print("Flat")
            d = self.snells_law(di, REF_IND, -o)
            d = d/np.linalg.norm(d)
            if(d is not None):
                pos_out.append( p )
                dir_out.append( d )

                discrim = np.dot(rs,d)**2 - np.linalg.norm(rs)**2 + r**2
                if(discrim < 0):
                    print("Negative discriminant!")
                    return [p], [ray_dir]
                # Circle has two intersections
                alpha1 = np.dot(-rs,d) - np.sqrt(discrim)
                alpha2 = np.dot(-rs,d) + np.sqrt(discrim)
                alphaMin = min(alpha1,alpha2)
                alphaMax = max(alpha1,alpha2)

                p1 = p + alphaMin*d #Closest intersection
                p2 = p + alphaMax*d

                if(alphaMin > 0 and np.dot(p1 - c, -o) + r < t):
                    pos_new = p + alphaMin*d
                elif(alphaMax > 0 and np.dot(p2 - c, -o) + r < t):
                    pos_new = p + alphaMax*d
                else:
                    print("No positive alpha")
                    return [p], [ray_dir]

                pos_out.append(pos_new)
                rs2 = pos_new - c
                d_new = self.snells_law(d, 1/REF_IND, rs2/np.linalg.norm(rs2))
                if(d_new is not None):
                    dir_out.append(d_new)
                    #print("No error")
                else:
                    pass
                    #print("Invalid snell dir")
                    #dir_out.append(np.array([-d[1],d[0]]))
                return pos_out, dir_out
            print("Flat refraction error!")
            return [p], [ray_dir]

            #Where is intersection with curved surface?

    def snells_law(self, ray_dir_inc, ref_index, norm_dir):
        REF_IND = ref_index
        d = np.array(ray_dir_inc)/np.linalg.norm(ray_dir_inc)
        c = self.getCenterPoint()

        n = (norm_dir)/np.linalg.norm(norm_dir) #normal vector
        nt= np.array([n[1],-n[0]])    #tangent vector (perp. to normal)

        rad = 1-(1/REF_IND)**2*(1-np.dot(d,n)**2)
        if(rad <0 ):
            return None
        dir_new =  n*np.sqrt(rad)*np.sign(np.dot(d,n)) + \
                  nt*(1/REF_IND*np.dot(d,nt))
        return dir_new

    def checkBoundaries(self,pos):
        return False

    def angleBetween(self, angle, b1, b2):
        diff1, diff2 = abs(angle%360 - b1%360), abs(angle%360 - b2%360)
        width = abs(b1-b2)
        if(width > 180):
            width = 360-width
        if(diff1 > 180):
            diff1 = 360-diff1
        if(diff2 > 180):
            diff2 = 360-diff2
        return (diff1 < width) and (diff2 < width)

    def setOrientation(self,angleDeg):
        self.orientation = angleDeg%360

    def draw(self, screen, screenPosFunction):
        center = self.getCenterPoint()
        screenX, screenY, scaleX, scaleY = screenPosFunction(center)
        R = self.boundaries[0]
        t = self.boundaries[1]
        angExtent = np.arccos(1-t/R)*180/np.pi
        color = BLUE
        if(isinstance(self.properties, dict)):
            color = self.properties['color']

        b1, b2 = ((self.orientation - angExtent)%360)*np.pi/180, ((self.orientation + angExtent)%360)*np.pi/180

        p1 = np.array([R*scaleX*np.cos(-b1) + screenX, R*scaleY*np.sin(-b1) + screenY])
        p2 = np.array([R*scaleX*np.cos(-b2) + screenX, R*scaleY*np.sin(-b2) + screenY])


        pygame.draw.arc(screen,color,[screenX-R*scaleX,screenY-R*scaleY,R*scaleX*2,R*scaleY*2],b1,b2,2)
        pygame.draw.line(screen,color,p1,p2,2)
        #pygame.draw.arc(screen,color, , ,width=2)

    def drawSelected(self,screen,screenPosFunc):
        self.draw(screen,screenPosFunc)
        screenX, screenY, scaleX, scaleY = screenPosFunc(self.pos)
        pygame.draw.circle(screen, BLACK, [screenX, screenY], 10,0)
