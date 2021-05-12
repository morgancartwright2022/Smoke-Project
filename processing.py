from PIL import Image, ImageDraw, ImageFont,ImageFilter,ImageStat
from enum import Enum
from queue import Queue
import math
# A somewhat complicated means of compressing the smoke image.
#This has a few advantages: <.5x size in memory, dynamic upscaling,
#easily able to simplify points for reduced size, no need for 2d arrays.
#Disadvantages: probably massive overkill, limits sizes to powers of 2.

#Uses a space-filling Hilbert Curve to encode a position. Lossless/Lossy capable.
#https://en.wikipedia.org/wiki/Hilbert_curve#Applications_and_mapping_algorithms
    
class Hilbert():
    def __init__(self,img):
        self.img = img
        self.Dither = self.Riemersa((0,0),img.width,img)
    #Credit: https://www.compuphase.com/riemer.htm Rewritten by me
    class Riemersa():
        errScale = 6
        errSize = 16
        threshold = 30
        gain = threshold-127
        def __init__(self,xy,size,img):
            self.cx = xy[0]
            self.cy = xy[1]
            self.size = size
            self.img = img
            
            self.errorQueue = []
            self.errorWeights = []
            k=math.pow(math.e,(math.log(self.errScale)/(self.errSize-1)))

            for i in range(self.errSize):
                weight=(1/self.errScale)*math.pow(k,i)
                self.errorQueue.append(0)
                self.errorWeights.append(weight)

        def process(self):
            self._calculate(math.floor(math.log2(self.size)), 'l')
        def _calculate(self,level,dir): 
            if level==1:
                if dir == 'l':
                    self._move('r')
                    self._move('d')
                    self._move('l')

                elif dir == 'r':
                    self._move('l')
                    self._move('u')
                    self._move('r')

                elif dir == 'u':
                    self._move('d')
                    self._move('r')
                    self._move('u')

                elif dir == 'd':
                    self._move('u')
                    self._move('l')
                    self._move('d')

            else:
                if dir == 'l':
                    self._calculate(level-1,'u')
                    self._move('r')
                    self._calculate(level-1,'l')
                    self._move('d')
                    self._calculate(level-1,'l')
                    self._move('l')
                    self._calculate(level-1,'d')

                elif dir == 'r':
                    self._calculate(level-1,'d')
                    self._move('l')
                    self._calculate(level-1,'r')
                    self._move('u')
                    self._calculate(level-1,'r')
                    self._move('r')
                    self._calculate(level-1,'u')

                elif dir == 'u':
                    self._calculate(level-1,'l')
                    self._move('d')
                    self._calculate(level-1,'u')
                    self._move('r')
                    self._calculate(level-1,'u')
                    self._move('u')
                    self._calculate(level-1,'r')

                elif dir == 'd':
                    self._calculate(level-1,'r')
                    self._move('u')
                    self._calculate(level-1,'d')
                    self._move('l')
                    self._calculate(level-1,'d')
                    self._move('d')
                    self._calculate(level-1,'l')

        def _move(self,dir):
            if self.cx>=0 and self.cx < self.size and self.cy>=0 and self.cy < self.size:
                pxValue = self.dither(self.img.getpixel((self.cx,self.cy)))
                self.img.putpixel((self.cx,self.cy),pxValue)
            if dir == 'l':
                self.cx-=1
            elif dir == 'r':
                self.cx+=1
            elif dir == 'u':
                self.cy-=1
            elif dir == 'd':
                self.cy+=1 
        
        def dither(self,pVal=0):
            error=0
            for i in range(self.errSize):
                error += self.errorQueue[i] * self.errorWeights[i]
            value = 255 if (pVal+error) >= self.threshold else 0
            self.errorQueue.pop(self.errSize-1)
            self.errorQueue = [pVal-value+self.gain] + self.errorQueue
            return value

    ########## Old ##########        
           
    # Credit: https://www.youtube.com/watch?v=dSK-MW-zuAc Rewritten and modified by me
    def drawhc(self,pl,size,blockSize=1): #blocksize is unsupported for effects
        ord = math.floor(math.log2(size/blockSize))
        n = size/blockSize #also hcK
        #print(str(ord))
        points = [
            (0,0),
            (0,1), 
            (1,1),
            (1,0)
        ]
        loc = pl 
        index = loc & 3
        rx = points[index][0]
        ry = points[index][1]
        for i in range(1,(ord)): #for i in range(1,order):
            ro = pow(2,i) #relative offset
            loc = loc >> 2 #bitwise shift. self._move two bits over.
            index = loc & 3 #bitwise and. do AND between loc and 3 per bit
            if index == 0:
                tmp = rx
                rx = ry
                ry = tmp
            elif index == 1:
                ry+=ro
            elif index == 2:
                rx+=ro
                ry+=ro
            elif index == 3:
                tmp = ro - 1-rx
                rx = ro - 1-ry
                ry = tmp
                rx+=ro
        x=rx*blockSize #x=rx*(width/hcK)
        y=ry*blockSize #y=ry*(width/hcK)
        return (x,y) 

    #Credit: Me
    def other(self,xy,size,blockSize=1,level=1,lst=[]): #blocksize is unsupported for effects
        ord = math.floor(math.log2(size/blockSize))
        rsize = math.floor((size/blockSize)-1)
        wlist=lst
        if ord >= 0:
            rxy=(math.floor(xy[0]/blockSize),math.floor(xy[1]/blockSize))
            midpoint = rsize//2 + 1
            qx = math.floor(rxy[0]/midpoint) #quadrant x
            qy = math.floor(rxy[1]/midpoint) #quadrant y
            quadrant = 0
            total = math.floor((size*size)/(blockSize*blockSize))
            if qx==0:
                if qy==0:
                    quadrant = 0
                else:
                    quadrant = 1
            else:
                if qy==0:
                    quadrant = 3
                else:
                    quadrant = 2
            tally=lst+[math.floor((quadrant*total)/4)]
            nx=0
            ny=0
            if quadrant==3:
                nx=midpoint-1-rxy[1]
                ny=rsize-rxy[0]
            elif quadrant==0:
                nx=rxy[1]
                ny=rxy[0]
            elif quadrant==2:
                nx=rxy[0]-midpoint
                ny=rxy[1]-midpoint
            elif quadrant==1:
                nx=rxy[0]
                ny=rxy[1]-midpoint
            return self.other((nx*blockSize,ny*blockSize),size/2,blockSize,level-1,tally)
        else:
            return sum(lst)

# Process the image
def process(im):
    sm = im.convert("L")
    pt = (15,8)
    sm=sm.filter(ImageFilter.GaussianBlur(2))
    h = Hilbert(sm)
    h.Dither.process()
    sm=sm.filter(ImageFilter.GaussianBlur(4))
    return sm