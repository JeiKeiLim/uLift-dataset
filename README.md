# uLift Anaerobic Workout Dataset

<img src="https://raw.githubusercontent.com/JeiKeiLim/mygifcontainer/master/workout_dataset_gifs/13_burpee.gif"/>

[See all 15 workout gifs(59.2 MB)](./docs/workout_types.md)

# 1. Contents
## 1.1 Sensor Type
- 3-aixs acceleromter sensor data

## 1.2 Basic contents
1. Whole session data
2. Annotation for each workout and rest
3. Annotation for the workout type and the number of repetition
4. Segmented data for each workout and rest

## 1.2 Collected Workout Name and Class Number
|Class Number|Workout Name|
|------------|------------|
|00|SQUAT|
|01|PUSH_UP|
|02|LUNGE|
|03|JUMPING_JACK|
|04|BENCH_PRESS|
|05|GOOD_MORNING|
|06|DEAD_LIFT|
|07|PUSH_PRESS|
|08|BACK_SQUAT|
|09|ARM_CURL|
|10|BB_MILITARY_PRESS|
|11|BB_BENT_OVER_ROW|
|12|BURPEE|
|13|LEG_RAISED_CRUNCH|
|14|LATERAL_RAISE|


## 1.3 Dataset description
<img src="https://raw.githubusercontent.com/JeiKeiLim/mygifcontainer/master/workout_dataset_gifs/dataset_description.png"/>
1. Total session number : 158
2. Workout segments : 2,355
3. Rest segments : 2,552
4. Total repetition number : 23,738
5. Average session number per a participant : 4
6. Total collection time : 40 Hours
7. Total workout collection time : 14 Hours
8. Total rest collection time : 26 Hours

# 2. Structure description
## 2.1 Directory Structure
```
(01) 	|-- uLift_sensor_dataset
(02) 		|-- nickname
(03) 			|-- nickname_year_date_time_whole.csv
(04) 			|-- nickname_year_date_time_whole.info
(05) 			|-- nickname_year_date_time_number_(0 to 14).csv
(06) 			|-- nickname_year_date_time_number_(0 to 14).info
(07) 			|-- nickname_year_date_time_number_rest.csv
(08) 			|-- nickname_year_date_time_number_rest.info
(09) 	|-- docs
(10) 		|-- Documentation files
(09) 	|-- dataset_loader
(10) 		|-- python dataset loader
(09) 	|-- matlab_scripts
(10) 		|-- Matlab script files
```

> **(01 - 02)** - uLift\_sensor\_dataset/nickname
>> - Contains sensor dataset
>> - The name of each directory represents the nickname of the participants.

> **(03 - 04)** - nickname\_year\_date\_time\_whole.(csv or info)
>> - Contains a whole data collection session

> **(05 - 06)** - nickname/nickname\_year\_date\_time\_***number***\_***type***.(csv or info)
>> - Contains the segmented workout data
>> - ***number***
>>> - Ascending order number of workout
>> - ***type***
>>> - Workout type number

> **(07 - 08)** - nickname/nickname\_year\_date\_time\_***number***\_rest.(csv or info)
>> - Contains the segmented rest data
>> - ***number***
>>> - Ascending order number of rest

> **(09 - 10)** - scripts
>> - Matlab scripts for fine adjustment of annotation (video dataset is required)


## 2.2 File Extensions
### 2.2.1 .csv
- Contains sensor data
- **Columns**
	- Sensor number,timestamp,accX,accY,accZ
		- Row type
			- 1 : sensor data
			- -1 : Start of the workout
			- -2 : End of the workout
			- -1 and -2 can only be found in whole.csv
		- timestamp
			- The arrival time of the sensor from BLE communication
			- The exact time from the sensor might differ.
		- accX, accY, accZ
			- Accelerometer 3-axis sensor data.
			- When the row type is negative, accZ represents the workout type number. And accX and accY becomes -1

### 2.2.2 .info
- Contains information on the same file name.csv
- **Basic Columns**
	- nick\_name, workout\_experience(month), gender, birthyear, weight(Kg), height(cm)
- **whole.info**
	- Basic Columns
	- Workout class number and name
		- This information is identical to every whole.info
- **workout.info**
	- Basic Columns
	- Workout type number,Workout type name, Repetition number
- **rest.info**
	- Basic Columns
