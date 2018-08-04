# Vanilla Outdoor Dead Reckoning

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


## Results 
#### Original GPS signal (not perfect of course but not noisy as odometry sensors.. power consuming :) )
![Original](https://raw.githubusercontent.com/mohammed-elkomy/vanilla-dead-reckoning/master/imgs/Screenshot_20180804_015656.png)

#### Dead Reckoned with GPS resetting... less power consuming and still accurate enough
![Dead Reckoned with GPS resetting](https://raw.githubusercontent.com/mohammed-elkomy/vanilla-dead-reckoning/master/imgs/Screenshot_20180804_015632.png)

## Dedication 
In the memory of Dr.Mostafa El-Hamshary who was lecturing us in spite of his illness.. then passed away after two weeks of that sad day. 