from PIL import Image
import drawing, processing

# Properties
#      name: name of files
# expansion: number of iterations in L-System
#      size: length and width of lines, radius of circles
#    energy: length of lines, randomness of lines and circles
#    weight: angle of turns
#      wind: horizontal distance added to lines
name = "test"
expansion = 5
size = 5
energy = 5
weight = 5
wind = 0

commands = drawing.write(expansion)
unfilteredImg = drawing.draw(512, 512, commands, size, energy, weight, wind)
unfilteredImg.save(name + ".png", "PNG")
filteredImg = processing.process(unfilteredImg)
filteredImg.save(name + "_filtered.png", "PNG")