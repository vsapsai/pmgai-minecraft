#
# This file is part of The Principles of Modern Game AI.
# Copyright (c) 2015, AiGameDev.com KG.
#

import os                                       # Built-in Python modules.
import sys
import math
import time
import random

sys.path.append('pymcworldgen')
import layer                                    # Modules from pymcworldgen.
import saveutils
import constants as c



class DistanceField(object):
    """Generates an island (currently iceberg) as a distance field.  This can be used either
    standalone, like in this example, or at the start of a pymcworldgen pipeline that uses 
    multiple step.s
    """

    def get_block(self, x, z, y):
        """For any point in the map, return the type of block at that location.
        
        y (int) represents altitude, positive is up and negative is down.
        x and z (int) are the lattitude and logitude in the map. 
        """ 

        def safe_fmod(x, y):
            return math.fmod(math.fabs(x), y) - y / 2.0
        # Add simple noise to the coordinates to make it less rigid!
        nx = safe_fmod(x, 64.0) + 2*math.sin(z/4.7)
        nz = safe_fmod(z, 64.0) + 2*math.cos(x/5.9)
        ny = y + math.sin(0.75 + x/7.8 + z/9.1)
        #nx = math.fmod(math.fabs(x), 64.0) - 32.0
        #nz = z
        #ny = y

        # Manhattan distance field to center of map: floating iceberg.
        if abs(nx) + abs(nz) + abs(ny*8) < 20:
            return c.MAT_DIRT

        # Anything that's not solid but under the sea level?
        if y < -2:
            return c.MAT_WATER
        if y < 0:
            return c.MAT_SNOW

        return c.MAT_AIR

    def getChunk(self, cx, cz):
        """Implements the pymcworldgen layer API, returning a chunk of 16x16 with height 128
        that can be stored on disk.
        
        (You shouldn't need to change this.)
        """

        WIDTH = c.CHUNK_WIDTH_IN_BLOCKS
        HALF_HEIGHT = c.CHUNK_HEIGHT_IN_BLOCKS//2

        chunk = layer.Chunk(cx, cz)
        for x in range(cx * WIDTH, (cx+1) * WIDTH):
            for z in range(cz * WIDTH, (cz+1) * WIDTH):
                for y in range(-HALF_HEIGHT, +HALF_HEIGHT): 
                    chunk.blocks[x%WIDTH][z%WIDTH][y+HALF_HEIGHT] = self.get_block(x, z, y)
        return chunk


def generate():
    """Main entry point that generates a world chunk by chunk, then saves it to disk for
    later rendering or use within the game.
    """

    start_time = time.clock()
    island = saveutils.createWorld("nuclai.world")

    worldsizex = 8
    worldsizez = 8

    pipeline = DistanceField()

    for chunkrow in range(-worldsizex, worldsizex):
        print("Generating row ", chunkrow)

        for chunkcol in range(-worldsizez, worldsizez):
            currchunk = pipeline.getChunk(chunkrow, chunkcol)
            saveutils.setWorldChunk(island, currchunk, chunkrow, chunkcol)
    
    saveutils.saveWorld(island)
    print("Processing took", start_time - time.clock(), "seconds.")


if __name__ == "__main__":
    os.makedirs("output", exist_ok=True)
    generate()
