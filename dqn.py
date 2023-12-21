import numpy as np
from matplotlib import pyplot as plt

class Field:
    def __init__(self, height=867, width=1000):
        self.width      = width
        self.height     = height
        self.body = np.zeros(shape=(self.height, self.width))

    def update_field(self, buoys):#, boat):
        try:
            # Clear the field:
            self.body = np.zeros(shape=(self.height, self.width))

            # Mark out of bounds range:
            for x in range(0,999):
                for y in range(0, 866):
                    if ((x<290) & (0.055866*x -y > 6.2)):
                        self.body[y,x] = 1
                    elif ((x>=290) & (x<428) & (0.261*x -y > 65.65)):
                        self.body[y,x] = 1
                    elif ((x>=428) & (x<576) & (0.3514*x -y > 104.38)):
                        self.body[y,x] = 1
                    elif ((x>=576) & (x<737) & (0.3913*x -y > 127.4)):
                        self.body[y,x] = 1
                    elif ((x>=737) & (x < 745) & (19.5*x -y > 14210)):
                        self.body[y,x] = 1
                    elif ((x>=745) & (0.7953*x -y > 275)):
                        self.body[y,x] = 1

                    if ((x>=893) & (3.27*x+y > 3789.3)):
                        self.body[y,x] = 1
                    elif (y-0.299*x > 599):
                        self.body[y,x] = 1

                    if ((x<111) & (y+5.4*x < 599)):
                        self.body[y,x] = 1

            # Put the buoys on the field:
            for buoy in buoys:
                self.body[buoy.y:min(buoy.y+buoy.height,self.height),buoy.x:min(buoy.x+buoy.width, self.width)] = buoy.symbol
            # Put the player on the field:
            #self.body[boat.y:boat.y+boat.height,
                   #   boat.x:boat.x+boat.width] += boat.body 
        except :
            pass

class Buoy:        
    def __init__(self, y = 0, x = 0, symbol = -1, sideways = False):
        self.y            = y
        self.x            = x
        self.height       = 2 if sideways else 6
        self.width        = 6 if sideways else 2
        self.symbol       = symbol
        self.body         = np.ones(shape = (self.height, self.width))*symbol

a = Field()


outer_boundary_1 = Buoy(0,111, 2)
outer_boundary_2 = Buoy(599,0,2, True)
outer_boundary_3 = Buoy(866, 893, 2)
outer_boundary_4 = Buoy(519, 999, 2, True)
start_boundary = Buoy(317, 745,  3)
finish_boundary = Buoy(229, 737,  3)

depth_marker_boundary_1 = Buoy(10, 290, 4)
depth_marker_boundary_2 = Buoy(46, 428, 4)
depth_marker_boundary_3 = Buoy(98, 576, 4)
depth_marker_boundary_4 = Buoy(161, 737, 4)

gateA_red= Buoy(359, 723, 5)
gateA_green = Buoy(361, 733, 6)

slalom_red_01 = Buoy(407, 713, 5)
slalom_green_02 = Buoy(451, 697, 6)
slalom_red_03 = Buoy(498, 685, 5)
slalom_green_04 = Buoy(542, 674, 6)
slalom_red_05 = Buoy(587, 659, 5)

gateB_red = Buoy(630, 640, 5)
gateB_green = Buoy(634, 649, 6)

gateC_red = Buoy(617, 605, 5, True)
gateC_green = Buoy(626, 600, 6, True)

rings_green_01 = Buoy(604, 558, 6)
rings_red_02 = Buoy(589, 513, 5)
rings_green_03 = Buoy(576, 472, 6)
rings_red_04 = Buoy(561, 428, 5)
rings_green_05 = Buoy(544, 383, 6)

gateD_red = Buoy(525, 343, 5, True)
gateD_green = Buoy(533, 337, 6, True)

colorpick_blue = Buoy(516, 264, 7, True)
colorpick_orange = Buoy(511, 262, 8, True)
colorpick_magenta = Buoy(506, 260, 9, True)
colorpick_yellow = Buoy(501, 258, 10, True)

sensorDep_zebra = Buoy(301, 336, 11)
shoreDep_black = Buoy(104, 398, 12)

search_rescue = Buoy(165, 578, 13)

buoys_list = [outer_boundary_1, outer_boundary_2, outer_boundary_3, outer_boundary_4, start_boundary, finish_boundary, 
              depth_marker_boundary_1, depth_marker_boundary_2, depth_marker_boundary_3, depth_marker_boundary_4,
              gateA_green, gateA_red, gateB_green, gateB_red, gateB_green, gateC_red, gateC_green, gateD_green, gateD_red,
              slalom_red_01, slalom_green_02, slalom_red_03, slalom_green_04, slalom_red_05,
              rings_green_01, rings_red_02, rings_green_03, rings_red_04, rings_green_05,
              colorpick_blue, colorpick_orange, colorpick_magenta, colorpick_yellow,
              sensorDep_zebra, shoreDep_black, search_rescue]

a.update_field(buoys_list)

plt.imshow(a.body, interpolation='nearest')
plt.show()

