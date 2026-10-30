"""Continuous snake rules with segment-distance collision checks."""
import math
import random

def distance_to_segment(point, start, end):
    dx,dy=end[0]-start[0],end[1]-start[1]
    length=dx*dx+dy*dy
    t=0 if length==0 else max(0,min(1,((point[0]-start[0])*dx+(point[1]-start[1])*dy)/length))
    return math.hypot(point[0]-(start[0]+t*dx),point[1]-(start[1]+t*dy))

class GestureSnake:
    def __init__(self,width=1280,height=720,seed=None):
        self.width,self.height=width,height;self.rng=random.Random(seed);self.reset()
    def reset(self):
        self.points=[];self.lengths=[];self.length=0.;self.allowed=150.;self.score=0;self.over=False;self.food=self.new_food()
    def new_food(self):
        return (self.rng.randint(25,max(25,self.width-25)),self.rng.randint(25,max(25,self.height-25)))
    def update(self,head):
        if self.over:return
        if not self.points:self.points.append(head);return
        distance=math.dist(self.points[-1],head)
        if distance>200: # tracking was lost: do not draw an artificial long segment
            self.points=[head];self.lengths=[];self.length=0.;return
        if distance<1:return
        self.points.append(head);self.lengths.append(distance);self.length+=distance
        if math.dist(head,self.food)<25:
            self.score+=1;self.allowed+=50;self.food=self.new_food()
        while self.length>self.allowed and self.lengths:
            self.length-=self.lengths.pop(0);self.points.pop(0)
        # Exclude the recent 60 pixels of neck to avoid immediate self-collision.
        recent=0.
        for i in range(len(self.lengths)-1,-1,-1):
            recent+=self.lengths[i]
            if recent>60 and distance_to_segment(head,self.points[i],self.points[i+1])<10:
                self.over=True;break
