import tello
import cv2
import os
import sys
import threading
from time import sleep, time
from socket import *

class Save_a_road:
    def __init__(self, ip='192.168.10.3', port=8889):
        self.tello = tello.Tello(ip, port)
        self.frame = None
        self.isDetect = False
        
        try:
            self.android_socket = socket(AF_INET, SOCK_DGRAM)
            self.android_socket.bind(('', 32990))
        except Exception as e:
            print ("Android socket bind fail!")

    def move(self):
        # wait for get frame
        sleep(3)

        # waiting for get frame
        start = time()

        while True:

            # accpet android connection
            android = android_socket.accept()
            threading.Thread(target=self.send_pic_to_android)

            if time() - start > 5:
                break
            if self.tello.socket is None:
               print ("tello disconnected")
               break

            if self.tello.cap is not None:
               self.frame = self.tello.readFrame()

            if self.frame is not None:
                print ("Debug / Captured!")
                pic = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)

                pic = cv2.resize(pic, (700, 525))

                # if 담배가 감지되면 android로 사진 전송:
                #    isDetect = True

            cv2.imwrite('text.jpg', pic)
            self.tello.send_command('takeoff33333')
            sleep (0.5)

        self.tello.send_command('land33333')
        self.tello.disconnect()

        if self.tello.cap is not None:
            self.tello.cap.release()
            print ('cap release')

    def send_pic_to_android(self, conn):
        while True:
            msg = conn.recv(2048)

            if not msg:
                print ("Android disconnect!")
                conn.close()
                return False

            if isDetect == True:
                pic_str = cv2.imencode(self.frame, cv2.COLOR_BGR2RGB)
                conn.send(pic_str.tobytes())
                isDetect = False

        conn.close()
        
    def auto_drive(self):
        drive = threading.Thread(target=self.move)
        drive.start() 

def main():
    drone = Save_a_road()

    if not drone.tello.tryConnect():
        print ("Connection failed!")

    drone.auto_drive()

    sys.exit(0)

if __name__ == "__main__":
    main()
