import cv2
import imutils
import numpy as np
import pytesseract
from picamera.array import PiRGBArray
from picamera import PiCamera
import pymongo
import RPi.GPIO as GPIO
import time

# MongoDB connection URI
mongo_uri = f"mongodb+srv://aadi333:Aadimahala70154@cluster0.wstqz17.mongodb.net/?retryWrites=true&w=majority"

# Connect to MongoDB
client = pymongo.MongoClient(mongo_uri)
db = client["AdvanceParking"]
collection = db["database"]

# Initialize the PiCamera
camera = PiCamera()
camera.resolution = (640, 480)
camera.framerate = 30
raw_capture = PiRGBArray(camera, size=(640, 480))

# GPIO setup for ultrasonic sensor
GPIO_TRIGGER = 23
GPIO_ECHO = 24
GPIO.setmode(GPIO.BCM)
GPIO.setup(GPIO_TRIGGER, GPIO.OUT)
GPIO.setup(GPIO_ECHO, GPIO.IN)

# Camera ID
camera_id = 1
ultrasonic_sensor_id = 1  # Add the sensor ID for the ultrasonic sensor

def distance():
    GPIO.output(GPIO_TRIGGER, True)
    time.sleep(0.00001)
    GPIO.output(GPIO_TRIGGER, False)

    StartTime = time.time()
    StopTime = time.time()

    while GPIO.input(GPIO_ECHO) == 0:
        StartTime = time.time()

    while GPIO.input(GPIO_ECHO) == 1:
        StopTime = time.time()

    TimeElapsed = StopTime - StartTime
    distance = (TimeElapsed * 34300) / 2
    return distance

# Capture frames continuously
for frame in camera.capture_continuous(raw_capture, format="bgr", use_video_port=True):
    # Extract the array from the frame
    frame_image = frame.array

    # Convert the frame to grayscale
    gray_frame = cv2.cvtColor(frame_image, cv2.COLOR_BGR2GRAY)
    gray_frame = cv2.bilateralFilter(gray_frame, 11, 17, 17)  # Blur to reduce noise
    edged_frame = cv2.Canny(gray_frame, 30, 200)  # Perform Edge detection

    # Find contours in the edged image
    contours = cv2.findContours(edged_frame.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    contours = imutils.grab_contours(contours)
    contours = sorted(contours, key=cv2.contourArea, reverse=True)[:10]
    screen_contour = None

    # Loop over the contours
    for contour in contours:
        perimeter = cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, 0.018 * perimeter, True)

        # Check if the contour has four vertices
        if len(approx) == 4:
            screen_contour = approx
            break

    # Check if a contour is found
    if screen_contour is not None:
        # Create a mask using the contour
        mask = np.zeros(gray_frame.shape, np.uint8)
        new_image = cv2.drawContours(mask, [screen_contour], 0, 255, -1)
        new_image = cv2.bitwise_and(frame_image, frame_image, mask=mask)

        # Extract the region of interest (ROI) based on the contour
        (x, y) = np.where(mask == 255)
        (top_x, top_y) = (np.min(x), np.min(y))
        (bottom_x, bottom_y) = (np.max(x), np.max(y))
        cropped_image = gray_frame[top_x:bottom_x + 1, top_y:bottom_y + 1]

        # Use Tesseract to extract text from the cropped image
        detected_number = pytesseract.image_to_string(cropped_image, config='--psm 11')
        print("Detected Number is:", detected_number)

        # Get the distance from the ultrasonic sensor
        dist = distance()
        print("Measured Distance = %.1f cm" % dist)

        # Store the detected number, camera ID, and sensor data in MongoDB
        data = {
            "camera_id": camera_id,
            "ultrasonic_sensor_id": ultrasonic_sensor_id,
            "detected_number": detected_number,
            "distance": dist
        }
        collection.insert_one(data)

    # Display the processed frame
    cv2.imshow("Frame", frame_image)

    # Wait for a key press
    key = cv2.waitKey(1) & 0xFF

    # Clear the stream for the next frame
    raw_capture.truncate(0)

    # If 'q' key is pressed, exit the loop
    if key == ord("q"):
        break

# Close MongoDB connection
client.close()

# Clean up GPIO
GPIO.cleanup()

# Close all windows
cv2.destroyAllWindows()
