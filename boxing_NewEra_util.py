import numpy as np
import vgamepad
import time

#angle calculation for state detection
def calculate_angle(a, b, c):
    a = np.array(a)
    b = np.array(b)
    c = np.array(c)

    radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
    angle = np.abs(radians * 180.0 / np.pi)

    if angle > 180.0:
        angle = 360 - angle
    return angle


#dx,dy,speed of keypoint movement between two frames
def calculate_movement(current, previous):
    if previous is None:
        return [0,0,0]

    dx = current[0] - previous[0]
    dy = current[1] - previous[1]
    speed = np.sqrt(dx ** 2 + dy ** 2)

    keypoint_movement = [dx,dy,speed]
    return keypoint_movement


def is_person_blocking(left_hand,right_hand,eye):

    if left_hand[1] < eye[1] and right_hand[1] < eye[1]:
        return True
    return False



def block_punch(block_bool,gamepad):
    if block_bool:
        gamepad.press_button(vgamepad.XUSB_BUTTON.XUSB_GAMEPAD_RIGHT_SHOULDER)
    else:
        gamepad.release_button(vgamepad.XUSB_BUTTON.XUSB_GAMEPAD_RIGHT_SHOULDER)

    gamepad.update()




def get_state(left_angle, right_angle, state):

    #left hand
    if left_angle > 60 and state[0] == 'GUARD':
        #print(left_angle)
        state[0] = 'EXTENDING'
    elif left_angle <= 50 and state[0] == 'EXTENDING':
        state[0] = 'RETRACTING'
    elif left_angle < 25 and (state[0] == 'RETRACTING'):
        state[0] = 'GUARD'
    # right hand
    if right_angle > 60 and state[1] == 'GUARD':
        #print(right_angle)
        state[1] = 'EXTENDING'
    elif right_angle <= 50 and state[1] == 'EXTENDING':
        state[1] = 'RETRACTING'
    elif right_angle < 25 and (state[1] == 'RETRACTING'):
        state[1] = 'GUARD'

    return state




def is_person_slipping(state,nose,left_hip,right_hip):

    if state[0] == 'GUARD' and state[1] == 'GUARD':
        if nose[0] < right_hip[0]-0.05 or nose[0] > left_hip[0] + 0.05:
            #print('Slipping')
            return True
    return False




def slip_direction(nose,left_hip,right_hip):
    if nose[0] < (right_hip[0]+0.05):
        return 'RIGHT'
    elif nose[0] > (left_hip[0]-0.05):
        return 'LEFT'
    return None



def slip_punch(direction,gamepad):

    if direction is None:
        return

    if direction == 'RIGHT':
        #print('Slip Right')
        gamepad.right_joystick(x_value=30000, y_value=0)
        gamepad.update()

        time.sleep(0.01)

        # Return to center
        gamepad.right_joystick(0, 0)
        gamepad.update()
    elif direction == 'LEFT':
        #print('Slip Left')
        gamepad.right_joystick(x_value=-30000, y_value=0)
        gamepad.update()

        time.sleep(0.01)

        # Return to center
        gamepad.right_joystick(0, 0)
        gamepad.update()




def is_person_moving(state,left_hip_movement,right_hip_movement):

    if (left_hip_movement[2] > 0.04 and right_hip_movement[2] > 0.04) and (state[0] == 'GUARD' and state[1] == 'GUARD'):
        #print('LEFT HIP DX: ' + str(left_hip_movement[0]) + ' RIGHT HIP DX: ' + str(right_hip_movement[0]))
        #print('LEFT HIP SPEED: '+str(left_hip_movement[2])+ ' RIGHT HIP SPEED: ' + str(right_hip_movement[2]))
        return True
    return False




def person_movement(left_hip_movement,right_hip_movement):

    if left_hip_movement > 0.04 and right_hip_movement > 0.04:
        return 'LEFT'
    elif left_hip_movement < -0.04 and right_hip_movement < -0.04:
        return 'RIGHT'

    return None




def move_person(direction,gamepad):
    if direction is None:
        return

    if direction == 'RIGHT':

        gamepad.left_joystick(x_value=30000, y_value=0)
        gamepad.update()

        time.sleep(0.3)

        # Return to center
        gamepad.left_joystick(0, 0)
        gamepad.update()
    elif direction == 'LEFT':
        gamepad.left_joystick(x_value=-30000, y_value=0)
        gamepad.update()

        time.sleep(0.3)

        # Return to center
        gamepad.left_joystick(0, 0)
        gamepad.update()



def is_hand_punching(hand_movement, state, prev_state, buffer_length):

    if hand_movement[2]>0.06:
        if state == 'RETRACTING' and prev_state == 'EXTENDING' and buffer_length>4:
            return True
    return False



def get_important_landmarks(landmarks,mp_pose):
    if landmarks:
        # Get left and right shoulder landmarks
        left_shoulder = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,
                         landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
        right_shoulder = [landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x,
                         landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y]
        # Get left and right elbow landmarks
        left_elbow = [landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].x,
                     landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].y]
        right_elbow = [landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].x,
                      landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].y]
        # Get left and right wrist landmarks
        left_wrist = [landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].x,
                      landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].y]
        right_wrist = [landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].x,
                       landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].y]
        left_eye = [landmarks[mp_pose.PoseLandmark.LEFT_EYE.value].x,
                      landmarks[mp_pose.PoseLandmark.LEFT_EYE.value].y]
        right_eye = [landmarks[mp_pose.PoseLandmark.RIGHT_EYE.value].x,
                    landmarks[mp_pose.PoseLandmark.RIGHT_EYE.value].y]
        left_hip = [landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].x,
                    landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].y]
        right_hip = [landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].x,
                     landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].y]
        nose = [landmarks[mp_pose.PoseLandmark.NOSE.value].x,
                     landmarks[mp_pose.PoseLandmark.NOSE.value].y]
    else:
        left_shoulder = None
        right_shoulder = None
        left_elbow = None
        right_elbow = None
        left_wrist = None
        right_wrist = None
        left_eye = None
        right_eye = None
        left_hip = None
        right_hip = None
        nose = None



    return left_shoulder, right_shoulder, left_elbow, right_elbow, left_wrist, right_wrist, left_eye, right_eye, left_hip, right_hip, nose




############################################################################################

def classify_punch(hand,hand_buffer, angle_buffer,hand_landmarks,hand_movement):


    max_angle_index = find_max_angle_index(angle_buffer)

    dx,dy = get_metavoli(hand_buffer[max_angle_index],hand_landmarks)
    print('DX: ' + str(dx) + ' DY: ' + str(dy))
    print('Y: '+ str(hand_buffer[max_angle_index][1]))


    if abs(dx) > abs(dy):
       if 0.35 < hand_buffer[max_angle_index][1] <0.7:
           return hand + ' HOOK'
       elif hand_buffer[max_angle_index][1] >= 0.7:
           return hand + ' BODY HOOK'
    elif abs(dx) < abs(dy):
       if  hand_buffer[max_angle_index][1] < 0.3:
           return hand + ' STRAIGHT'
       elif hand_buffer[max_angle_index][1] > 0.75:
           return hand + ' UPPERCUT'
    return None




def find_max_angle_index(angle_buffer):

    return angle_buffer.index(max(angle_buffer))



def get_metavoli(max_angle_landmarks,current_landmarks):

    dx = current_landmarks[0] - max_angle_landmarks[0]
    dy = current_landmarks[1] - max_angle_landmarks[1]

    return dx, dy



def press_button(punch,gamepad):

   if punch is None:
       return

   print(punch)

   if punch == 'LEFT STRAIGHT':
       gamepad.press_button(button=vgamepad.XUSB_BUTTON.XUSB_GAMEPAD_A)
       gamepad.update()

       time.sleep(0.01)

       # Release A button
       gamepad.release_button(button=vgamepad.XUSB_BUTTON.XUSB_GAMEPAD_A)
       gamepad.update()
   elif punch == 'RIGHT STRAIGHT':
       gamepad.press_button(button=vgamepad.XUSB_BUTTON.XUSB_GAMEPAD_Y)
       gamepad.update()

       time.sleep(0.01)

       # Release A button
       gamepad.release_button(button=vgamepad.XUSB_BUTTON.XUSB_GAMEPAD_Y)
       gamepad.update()
   elif punch == 'LEFT HOOK':
       gamepad.press_button(button=vgamepad.XUSB_BUTTON.XUSB_GAMEPAD_X)
       gamepad.update()

       time.sleep(0.05)

       # Release A button
       gamepad.release_button(button=vgamepad.XUSB_BUTTON.XUSB_GAMEPAD_X)
       gamepad.update()
   elif punch == 'RIGHT HOOK':
       gamepad.press_button(button=vgamepad.XUSB_BUTTON.XUSB_GAMEPAD_B)
       gamepad.update()

       time.sleep(0.01)

       # Release A button
       gamepad.release_button(button=vgamepad.XUSB_BUTTON.XUSB_GAMEPAD_B)
       gamepad.update()
   elif punch == 'LEFT UPPERCUT':

       # Press L2 (Left Trigger)
       gamepad.left_trigger(value=255)  # 0-255 range

       gamepad.update()

       time.sleep(0.01)
       # Press X
       gamepad.press_button(vgamepad.XUSB_BUTTON.XUSB_GAMEPAD_A)

       gamepad.update()

       time.sleep(0.01)

       gamepad.release_button(vgamepad.XUSB_BUTTON.XUSB_GAMEPAD_A)
       gamepad.update()

       time.sleep(0.01)

       gamepad.left_trigger(value=0)
       gamepad.update()

   elif punch == 'RIGHT UPPERCUT':
       # Press L2 (Left Trigger)
       gamepad.left_trigger(value=255)  # 0-255 range

       gamepad.update()

       time.sleep(0.01)
       # Press X
       gamepad.press_button(vgamepad.XUSB_BUTTON.XUSB_GAMEPAD_Y)

       gamepad.update()

       time.sleep(0.01)

       gamepad.release_button(vgamepad.XUSB_BUTTON.XUSB_GAMEPAD_Y)
       gamepad.update()

       time.sleep(0.01)

       gamepad.left_trigger(value=0)
       gamepad.update()
   elif punch == 'LEFT BODY HOOK':
       # Press L2 (Left Trigger)
       gamepad.left_trigger(value=255)  # 0-255 range

       gamepad.update()

       time.sleep(0.01)
       # Press X
       gamepad.press_button(vgamepad.XUSB_BUTTON.XUSB_GAMEPAD_X)

       gamepad.update()

       time.sleep(0.01)

       gamepad.release_button(vgamepad.XUSB_BUTTON.XUSB_GAMEPAD_X)
       gamepad.update()

       time.sleep(0.01)

       gamepad.left_trigger(value=0)
       gamepad.update()
   elif punch == 'RIGHT BODY HOOK':
       # Press L2 (Left Trigger)
       gamepad.left_trigger(value=255)  # 0-255 range

       gamepad.update()

       time.sleep(0.01)
       # Press X
       gamepad.press_button(vgamepad.XUSB_BUTTON.XUSB_GAMEPAD_B)

       gamepad.update()

       time.sleep(0.01)

       gamepad.release_button(vgamepad.XUSB_BUTTON.XUSB_GAMEPAD_B)
       gamepad.update()

       time.sleep(0.01)

       gamepad.left_trigger(value=0)
       gamepad.update()