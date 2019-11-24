import tello
import cv2
import datetime
import os
import sys
from time import sleep

class Save_a_road:
    def __init__(ip='192.168.10.3', port=8889):
        self.tello = tello.Tello(ip, port)

        self.frame = None

    # self.frame = self.tello.readFrame()


def main():
    drone = Save_a_road()

    if not drone.tryConnect():
        print ("Connection failed!")

    try:
        if drone.tello.cap is not None:
           drone.tello.cap.release()
            print ('cap release')

        if self.tello.socket is None:
            print ("tello is not connected.")
            return

        drone.tello.send_command('takeoff')
        sleep(3000)
        drone.tello.send_command('land')

        sys.exit(o)

    finally:
        drone.tello.disconnect()
