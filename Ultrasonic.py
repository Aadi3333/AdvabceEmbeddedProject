#Libraries
import pymongo
import RPi.GPIO as GPIO
import time
from datetime import datetime  # Import the datetime module

connection_string = f"mongodb+srv://username:password@cluster0.wstqz17.mongodb.net/?retryWrites=true&w=majority"
client = pymongo.MongoClient(connection_string)
db = client["mydatabase"]
col = db["mycollection"]
 
#GPIO Mode (BOARD / BCM)
GPIO.setmode(GPIO.BCM)
 
#set GPIO Pins
GPIO_TRIGGER = 23
GPIO_ECHO = 24
 
#set GPIO direction (IN / OUT)
GPIO.setup(GPIO_TRIGGER, GPIO.OUT)
GPIO.setup(GPIO_ECHO, GPIO.IN)
 
def distance():
    # set Trigger to HIGH
    GPIO.output(GPIO_TRIGGER, True)
 
    # set Trigger after 0.01ms to LOW
    time.sleep(0.00001)
    GPIO.output(GPIO_TRIGGER, False)
 
    StartTime = time.time()
    StopTime = time.time()
 
    # save StartTime
    while GPIO.input(GPIO_ECHO) == 0:
        StartTime = time.time()
 
    # save time of arrival
    while GPIO.input(GPIO_ECHO) == 1:
        StopTime = time.time()
 
    # time difference between start and arrival
    TimeElapsed = StopTime - StartTime
    # multiply with the sonic speed (34300 cm/s)
    # and divide by 2, because there and back
    distance = (TimeElapsed * 34300) / 2
 
    return distance
 
if __name__ == '__main__':
    try:
        while True:
            dist = distance()
            print("Measured Distance = %.1f cm" % dist)
            current_time = datetime.now()
            device_id = "1"  # Replace with your device ID
            
            # Create a data entry
            data_entry = {"distance": dist, "timestamp": current_time}
            
            # Check if a document with the device ID exists
            existing_data = col.find_one({"_id": device_id})
            
            if existing_data:
                # If the document exists, append the new data entry to an array
                col.update_one({"_id": device_id}, {"$push": {"data": data_entry}})
            else:
                # If the document doesn't exist, create a new one with an array of data entries
                sensor_data = {"_id": device_id, "data": [data_entry]}
                col.insert_one(sensor_data)

            time.sleep(1)

        # Reset by pressing CTRL + C
    except KeyboardInterrupt:
        print("Measurement stopped by User")
        GPIO.cleanup()





