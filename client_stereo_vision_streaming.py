import socket
import pickle
import numpy as np
import cv2
import base64
import sys
import struct
import time
from picamera2 import Picamera2, Preview
from picamera.array import PiRGBArray

class stereo_camera_streaming():
    def __init__(self, server_ip:str, server_port:int) -> None:
        self._server = server_ip
        self._port = server_port
        self._client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._client.setsockopt(socket.SOL_SOCKET,socket.SO_SNDBUF, 10000000)
        self._picamLeft = Picamera2(0)
        self._picamRight = Picamera2(1)

        rawCaptureLeft = PiRGBArray(self._picamLeft)
        rawCaptureRight = PiRGBArray(self._picamRight)
        configLeft = self._picamLeft.create_video_configuration(buffer_count=6, main={"size":(640,480)})
        self._picamLeft.configure(configLeft)

        configRight = self._picamRight.create_video_configuration(buffer_count=6, main={"size":(640,480)})
        self._picamRight.configure(configRight)

        self._picamLeft.start()
        self._picamRight.start()
        time.sleep(2)

    def start(self):
        self._client.connect((self._server, self._port))
        while True:
            image_arr_left = self._picamLeft.capture_array()
            image_arr_right = self._picamRight.capture_array()
            frame_left = cv2.cvtColor(image_arr_left, cv2.COLOR_RGB2BGR)
            frame_rigth = cv2.cvtColor(image_arr_right, cv2.COLOR_RGB2BGR)
            ret1, buff1 = cv2.imencode(".jpg", frame_left, [int(cv2.IMWRITE_JPEG_QUALITY),30])
            ret2, buff2 = cv2.imencode(".jpg", frame_rigth, [int(cv2.IMWRITE_JPEG_QUALITY),30])
            imageDict = {'ImageLeft': buff1, 'ImageRigth': buff2}
            pickleData = pickle.dumps(imageDict)
            size = len(pickleData)
            self._client.sendall(struct.pack(">L", size) + pickleData)
            if cv2.waitKey(1) & 0xFF == 27:
                break

SERVER = "192.168.0.104"
PORT = 5055
print(f"[CLIENT] conection to HOST:{(SERVER, PORT)}")

stereo_cam_streaming = stereo_camera_streaming(SERVER, PORT)
stereo_cam_streaming.start()





