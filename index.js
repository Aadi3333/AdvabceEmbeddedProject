const bodyParser = require('body-parser');
const mongoose = require('mongoose');
mongoose.connect('mongodb://127.0.0.1:27017/Ultrasonic');

const sensor = require('./models/ultrasonic');
const { SerialPort } = require('serialport');
const { ReadlineParser } = require('@serialport/parser-readline');

const serial_port = new SerialPort({
    path: 'COM8',
    baudRate: 9600
})  

const parser = serial_port.pipe(new ReadlineParser({ delimiter: '\r\n' }));


let sum = 0;
parser.on('data', async (data) => {

    const array_data = data.split(" ");

    // 1 10:58:46 14:9:2023 10.5

    const sensor_id = array_data[0];
    const time = array_data[1];
    const date = array_data[2];
    const distance = array_data[3];
 

    console.log("Sensor: " + sensor_id);
    console.log("Time: " + time);
    console.log("Date: " + date);
    console.log("Distance: " + distance);
 
    try {
        const abc = await sensor.findOne({ 'device_id': sensor_id }).exec();

        if (abc == null) {
            var document = {
                'device_id': parseInt(sensor_id),
                'sensorData': [
                    {
                        'time': time,
                        'date': date,
                        'location': {
                            'Distance': distance,
                        },

                    }
                ]
            }
            const create = await sensor.create(document);
            console.log(create);
        }

        if (abc != null) {
            console.log(abc);
        }

    } catch (error) {
        console.log(error);
    }

    try {
        const xyz = await sensor.updateOne({ 'device_id': sensor_id }, {
            $push: {
                'sensorData': [
                    {
                        'time': time,
                        'date': date,
                        'location': {
                            'Distance': distance,
                        },

                    }
                ]
            }
        })

        console.log(xyz);

    } catch (error) {
        console.log(error);
    }

    console.log(data);
});