import cv2
import mediapipe as mp
from boxing_NewEra_util import slip_punch,slip_direction,is_person_slipping,block_punch,is_person_blocking,move_person,is_person_moving,person_movement,press_button,classify_punch,calculate_angle,get_state, calculate_movement, is_hand_punching,get_important_landmarks
import vgamepad

#pose detection object and drawing
mp_drawing = mp.solutions.drawing_utils
mp_pose= mp.solutions.pose

#create gamepad
gamepad = vgamepad.VX360Gamepad()

#read webcam
webcam = cv2.VideoCapture(0)

#starting person state
state = ['GUARD','GUARD']

#buffers
left_hand_buffer = []
right_hand_buffer = []

left_angle_buffer = []
right_angle_buffer = []


#temporary
punch_count = 0

#angles
left_angle = None
right_angle = None

#punches current and prev
left_punch = None
right_punch = None

prev_left_wrist = None
prev_right_wrist = None

#hips current and prev
left_hip = None
right_hip = None

prev_left_hip = None
prev_right_hip = None

#nose current and prev
nose = None

block_state = False

prev_state = ['GUARD','GUARD']


#setup mediapipe instance
with mp_pose.Pose(min_detection_confidence=0.5,min_tracking_confidence=0.5) as pose:
    while True:
        #read frame
        ret, frame = webcam.read()

        #Recolor image to RGB for mediapipe
        img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img.setflags(write=False)
        #Make detection
        results = pose.process(img)

        #Recolor back to BGR for cv2
        img.setflags(write=True)
        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

        left_wrist = None
        right_wrist = None
        #Extract landmarks
        try:
            landmarks = results.pose_landmarks.landmark

            #get landmarks for important body parts
            left_shoulder, right_shoulder, left_elbow, right_elbow, left_wrist, right_wrist, left_eye,right_eye, left_hip, right_hip, nose = get_important_landmarks(landmarks,mp_pose)

            #angle calculation
            left_angle = calculate_angle(left_shoulder,left_elbow,left_wrist)
            right_angle = calculate_angle(right_shoulder, right_elbow, right_wrist)

            #hip movement calculation
            left_hip_movement = calculate_movement(left_hip, prev_left_hip)
            right_hip_movement = calculate_movement(right_hip, prev_right_hip)

            #get wrist movement for punch detection
            left_hand_movement = calculate_movement(left_wrist, prev_left_wrist)
            right_hand_movement = calculate_movement(right_wrist, prev_right_wrist)

            #update state
            state = get_state(left_angle,right_angle,state)


            #Manage buffers(append when extending + first
            if state[0] == 'EXTENDING':
                left_hand_buffer.append(left_wrist)
                left_angle_buffer.append(left_angle)
            elif state[0] == 'RETRACTING':
                pass
            else:
                left_hand_buffer.clear()
                left_angle_buffer.clear()
            if state[1] == 'EXTENDING':
                right_hand_buffer.append(right_wrist)
                right_angle_buffer.append(right_angle)
            elif state[1] == 'RETRACTING':
                pass
            else:
                right_hand_buffer.clear()
                right_angle_buffer.clear()



            #Punching management
            if is_hand_punching(left_hand_movement,state[0],prev_state[0],len(left_hand_buffer)):
                left_punch = classify_punch('LEFT',left_hand_buffer,left_angle_buffer,left_wrist,left_hand_movement)
                #trigger punch
                press_button(left_punch,gamepad)

                #print('Left Buffer Length: ' + str(len(left_hand_buffer)))
            if is_hand_punching(right_hand_movement,state[1],prev_state[1],len(right_hand_buffer)):
                right_punch = classify_punch('RIGHT', right_hand_buffer, right_angle_buffer, right_wrist, right_hand_movement)
                press_button(right_punch,gamepad)
                #print('Right Buffer Length: ' + str(len(right_hand_buffer)))



            #Movement management
            #if movement detected move player towards direction
            if is_person_moving(state,left_hip_movement,right_hip_movement):

                person_movement_ = person_movement(left_hip_movement[0],right_hip_movement[0])

                move_person(person_movement_,gamepad)



            #blocking management
            block_bool = is_person_blocking(left_wrist,right_wrist,left_eye)
            if block_state != block_bool:
                block_punch(block_bool,gamepad)
                block_state = block_bool



            #slipping management
            if is_person_slipping(state,nose,left_hip,right_hip):
                print("Execiuting slip")

                slip_direction_ = slip_direction(nose, left_hip, right_hip)
                slip_punch(slip_direction_,gamepad)




            #Current and prev hand management
            if left_wrist and right_wrist:
                prev_left_wrist = left_wrist
                prev_right_wrist = right_wrist

            #current and prev state management
            if state[0] and state[1]:
                prev_state[0] = state[0]
                prev_state[1] = state[1]

            #Current and prev hip management
            if left_hip and right_hip:
                prev_left_hip = left_hip
                prev_right_hip = right_hip





        except Exception as e:
            print(e)

        #Render detections
        #mp_drawing.draw_landmarks(img,results.pose_landmarks, mp_pose.POSE_CONNECTIONS)



        if left_punch is not None:
            cv2.putText(img, left_punch, (30, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (78, 210, 0), 2)

        if right_punch is not None:
            cv2.putText(img, right_punch, (30, 90), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

        #visualize frame
        cv2.imshow('webcam',img)

        #break when q pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break




webcam.release()
cv2.destroyAllWindows()