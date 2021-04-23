from PIL import Image, ImageDraw
import math

width = 100
height = 100
im = Image.new("I", (width, height), color=0)

commands = "f+ff-f-f+f"
angleChange = math.pi/2
lineLength = 10

ang = 0
x = width/2
y = height/2

draw = ImageDraw.Draw(im)
for char in commands:
    if char == "f":
        nx = x + lineLength*math.cos(ang)
        ny = y + lineLength*math.sin(ang)
        draw.line([(x, y), (nx, ny)], fill=255)
        x = nx
        y = ny
    if char == "+":
        ang += angleChange
    if char == "-":
        ang -= angleChange

im.show()