from ast import match_case
import glob
import os
import sys
import codecs
import numpy as np
from PIL import Image
import re
from collections import defaultdict

#create output file
f = codecs.open("./testDisplay/animations.h", "w", "utf-8")


#Size of the output display. 
displaySize = (12,6)
pixelCount = displaySize[1]*displaySize[0]
mostFrames = 0
structNames = []


f.write('''
#include <FastLED.h>
#include <arduino.h>
#include <util/atomic.h>

typedef struct Gif {
    const int width;
    const int height;
    const int palette_count;
    const int frame_count;
    const char (*data)[%d];
    const uint32_t *palette;
    const uint16_t *duration;
} Gif;

class Anim{
    public:
    int frames = 10;
    int size = 72;
    CRGB leds[%d];
    char buffer[12][72] = {0};
    uint32_t palette [64] = {0};
    uint16_t duration [12] = {0};
    uint32_t uniformColors[5] = {0x000000, 0xffffff,0xff0000,0x0000ff,0xf66dff};
    int uniformColorIndex = 0;
    char current_frame = 0;
    int frame_count;
    volatile Gif* next = nullptr;
    Anim(){{}};

    void load(const Gif gif){
        current_frame = 0;
        frame_count = gif.frame_count;
        for(int i = 0; i < gif.frame_count; i++)
        memcpy_P(buffer[i], gif.data[i], sizeof (char)*size);
        memcpy_P(palette, gif.palette,sizeof(uint32_t)*gif.palette_count);
        memcpy_P(duration,gif.duration,  sizeof(uint16_t)*gif.frame_count);
    };

    void updateMatrix(bool nextFrame=true){
        if(next){
            Gif* tmp = nullptr;
            ATOMIC_BLOCK(ATOMIC_RESTORESTATE) {
            tmp = next;
            }
            load(*tmp);
            next = nullptr;
        }

        if(uniformColorIndex){
            for(uint8_t i = 0; i < size; i++)
                leds[i] = buffer[current_frame][i]?uniformColors[uniformColorIndex]:0x000000;
        }else{
            for(uint8_t i = 0; i < size; i++)
                       leds[i] = palette[buffer[current_frame][i]];
        }

       
        current_frame = nextFrame?((current_frame+1) %% frame_count):current_frame;
    };
    int getDelay(){
        return duration[current_frame];
    }
};
'''%(pixelCount,pixelCount))

#get iterator of all gif files and iterate
for infile in glob.glob("**/*.gif"):

    #Open file
    with Image.open(infile) as im:
        #Comment
        f.write("//"+infile+"\n")

        #Get file name without the extension. Used for automatic naming of structs.     
        structName = os.path.basename(infile).lower().translate(str.maketrans(" ","_")).split(".")[-2]
        structNames.append(structName)

        #Empty palette array. Max 256 colors. Palette is global across all frames of gif. 
        palette = []

        #Empty frame duration array. Miliseconds in integer.
        duration = []

        #Write array data. Append colors to palette as necessary.
        f.write("\tconst PROGMEM char "+structName+'_data[{}][{}]'.format(im.n_frames, im.size[0]*im.size[1]) +" = {"+"\n")

        #Iterate over frames
        for i in range(im.n_frames):
            #Set context to relevant frame
            im.seek(i)
            #Add frame duration to array
            duration.append(im.info['duration'] if im.info['duration'] > 60 else 60)
            #Get RGB data as python list
            pixels = list(im.getdata().convert("RGB"))
            #Create array of color indexes.
            res = [100 for _ in range(pixelCount)]
            for pIndex, p in enumerate(pixels):
                if p not in palette:
                    palette.append(p)

                if int(np.floor(pIndex//displaySize[0]))%2:
                    t = int(np.floor(pIndex/displaySize[0]) * displaySize[0] + displaySize[0]-1 - pIndex%displaySize[0])
                    res[t] = palette.index(p)
                else:
                    res[pIndex] = palette.index(p)
            #Write frame data.
            f.write("\t")
            f.write((str(res).translate(str.maketrans("[]","{}")))+("," if i+1 != im.n_frames else " ")+"\n")
        f.write("\t};"+"\n")

        
        #Write gif palette. Colors are stored as 24-bit hex,.
        f.write("\tconst PROGMEM uint32_t "+structName+"_palette[{}]".format(len(palette))+" = ")
        pal = ['0x%02x%02x%02x' % i for i in palette]
        f.write((str(pal).translate(str.maketrans("[]'","{} ")))+";\n")
        #Write gif frame durations.
        f.write("\tconst PROGMEM uint16_t "+structName+"_duration[{}]".format(len(duration))+" = ")
        f.write((str(duration).translate(str.maketrans("[]'","{} ")))+";\n")
        

        f.write("const Gif "+structName+f" = {{{im.size[0]},{im.size[1]},{len(pal)},{im.n_frames},{structName+'_data'},{structName+'_palette'},{structName+'_duration'}}} ;\n")
        


f.write("const Gif gifs[{}]".format(len(sorted(structNames)))+" = "+"\n")
f.write((str([s for s in sorted(structNames)]).translate(str.maketrans("[]'","{} ")))+";\n")

print(structNames)
f.close()