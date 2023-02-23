# Description:  Program written by Team LionTech from
#               Colegiul National "Mihai Eminescu" Oradea, Romania for
#               Phase 2 of AstroPi Mission Space Lab competition 2022/2023
# Team Members: Elisa Erzse, Vlad Marian, Mihnea Popovici,
#               Mădălin Toma, Andrei Droj
# Teacher:      Amelia Stoian

from sensors import SensorReader, SensorDataLogger
from collect_images import ImageCollector
from iss_data import ISSData
import datetime as dt
from orbit import ISS
from skyfield.api import load, load_file
import os
from utilities import create_directory_if_not_exists, get_file_time_stamp, printProgress

# Mission parameters
TEAM_NAME = 'LionTech'
DATA_PATH_NAME = 'data'
LOG_PATH_NAME = 'logs'
IMAGE_PATH_NAME = 'images'
MISSION_TIME = 175 # in minutes
PROGRESS_DELTA = 600 #minutes between updating the progress bar

# Working path definition
dir_path = os.path.dirname(os.path.realpath(__file__))
parent_dir = os.path.abspath(os.path.join(dir_path, os.pardir))
data_path = f'{parent_dir}/{DATA_PATH_NAME}'
create_directory_if_not_exists(data_path)

# Datetime variables to store the start time and the current time
start_time = dt.datetime.now()
now_time = dt.datetime.now()
last_photo_time = dt.datetime.now()
file_time_stamp = get_file_time_stamp(start_time)
timescale = load.timescale()


if __name__ == '__main__':
    # Main programm
    print('LionTech Mission Space Lab')
    print('- Systems checked at:         {}'.format(now_time.strftime('%Y-%b-%d %Hh%Mm%Ss')))
    print('- Data collection started at: {}'.format(now_time.strftime('%Y-%b-%d %Hh%Mm%Ss')))

    # Setup for log, image and error directory paths
    image_dir = f'{data_path}/{IMAGE_PATH_NAME}'
    log_dir = f'{data_path}/{LOG_PATH_NAME}'
    errorfilename = log_dir + '/Errors_{}.txt'.format(file_time_stamp)

    # Header names for collected data
    header_values = [TEAM_NAME, 'Timestamp', 
                    'Longitude', 'Latitude', 'Height', 
                    'Temperature', 'Temp_from_pressure',
                     'Humidity', 'Pressure', 
                     'AccelX', 'AccelY', 'AccelZ', 
                     'CompassMag', 'CompassX', 'CompassY', 'CompassZ', 
                     'Pitch', 'Roll', 'Yaw']
    header = ','.join(header_values)

    # Create ISS instance
    iss = ISSData(dir_path)
    print('- Collecting data .................................')

    # Create Image, Sensor data collectors and Logger instances
    collector = ImageCollector(image_dir)
    sensor_reader = SensorReader()
    logger = SensorDataLogger(log_dir, header)
    
    # Update ISS position
    iss_position = iss.get_current_position()

    # Start mission iteration
    current_iteration = 0
    while (now_time < start_time + dt.timedelta(minutes = MISSION_TIME)):
        try:
            # Update time
            now_time = dt.datetime.now()

            # Update sensor readings and images and log the results
            sensor_data = sensor_reader.read_sensor_data()
            collector.capture_image(image_dir)
            logger.log_sensor_data(TEAM_NAME, now_time.timestamp(), *iss_position, *sensor_data)
            
            last_iteration = current_iteration
            current_iteration = (now_time - start_time).seconds // PROGRESS_DELTA  # measuring time progress by 10 minutes 
            if current_iteration != last_iteration:
                printProgress(current_iteration * 10, MISSION_TIME, prefix = '-   Progress:', suffix = 'Complete')


        except Exception as e:
            with open(errorfilename, 'a') as f:
                f.write('Mission error: ' + str(e) + '\n')

    print('- Mission ended at:           {}'.format(now_time.strftime('%Y-%b-%d %Hh%Mm%Ss')))
    print('- Total runtime:              {}'.format((now_time - start_time)))
    print('Mission accomplished - Team LionTech')
    sensor_reader.clear()