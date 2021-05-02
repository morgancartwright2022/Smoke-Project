from PIL import Image, ImageDraw
import math

# Create basic image
width = 150
height = 150
im = Image.new("I", (width, height), color=0)

# L-system variables
# Special characters are...
#   F: draw line
# +-: change angle
# []: save/load position
#  o: draw a circle
start = "X"
current = start
rules = {
    "X": "oF[+Xo][-Xo]"
}
angleChange = math.pi/8
lineLength = 15
circleRadius = 8
color = 255
iterations = 4

# State variables
x = width/2
y = height
angle = -math.pi/2
saved = []

# Change the input string as described by rules for each iteration
new = ""
for i in range(iterations):
    for char in current:
        if char in rules:
            new += rules[char]
        else:
            new += char
    current = new
    new = ""

for r in rules:
    current = current.replace(r, "F")
print(current)

# Draw the resulting image
draw = ImageDraw.Draw(im)
for char in current:
    if char == "f":
        x += lineLength*math.cos(angle)
        y += lineLength*math.sin(angle)
    if char == "F":
        nx = x + lineLength*math.cos(angle)
        ny = y + lineLength*math.sin(angle)
        draw.line([(x, y), (nx, ny)], fill=color, width=5)
        x = nx
        y = ny
    if char == "+":
        angle -= angleChange
    if char == "-":
        angle += angleChange
    if char == "[":
        state = {"x": x, "y": y, "angle": angle}
        saved.append(state)
    if char == "]":
        lastSaved = saved.pop()
        x = lastSaved["x"]
        y = lastSaved["y"]
        angle = lastSaved["angle"]
    if char == "o":
        draw.ellipse([(x - circleRadius, y - circleRadius), (x + circleRadius, y + circleRadius)], fill=color)

# Display the image
im.show()