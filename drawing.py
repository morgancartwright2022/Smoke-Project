from PIL import Image, ImageDraw
import math, random

# Write out and iteratively alter the commands
def write(expansion):
    # L-system variables
    # Special characters are...
    #  F: draw line
    #  f: move position forward
    # +-: change angle
    #  ^: set angle to upward position
    # []: save/load position
    #  o: draw a circle
    start = "A"
    current = start
    rules = {
        "A": "[^oW]f[^oFoW]f[^oW]",
        "W": "WoFo[+FoFoX][-FoFoX]",
        "X": "fofo[++Xo][--Xo]"
    }
    iterations = expansion + 2

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

    # Print resulting commands (optional)
    # print(current)

    for r in rules:
        current = current.replace(r, "")

    return current

# Draw the image
def draw(width, height, commands, size, energy, weight, wind):
    # Create blank image
    im = Image.new("RGB", (width, height), color=(0,0,0))

    # Drawing variables
    angleChange = math.pi/12 * (weight/3)
    lineLength = 5 + size*2 + math.floor(energy/2)
    lineVariance = energy
    lineWidth = size
    circleRadius = 1 + size
    circleVariance = math.floor(energy/3)
    color = (255,255,255)

    # State variables
    x = width/2
    y = height
    angle = 0
    saved = []

    draw = ImageDraw.Draw(im)
    def randLength():
        return lineLength + random.randint(-lineVariance, lineVariance)

    # Draw out image based on commands and variables
    for char in commands:
        if char == "f":
            x += randLength()*math.cos(angle) + wind
            y += randLength()*math.sin(angle)
        if char == "F":
            nx = (x + randLength()*math.cos(angle)) + wind
            ny = y + randLength()*math.sin(angle)
            draw.line([(x, y), (nx, ny)], fill=color, width=lineWidth)
            x = nx
            y = ny
        if char == "+":
            angle += -angleChange
        if char == "-":
            angle += angleChange
        if char == "^":
            angle = 3*math.pi/2
        if char == "[":
            state = {"x": x, "y": y, "angle": angle}
            saved.append(state)
        if char == "]":
            lastSaved = saved.pop()
            x = lastSaved["x"]
            y = lastSaved["y"]
            angle = lastSaved["angle"]
        if char == "o":
            r = circleRadius + random.randint(-circleVariance, circleVariance)
            draw.ellipse([(x - r, y - r), (x + r, y + r)], fill=color)

        if angle < 0:
            angle += 2*math.pi
        if angle > 2*math.pi:
            angle -= 2*math.pi

    return im