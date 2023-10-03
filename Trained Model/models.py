from django.db import models
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver
from datetime import datetime

User = get_user_model()

bookingsChoices = (
    ("Booked", "Booked"),
    ("Free", "Free"),
    ("Occupied", "Occupied"),
)

# Create your models here.
class ParkingSpace(models.Model):
    unique_id = models.CharField(max_length=255, unique=True, blank=False)
    current_state = models.CharField(max_length=255, choices=bookingsChoices, default='Free')
    is_Occupied = models.BooleanField(default=False)

class ParkingHistory(models.Model):
    parking = models.ForeignKey(ParkingSpace, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    when = models.DateTimeField(auto_now=True)
    book_from = models.DateTimeField(blank=False)
    end_from = models.DateTimeField(blank=False)
    state = models.CharField(max_length=255, choices=bookingsChoices)
    is_booking_complete = models.BooleanField(default=False)

    @property
    def is_booking_expired(self):
        return datetime.now() > self.end_from
    
@receiver(post_save, sender=ParkingHistory)
def update_booking_completion(sender, instance, created, **kwargs):
    if not created and instance.is_booking_expired and not instance.is_booking_complete:
        instance.parking.current_state = "Free"
        instance.parking.save()
        instance.is_booking_complete = True
        instance.save()

        # Check ultrasonic sensor value and update parking state
        ultrasonic_sensor_value = get_ultrasonic_sensor_value()
        if ultrasonic_sensor_value < 200:
            instance.parking.current_state = "Occupied"
            instance.parking.save()

def get_ultrasonic_sensor_value():
    # Replace this function with the logic to read the ultrasonic sensor value from MongoDB
    connection_string = "mongodb+srv://username:password@cluster0.wstqz17.mongodb.net/?retryWrites=true&w=majority"
    client = pymongo.MongoClient(connection_string)
    db = client["AdvanceParking"]  # Replace with your actual database name
    collection = db["database"]  # Replace with your actual collection name

    # Assuming the latest document in the collection contains the ultrasonic sensor value
    latest_document = collection.find_one(sort=[('_id', -1)])

    if latest_document:
        ultrasonic_sensor_value = latest_document.get("ultrasonic_sensor_value", 0)
        return ultrasonic_sensor_value
    else:
        return 0
    
@receiver(post_save, sender=ParkingHistory)
def update_booking_completion(sender, instance, created, **kwargs):
    if not created and instance.is_booking_expired and not instance.is_booking_complete:
        instance.parking.current_state = "Free"
        instance.parking.save()
        instance.is_booking_complete = True
        instance.save()