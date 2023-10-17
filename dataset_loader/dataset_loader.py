import pandas as pd
import os
import numpy as np
from tqdm import tqdm
from p_tqdm import p_map
from functools import partial


class SensorData:
    CSV_COLUMN_NAMES = ["SensorIndex", "Timestamp", "accX", "accY", "accZ"]

    def __init__(self, root, file_name, fix_timestamp=False):
        self.file_name = file_name
        self.root = root

        self.csv_path = root + "/" + file_name + ".csv"
        self.raw_data = pd.read_csv(self.csv_path, names=SensorData.CSV_COLUMN_NAMES)

        self.raw_data = self.raw_data.drop_duplicates(subset="Timestamp", keep="last")
        self.raw_data.reset_index(inplace=True, drop=True)

        self.sensor_data = self.raw_data[["accX", "accY", "accZ"]].values
        self.total_time_sec = (
            self.raw_data["Timestamp"].iloc[-1] - self.raw_data["Timestamp"].iloc[0]
        ) / 1000
        self.sampling_rate = self.raw_data.shape[0] / self.total_time_sec

        # Fix timestamp jerk caused by BLE communication.
        if fix_timestamp:
            self.fix_timestamp()

        tmp = file_name.split("_")
        self.file_date = int(tmp[1] + tmp[2])
        self.file_time = int(tmp[3])

        self.info_path = root + "/" + file_name + ".info"

        with open(self.info_path) as f:
            read_line = f.readline()
            split_info = read_line.split(",")

            self.user_nick_name = split_info[0]
            self.user_workout_experience = int(split_info[1])
            self.user_gender = split_info[2]
            self.user_birth_year = int(split_info[3])
            try:
                self.user_weight = float(split_info[4])
            except ValueError:
                self.user_weight = -1

            try:
                self.user_height = float(split_info[5].replace("\n", ""))
            except ValueError:
                self.user_height = -1

            self.info_not_processed = ""
            read_line = f.readline()
            while read_line:
                self.info_not_processed += read_line
                read_line = f.readline()

    def fix_timestamp(self):
        t_stamp = self.raw_data["Timestamp"]
        self.raw_data["Timestamp"] = np.linspace(
            t_stamp[0], t_stamp[t_stamp.shape[0] - 1], t_stamp.shape[0], dtype="long"
        )

    def get_x(self):
        return self.raw_data["Timestamp"].values

    def get_dx(self):
        return self.get_x() - self.get_x()[0]

    def print_user_info(self):
        print(
            "NickName : ",
            self.user_nick_name,
            ", " "WorkoutExperience : ",
            self.user_workout_experience,
            "month, ",
            "Gender : ",
            self.user_gender,
            ", BirthYear : ",
            self.user_birth_year,
            ", " "Weight : ",
            self.user_weight,
            ", Height : ",
            self.user_height,
            sep="",
        )

    def print_path(self):
        if issubclass(type(self), WorkoutSegment):
            print("WORKOUT!!!")
        elif issubclass(type(self), RestSegment):
            print("REST!!!")
        elif issubclass(type(self), WholeSession):
            print("WHOLE!!")

        print("csv :", self.csv_path)
        print(self.raw_data.head())
        print(self.sampling_rate)


class WorkoutSegment(SensorData):
    def __init__(self, root, file_name):
        super(WorkoutSegment, self).__init__(root, file_name)

        split_info = self.info_not_processed.split(",")
        self.workout_class_number = int(split_info[0])
        self.workout_class_name = split_info[1]
        self.repetition_number = int(split_info[2])

        del self.info_not_processed

    def print_workout_info(self):
        print(
            self.info_path,
            "::",
            self.workout_class_number,
            ":",
            self.workout_class_name,
            " :: ",
            self.repetition_number,
            sep="",
        )


class RestSegment(SensorData):
    def __init__(self, root, file_name):
        super(RestSegment, self).__init__(root, file_name)

        del self.info_not_processed


class WholeSession(SensorData):
    def __init__(self, root, file_name, verbose=0):
        super(WholeSession, self).__init__(root, file_name)

        self.workout_class_info = self.read_workout_info()
        del self.info_not_processed

        # Validate and save the annotation
        self.annotate_data = self.raw_data.query("SensorIndex < 0")
        self.workout_state = np.zeros(self.raw_data.shape[0])

        is_workout = False
        workout_start_index = 0
        for annotate_index in range(0, self.annotate_data.shape[0]):
            sensor_index = self.annotate_data.index[annotate_index]
            sensor_annotate = self.annotate_data.loc[sensor_index]["SensorIndex"]

            if verbose > 3:
                print(
                    "Sensor data annotation",
                    sensor_annotate,
                    is_workout,
                    self.file_name,
                    self.raw_data["Timestamp"].iloc[sensor_index],
                    is_workout,
                )

            if sensor_annotate == -1 and not is_workout:
                is_workout = True
                workout_start_index = sensor_index
            elif sensor_annotate == -2 and is_workout:
                is_workout = False
                self.workout_state[workout_start_index:sensor_index] = 1
            else:
                raise Exception(
                    "Sensor data annotation error!",
                    sensor_annotate,
                    is_workout,
                    self.file_name,
                    self.raw_data["Timestamp"].iloc[sensor_index],
                    is_workout,
                )

        self.workout_state = np.delete(self.workout_state, self.annotate_data.index)
        self.sensor_data = np.delete(self.sensor_data, self.annotate_data.index, axis=0)
        self.raw_data = self.raw_data.drop(self.annotate_data.index).reset_index()

    def read_workout_info(self):
        workout_class_info = []

        split_info = self.info_not_processed.split("\n")
        for info in split_info:
            if len(info) < 1:
                continue

            this_split_info = info.split(",")
            class_number = this_split_info[0]
            class_name = this_split_info[1]
            workout_class_info.append([int(class_number), class_name])

        return workout_class_info

    def print_workout_class_info(self):
        for info in self.workout_class_info:
            print(info)


class SessionData:
    def __init__(self, file_info, verbose=0):
        self.rest_segments = []
        self.workout_segments = []

        for info in file_info:
            if info[4] == "rest":
                self.rest_segments.append(RestSegment(info[0], info[1]))
            elif info[4] == "whole":
                self.whole_session = WholeSession(info[0], info[1], verbose=verbose)
            else:
                w_data = WorkoutSegment(info[0], info[1])
                self.workout_segments.append(w_data)

                # self.logi("info ::", w_data.file_name, w_data.repetition_number)

        # Delete workout with less than 2 repetitions.
        # This was caused by annotation mistake or unexpected situations.
        remove_list = []
        for data in self.workout_segments:
            if data.repetition_number <= 1:
                tstamp = data.raw_data["Timestamp"]
                tstamp_session = self.whole_session.raw_data["Timestamp"]
                start_t = tstamp[0]
                end_t = tstamp[tstamp.shape[0] - 1]
                tstamp_index = tstamp_session[
                    np.logical_and(
                        (tstamp_session >= start_t), (tstamp_session <= end_t)
                    )
                ].index

                self.whole_session.workout_state[
                    tstamp_index[0] : tstamp_index[tstamp_index.shape[0] - 1] + 1
                ] = 0

                delete_range = list(
                    range(tstamp_index[0], tstamp_index[tstamp_index.shape[0] - 1] + 1)
                )

                self.whole_session.workout_state = np.delete(
                    self.whole_session.workout_state, delete_range
                )
                self.whole_session.sensor_data = np.delete(
                    self.whole_session.sensor_data, delete_range, axis=0
                )
                self.whole_session.raw_data = self.whole_session.raw_data.drop(
                    delete_range
                ).reset_index(drop=True)

                remove_list.append(data)

        for data in remove_list:
            self.workout_segments.remove(data)


class DataSetLoader:
    def __init__(
        self,
        path,
        verbose=0,
        read_smallset=False,
        n_smallset=5,
        drop_lack_workout_type=False,
        multiprocess=True,
    ):
        self.root_path = path
        self.verbose = verbose

        if verbose > 0:
            print("Start loading dataset from", path, "...")

        files_info = self.get_files_info()
        merged_info = DataSetLoader.merge_file_info(files_info)

        # Get unique nick names
        self.unique_names = []
        for info in merged_info:
            self.unique_names.append(info[0][2].lower())

        self.unique_names = list(set(self.unique_names))
        self.unique_names.sort()

        if read_smallset:
            while (len(self.unique_names)) > n_smallset:
                self.unique_names.pop(0)

        self.datasets = []
        if self.verbose > 0:
            print(
                "... Reading {} datasets from {} subjects ...".format(
                    len(merged_info), len(self.unique_names)
                )
            )

        loading_infos = [
            info for info in merged_info if info[0][2].lower() in self.unique_names
        ]
        loading_msg = "Reading {} datasets from {} subjects ...".format(
            len(merged_info), len(self.unique_names)
        )

        if multiprocess:
            self.datasets = p_map(
                partial(SessionData, verbose=verbose), loading_infos, desc=loading_msg
            )
        else:
            self.datasets = [
                SessionData(info, verbose=verbose)
                for info in tqdm(loading_infos, desc=loading_msg)
            ]

        if self.verbose > 0:
            print(
                "... Done Reading {} datasets from {} subjects!".format(
                    len(self.datasets), len(self.unique_names)
                )
            )

        # Dropping the session data that does not contain every 15 workout types
        if drop_lack_workout_type:
            drop_candidate = []
            for d_set in self.datasets:
                check_list = np.zeros((15,))
                for w_data in d_set.workout_segments:
                    check_list[w_data.workout_class_number] = 1

                if check_list.sum() < 15:
                    drop_candidate.append(d_set)

            if self.verbose > 0:
                print("... Drop Dataset :", len(drop_candidate))
                print("... Current length :", len(self.datasets))

            for d_set in drop_candidate:
                sinner_list = ""
                sinner_list += "Sinner : %s, Sin list :" % d_set.whole_session.file_name

                for w_data in d_set.workout_segments:
                    sinner_list += "%d," % w_data.workout_class_number
                print(sinner_list)
                self.datasets.remove(d_set)

            if self.verbose > 0:
                print("... Current length :", len(self.datasets))

        if verbose > 0:
            print("Done reading dataset!")

    def get_training_test_sets(self, cv_idx=0, n_cv=6):
        n_test = len(self.unique_names) // n_cv

        test_idx = [i for i in range(cv_idx * n_test, (cv_idx + 1) * n_test)]
        test_set = []
        training_set = []

        for i in range(len(self.unique_names)):
            dataset = self.get_session_data_by_nick_name(self.unique_names[i])
            for d_set in dataset:
                if i in test_idx:
                    test_set.append(d_set)
                else:
                    training_set.append(d_set)

        if self.verbose > 0:
            print("Testing index : %s" % test_idx)
            print(
                "Training, Testing Length : (%02d, %02d)"
                % (len(training_set), len(test_set))
            )

        return training_set, test_set

    @staticmethod
    def get_file_name_info(name):
        name_split = name.split("_")
        user = name_split[0]
        date = name_split[1] + "-" + name_split[2] + "-" + name_split[3]
        if len(name_split) == 5:
            file_type = name_split[4]
        else:
            file_type = name_split[5]

        return user, date, file_type

    @staticmethod
    def merge_file_info(files_info):
        file_names = []
        for f_info in files_info:
            file_names.append(f_info[2] + f_info[3])

        unique_set = list(set(file_names))

        merged_info = []
        for unique_name in unique_set:
            unique_index = [
                i for i in range(len(file_names)) if file_names[i] == unique_name
            ]

            info_set = []
            for index in unique_index:
                info_set.append(files_info[index])

            info_set = sorted(info_set, key=lambda x: x[1])

            merged_info.append(info_set)

        return sorted(merged_info, key=lambda x: x[0][1])

    def get_files_info(self):
        dir_list = os.walk(self.root_path)

        data_path_set = []

        for root, dirs, files in dir_list:
            for file in files:
                name, ext = os.path.splitext(file)
                if ext.endswith("csv"):
                    user, date, file_type = DataSetLoader.get_file_name_info(name)
                    data_path_set.append([root, name, user, date, file_type])

        return data_path_set

    def get_session_data_by_nick_name(self, nick_name):
        session_data = []
        for s_data in self.datasets:
            if nick_name == s_data.whole_session.user_nick_name.lower():
                session_data.append(s_data)

        return session_data

    def get_session_data_by_nickname_idx(self, idx):
        return self.get_session_data_by_nick_name(self.unique_names[idx])

    def get_random_session(self):
        return self.datasets[np.random.randint(0, len(self.datasets))]
