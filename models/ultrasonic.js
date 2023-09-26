const mongoose = require('mongoose');

module.exports = mongoose.model('Ultrasonic Sensor', new mongoose.Schema({
    device_id: Number,
    sensorData: [
        {
            time: String,
            date: String,
            location: {
                distance: {
                    type: String,
                    required: true
                }
            },
        }
    ]
}, { collection: 'Ultrasonic' }));