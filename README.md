# AstroPi Project

This project is designed to perform both primary and secondary missions using the AstroPi on the International Space Station.

## Primary Mission

The primary mission of this project is to collect and process scientific data from the AstroPi's sensors. The data collected will be used to study TBD on the International Space Station and to investigate the TBD.

#### Algorithm Description

To achieve this mission, we have developed a data acquisition algorithm that collects data from the AstroPi's sensors and saves it to a log file. The algorithm also captures images of the Earth from the AstroPi's camera and stores them in a separate directory. 
* The Astro Pi device will record the environmental data and will save it in a file log useful for further analysis.
* The file log will have a collection of data for each line. 
* The survey will be accomplished every second and the temperature, humidity and pressure values will be saved by reporting  time of the collection of data, too. 

## Secondary Mission

The secondary mission of this project is to perform image processing on the images collected during the primary mission. The goal is to identify patterns and anomalies in the images and to study the effects of the space environment on Earth and the stars.

#### Data Acquisition Code Description

&nbsp;&nbsp;&nbsp;&nbsp; ▸ To achieve this mission, we have developed a separate data acquisition code that captures images from the AstroPi's camera and saves them to a directory. The code also captures sensor data and stores it in a log file for later processing. 

## Overview

The AstroPi Project is divided into two main parts: data acquisition and image processing.

The data acquisition part of the project collects data from the AstroPi's sensors and saves it to a file. The main entry point for this part of the project is `code/data_acquisition/main.py`, which initializes the sensors, starts data collection, and saves the data to a file.

The image processing part of the project processes the images collected by the AstroPi. The main entry point for this part of the project is `code/image_processing/process_image.py`, which contains the main logic for processing images collected by the AstroPi.

The project also includes documentation, hardware schematics, and 3D models of the AstroPi case and mounting hardware.

## Folder Structure

- `code/`: contains the source code for the project, including the data acquisition and image processing algorithms.
- `data/`: contains the data collected by the AstroPi during the primary mission, including the raw images and sensor data logs.
- `docs/`: contains the project documentation, including the design documents, user manuals, and API references.
- `hardware/`: contains the hardware schematics, 3D models, and parts list for the AstroPi.
- `reports/`: contains the project reports, including the final report and any intermediate reports created during the project.

Please see the individual README files in each folder for more information about their contents and usage.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT) 
See the [LICENSE](LICENSE.txt) file for license rights and limitations (MIT).
