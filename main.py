import numpy as np
from matplotlib import pyplot as plt
import pygame
import time

debug_nogame = False
debug_displaygraph = False

def cosd(x):
    return np.cos(np.deg2rad(x))

def sind(x):
    return np.sin(np.deg2rad(x))

class Field:
    def __init__(self, height=867, width=1000):
        self.width      = width
        self.height     = height
        self.body = np.zeros(shape=(self.height, self.width))
        self.collisions = 0

    def store_background(self):
        self.template = np.zeros(shape=(self.height, self.width))
        # Mark out of bounds range:
        for x in range(0,999):
            for y in range(0, 866):
                if ((x<290) & (0.055866*x -y > 6.2)):
                    self.template[y,x] = 1
                elif ((x>=290) & (x<428) & (0.261*x -y > 65.65)):
                    self.template[y,x] = 1
                elif ((x>=428) & (x<576) & (0.3514*x -y > 104.38)):
                    self.template[y,x] = 1
                elif ((x>=576) & (x<737) & (0.3913*x -y > 127.4)):
                    self.template[y,x] = 1
                elif ((x>=737) & (x < 745) & (19.5*x -y > 14210)):
                    self.template[y,x] = 1
                elif ((x>=745) & (0.7953*x -y > 275)):
                    self.template[y,x] = 1

                if ((x>=893) & (3.27*x+y > 3789.3)):
                    self.template[y,x] = 1
                elif (y-0.299*x > 599):
                    self.template[y,x] = 1

                if ((x<111) & (y+5.4*x < 599)):
                    self.template[y,x] = 1

    def update_field(self, buoys, boat):
        try:
            # Clear the field:
            self.body = np.copy(self.template)
            self.collisions = 0

            # Put the buoys on the field:
            for buoy in buoys:
                self.body[buoy.y:min(buoy.y+buoy.height,self.height),buoy.x:min(buoy.x+buoy.width, self.width)] = buoy.symbol

            # Put the player on the field:
            #check for collision of front tip:
            if (self.body[int(boat.y), int(boat.x)] != 0):
                self.collisions += 1
            #place the front tip of the boat:
            #print('a')
            self.body[int(boat.y), int(boat.x)] = boat.tipsymbol

            #paint rest of boat:
                #to further refine later: project two lines at angle to guide tip shape, and don't paint the pixel if it's outside that boundary
                #this will allow the first step (tapered width) to be skipped also
            if (boat.bearing < 10 or boat.bearing > 350):
                #do custom boat vertical to override bug
                for n in range(int(-boat.width/2), int(boat.width/2)):
                    for y in range(1, boat.length):
                        if (self.body[int(boat.y+y), int(n + boat.x)] != 0 and self.body[int(boat.y+y), int(n + boat.x)] < 20):
                            self.collisions += 1
                        self.body[int(boat.y+y), int(n+boat.x)] = boat.symbol

            elif (boat.bearing > 170 and boat.bearing < 190):
                #do custom vertical boat to override bug
                for n in range(int(-boat.width/2), int(boat.width/2)):
                    for y in range(1, boat.length):
                        if (self.body[int(boat.y-y), int(n + boat.x)] != 0 and self.body[int(boat.y-y), int(n + boat.x)] < 20):
                            self.collisions += 1
                        self.body[int(boat.y-y), int(n+boat.x)] = boat.symbol

            elif (boat.bearing > 180):
                m = 1/(-sind(boat.bearing) / cosd(boat.bearing))
                for n in range(int(-boat.width/2), int(boat.width/2)):
                    if (n >= boat.width-1 and n <= boat.width+1):
                        x=1
                        y=m*x + n
                        if (self.body[int(int(y)+boat.y),int(x+boat.x)] != 0 and self.body[int(int(y)+boat.y),int(x+boat.x)] < 20):
                            self.collisions += 1
                        self.body[int(int(y)+boat.y),int(x+boat.x)] = boat.symbol

                    for x in range (2,boat.length):
                        y=m*x + n
                        if (np.sqrt(int(y)**2 + x**2) <= (boat.length)):
                            if (self.body[int(int(y)+boat.y),int(x+boat.x)] != 0 and self.body[int(int(y)+boat.y),int(x+boat.x)] < 20):
                                self.collisions += 1
                            self.body[int(int(y)+boat.y),int(x+boat.x)] = boat.symbol

            else:
                m = 1/(sind(boat.bearing) / cosd(boat.bearing))
                for n in range(int(-boat.width/2), int(boat.width/2)):
                    if (n >= boat.width-1 and n <= boat.width+1):
                        x=1
                        y=m*x + n
                        if (self.body[int(int(y)+boat.y),int(-x+boat.x)] != 0 and self.body[int(int(y)+boat.y),int(-x+boat.x)] < 20):
                            self.collisions += 1
                        self.body[int(int(y)+boat.y),int(-x+boat.x)] = boat.symbol
                    for x in range (2,boat.length):
                        y=m*x + n
                        if (np.sqrt(int(y)**2 + (x)**2) <= (boat.length)):
                            if (self.body[int(int(y)+boat.y),int(-x+boat.x)] != 0 and self.body[int(int(y)+boat.y),int(-x+boat.x)] < 20):
                                self.collisions += 1
                            self.body[int(int(y)+boat.y),int(-x+boat.x)] = boat.symbol
        except :
            pass

class Buoy:
    def __init__(self, y = 0, x = 0, symbol = -1, sideways = False):
        self.y            = y
        self.x            = x
        self.height       = 2 if sideways else 6
        self.width        = 6 if sideways else 2
        self.symbol       = symbol

class Boat:
    def __init__(self, y, x, bearing):
        self.y = y
        self.x = x
        self.bearing = bearing
        self.speed = 0

        self.symbol = 20
        self.tipsymbol = 21
        self.length = 31
        self.width = 8
        self.SPEEDMAX = 100

        self.movementLog = [[y,x,bearing]]

    def frame_update(self, steering_change, speed_change):
        #attenuate from friction
        self.speed *= 0.85

        #propogate speed and direction changes from previous frame inputs
        self.x += self.speed * cosd(self.bearing-90)
        self.y += self.speed * sind(self.bearing-90)

        #assign steering direction change and speed change, will take effect next frame
        self.bearing +=steering_change
        self.speed += speed_change

        #check for overflows
        if self.bearing >= 360: self.bearing -= 360
        if self.bearing < 0 : self.bearing += 360
        if self.speed >= self.SPEEDMAX: self.speed = self.SPEEDMAX
        if self.speed <= -self.SPEEDMAX: self.speed = -self.SPEEDMAX

        #update movement log
        self.movementLog = np.append(self.movementLog, [[self.y,self.x,self.bearing]], axis=0)

class Coin:
    x = 0
    y = 0
    collected = False
    multiplier = 1

    def __init__(self, x_set, y_set, mult):
        x = x_set
        y = y_set
        multiplier = mult
        collected = False

    def collect(self):
        collected = True

######################################################################################
class Environment:
    F_HEIGHT      = 867 # Height of the field
    WIDTH         = 1000 # Width of the field and the walls

    HEIGHT_MUL    = 1 # Height Multiplier (used to draw np.array as blocks in pygame )
    WIDTH_MUL     = 1 # Width Multiplier (used to draw np.array as blocks in pygame )
    WINDOW_HEIGHT = (F_HEIGHT+1) * HEIGHT_MUL # Height of the pygame window
    WINDOW_WIDTH  = (WIDTH) * WIDTH_MUL       # Widh of the pygame window

    ENVIRONMENT_SHAPE = (F_HEIGHT,WIDTH,1)
    ACTION_SPACE      = [0,1,2,3,4]
    ACTION_SPACE_SIZE = len(ACTION_SPACE)
    PUNISHMENT        = -100  # Punishment increment
    REWARD            = 10    # Reward increment
    score             = 0     # Initial Score

    MOVE_PLAYER_EVERY = 1     # Every how many frames the player moves.
    frames_counter    = 0
    vessel = Boat

    def __init__(self):
        # Colors:
        self.BLACK      = (25,25,25)
        self.WHITE      = (255,255,255)
        self.RED        = (255, 80, 80)
        self.ORANGE = (255,123,0)
        self.BLUE       = (0,0, 255)
        self.GREEN = (80,255,80)
        self.BOAT_COLOR = (186, 0, 177)
        self.BOATTIP_COLOR = (245, 0, 208)
        self.OCEAN_COLOR = (86, 141, 163)
        self.YELLOW = (255, 255, 80)
        self.GRAY = (143,143,143)
        self.MAGENTA = (120, 0, 58)
        self.OOBCOLOR = (14, 36, 56)
        self.field = self.buoys_list = self.boats_list = None
        self.current_state = self.reset()
        self.val2color  = {0:self.OCEAN_COLOR, 1:self.OOBCOLOR, 2:self.YELLOW, 3:self.BLUE, 4:self.GRAY, 5:self.RED, 6:self.GREEN,
                           7:self.BLUE, 8:self.ORANGE, 9:self.MAGENTA, 10:self.YELLOW, 11:self.WHITE, 12:self.BLACK,
                           13:self.BLUE, 20:self.BOAT_COLOR, 21:self.BOATTIP_COLOR}
        self.vessel = Boat(348, 735, 200)
    def reset(self):
        self.score          = 0
        self.frames_counter = 0
        self.game_over      = False

        self.field = Field()
        self.field.store_background()

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

        self.buoys_list = [outer_boundary_1, outer_boundary_2, outer_boundary_3, outer_boundary_4, start_boundary, finish_boundary,
                    depth_marker_boundary_1, depth_marker_boundary_2, depth_marker_boundary_3, depth_marker_boundary_4,
                    gateA_green, gateA_red, gateB_green, gateB_red, gateB_green, gateC_red, gateC_green, gateD_green, gateD_red,
                    slalom_red_01, slalom_green_02, slalom_red_03, slalom_green_04, slalom_red_05,
                    rings_green_01, rings_red_02, rings_green_03, rings_red_04, rings_green_05,
                    colorpick_blue, colorpick_orange, colorpick_magenta, colorpick_yellow,
                    sensorDep_zebra, shoreDep_black, search_rescue]

        self.vessel = Boat(348, 735, 200)

        self.field.update_field(self.buoys_list, self.vessel)

        observation = self.field.body
        return observation
    def print_text(self, WINDOW = None, text_cords = (0,0), center = False,
                   text = "", color = (0,0,0), size = 32):
        pygame.init()
        font = pygame.font.Font('freesansbold.ttf', size)
        text_to_print = font.render(text, True, color)
        textRect = text_to_print.get_rect()
        if center:
            textRect.center = text_cords
        else:
            textRect.x = text_cords[0]
            textRect.y = text_cords[1]
        WINDOW.blit(text_to_print, textRect)

    def step(self, speed_action, angle_action):
        global score_increased

        self.frames_counter += 1
        reward = 0
        self.score += 1

        self.vessel.frame_update(angle_action, speed_action)

        # Update the field :
        self.field.update_field(self.buoys_list, self.vessel)

        if self.score >= winning_score:
            self.game_over = True

        if (debug_displaygraph):
            plt.imshow(a.body, interpolation='nearest')
            plt.show()

        # If good thing occured increase the reward +1 #######################disabled for now
        if (False):
            if (reward_condition):
                reward += self.REWARD * occurances
                self.score  += self.REWARD * occurances

            #deduct points for collisions
            reward -= self.field.collisions * self.REWARD

            # score_changed : a flag
            score_changed = True
            score_changed = False


        # Return New Observation , reward
        #return self.field.body, reward


    def render(self, WINDOW = None, human=False):

        if human:
            ################ Check Actions #####################
            action_speed = 0
            action_direction = 0
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        action_direction = -30
                    if event.key == pygame.K_RIGHT:
                        action_direction = 30
                    if event.key == pygame.K_UP:
                        action_speed = 5
                    if event.key == pygame.K_DOWN:
                        action_speed = -5
                    if event.key == pygame.K_q:
                        self.game_over = True
                        break
            ################## Step ############################
        self.step(action_speed, action_direction)

        ################ Draw Environment ###################
        WINDOW.fill(self.WHITE)
        for r in range(self.field.body.shape[0]):
            for c in range(self.field.body.shape[1]):
                pygame.draw.rect(WINDOW,
                                 self.val2color[int(self.field.body[r][c])],
                                 (c, r, 1, 1))

        self.print_text(WINDOW = WINDOW, text_cords = (self.WINDOW_WIDTH // 2, int(self.WINDOW_HEIGHT*0.1)),
                       text = str(self.score), color = self.RED, center = True)
        self.print_text(WINDOW = WINDOW, text_cords = (0, int(self.WINDOW_HEIGHT*0.9)),
                       text = str(self.field.collisions), color = self.RED)

        pygame.display.update()
####################################################################################


if (debug_nogame):
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

    a.update_field(buoys_list, [])

    vessel = Boat(348, 735, 200)
    a.update_field(buoys_list, vessel)
    print("collisions = %d", a.collisions)

    np.savetxt("currentwater.txt", a.body, fmt="%d")

    plt.imshow(a.body, interpolation='nearest')
    plt.show()

else:
    # Make an environment object
    env            = Environment()
    # Change wall speed to 3 (one step every 3 frames)
    env.WALL_SPEED = 3

    # Initialize some variables
    WINDOW          = pygame.display.set_mode((env.WINDOW_WIDTH, env.WINDOW_HEIGHT))
    clock           = pygame.time.Clock()
    win             = False
    winning_score   = 100
    framecounter = 0

    # Repeat the game untill the player win (got a score of winning_score) or quits the game.
    game_over       = False
    _ = env.reset()
    pygame.display.set_caption("Game")
    while not game_over:
            clock.tick(2)
            framecounter += 1
            env.render(WINDOW = WINDOW, human=True)
            game_over = env.game_over
            if framecounter >= 200: game_over = True

    #####################################################
    WINDOW.fill(env.WHITE)
    if env.score >= winning_score:
        win = True
        env.print_text(WINDOW = WINDOW, text_cords = (env.WINDOW_WIDTH // 2, env.WINDOW_HEIGHT// 2),
                        text = f"You Win - Score : {env.score}", color = env.RED, center = True)
        np.savetxt("movements.txt", env.vessel.movementLog , fmt="%f")
    else:
        env.print_text(WINDOW = WINDOW, text_cords = (env.WINDOW_WIDTH // 2, env.WINDOW_HEIGHT// 2),
                        text = f"Game Over - Score : {env.score}", color = env.RED, center = True)
        np.savetxt("movements.txt", env.vessel.movementLog , fmt="%f")
    pygame.display.update()
    time.sleep(3)
