# Vanilla outdoor Dead Reckoning

## Outdoor Localization Task
The dataset contains odometry-sensor readings (
gyroscope, accelerometer,compass, gravity sensor and linear acceleration
) + GPS sensor reading

## Approach 
my approach is simply using a sliding window integrating acceleration signal to get velocity signal and one more integration for displacement signal combined with azimuth angle and for every interval I interpolate to get the next geographical location using geopy functions

I tried both
* Integrating every component
* integrating the magnitude 

I also tried resetting the location with the gps reading every 1 min and the results got so much better.
 