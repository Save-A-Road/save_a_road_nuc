import cv2
import numpy as np
from socket import *
import pickle
from datetime import datetime

def image_to_string(img):
    encode_param=[int(cv2.IMWRITE_JPEG_QUALITY), 90]
    result, imgencode = cv2.imencode('.jpg', frame, encode_param)
    data = np.array(imgencode)
    strData = data.tostring()

if __name__ == "__main__":

    try:

        serverPort = 22990
        serverSocket = socket(AF_INET, SOCK_STREAM)
        serverSocket.bind(('', serverPort))
        serverSocket.listen(1)

        print("The server is ready to receive on port", serverPort)
    
        # server socket #

        while True:
        
            (connectionSocket, clientAddress) = serverSocket.accept()
            print('\n\n\n')

            # connection socket #

            while True:

                print('Connection requested from', clientAddress)
	
                message = connectionSocket.recv(2048)
                data = ""

                if not message :

                    print('disconnected from', clientAddress)
                    break

                else:

                    requestCnt = requestCnt + 1
                    data = message.decode()
                    print("Command ", data)
                    print()
                    
                    
            connectionSocket.close()

        print("Server Off")    
        serverSocket.close()

    except KeyboardInterrupt:
        print()
        print("Server Off")
        serverSocket.close()

