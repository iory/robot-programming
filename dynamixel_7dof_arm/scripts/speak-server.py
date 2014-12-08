#!/usr/bin/python
#-*- coding:utf-8 -*-
import urllib, pycurl, os

import rospy
from std_msgs.msg import String


def callback(data):
    rospy.loginfo("speak {}".format(data.data))
    speakSpeechFromText(data.data)
    # rospy.loginfo(rospy.get_caller_id()+"I heard %s",data.data)

def downloadFile(url, fileName):
    fp = open(fileName, "wb")
    curl = pycurl.Curl()
    curl.setopt(pycurl.URL, url)
    curl.setopt(pycurl.WRITEDATA, fp)
    curl.perform()
    curl.close()
    fp.close()

def getGoogleSpeechURL(phrase, select_english=True):
    if select_english:
        googleTranslateURL = "http://translate.google.com/translate_tts?tl=en&"
    else:
        googleTranslateURL = "http://translate.google.com/translate_tts?tl=ja&"
    parameters = {'q': phrase}
    data = urllib.urlencode(parameters)
    googleTranslateURL = "%s%s" % (googleTranslateURL,data)
    return googleTranslateURL

def speakSpeechFromText(phrase):
    googleSpeechURL = getGoogleSpeechURL(phrase, select_english=True)
    downloadFile(googleSpeechURL,"tts.mp3")
    os.system("mplayer tts.mp3 &")

from sound_play.msg import *

def main():
    rospy.init_node('robotspeaker', anonymous=True)
    rospy.Subscriber("speaker", String, callback)
    rospy.spin()

if __name__ == '__main__':
    main()
