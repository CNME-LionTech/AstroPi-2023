import pandas as pd
import os
import logging
from termcolor import colored
from log_utils import LogColors
from datetime import datetime, timezone, timedelta
import calendar
import re
import cv2
import numpy as np

class ISSInstance:
    def __init__(self, expected_header='CDOSR'):
        self.df = pd.DataFrame()
        self.expected_header = [column.lower() for column in expected_header]

    def load_csv(self, filepath):
        temp_df = pd.read_csv(filepath)
        temp_df.columns = map(str.lower, temp_df.columns)
        self.df = pd.concat([self.df, temp_df])

    def load_csvs_from_directory(self, directory=None, common_header_keywords=None, specific_header_keyword=None):
        if directory is None:
            directory = os.getcwd()  # get current directory if no directory is provided
        if common_header_keywords is None:
            common_header_keywords = ['team', 'timestamp']  # header keywords common to both CSVs
        if specific_header_keyword is None:
            specific_header_keyword = 'LionTech'  # header keyword specific to one CSV
        try:
            suitable_files_found = False
            print(colored(f" * Looking for csv data logs", LogColors.MESSAGE, attrs=["dark"]))
            for root, _, files in os.walk(directory):
                csv_files = [f for f in files if f.endswith('.csv')]
                if not csv_files:
                    continue  # No CSV files in this directory, skip to the next
                print(colored(f"   CSV files found: {csv_files}", LogColors.MESSAGE, attrs=["dark"]))
            
            for filename in csv_files:
                filepath = os.path.join(root, filename)
                temp_df = pd.read_csv(filepath, nrows=1)  # Read the header row
                temp_df.columns = map(str.lower, temp_df.columns)
                # print(temp_df.columns)

                # Check if the CSV file has the common header keywords
                if all(keyword in temp_df.columns for keyword in common_header_keywords):
                    # Re-read the entire file if the header is correct
                    temp_df = pd.read_csv(filepath)  
                    temp_df.columns = map(str.lower, temp_df.columns)
                    self.df = temp_df
                    # print(self.df)
                    suitable_files_found = True
                    
                # if specific_header_keyword in temp_df.columns:
                #     # print(f" KW: {specific_header_keyword} found in {temp_df.columns}")
                #     self.df = pd.concat([self.df2, temp_df])
                #     print(f"Loaded file {filename} with {len(temp_df)} records into df2.")
                #     suitable_files_found = True
                else:
                    print(f"   ! File {filename} does not have the expected headers. Skipping this file.")
            
            if not suitable_files_found:
                print(colored("   ! No suitable CSV files found with the expected headers.", LogColors.ERROR, attrs=["dark"]))
        except FileNotFoundError:
            print(colored(f"   ! Directory {directory} not found.", LogColors.ERROR, attrs=["dark"]))

    def get_position_at_time(self, timestamp):
        closest_row = self.df.iloc[(pd.to_datetime(self.df['timestamp']) - pd.to_datetime(timestamp)).abs().argsort()[:1]]
        return dict(
            latitude=closest_row['latitude'].values[0],
            longitude=closest_row['longitude'].values[0],
            height=closest_row['height'].values[0],
            # temperature=closest_row['temperature'].values[0],
            # humidity=closest_row['humidity'].values[0],
            # pressure=closest_row['pressure'].values[0],
            pitch=closest_row['pitch'].values[0],
            roll=closest_row['roll'].values[0],
            yaw=closest_row['yaw'].values[0]
        )
    
    def get_field_types(self):
        """
        Returns the data types of the fields in the DataFrame.

        # Args:
        #     df (pd.DataFrame): The DataFrame to get the field types from.

        Returns:
            pd.Series: A series containing the data types of the fields in the DataFrame.
        """
        return self.df.dtypes

    def convert_epoch_to_components(self, epoch_timestamp):
        """
        Converts an epoch timestamp to a dictionary of components.

        Args:
            epoch_timestamp (int or float): The epoch timestamp to convert.

        Returns:
            dict: A dictionary with keys 'day', 'month', 'year', 'hour', 'minute', 'second', 'microsecond'.
        """
        dt = datetime.fromtimestamp(epoch_timestamp, tz=timezone.utc)
        components = {
            'day': dt.day,
            'month': dt.month,
            'year': dt.year,
            'hour': dt.hour,
            'minute': dt.minute,
            'second': dt.second,
            'microsecond': dt.microsecond
        }
        return components
    
    def extract_datetime_from_dirname(self, s):
        now = datetime.now()
        month_pattern = r'(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)'
        year_pattern = r'(\d{4})'
        day_pattern = r'(\d{2})'
        time_pattern = r'(\d{2})h(\d{2})m(\d{2})s'
        
        month_match = re.search(month_pattern, s)
        year_match = re.search(year_pattern, s)
        day_match = re.search(day_pattern, s)
        time_match = re.search(time_pattern, s)
        
        if month_match and year_match and day_match:
            year = int(year_match.group(1))
            month_str = month_match.group(0)
            day = int(day_match.group(1))
            
            # Convert month name to number
            datetime_object = datetime.strptime(month_str, "%b")
            month_number = datetime_object.month
            
            # Check if day is valid for that month
            if day > calendar.monthrange(year, month_number)[1]:
                return None

            # Check if year is within valid range and date is not in the future
            if (now.year - 30 <= year <= now.year) and (datetime(year, month_number, day) <= now):
                # Create a datetime object for the found date
                date = datetime(year, month_number, day)
                epoch_time = (date - datetime(1970, 1, 1)).total_seconds()
                
                # Look for a time stamp in the string and update the epoch time
                hours, minutes, seconds = 0, 0, 0
                if time_match:
                    hours = int(time_match.group(1))
                    minutes = int(time_match.group(2))
                    seconds = int(time_match.group(3))
                    
                    time_delta = timedelta(hours=hours, minutes=minutes, seconds=seconds)
                    epoch_time += time_delta.total_seconds()
                    
                return epoch_time

        return None
    
    def extract_datetime_from_dirlist(self, dirlist):
        dt_list = []
        for dir in dirlist:
            dt = self.extract_datetime_from_dirname(dir)
            if dt is not None and dt not in dt_list:
                dt_list.append(dt)
        
        if len(dt_list) == 0:
            return None
        elif len(dt_list) == 1:
            return float(dt_list[0])
        else:
            return float(max(dt_list))

class ImgProcessing:

    def __init__(self, iss_height=408000, iss_speed=7660):
        self.iss_height = iss_height
        self.iss_speed = iss_speed
        self.lk_params = dict(winSize=(15, 15), maxLevel=2, criteria=(cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 0.03))
        self.feature_params = dict(maxCorners=100, qualityLevel=0.3, minDistance=7, blockSize=7)

    def detect_features(self, img):
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        corners = cv2.goodFeaturesToTrack(gray, mask=None, **self.feature_params)
        return corners

    def track_features(self, img1, img2, p0):
        return cv2.calcOpticalFlowPyrLK(img1, img2, p0, None, **self.lk_params)

    def estimate_cloud_height(self, img1, img2, time_between_images, p0):
        ground_distance = self.iss_speed * time_between_images
        pixel_size = ground_distance / img1.shape[1]
        p1, _, _ = self.track_features(img1, img2, p0)
        pixel_displacement = np.linalg.norm(p1 - p0)
        ground_displacement = pixel_displacement * pixel_size
        cloud_height = self.iss_height * (ground_displacement / ground_distance)
        return cloud_height