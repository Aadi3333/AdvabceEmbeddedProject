import cv2
import imutils
import numpy as np
import pytesseract
from picamera.array import PiRGBArray
from picamera import PiCamera
import pymongo 

# MongoDB connection URI
mongo_uri = "mongodb+srv://aadi333:Aadimahala70154@cluster0.wstqz17.mongodb.net/?retryWrites=true&w=majority"

# Connect to MongoDB
client = pymongo.MongoClient(mongo_uri)
db = client["NumberPlate"]  
collection = db["detected_numbers"]

# Initialize the PiCamera
camera = PiCamera()
camera.resolution = (640, 480)
camera.framerate = 30
raw_capture = PiRGBArray(camera, size=(640, 480))

# Camera ID
camera_id = 1

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
        
        # Store the detected number in MongoDB
        data = {
            "camera_id": 1,
            "detected_number": detected_number
        }
        collection.insert_one(data)
    
    # Display the processed frame and cropped image
    cv2.imshow("Frame", frame_image)
    cv2.imshow('Cropped', cropped_image)
    
    # Wait for a key press
    key = cv2.waitKey(1) & 0xFF
    
    # Clear the stream for the next frame
    raw_capture.truncate(0)
    
    # If 'q' key is pressed, exit the loop
    if key == ord("q"):
        break

# Close MongoDB connection
client.close()

# Close all windows
cv2.destroyAllWindows()
