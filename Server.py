import cv2
import numpy as np
import tello
import pickle
import threading
from datetime import datetime

class save_a_road(self):

    def __init__(self,tello,outputpath):
        """
        Initial all the element of the GUI,support by Tkinter

        :param tello: class interacts with the Tello drone.

        Raises:
            RuntimeError: If the Tello rejects the attempt to enter command mode.
        """        

        self.tello = tello # videostream device
        self.outputPath = outputpath # the path that save pictures created by clicking the takeSnapshot button 
        self.frame = None  # frame read from h264decoder and used for pose recognition 
        self.thread = None # thread of the Tkinter mainloop
        self.stopEvent = None 

        # Set server socket to send Android
        self.serverSocket = socket(AF_INET, SOCK_STREAM)
        self.serverSocket.bind(('', 32990))
        self.serverSocket.listen(3)
        print("The server is ready to receive on port", serverPort)
        
        # control variables
        self.distance = 0.1  # default distance for 'move' cmd
        self.degree = 30  # default degree for 'cw' or 'ccw' cmd

        # if the flag is True, send image to Android
        self.isDectect = False

        # if the flag is TRUE,the auto-takeoff thread will stop waiting for the response from tello
        self.quit_waiting_flag = False

        # start a thread that constantly pools the video sensor for
        # the most recently read frame
        self.stopEvent = threading.Event()
        self.drone_thread = threading.Thread(target=self.videoLoop, args=())
        self.drone_thread.start()

        # connection thread
        self.tcp_thread = threading.Thread(target=self.android_connect, args=())
        # the sending_command will send command to tello every 5 seconds
        self.sending_command_thread = threading.Thread(target = self._sendingCommand)

    def videoLoop(self):
        """
        The mainloop thread
        Raises:
            RuntimeError: To get around a RunTime error that Tkinter throws due to threading.
        """

        try:
            # start the thread that get GUI image and drwa skeleton 
            time.sleep(0.5)
            self.sending_command_thread.start()
            while not self.stopEvent.is_set():                
                system = platform.system()

            # read the frame for GUI show
                self.frame = self.tello.read()
                if self.frame is None or self.frame.size == 0:
                    continue 
            
            # transfer the format from frame to image         
                image = Image.fromarray(self.frame)

            # we found compatibility problem between Tkinter,PIL and Macos,and it will 
            # sometimes result the very long preriod of the "ImageTk.PhotoImage" function,
            # so for Macos,we start a new thread to execute the _updateGUIImage function.
                if system =="Windows" or system =="Linux":                
                    self._updateGUIImage(image)

                else:
                    thread_tmp = threading.Thread(target=self._updateGUIImage,args=(image,))
                    thread_tmp.start()
                    time.sleep(0.03)                                                            
        except RuntimeError as e:
            print("[INFO] caught a RuntimeError")
           
    def _sendingCommand(self):
        """
        start a while loop that sends 'command' to tello every 5 second
        """    

        while True:
            self.tello.send_command('command')        
            time.sleep(5)

    def _setQuitWaitingFlag(self):  
        """
        set the variable as TRUE,it will stop computer waiting for response from tello  
        """       
        self.quit_waiting_flag = True

    def telloTakeOff(self):
        return self.tello.takeoff()                

    def telloLanding(self):
        return self.tello.land()

    def telloFlip_l(self):
        return self.tello.flip('l')

    def telloFlip_r(self):
        return self.tello.flip('r')

    def telloFlip_f(self):
        return self.tello.flip('f')

    def telloFlip_b(self):
        return self.tello.flip('b')

    def telloCW(self, degree):
        return self.tello.rotate_cw(degree)

    def telloCCW(self, degree):
        return self.tello.rotate_ccw(degree)

    def telloMoveForward(self, distance):
        return self.tello.move_forward(distance)

    def telloMoveBackward(self, distance):
        return self.tello.move_backward(distance)

    def telloMoveLeft(self, distance):
        return self.tello.move_left(distance)

    def telloMoveRight(self, distance):
        return self.tello.move_right(distance)

    def telloUp(self, dist):
        return self.tello.move_up(dist)

    def telloDown(self, dist):
        return self.tello.move_down(dist)

    def onClose(self):
        """
        set the stop event, cleanup the camera, and allow the rest of
        
        the quit process to continue
        """
        print("[INFO] closing...")
        self.stopEvent.set()
        del self.tello
        self.root.quit()


    def image_to_string(img):
        encode_param=[int(cv2.IMWRITE_JPEG_QUALITY), 90]
        result, imgencode = cv2.imencode('.jpg', frame, encode_param)
        data = np.array(imgencode)
        strData = data.tostring()

    def android_connect():
        try:
            while True:
        
                (connectionSocket, clientAddress) = self.serverSocket.accept()
                print ("\n\n\n")

                # connection socket #

                while True:

                    print('Connection requested from', clientAddress)
	
                    message = connectionSocket.recv(2048)
                    data = ""

                    if not message :
                        print('disconnected from', clientAddress)
                        break

                    else:
                        data = message.decode()
                        print("Command ", data)
                        print()
                        connectionSocket.send('test'.encode())
 
                connectionSocket.close()

            print("Server Off")    
            serverSocket.close()

        except KeyboardInterrupt:
            print()
            print("Server Off")
            serverSocket.close()

if __name__ == "__main__":
    main()
