#!/usr/bin/env python
# license removed for brevity
import rospy
from std_msgs.msg import String
import time

def talker():
    pub = rospy.Publisher('speaker', String, queue_size=10)
    rospy.init_node('talker', anonymous=True)
    r = rospy.Rate(1) # 10hz
    while not rospy.is_shutdown():
        str = "I am turtlebot"
        rospy.loginfo(str)
        pub.publish(str)
        time.sleep(5)

if __name__ == '__main__':
    try:
        talker()
    except rospy.ROSInterruptException: pass
