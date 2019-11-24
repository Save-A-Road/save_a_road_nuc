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

    def move(self):
        # wait for get frame
        sleep(3)

       # waiting for get frame
        start = time()

        while True:

            if time() - start > 5:
                break
            if self.tello.socket is None:
               print ("tello disconnected")
               break

           if self.tello.cap is not None:
               self.frame = self.tello.readFrame()

               if self.frame is not None:
                   print ("Debug / Captured!")
                   self.frame = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
            cv2.imwrite('text.jpg', self.frame)
            self.tello.send_command('takeoff33333')
            sleep (0.5)

        self.tello.send_command('land33333')
        self.tello.disconnect()

        if self.tello.cap is not None:
            self.tello.cap.release()
            print ('cap release')



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
