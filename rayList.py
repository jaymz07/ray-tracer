# Linked list of Rays.
# Main tracing code here


import numpy as np

#---------Ray Class----------------------------------
class Ray:
    def __init__(self, position, direction, intersect = None):
        self.pos = position
        self.direc = direction
        self.intersect = intersect
        self.last_element = None
        self.terminated = False

        self.color = None

        self.nextRays = []

class Trace:
    def __init__(self, ray_head=None):
        self.ray_head = ray_head  #Head of linked list

    # Recursively find last rays which have no intersection
    def get_last_rays(self, prev_ray=None):
        if(prev_ray is None):
            return self.get_last_rays(self.ray_head)
        if( len(prev_ray.nextRays) == 0):
            return [prev_ray]
        out = []
        for r in prev_ray.nextRays:
             lrs = self.get_last_rays(r)
             for lr in lrs:
                 if(not lr.terminated):
                    out.append(lr)
        return out

    # Return a bunch of lines that are easily drawn to screen
    def get_lines(self, prev_ray = None):
        if(prev_ray is None):
            return self.get_lines(self.ray_head)
        if( len(prev_ray.nextRays) == 0):
            if(prev_ray.intersect is not None):
                return [[prev_ray.pos, prev_ray.intersect]]
            return []
        if( len(prev_ray.nextRays) > 0):
            out = [[prev_ray.pos, prev_ray.intersect]]
            for r in prev_ray.nextRays:
                for l in self.get_lines(r):
                    out.append(l)
        return out

    # Ray tracing code. Take last rays of this tree and trace them to next bounce.
    def trace_next(self, elements):
        last_rays = self.get_last_rays()
        for r in last_rays:
            minDist = np.inf
            closestElem = None
            closestIntersect = None
            for elem in elements:
                intersect = elem.rayIntersection(r.pos, r.direc)
                #print(intersect)
                if(intersect is None):
                    continue
                dist = np.linalg.norm(intersect-r.pos)
                if(r.last_element is not None):
                    if elem is r.last_element:
                        continue
                if(dist < .001): # Avoid repeated bounce cycles?
                    print("BOUNCE CYCLE!!")
                    continue
    #                if(closestElem is not None and elem == closestElem):
    #                    continue
                if(minDist > dist):
                    minDist = dist
                    closestElem = elem
                    closestIntersect = intersect
            if(closestElem is not None):
                if(closestElem.elementType() != 'Lens'):
                    dir_new = closestElem.reflect(r.pos, r.direc, closestIntersect)
                    dir_new = dir_new / np.linalg.norm(dir_new)

                    #Build next link of the list
                    r.intersect = closestIntersect
                    next_ray = Ray(closestIntersect, dir_new)
                    next_ray.last_element = closestElem
                    r.nextRays.append(next_ray)

                elif(closestElem.elementType() == 'Lens'):
                    r.intersect = closestIntersect
                    newpos, newdirs = closestElem.refract(r.pos, r.direc, closestIntersect)
                    if(len(newpos) >0 and len(newdirs) >0):
                        #ray = {'pos' : closestIntersect, 'dir' : newdirs[0], 'color' : r['color']}
                        ray1 = Ray(closestIntersect, newdirs[0]) #internal ray of lens
                        if(len(newpos) == 2):
                            ray1.intersect = newpos[1]

                        if(len(newdirs) == 2):
                            ray2 = Ray(newpos[1], newdirs[1]) #lens exit ray
                            ray1.last_element = closestElem
                            ray2.last_element = closestElem
                            ray1.nextRays.append(ray2)
                            r.nextRays.append(ray1)
                            #newRays.append({'pos' : newpos[1], 'dir' : newdirs[1], 'color' : r['color']})
                        else:
                            ray1.terminated=True
                            r.nextRays.append(ray1)
            else:
                r.intersect = None
