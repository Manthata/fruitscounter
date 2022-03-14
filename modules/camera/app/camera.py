# reference https://github.com/miguelgrinberg/flask-video-streaming/blob/master/camera.py

import os
import cv2
from base_camera import BaseCamera


# setting this allows us to get rtsp stream from different devices
# especially android devices 
os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = "rtsp_transport;udp"

class Camera(BaseCamera):
    """
    This is a subclass of the base camera object and the methods implemented here are responsible for grabbing
    the video frames using cv2.VideoCapture() method. This Method uses two separate threads for fetching and processing
    image frames as such it is said to have a significant FPS and processing speed compared to using the Naive opencv.read() method, thus I used it here.

    NOTE :
    This sub class uses static method to grab frames and there is concern about whether this implementation is the correct use of static methods
    So I will implement the function again in a more pythonic way or in a way that is understandable with everyone.
    Honestly, I used the source code from the repository mentioned above and added a few edits so maybe I should implement my own original threading script.

    TODO:
    Re-implement this script in a much better way so everyone including myself -> @Mantahta William would understand.
    """

    def __init__(self, video_source):
        Camera.video_source = video_source
        super(Camera, self).__init__()

    @staticmethod
    def frames():
        camera = cv2.VideoCapture(Camera.video_source)
        if not camera.isOpened():
            raise RuntimeError("Could not start camera.")
        while True:
            # read current frame
            ret, frame = camera.read()
            if ret:
                yield frame
