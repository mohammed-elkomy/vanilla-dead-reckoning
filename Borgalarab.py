import math

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from UTIL.geoDistances import geopyDistance, myGeoDistance
from UTIL.utils_main import plot_gps_launch_chrome_gmplot, low_pass_filter_remove_gravity_component
from configs import use_real_time_gps_observations, get_observation_every, config, window

sensors = pd.read_csv('datasets/borgalarab/df_sensors.csv')
sensors = sensors[['seconds', 'Accelerator_x', 'Accelerator_y', 'Accelerator_z', 'Linear_Accelerator_x', 'Linear_Accelerator_y', 'Linear_Accelerator_z', 'Azimuth']]
sensors.sort_values('seconds')

gps = pd.read_csv('datasets/borgalarab/df_gps.csv')
gps = gps[['seconds', 'gps_latitude', 'gps_longitude', 'gps_speed']]
gps.sort_values('seconds')
samples_per_sec = gps['seconds'].shape[0] // (gps['seconds'].iloc[-1] - gps['seconds'].iloc[0])

# no need to filter the accelerometer signal .. the file contains the linear acceleration itself
# sensors['Accelerator_y'] = sensors['Accelerator_y'] - 9.81 # remove gravity :D
# sensors = low_pass_filter_remove_gravity_component(sensors)
# sensors.to_csv('sdsdsd.csv')

sensors = sensors[sensors['seconds'] > gps['seconds'][0]]
gps = gps[gps['seconds'] < sensors['seconds'].iloc[-1]]

print("test 1")
print(geopyDistance(lat=52.20472, long=0.14056, bearingAngleDeg=90, distanceMeasuredInKM=15))
print(myGeoDistance(lat=52.20472, long=0.14056, bearingAngleDeg=1.57, distanceMeasuredInKM=15))
print("test 2")
print(geopyDistance(lat=42.189275, long=-76.85823, bearingAngleDeg=30, distanceMeasuredInKM=.5 * 1.60934))
print(myGeoDistance(lat=42.189275, long=-76.85823, bearingAngleDeg=math.pi / 6, distanceMeasuredInKM=.5 * 1.60934))

acc_norm = np.array(np.sqrt(sensors['Linear_Accelerator_x'] * sensors['Linear_Accelerator_x'] + sensors['Linear_Accelerator_y'] * sensors['Linear_Accelerator_y'] + sensors['Linear_Accelerator_z'] * sensors['Linear_Accelerator_z']))

seconds = np.array(sensors['seconds'])
Azimuth_readings = np.array(sensors['Azimuth'])
velocity_norm = np.zeros(shape=acc_norm.shape)
distance_norm = np.zeros(shape=acc_norm.shape)

lat = np.zeros(shape=acc_norm.shape)
long = np.zeros(shape=acc_norm.shape)

landmark_lat = []
landmark_long = []

lat[0:3] = gps['gps_latitude'][0]
long[0:3] = gps['gps_longitude'][0]
velocity_norm[0:3] = gps['gps_speed'][0]

print("initializations\n", gps[:1], '\n')


def integrate_after_norm_no_reset():  # just integration
    for index in range(3, acc_norm.shape[0]):
        deltaT = (seconds[index] - seconds[index - 1])
        velocity_norm[index] = velocity_norm[index - 1] + acc_norm[index] * deltaT
        distance_norm[index] = distance_norm[index - 1] + velocity_norm[index] * deltaT + .5 * acc_norm[index] * deltaT * deltaT

    for index in range(3, acc_norm.shape[0]):
        lat[index], long[index] = geopyDistance(lat=lat[index - 1], long=long[index - 1], distanceMeasuredInKM=(distance_norm[index] - distance_norm[index - 1]) / 1000.0, bearingAngleDeg=Azimuth_readings[index])

    pointsToPlot = 100
    plt.plot(seconds[4:pointsToPlot], acc_norm[4:pointsToPlot])
    plt.plot(seconds[4:pointsToPlot], velocity_norm[4:pointsToPlot])
    plt.plot(seconds[4:pointsToPlot], distance_norm[4:pointsToPlot])
    plt.legend(['Acceleration', 'Velocity', 'Distance'])


def RK4_after_norm_no_reset():  # RK4
    for index in range(3, acc_norm.shape[0]):
        # https://en.wikipedia.org/wiki/Runge%E2%80%93Kutta_methods
        deltaT = (seconds[index] - seconds[index - 1])
        avg_acc = (acc_norm[index] + 2 * acc_norm[index - 1] + 2 * acc_norm[index - 2] + acc_norm[index - 3]) / 6.0
        velocity_norm[index] = velocity_norm[index - 1] + avg_acc * deltaT
        avg_velo = (velocity_norm[index] + 2 * velocity_norm[index - 1] + 2 * velocity_norm[index - 2] + velocity_norm[index - 3]) / 6.0
        distance_norm[index] = distance_norm[index - 1] + avg_velo * deltaT + .5 * avg_acc * deltaT * deltaT

    for index in range(3, acc_norm.shape[0]):
        lat[index], long[index] = geopyDistance(lat=lat[index - 1], long=long[index - 1], distanceMeasuredInKM=(distance_norm[index] - distance_norm[index - 1]) / 1000.0, bearingAngleDeg=Azimuth_readings[index])

    pointsToPlot = 100
    plt.plot(seconds[4:pointsToPlot], acc_norm[4:pointsToPlot])
    plt.plot(seconds[4:pointsToPlot], velocity_norm[4:pointsToPlot])
    plt.plot(seconds[4:pointsToPlot], distance_norm[4:pointsToPlot])
    plt.legend(['Acceleration', 'Velocity', 'Distance'])





def integrate_after_norm_window_reset():  # window based
    global lat
    global long
    global velocity_norm

    current_lat_long_ind = 1
    for index in range(1, acc_norm.shape[0] - window, window):
        current_dist = 0
        current_velo = 0
        for i in range(window):
            subIndex = index + i
            deltaT = (seconds[subIndex] - seconds[subIndex - 1])
            current_velo = current_velo + acc_norm[subIndex] * deltaT
            current_dist = current_dist + current_velo * deltaT + .5 * acc_norm[subIndex] * deltaT * deltaT

        lat[current_lat_long_ind], long[current_lat_long_ind] = geopyDistance(lat=lat[current_lat_long_ind - 1], long=long[current_lat_long_ind - 1], distanceMeasuredInKM=current_dist / 1000.0, bearingAngleDeg=np.average(Azimuth_readings[index:index + window]))

        if use_real_time_gps_observations and current_lat_long_ind % ((samples_per_sec * get_observation_every) // window) == 0:
            factor = round(sensors.shape[0] / gps.shape[0])
            lat[current_lat_long_ind] = gps['gps_latitude'].iloc[index // factor]
            long[current_lat_long_ind] = gps['gps_longitude'].iloc[index // factor]

            landmark_lat.append(lat[current_lat_long_ind])
            landmark_long.append(long[current_lat_long_ind])

        velocity_norm[current_lat_long_ind] = current_velo
        current_lat_long_ind += 1

    lat = lat[:current_lat_long_ind]
    long = long[:current_lat_long_ind]
    velocity_norm = velocity_norm[:current_lat_long_ind]


def integrate_before_norm_no_window_reset():
    acceleration = np.array([sensors['Linear_Accelerator_x'].values, sensors['Linear_Accelerator_y'].values, sensors['Linear_Accelerator_z'].values]).transpose()
    velocity = np.zeros(shape=(acc_norm.shape[0], 3))
    distance = np.zeros(shape=(acc_norm.shape[0], 3))

    for i in range(1, acceleration.shape[0]):
        deltaT = (seconds[i] - seconds[i - 1])
        velocity[i] = velocity[i - 1] + acceleration[i] * deltaT
        distance[i] = distance[i - 1] + velocity[i] * deltaT + .5 * acceleration[i] * deltaT * deltaT
        if i % 40 == 0:
            velocity[i] = distance[i] = np.zeros(shape=[1, 3])

    velocity[0] = velocity[1]
    distance[0] = distance[1]
    for index in range(3, acc_norm.shape[0]):
        lat[index], long[index] = geopyDistance(lat=lat[index - 1], long=long[index - 1],
                                                distanceMeasuredInKM=(np.linalg.norm(distance[index])) / 1000.0,
                                                bearingAngleDeg=Azimuth_readings[index])

        if use_real_time_gps_observations and index % (samples_per_sec * get_observation_every) == 0:
            factor = round(sensors.shape[0] / gps.shape[0])

            lat[index] = gps['gps_latitude'].iloc[index // factor]
            long[index] = gps['gps_longitude'].iloc[index // factor]

            landmark_lat.append(lat[index])
            landmark_long.append(long[index])


if config == 1:
    integrate_after_norm_no_reset()
elif config == 2:
    RK4_after_norm_no_reset()
elif config == 3:
    integrate_after_norm_window_reset()
elif config == 4:
    integrate_before_norm_no_window_reset()

plot_gps_launch_chrome_gmplot(gps)

gps_from_sensors = pd.DataFrame({'gps_longitude': long, 'gps_latitude': lat, 'gps_speed': velocity_norm})
print("---------sensors---------")
print(sensors.head(10))
print(sensors.tail(10), end='\n\n')

print("---------original lat/long---------")
print(gps.head(10))
print(gps.tail(10))
print("---------predicted lat/long---------")
print(gps_from_sensors.head(10))
print(gps_from_sensors.tail(10))

plot_gps_launch_chrome_gmplot(gps_from_sensors, (landmark_lat, landmark_long))
plt.show()
