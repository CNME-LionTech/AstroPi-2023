import os
from orbit import ISS
from skyfield.api import load, load_file, Loader
from sense_hat import SenseHat
from utilities import create_directory_if_not_exists, convert_angle_to_exif

class ISSData:
    def __init__(self, dir_path):
        self.ephemeris = self.loadEphemeris(dir_path)
        self.time = load.timescale().now()
        self.position = ISS.at(self.time)
        self.subpoint = self.position.subpoint()
        self.latitude = round(self.subpoint.latitude.degrees, 6)
        self.longitude = round(self.subpoint.longitude.degrees, 6)
        self.height = round(self.subpoint.elevation.m, 3)
        self.location = ISS.coordinates()
        #self.iss = ISS(self.ephemeris)

    def loadEphemeris(self, dir_path, ephem_dir='Ephem'):
        # Download ephemeris
        try: 
            ephem_dir = os.path.join(dir_path, ephem_dir)
            create_directory_if_not_exists(ephem_dir)
            ephem_filename = 'de421.bsp'
            ephem_path = os.path.join(ephem_dir, ephem_filename)
            if os.path.exists(ephem_path):
                self.ephemeris = load_file(ephem_path)  # ephemeris DE421
            else:
                load = Loader(ephem_dir)
                self.ephemeris = load('de421.bsp')
            print('- Ephemeris loaded:          ', ephem_filename)

        except Exception as e:
            with open('errorfile', 'w') as f:
                f.write('Mission error: ' + str(e))

    def get_current_position(self):
        # Obtain the current time `t`
        self.time = load.timescale().now()

        # Compute the position of the ISS at time `t`
        self.position = ISS.at(self.time)

        # Compute the coordinates of the Earth location directly beneath the ISS
        self.subpoint = self.position.subpoint()

        self.latitude = round(self.subpoint.latitude.degrees, 6)
        self.longitude = round(self.subpoint.longitude.degrees, 6)
        self.height = round(self.subpoint.elevation.m, 3)

        return self.latitude, self.longitude, self.height

    def read_iss_position(self):
        south, exif_latitude = convert_angle_to_exif(self.latitude)
        west, exif_longitude = convert_angle_to_exif(self.longitude)
        return south, exif_latitude, west, exif_longitude, round(self.height, 2)

    def get_iss_time(self):
        return self.time

    def get_iss_position(self):
        self.subpoint = self.position.subpoint()

        self.latitude = round(self.subpoint.latitude.degrees, 6)
        self.longitude = round(self.subpoint.longitude.degrees, 6)
        self.height = round(self.subpoint.elevation.m, 3)

        return self.latitude, self.longitude, self.height
