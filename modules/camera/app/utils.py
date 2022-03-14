import cv2
import numpy as np
import logging


def resize_image(image: np.ndarray):
    """resize the input image and return a jpeg encoded image"""
    k = 5
    width = int((image.shape[1]) / k)
    height = int((image.shape[0]) / k)
    # resize the image by resize() function of openCV library

    scaled = cv2.resize(image, (width, height), interpolation=cv2.INTER_AREA)
    return cv2.imencode(".jpg", scaled)[1]

def image2bytes(image):
    """
    This function checks if the input image is np.ndarray or not and if the image is np.ndarray(opencv format) then it's converted to image string
    else it's converted to image array and then to image string
    """

    # if isinstance(image, np.udarray) is better than using type 
    if isinstance(image, np.ndarray):
        image_string = cv2.imencode(".jpg", image)[1].tobytes()

        return image_string
    else:
        image = np.array(image, dtype=np.uint8)
        image_string = cv2.imencode(".jpg", image)[1].tobytes()

        return image_string


def get_logger(logger_name: str) -> logging.Logger:
    """ this is a logger funtion """
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler()
    handler.setLevel(logging.INFO)
    logger.addHandler(handler)
    return logger
