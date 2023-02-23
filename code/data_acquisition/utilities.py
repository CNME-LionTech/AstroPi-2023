import os
import csv
import sys
from datetime import datetime

def create_directory_if_not_exists(directory_path):
    """Creates the specified directory if it does not exist."""
    if not os.path.exists(directory_path):
        os.mkdir(directory_path)

def get_file_time_stamp(timestamp=None):
    """Returns a string representing the current time in the format
    'YYYYMonDD_HHhMMmSSs'.
    """
    if not timestamp:
        timestamp = datetime.now()
    return timestamp.strftime('%Y%b%d_%Hh%Mm%Ss')

def create_csv_file(directory, filename, header=None):
    """Creates a CSV file with the specified filename and header in the
    specified directory.
    """
    create_directory_if_not_exists(f'{directory}')
    csv_file = f'{directory}/{filename}_{get_file_time_stamp()}.csv'
    if not header:
        header = ("Team","Timestamp","Longitude", "Latitude","Height","Temperature","Temp_from_pressure","Humidity","Pressure","AccelX","AccelY","AccelZ","CompassMag","CompassX","CompassY","CompassZ","Pitch","Roll","Yaw")
    with open(csv_file, 'w', buffering=1) as f:
        writer = csv.writer(f)
        writer.writerow(header)
    return csv_file

def add_csv_data(filename, data):
    """Adds a row of data to the specified CSV file in the specified directory."""
    with open(filename,'a') as f:
        writer = csv.writer(f)
        writer.writerow(data)

def convert_angle_to_exif(angle):
    """Converts an ephem angle (degrees:minutes:seconds) to an EXIF-appropriate representation."""
    degrees, minutes, seconds = (float(field) for field in str(angle).split(':'))
    exif_angle = '{:.0f}/1,{:.0f}/1,{:.0f}/10'.format(abs(degrees), minutes, seconds*10)
    return degrees < 0, exif_angle

def format_timestamp(timestamp):
    """Formats the given timestamp as a string in the format 'YYYY-Mon-DD HH:MM:SS'."""
    return timestamp.strftime('%Y-%b-%d %H:%M:%S')

# Print iterations progress
def printProgress (iteration, total, prefix = '', suffix = '', decimals = 1):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
    """
    percent = ('{:' + str(decimals+4) + '.' + str(decimals) + 'f}').format(100 * (iteration / float(total)))
    print('{} {}% {}'.format(prefix, percent, suffix), flush=True)
    sys.stdout.flush()

    # Print New Line on Complete
    if iteration == total: 
        print()