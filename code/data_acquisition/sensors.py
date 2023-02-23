from sense_hat import SenseHat
from utilities import convert_angle_to_exif, get_file_time_stamp, create_csv_file, add_csv_data

LOG_FILE_NAME = "LionTech_Log"

class SensorReader:
    def __init__(self):
        self.sense = SenseHat()
        self.sense.clear()

    def clear(self):
        self.sense.clear()

    def read_temperature(self):
        return round(self.sense.get_temperature(), 3)

    def read_temperature_from_pressure(self):
        return round(self.sense.get_temperature_from_pressure(), 3)

    def read_humidity(self):
        return round(self.sense.get_humidity(), 3)

    def read_pressure(self):
        return round(self.sense.get_pressure(), 3)

    def read_accelerations(self):
        """ Function for reading the accelerations on the three axes.
        The reading contains the acceleration on x, y and z-axis, in
        variables rawAccelX, rawAccelY and rawAccelZ."""
        
        self.sense.set_imu_config(False, False, True)
        rawAccel = self.sense.get_accelerometer_raw()
        rawAccelX = round(rawAccel['x'],3)
        rawAccelY = round(rawAccel['y'],3)
        rawAccelZ = round(rawAccel['z'],3)
        
        return rawAccelX, rawAccelY, rawAccelZ

    def read_compass(self):
        """ Function for reading the data from the compass. The readings
        contains both the direction of the North, in variable comp, and
        the magnetic intensity on x, y and z-axis, in variables rawCompX,
        rawCompY and rawCompZ.
        """

        self.sense.set_imu_config(True, False, False)
        comp = round(self.sense.get_compass(),3)
        rawComp = self.sense.get_compass_raw()
        rawCompX = round(rawComp['x'],3)
        rawCompY = round(rawComp['y'],3)
        rawCompZ = round(rawComp['z'],3)

        return comp, rawCompX, rawCompY, rawCompZ

    def read_orientation(self):
        """ Function for reading the SenseHat orientation data. The readings 
        contain the pitch, roll and yaw as separate values.
        """

        self.sense.set_imu_config(False, True, True)
        rawAccel = self.sense.get_orientation()
        pitch = round(rawAccel['pitch'],2)
        roll = round(rawAccel['roll'],2)
        yaw = round(rawAccel['yaw'],2)
        return pitch, roll, yaw

    def read_sensor_data(self):
        temp = self.read_temperature()
        temp_p = self.read_temperature_from_pressure()
        humidity = self.read_humidity()
        pressure = self.read_pressure()
        accelX, accelY, accelZ = self.read_accelerations()
        compass_row, compassX, compassY, compassZ = self.read_compass()
        orientationX, orientationY, orientationZ = self.read_orientation()
        return temp, temp_p, humidity, pressure, accelX, accelY, accelZ, compass_row, compassX, compassY, compassZ, orientationX, orientationY, orientationZ

class SensorDataLogger:
    def __init__(self, log_dir, header = None):
        self.log_dir = log_dir
        self.log_file = create_csv_file(log_dir, LOG_FILE_NAME)

    def log_sensor_data(self, team_name, timestamp, lat, lon, height, temp, temp_p, humidity, pressure, accelx, accely, accelz, compassr, compassx, compassy, compassz, pitch, roll, yaw):
        row = [team_name, timestamp, lon, lat, height, temp, temp_p, humidity, pressure, accelx, accely, accelz, compassr, compassx, compassy, compassz, pitch, roll, yaw]
        add_csv_data(self.log_file, row)
