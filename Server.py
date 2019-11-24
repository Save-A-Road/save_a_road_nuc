import tello
import cv2
import os
import sys
import threading
from time import sleep, time

class Save_a_road:
    def __init__(self, ip='192.168.10.3', port=8889):
        self.tello = tello.Tello(ip, port)

        self.frame = None

    # self.frame = self.tello.readFrame()

    def move(self):
        start = time.time()

        if drone.tello.socket is None:
            print ("tello discnnected")
        self.tello.send_command('takeoff')

        while True:
            if time.time() - start > 3:
                break
        self.tello.send_command('land')

    def auto_drive(self):
        drive = threading.Thread(target=self.move)
        drive.start()


def main():
    drone = Save_a_road()

    if not drone.tello.tryConnect():
        print ("Connection failed!")

    drone.auto_drive()

    try:
        if drone.tello.cap is not None:
            drone.tello.cap.release()
            print ('cap release')

        sys.exit(0)

    finally:
        print ('exec finally')
        drone.tello.disconnect()

if __name__ == "__main__":
    main()
