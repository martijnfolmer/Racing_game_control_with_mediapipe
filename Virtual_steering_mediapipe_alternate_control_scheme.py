import cv2
import math
import vgamepad as vg
from Mediapipe_hand_detection import MediapipeHandDetection     # for when we use mediapipe


class VirtualSteering():

    def __init__(self):
        print("Initializing the VirtualSteeringClass")
        self.cap = cv2.VideoCapture(0)

        window_size = 1280, 720
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, window_size[0])            # Set the size of our capture
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, window_size[1])

        # MediapipeHandDetection
        self.MHD = MediapipeHandDetection()       # using the google medipipe model

        # gamepad values
        self.gamepad = vg.VX360Gamepad()

        # input values:
        self.Lx_min = 740
        self.Lx_max = 1280-150       # min and max values
        self.Lx_height = 30
        self.Lx_loc_y = 450

        self.wheel_angle_min = 180      # if Lx = Lx_min, it means we are at angle 180
        self.wheel_angle_max = 0        # if Lx = Lx_max, it means we are at angle = 0,

        self.Ry_min = 150         # minimum Ry
        self.Ry_max = 570       # total down
        self.Ry_loc_x = 100     # location of the meter on screen
        self.Ry_width = 100     # width of the meter

        self.thrust_min = 0
        self.thrust_max = 255
        self.break_min = 0          # so if over halfway down, we are breaking
        self.break_max = 255

        # steering wheel options:
        self.wheel_r = int(window_size[0]*0.2)              # current radius
        self.wheel_r_acc_max = int(window_size[0]*0.3)      # this is the biggest radius, at which acc will become max
        self.wheel_r_acc_min = int(window_size[0]*0.2)      # if radius becomes more than this, we accelerate
        self.wheel_r_decc_max = int(window_size[0]*0.015)   # minimum radius, at which decceleration
        self.wheel_r_decc_min = int(window_size[0]*0.15)    # if below this, we start braking

        self.wheel_r_acc_max = 700/2
        self.wheel_r_acc_min = 550/2
        self.wheel_r_decc_max = 250/2
        self.wheel_r_decc_min = 450/2

        self.wheel_angle = 0
        self.wheel_cent = (0, 0)
        self.wheel_spoke1 = (0, 0)         # the spokes of the steering wheel
        self.wheel_spoke2 = (0, 0)
        self.wheel_spoke3 = (0, 0)

        self.wheel_color_norm = (255, 255, 255)
        self.wheel_color_acc = (0, 255, 0)
        self.wheel_color_decc = (0, 0, 255)
        self.wheel_color_cur = self.wheel_color_norm

        self.joystickvalues = 0         # for gamepad sample

        self.hand_left = []
        self.hand_right = []
        self.hist_n = 5             # how many frames we are

        self.xl, self.yl = -1, -1
        self.xr, self.yr = -1, -1

    def UpdateDetectedHandsHistory(self, all_hands):

        # just update based on detection
        self.xl = -1
        self.yl = -1
        self.xr = -1
        self.yr = -1
        if all_hands[0][0] != -1 and all_hands[1][0] == -1:
            self.xl, self.yl = all_hands[0][1], all_hands[0][2]
        elif all_hands[1][0] != -1 and all_hands[0][0] == -1:
            self.xr, self.yr = all_hands[1][1], all_hands[1][2]
        elif all_hands[0][0] != -1 and all_hands[1][0] != -1:

            if all_hands[0][1] > all_hands[1][1]:
                self.xl, self.yl = all_hands[0][1], all_hands[0][2]
                self.xr, self.yr = all_hands[1][1], all_hands[1][2]
            else:
                self.xl, self.yl = all_hands[1][1], all_hands[1][2]
                self.xr, self.yr = all_hands[0][1], all_hands[0][2]

    def UpdateGamePad(self, thrust_c, break_c):

        # we need to input the stuff
        ang_joystick = self.wheel_angle*1.0+90      # this is updated in

        # print(f"Ang joystick : {ang_joystick}")

        xjoystick = 32768 * math.cos(math.radians(ang_joystick))
        yjoystick = 32768 * math.sin(math.radians(ang_joystick))

        xjoystick = int(min(max(xjoystick, -32768), 32767))
        yjoystick = int(min(max(yjoystick, -32768), 32767))
        # print(xjoystick, yjoystick)
        self.gamepad.left_joystick(x_value=xjoystick, y_value=yjoystick)  # values between -32768 and 32767

        # update the triggers and break.
        right_trigger_val =  min(255, max(0, int(thrust_c)))
        left_trigger_val = min(255, max(0, int(break_c*1.5)))

        self.gamepad.left_trigger(value=left_trigger_val)  # value between 0 and 255
        self.gamepad.right_trigger(value=right_trigger_val)  # value between 0 and 255

        # this updates the game
        self.gamepad.update()  # send the updated state to the computer

    def GetAvgHandValues(self, hand_to_avg):

        if len(hand_to_avg) > 0:
            hand_x = 0
            hand_y = 0
            for i in range(len(hand_to_avg)):
                hand_x += hand_to_avg[i][1]
                hand_y += hand_to_avg[i][2]
            hand_x /= len(hand_to_avg)
            hand_y /= len(hand_to_avg)
        else:
            hand_x, hand_y = -1, -1
        return hand_x, hand_y

    def UpdateWheelValues(self, xcent, ycent, r, angle):

        # values from variables
        self.wheel_cent = (int(xcent), int(ycent))
        self.wheel_r = int(r)
        self.wheel_angle = -(angle-90)              # for visualisation
        # print(f"Current wheel angle : {angle}")

        # visual, get the spokes
        p1_alpha = self.wheel_angle + 45 + 180
        p2_alpha = self.wheel_angle + 135 + 180
        p3_alpha = self.wheel_angle + 270 + 180

        self.wheel_spoke1 = (int(self.wheel_cent[0] + math.cos(math.radians(p1_alpha)) * self.wheel_r),
              int(self.wheel_cent[1] + math.sin(math.radians(p1_alpha)) * self.wheel_r))
        self.wheel_spoke2 = (int(self.wheel_cent[0] + math.cos(math.radians(p2_alpha)) * self.wheel_r),
              int(self.wheel_cent[1] + math.sin(math.radians(p2_alpha)) * self.wheel_r))
        self.wheel_spoke3 = (int(self.wheel_cent[0] + math.cos(math.radians(p3_alpha)) * self.wheel_r),
              int(self.wheel_cent[1] + math.sin(math.radians(p3_alpha)) * self.wheel_r))

        self.wheel_color_cur = self.wheel_color_norm

    def UpdateWheelAndThrustValues(self, Lx, Ry):

        # print(Lx)
        if Lx != -1:
            wheel_angle_cur = (1-max(0,min(1,(Lx-self.Lx_min)/(self.Lx_max-self.Lx_min))))*(self.wheel_angle_min-self.wheel_angle_max)
        else:
            wheel_angle_cur = 0

        self.UpdateWheelValues((self.Lx_min+self.Lx_max)/2, self.Lx_loc_y + 150, 100, wheel_angle_cur)

        if Ry != -1:
            midx = (self.Ry_min + self.Ry_max)/2
            if Ry < midx:
                frac = abs(Ry-midx)/(abs(midx-self.Ry_min))
                thrust_c = frac * 255
                break_c = 0
            else:
                frac = abs(Ry-midx)/(abs(midx-self.Ry_max))
                thrust_c = 0
                break_c = frac *255
        else:
            thrust_c = 0
            break_c = 0

        return wheel_angle_cur, thrust_c, break_c

    def Visualisation_threat(self, frame, Lx, Ry):

        x1, y1 = self.Lx_min, self.Lx_loc_y - self.Lx_height/2
        x2, y2 = self.Lx_max, self.Lx_loc_y + self.Lx_height/2
        frame = cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 0, 0), 5)
        frame = cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (255, 255, 255), 3)

        if Lx != -1:
            Lx = max(min(Lx, self.Lx_max), self.Lx_min)
            midx = (x2+x1)/2
            if Lx<(x2+x1)/2:
                frame = cv2.rectangle(frame,(int(Lx), int(y1)), (int(midx), int(y2)), (255,0,0),-1)
            else:
                frame = cv2.rectangle(frame, (int(midx), int(y1)), (int(Lx), int(y2)), (0, 255, 0),-1)

        # Thrust values
        x1, y1 = self.Ry_loc_x - self.Ry_width / 2, self.Ry_min,
        x2, y2 = self.Ry_loc_x + self.Ry_width / 2, self.Ry_max
        frame = cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 0, 0), 5)
        frame = cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (255, 255, 255), 3)

        midx = (y1+y2)/2
        if Ry != -1:
            if Ry<midx:
                # frame = cv2.rectangle(frame, (int(x1), int(Ry)), (int(x2), int(midx)), (0, 0, 0), 5)
                frame = cv2.rectangle(frame, (int(x1), int(Ry)), (int(x2), int(midx)), (0, 255, 0), -1)
            else:
                # frame = cv2.rectangle(frame, (int(x1), int(midx)), (int(x2), int(Ry)), (0, 0, 0), 5)
                frame = cv2.rectangle(frame, (int(x1), int(midx)), (int(x2), int(Ry)), (0,0,255), -1)

        return frame

    def StartDetection(self):
        print("We started our detection")

        while True:
            success, image = self.cap.read()
            if not success:
                print("Ignoring empty camera frame.")
                # If loading a video, use 'break' instead of 'continue'.
                continue

            # run the Hand detection using mediapipe, which results in a list [[-1/1, xcoor, ycoor],[-1/1, xcoor, ycoor]
            all_hands = self.MHD.DetectSingleImg(image)           # mediapipe specific

            # smoothing over history
            self.UpdateDetectedHandsHistory(all_hands=all_hands)

            # so we get stuff from all_hands, which will tell us something:
            wheel_angle_cur, thrust_c, break_c = self.UpdateWheelAndThrustValues(self.xl, self.yr)

            # visualisation
            image = self.Visualisation_threat(image, self.xl, self.yr)

            # update gamepad
            self.UpdateGamePad(thrust_c, break_c)

            # visuals: Draw the center of the detected hands
            for hands_cur in all_hands:
                if hands_cur[0] == 1:
                    image = cv2.circle(image, (int(hands_cur[1]), int(hands_cur[2])), 12, (0, 0, 0), -1)
                    image = cv2.circle(image, (int(hands_cur[1]), int(hands_cur[2])), 10, (255, 255, 255), -1)

            # our smoothed keypoints
            if self.xl != -1 and self.yl != -1:
                image = cv2.circle(image, (int(self.xl), int(self.yl)), 12, (0, 0, 0), -1)
                image = cv2.circle(image, (int(self.xl), int(self.yl)), 10, (255, 0, 255), -1)
            if self.xr != -1 and self.yr != -1:
                image = cv2.circle(image, (int(self.xr), int(self.yr)), 12, (0, 0, 0), -1)
                image = cv2.circle(image, (int(self.xr), int(self.yr)), 10, (255, 0, 255), -1)

            # visuals, draw the wheel and its spokes
            image = cv2.circle(image, self.wheel_cent, self.wheel_r, (0, 0, 0), 7)
            image = cv2.circle(image, self.wheel_cent, self.wheel_r, self.wheel_color_cur, 5)
            image = cv2.line(image, self.wheel_cent, self.wheel_spoke1, (0, 0, 0), 7)
            image = cv2.line(image, self.wheel_cent, self.wheel_spoke1, self.wheel_color_cur, 5)
            image = cv2.line(image, self.wheel_cent, self.wheel_spoke2, (0, 0, 0), 7)
            image = cv2.line(image, self.wheel_cent, self.wheel_spoke2, self.wheel_color_cur, 5)
            image = cv2.line(image, self.wheel_cent, self.wheel_spoke3, (0, 0, 0), 7)
            image = cv2.line(image, self.wheel_cent, self.wheel_spoke3, self.wheel_color_cur, 5)

            # show it
            image = cv2.flip(image, 1)
            cv2.imshow('image', image)
            cv2.waitKey(1)


if __name__ == "__main__":

    VS = VirtualSteering()
    VS.StartDetection()
