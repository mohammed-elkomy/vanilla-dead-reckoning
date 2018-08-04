import json

import numpy as np
import pandas as pd
import requests

from UTIL.html_map_generator import launch_with_gmplot


# ------------------------------------------------------------------#
# https://developers.google.com/maps/documentation/roads/snap
def map_matching(df_gps):
    pathText = ""
    for _, row in df_gps.iterrows():
        pathText += str(row['gps_latitude']) + ',' + str(row['gps_longitude']) + '|'

    params = {'interpolate': 'false', 'key': 'AIzaSyAh_kVMPVx5SnrNyvixsrbUiXaocn-tzE4', 'path': pathText[:-1]}
    print(params)
    # gps[['gps_longitude', 'gps_latitude']]
    response = requests.get('https://roads.googleapis.com/v1/snapToRoads', params).text
    print(response)
    response = json.loads(response)
    gps_latitude = []
    gps_longitude = []
    for idx, point in enumerate(response['snappedPoints']):
        gps_latitude.append(point['location']['latitude'])
        gps_longitude.append(point['location']['longitude'])

    print(json.dumps(response, indent=4, sort_keys=True))
    return pd.DataFrame({'gps_latitude': gps_latitude, 'gps_longitude': gps_longitude, 'seconds': df_gps['seconds'].values})


# snapToRoad = map_matchin(gps[:100])
# snapToRoad.to_csv(path_or_buf='../datasets/df_gps_snapped.csv', sep=',')


# ------------------------------------------------------------------#
def plot_gps_launch_chrome_gmplot(df_gps, landmark_lat_long_list_pair=None):
    lat_long = []
    for _, row in df_gps.iterrows():
        lat_long.append([row['gps_latitude'], row['gps_longitude']])

    launch_with_gmplot(lat_long, landmark_lat_long_list_pair)


# ------------------------------------------------------------------#
def low_pass_filter_remove_gravity_component(sensors):
    # 'seconds', 'Accelerator_x', 'Accelerator_y', 'Accelerator_z', 'Azimuth'
    grav_x = np.zeros(shape=[sensors.shape[0]])
    grav_y = np.zeros(shape=[sensors.shape[0]])
    grav_z = np.zeros(shape=[sensors.shape[0]])

    alpha = .8
    for i, row in sensors.iterrows():
        if i != 0:
            grav_x[i] = grav_x[i - 1] * alpha + row['Accelerator_x'] * (1 - alpha)
            grav_y[i] = grav_y[i - 1] * alpha + row['Accelerator_y'] * (1 - alpha)
            grav_z[i] = grav_z[i - 1] * alpha + row['Accelerator_z'] * (1 - alpha)

    return pd.DataFrame({'seconds': sensors['seconds'].values,
                         'Linear_Accelerator_x': sensors['Accelerator_x'] - grav_x, 'Linear_Accelerator_y': sensors['Accelerator_y'] - grav_y, "Linear_Accelerator_z": sensors['Accelerator_z'] - grav_z,
                         "Azimuth": sensors['Azimuth'].values})
