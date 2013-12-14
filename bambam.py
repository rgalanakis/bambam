#!/usr/bin/python
#Copyright (C) 2007-2008 Don Brown 2010 Spike Burch <spikeb@gmail.com>
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

import fnmatch
import os
import random
import string
import sys

import pygame
from pygame.locals import *


# figure out the install base to use with image and sound loading
progInstallBase = os.path.dirname(os.path.normpath(sys.argv[0]))
datadir = os.path.join(progInstallBase, 'data')


# Load image in data/, handling setting of the transparency color key
def load_image(name):
    fullname = os.path.join(datadir, name)

    try:
        image = pygame.image.load(fullname)
    except pygame.error, message:
        print "Cannot load image:", name
        raise SystemExit(message)
    image = image.convert()
    colorkey = image.get_at((0, 0))
    image.set_colorkey(colorkey, RLEACCEL)
    return image


class NoneSound(object):
    def play(self):
        pass


def load_sound(name):
    if not pygame.mixer:
        return NoneSound()
    fullname = os.path.join(datadir, name)
    try:
        sound = pygame.mixer.Sound(fullname)
    except pygame.error, message:
        print "Cannot load sound:", fullname
        raise SystemExit, message
    return sound


def load_resources(ext, loader):
    for f in os.listdir(datadir):
        if fnmatch.fnmatch(f, ext):
            yield loader(f)


def process_event(events, quit_pos):
    for event in events:
        if event.type == QUIT:
            sys.exit(0)
        elif event.type == KEYDOWN or event.type == MOUSEBUTTONDOWN:
            #print "eepos: %s" % (quit_pos)

            if event.type == KEYDOWN:
                if event.key == K_q:
                    quit_pos = 1
                elif ((event.key == K_u) and (quit_pos == 1)):
                    quit_pos = 2
                elif event.key == K_i and quit_pos == 2:
                    quit_pos = 3
                elif event.key == K_t and quit_pos == 3:
                    sys.exit(0)
                else:
                    quit_pos = 0

            # Clear the background 10% of the time
            if random.randint(0, 10) == 1:
                screen.blit(background, (0, 0))
                pygame.display.flip()

            # Play a sound 50% of the time
            if random.randint(0, 1) == 1:
                random.choice(sounds).play()

            # Print an image 20% of the time or if no letter can be printed.
            if (random.randint(0, 5) == 1
                or event.type == MOUSEBUTTONDOWN
                or not is_alpha(event.key)):
                print_image()
            else:
                print_letter(event.key)

            pygame.display.flip()
    return quit_pos


def print_image():
    """Prints an image at a random location."""
    global screenheight, screenwidth
    img = images[random.randint(0, len(images) - 1)]
    w = random.randint(0, screenwidth - img.get_width())
    h = random.randint(0, screenheight - img.get_height())
    screen.blit(img, (w, h))


def is_alpha(key):
    """Is the key that was pressed alphanumeric."""
    return key < 255 and (chr(key) in string.letters or chr(key) in string.digits)


def print_letter(key):
    """Prints a letter at a random location."""
    global screenheight, screenwidth
    font = pygame.font.Font(None, 256)
    text = font.render(chr(key), 1, colors[random.randint(0, len(colors) - 1)])
    textpos = text.get_rect()
    center = (textpos.width / 2, textpos.height / 2)
    w = random.randint(0 + center[0], screenwidth - center[0])
    h = random.randint(0 + center[1], screenheight - center[1])
    textpos.centerx = w
    textpos.centery = h
    screen.blit(text, textpos)

# Main application
#
if not pygame.font:
    print 'Warning, fonts disabled'
if not pygame.mixer:
    print 'Warning, sound disabled'

pygame.init()

window = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
pygame.display.set_caption('Bam Bam')
screen = pygame.display.get_surface()
screenwidth = screen.get_width()
screenheight = screen.get_height()
BACKGROUNDCOL = [random.randint(200, 250) for _ in range(3)]
background = pygame.Surface(screen.get_size())
background = background.convert()
background.fill(BACKGROUNDCOL)

screen.blit(background, (0, 0))
pygame.display.flip()

sounds = list(load_resources('*.wav', load_sound))
colors = ((0, 0, 255), (255, 0, 0), (0, 255, 0), (255, 0, 255), (255, 255, 0))
images = list(load_resources('*.gif', load_image))

quit_pos = 0

clock = pygame.time.Clock()
while True:
    clock.tick(60)
    quit_pos = process_event(pygame.event.get(), quit_pos)