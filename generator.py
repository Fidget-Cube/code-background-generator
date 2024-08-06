from PIL import Image
import os
import random

with open("messages.txt", "r") as fp:
    MESSAGES = fp.readlines()
MESSAGES = [i.strip() for i in MESSAGES]
OUTFILE = "test.bmp"

class imageState:
    def __init__(self, messages, mode="RGB", size=(384,384), endpoint_color=(0,191,255), text_color=(255,255,255)):
        self.images = [Image.new(mode=mode, size=size)]
        self.size = size
        self.maxlength = 0
        self.startindex = len(messages) * 5
        self.endpoint_color=endpoint_color
        self.text_color=text_color
        self.stateObjects = []
        starting_points = []                       # To prevent collisions
        for i in range(len(messages)):
            binary_msg = self.msg2bin(messages[i])
            if len(binary_msg)+2 > size[1]:        # Ignore messages longer than the length of the screen
                print(f"Message too long: {messages[i]} - {len(binary_msg)} bits")
                continue
            if len(binary_msg) > self.maxlength:
                self.maxlength = len(binary_msg)
            stateObject = {}
            stateObject['message'] = binary_msg
            for x in range(100):                   # 100 tries max, shouldn't reach this point
                stateObject['starting_point'] = (random.randint(0, size[0]-1), random.randint(0, size[1]-1))
                if stateObject['starting_point'][0] not in starting_points:
                    starting_points.append(stateObject['starting_point'][0])
                    # Give messages a 1 column buffer
                    starting_points.append(stateObject['starting_point'][0]+1)
                    starting_points.append(stateObject['starting_point'][0]-1)
                    break
            stateObject['counter'] = 0 - (i * 5)   # Tier each of the messages so they start printing at different times
            self.stateObjects.append(stateObject)

    def msg2bin(self, msg):
        line = ""
        for char in msg:
            line += bin(ord(char))[2:].zfill(8)
        return line
    
    def draw(self):
        newimage = self.images[-1].copy()
        for object in self.stateObjects:
            if object['counter'] < 0:                               # Do nothing until counter reaches start
                object['counter'] += 1
                continue
            elif object['counter'] == 0:                            # Draw start pixel
                newimage.putpixel(object['starting_point'], self.endpoint_color)
            elif object['counter'] <= len(object['message']):       # Draw message
                if object['message'][object['counter']-1] == '1':
                    newimage.putpixel((object['starting_point'][0], (object['starting_point'][1]+object['counter']) % self.size[1]), self.text_color)
            elif object['counter'] == len(object['message']) + 1:   # Draw end pixel
                newimage.putpixel((object['starting_point'][0], (object['starting_point'][1]+object['counter']) % self.size[1]), self.endpoint_color)
            elif object['counter'] > len(object['message']) + 1:    # Fade out all pixels
                for i in range(len(object['message'])+2):
                    pixel = newimage.getpixel((object['starting_point'][0], (object['starting_point'][1]+i) % self.size[1]))
                    newpixel = []
                    for val in pixel:
                        newpixel.append(val - 10)                   # Decrease in increments of 10, starting at the end of the count
                        if newpixel[-1] < 0:
                            newpixel[-1] = 0
                    newimage.putpixel((object['starting_point'][0], (object['starting_point'][1]+i) % self.size[1]), tuple(newpixel))
            object['counter'] += 1
            if object['counter'] >= self.maxlength + 32:            # Once the drawing completes, restart it
                object['counter'] = 0
        self.images.append(newimage)
    
    def save_gif(self, filename, output_folder='.'):
        self.images[0].save(os.path.join(output_folder, filename), save_all=True, append_images=self.images[1:], loop=0)
    
    def save_bmp(self, filename, output_folder='./img'):
        for i in range(len(self.images)):
            image = self.images[i].resize((1536,1536), resample=Image.BOX)      # It's very slow to resize the images afterwards, but also very easy to program
            image.save(os.path.join(output_folder, str(i).zfill(3) + filename))
        # Once .bmp images are saved, they can be combined into a .gif using ffmpeg
        # ffmpeg -i %003d<filename_bmp> <filename_gif>
    
    def main(self, filename):
        for i in range(((self.maxlength+32)*2)+self.startindex): # We will draw images up until the startindex plus twice the longest message (including endpoints and fade out frames)
            self.draw()
        self.images = self.images[self.startindex:]             # And only save images past the startindex
        if ".bmp" in filename:
            self.save_bmp(filename)
        elif ".gif" in filename:
            self.save_gif(filename)

img = imageState(MESSAGES)
img.main(OUTFILE)
