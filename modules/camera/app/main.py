# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for
# full license information.

from email.mime import image
import time
import sys
import os
import requests
import json
from azure.iot.device import IoTHubModuleClient, Message
from camera import Camera
from utils import image2bytes, resize_image
import logging
import cv2
# global counters
SENT_IMAGES = 0

# global client
CLIENT = None

# Send a message to IoT Hub
# Route output1 to $upstream in deployment.template.json
def send_to_hub(strMessage):
    """Send classification results to iothub"""
    message = Message(bytearray(strMessage, 'utf8'))
    CLIENT.send_message_to_output(message, "output1")
    global SENT_IMAGES
    SENT_IMAGES += 1
    print( f"Total images sent: {SENT_IMAGES}")

# Send an image to the image classifying server
# Return the JSON response from the server with the prediction result
def send_frame_for_processing(frame, imageProcessingEndpoint):
    """Send the image frames to the processing engine"""

    headers = {'Content-Type': 'application/octet-stream'}
    image_string = image2bytes(frame)
    
    try:
        response = requests.post(imageProcessingEndpoint, headers = headers, data = image_string)
        print("Response from classification service: (" + str(response.status_code) + ") " + json.dumps(response.json()) + "\n")
    except Exception as error_:
        print(error_)
        print("No response from classification service")
        return None

    return json.dumps(response.json())

def get_inferences(frame, image_processing_endpoint, stage):
    """
    Get inferences from the processing end poin

    When developing on the local environment you can run the program without connecting to iot edge
    
    """

    if stage == "dev":
        
        try:
            classification = send_frame_for_processing(frame, image_processing_endpoint)
            if classification:
                return classification
        except KeyboardInterrupt:
            print ( "IoT Edge module sample stopped" )
    
    else:
        try:
            print ( "Simulated camera module for Azure IoT Edge. Press Ctrl-C to exit." )

            try:
                global CLIENT
                CLIENT = IoTHubModuleClient.create_from_edge_environment()
                CLIENT.connect()
            except Exception as iothub_error:
                print ( f"Unexpected error {iothub_error} from IoTHub")
                return

            print ( "The sample is now sending images for processing and will indefinitely.")

            while True:
                classification = send_frame_for_processing(frame, image_processing_endpoint)
                if classification:
                    send_to_hub(classification)
                    return classification
        except KeyboardInterrupt:
            print ( "IoT Edge module sample stopped" )

if __name__ == '__main__':
    #TODO : Put varialbes in the deployment template : VIDEO_SOURCE 
    
    try:
        #video_source = os.getenv("VIDEO_SOURCE")
        VIDEO_SOURCE = -1
        CAMERA_OBJ = Camera(VIDEO_SOURCE)
        time.sleep(10)

        STAGE = os.getenv("STAGE")
        logging.info("stage = ${STAGE}")
        logging.info("stage = ${VIDEO_SOURCE}")
        IMAGE_PROCESSING_ENDPOINT = os.getenv('IMAGE_PROCESSING_ENDPOINT', "http://localhost:8000/classifier/image")
    except ValueError as error:
        print ( error )
        sys.exit(1)

    while True:
            FRAME_ORG = CAMERA_OBJ.get_frame()
            FRAME_PROCESSED = resize_image(FRAME_ORG)
            # get inferences
            if ((FRAME_ORG.any() and IMAGE_PROCESSING_ENDPOINT) != ""):
                inferences = get_inferences(FRAME_PROCESSED, IMAGE_PROCESSING_ENDPOINT, stage=STAGE)
            else: 
                print ( "Error: Image path or image-processing endpoint missing" )
            # Display the resulting frame
            cv2.imshow('frame', FRAME_ORG)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        # Destroy all the windows
    cv2.destroyAllWindows()

