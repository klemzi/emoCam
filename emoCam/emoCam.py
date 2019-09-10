import cv2
import cognitive_face as CF
import numpy as np
from datetime import datetime as dt
import time
from iothub_client import IoTHubClient, IoTHubTransportProvider, IoTHubMessage
import json

######### hub connection #############
protocol = IoTHubTransportProvider.HTTP
connection_string = 'HostName=friothub.azure-devices.net;DeviceId=frdevice;SharedAccessKey=IjdRpgo9EbOhGKVuCbHvu85hE9MkLPgM6/uygk9CSNs='
client = IoTHubClient(connection_string, protocol)

# cognitive Face variables
SUBSCRIPTION_KEY = 'f14a1dc6045148ca951ab5c1d1655e1c'
BASE_URL = 'https://faceregdemo.cognitiveservices.azure.com/face/v1.0'
# cognitive Face init
CF.BaseUrl.set(BASE_URL)
CF.Key.set(SUBSCRIPTION_KEY)
# time control variables
start_time = dt.now()
# 30 seconds interval
interval_time = 30

#init capture
cap = cv2.VideoCapture(0)
# parse json
def send_emotions(data):
    for i in range(len(data)):
        emotion = data[i]['faceAttributes']['emotion']
        print ('Sending emotion to IoT Hub')
        try:
            emotion = json.dumps(emotion)
            message = IoTHubMessage(emotion)
            set_content_result = message.set_content_encoding_system_property("utf-8")
            set_content_type_result = message.set_content_type_system_property("application/json")
            client.send_event_async(message, send_confirmation_callback, None)
        except Exception as e:
            print(e)
            return False
        time.sleep(5)
    return True



def send_confirmation_callback(message, result, user_context):
    print("Confirmation recieved for message with result = %s" % (result))
        

# Check if the webcam is opened correctly
if not cap.isOpened():
    raise IOError("Cannot open webcam")

while True:
    ret, frame = cap.read()
    frame = cv2.resize(frame, None, fx=0.5, fy=0.5, interpolation=cv2.INTER_AREA)
    cv2.imshow('Input', frame)

    if ((dt.now() - start_time).seconds > interval_time):
        print ('taking a picture')
        cv2.imwrite('./image.jpg', frame)
        response = CF.face.detect('./image.jpg' ,face_id=False, landmarks=False, attributes='emotion')
        print(response)
        if response:
            ret = send_emotions(response)
            if ret:
                print("delivered to IOT Hub")
        start_time = dt.now()
    c = cv2.waitKey(1)
    if c == 27:
        cap.release()
        cv2.destroyAllWindows()
        break

