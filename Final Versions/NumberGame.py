#!/usr/bin/env python
# encoding=utf8

#import modules
import random
import rospy
import os
import sys
import time
import string
from std_msgs.msg import String
from std_msgs.msg import Float64MultiArray
from sensor_msgs.msg import JointState
from thumb.msg import Res
import rosbag
import message_filters
from heapq import nlargest


#initialize variables
frame = 0 #necessary? 2, 1, 0, -1
state = 0
button = 0
statelist = []
buttonlist = []


#script function
def dictionary_set():
    #setting up phrase dictionaries
#check GOOGLE DOC
    #to guess
    guess_dict = {1: 'Is your number {}? Please show me a thumbs up or down.', #2.5 sec
                    2: 'I guess {}. Did I guess your number?', #5.5 sec
                    3: 'Ok I think I know your number. Is it {}?', #5.5 sec
                    4: 'Is {} right? Please show me yes or no.'} #2.5 sec
    #higher or lower
    second_dict = {1: 'Hey {} is your number larger than {}? Show me yes or no.', #7 sec 
                    2: 'Oh no I guessed {}. Did I guess bigger than your number {}?', #7 sec
                    3: 'Hmm is {} bigger than mine {}?'} #4 sec  
    #to encourage play during game 
    encourage_dict = {1:'Good job {}!', #2.5 sec
                    2:'That was your best one so far! Keep up the good work {}!', #7 sec
                    3:'I can tell you are trying really hard {}, nice job!', #5 sec
                    4:'You are getting better at this {}, wow!', #4 sec
                    5:'I know this is hard {}, keep trying!'} #4.5 sec
    clarify_dict = {1: 'Sorry {} I didn’t see that, could you repeat that answer for me please?', #6 sec
                    2: 'I think that was a {}. If I’m right could you make a thumbs {} for me please?', #6.5 sec
                    3: 'Could you please show me that answer again {}?'} #4 sec 
    reward_dict = {1: 'Let’s party!', #2 sec
                    2: 'I have a joke {}, why did a crocodile marry a chicken? Because crock-o-doodle-doodle is a good last name!', #9.5 sec
                    3: 'What is your favorite color {}? Mine is blue.', #5.5 sec
                    4: 'I like playing games with you {}, you’re very fun. Do you like playing with me?'} #8 sec
    return guess_dict,second_dict,encourage_dict,clarify_dict,reward_dict


#camera+button (and feedback) functions
def isThumbUp_Down():
def isThumbUp_Down():
    #wait for 5s to get the best thumb input during 5s, get 50 results totally
    global start_time, name
    
    i = 1
    reses = []
    angles = []
    feed_flag = 1 # to prevent if the child wants to replay
    while(i<20):
        # print i
        #get thumb messages
        msg = rospy.wait_for_message("/thumb_result",String)
        msg = str(msg.data)
        msg_list = msg.split('+')
        res_msg = int(msg_list[0])
        angle_msg = float(msg_list[1])
        reses.append(res_msg)
        angles.append(angle_msg)

        ###comment out this section if beaglebone isn't running###
        #get button messages
        data = rospy.wait_for_message("/openwearable_new",String)
        strdata = str(data)

        # hacky split
        val = strdata.split(':')
        val = val[1].split('\\t')
        temp = val[0].split('"')
        
        global frame
        global state
        global button
        global yescounter
        global nocounter
        global wrongcounter
        
        frame = int(temp[1])
        state = int(val[1])
        button = int(val[2])
        
        print(frame, state, button)
        
        if button == 1:#you have trouble and want to replay
            print("Ok! Please try again.")
            i=0
            reses = []
            angles = []
            feed_flag = 0
        if button == -1:
            #quit the game
            #print("Number of yes: "+str(yescounter)+". Number of no: "+str(nocounter)+". Number wrong: "+str(wrongcounter))
            speechSay_pub.publish("OK! Thanks for playing with me! Bye-bye!")
            choose_behaviors(17)
            sys.exit()
        ### -------------------- ###
        
#        i = i+1
#        if i ==5 and feed_flag == 1:#do feedback function
#            feedback_function(abs(angle_msg),time.time()-start_time,name)
#        time.sleep(0.1)

    print("finished")
    if reses.count(1) > 10: #if thumbs up more than half the time
        angles = nlargest(10, angles)
        res = sum(angles)/len(angles)
        return 1, res
    elif reses.count(-1) > 10: #if thumbs down more than half the time
        angles = [ -x for x in angles]
        angles = nlargest(10, angles)
        res = -sum(angles)/len(angles)
        return -1,res
    else:
        return 0,sum(angles)/len(angles)
    
    
#data collection function
def record_data(camera_angle,time,button,script,image_raw,QT_motor):
    data_list = [camera_angle,time,button,script,image_raw,QT_motor]
    #use rosbag to record data:
    #astra camera data/QT camera data/angle result data/button data/game playing data:sentence said by QT and children response
    #astra camera data should be recorded on the local computer, use compressed
    #QT camera just rosbag /image_raw
    #QT behavior: moter, speech, and emotion topic
        #parametric position of joints
    #QT speech string
    #number of yes, no, button presses (wrong answer)
    #feedback function measurements - thumb angle, name, time, history of gestures, number of clarification/reward/encouragement
    #number of games played
    #any experimenter interventions or errors

    #air pressure, button, orthosis, fram data (done on beaglebone separately)
    print data_list
#export the data to a csv file
#call these lines in script:   ds = TimeSynchronizer( <all the Subscribers for the data>, queue size (10)) 
#ds.registerCallback(record_data)


#orthosis/button/IMU subscriber function 
#see openWearable/ros/ow_subscriber.py for original script 
def callback():
    i=1
    while i<20:
        data = rospy.wait_for_message("/openwearable_new",String)
        strdata = str(data)

        # hacky split
        val = strdata.split(':')
        val = val[1].split('\\t')
        temp = val[0].split('"')
        
        global frame
        global state
        global button
        # global statelist
        # global buttonlist
        
        frame = int(temp[1])
        state = int(val[1])
        button = int(val[2])
        # statelist.append(state)
        # buttonlist.append(button)
        print(frame, state, button)
        i = i+1

        if button == 1:
            return 1
        if button == -1:
            return -1
        
    return 0
    
def listener():
    #global statelist
    #global buttonlist
    #statelist = []
    #buttonlist = []
    #rospy.init_node('listener', anonymous=True)
    #rospy.Subscriber('openwearable', String, callback)
    #rospy.sleep(3) #change sleep value to be amount of time to answer (5 sec?)
    pass


if __name__=="__main__":
    #initialize dictionary
    guess_dict,second_dict,encourage_dict,clarify_dict,reward_dict = dictionary_set()
    
    game_flag = 0 #set to 0 to play intro
    start_time = time.time()
    #name = 'Catherine'
    
    while 1:
        #game always running, until shutdown by children
        # exit_msg = rospy.wait_for_message()
        # if exit_msg.flag == False:
        # once_again = raw_input('Play again? ') #type 'yes' or 'no'
            # use # number = sys.stdin.readline() if prompt
                # number.split()[0]
        print("Do you want to play again? Show me thumbs up/down.")
#edit ^ to not be the same every time
        res, the_angle = isThumbUp_Down()
        if res == -1:
            #game over
            speechSay_pub.publish("I had a great time with you today. Bye-bye!")
#match with transcript
            choose_behaviors(17)
            break
        elif res == 1:
            if game_flag == 0:#the first time to play
                #introduction
                print("Hello, my name is T Q Computer. What is your name? ") 
                name = raw_input('What is your name? ')
                print("Hi   "+name+""",      I would like to play a guessing game with you. 
                In the game I get to ask you questions, and you get to answer yes or no
                by using a thumbs up or a thumbs down with your right arm.
                Let's practice. Can you show me a thumbs up to say yes?""")
                #configuration
                print("Please do a thumbs up!")
                res, the_angle = isThumbUp_Down()
                if res == 1:
                    print("Awesome! Now can you show me a thumbs down to say no?")
                # correctdown = raw_input('Please do a thumb down! ')
                print("Please do a thumbs down!")
                res, the_angle = isThumbUp_Down()
                # if correctdown == 'down':
                if res == -1:
                    print("""Thanks!! During the game, please keep your hand flat on the 
                        arm rest until I ask you a question. If your thumb 
                        is going the wrong way, just push the gren button. And just do your best. 
                        Can you please show me yes if that’s ok?""")
            
            #initialize variables
            nocounter = 0
            yescounter = 0
            wrongcounter = 0
            high = 51
            low = -1

            res, the_angle = isThumbUp_Down()
            if res == 1:
                #play game now
                print("Let's play now! Please think of a number between 1 and 50.") #6.5 sec
                start = input('What is your number? ') #type a number - no rospy.sleep because waiting for input
#we need to input this from camera computer and subscriber to get the number
                print("I'm thinking of your number.") #3 sec
                while start < 51:
                    half_range = int((high-low)/2)
                    current = half_range+low
                    random_add = random.randrange(-half_range,half_range) #never add on outside of the guessing range
                    QT = current+random_add
                    random_guess = random.randrange(1,len(guess_dict))
                    #ask if correct 
                    print(guess_dict[random_guess].format(QT))    

                    res, the_angle = isThumbUp_Down()
                    if res == -1:
                        if QT == start: #prompt if they make a wrong answer about the correctness of QTs guess
                            random_clar = random.randrange(1,len(clar_dict))
                            print(clarify_dict[random_clar].format(name))
                            wrongcounter += 1
                        else:
                            #ask if higher or lower
                            random_second = random.randrange(1,len(second_dict))
                            print(second_dict[random_second].format(name,QT))                          
                            nocounter += 1
                            while True:
                                print("Please do a thumbs up/down to say higher or lower")
#how many times should kids be reminded of this?
                                res, the_angle = isThumbUp_Down()
                                if res == 1:
                                    if QT > start:
                                        random_clar = random.randrange(1,len(clar_dict))
                                        print(clarify_dict[random_clar].format(name))
                                        wrongcounter += 1
                                    else:
                                        low = QT
                                        yescounter += 1
                                        break
                                if res == -1:
                                    if QT < start:
                                        random_clar = random.randrange(1,len(clar_dict))
                                        print(clarify_dict[random_clar].format(name))
                                        wrongcounter += 1
                                    else:
                                        high = QT
                                        nocounter += 1
                                        break #break from inner while loop
                                else:
                                    print("Wrong input! Please input again.")
#what should QT say?

                    elif res == 1:
                        print('Hooray! I got it! Thanks' + name + 'for playing with me. Do you want to play again with me?') #9 sec
#vary this message. also should they play a minimum of 3 games mandatory, the rest optional? 
                        yescounter += 1
                        print("Number of yes: "+str(yescounter)+". Number of no: "+str(nocounter)+". Number wrong: "+str(wrongcounter))
                        game_flag = game_flag + 1
                        break
        else:
            print("Wrong input! Please input again.")
#what should QT say?
