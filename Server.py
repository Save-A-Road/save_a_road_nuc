import tello
import cv2
import os
import sys
import threading
from time import sleep, time
from socket import *

class Save_a_road:
    def __init__(self, ip='192.168.10.4', port=8889):
        self.tello = tello.Tello(ip, port)
        self.frame = None
        self.isDetect = False
        
        try:
            self.android_socket = socket(AF_INET, SOCK_STREAM)
            self.android_socket.bind(('', 32990))
            self.android_socket.listen(3)
        except Exception as e:
            print ("Android socket bind fail!")

    def move(self):
        # wait for get frame
        sleep(3)

        # waiting for get frame
        start = time()

        cv2.namedWindow('test', cv2.WINDOW_NORMAL)

        while True:

            # accpet android connection
            #android = self.android_socket.accept()
            #threading.Thread(target=self.send_pic_to_android, demon=True)

            if time() - start > 30:
                break
            if self.tello.socket is None:
               print ("tello disconnected")
               break

            if self.tello.cap is not None:
               self.frame = self.tello.readFrame()

            if self.frame is not None:
                self.frame = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
                cv2.imshow('test', self.frame)

                # if 담배가 감지되면 android로 사진 전송:
                #    isDetect = True

            cv2.imwrite('test.jpg', self.frame)
            self.tello.send_command('takeoff')
            sleep(3)
            self.tello.send_command('up 50')
            sleep(3)
            self.tello.send_command('1forward 50')
            sleep(3)
            self.tello.send_command('cw 45')
            sleep(3)
            self.tello.send_command('ccw 90')
            sleep(3)
            self.tello.send_command('cw 45')
            sleep(3)

        self.tello.send_command('land')
        cv2.destroyAllWindow()

        if self.tello.cap is not None:
            self.tello.cap.release()
            print ('cap release')

        self.tello.disconnect()

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
        drive.join()
        
        print("finish")
 

def main():
    drone = Save_a_road()

    if not drone.tello.tryConnect():
        print ("Connection failed!")

    drone.auto_drive()

    sys.exit(0)

if __name__ == "__main__":
    main()
