import numpy as np

"""
Author : Taeyoung Kim
Driving algorithm for Robot Navigation Mid-term projects
"""
class CustomDriver:
    BUBBLE_RADIUS = 135     # 버블 반지름 default 160,150,140
    PREPROCESS_CONV_SIZE = 3    # default 3
    BEST_POINT_CONV_SIZE = 113   # default 80,120,117
    MAX_LIDAR_DIST = 3000000    # 3m
    
    ONE_DEGREE = np.pi / 180   # 1 degrees
    TWO_DEGREES = np.pi / 90    # 2 degrees
    FIVE_DEGREES = np.pi / 36   # 5 degrees
    TEN_DEGREES = np.pi / 18    # 10 degrees
    FIFTEEN_DEGREES = np.pi / 12    # 15 degrees
    TWENTY_DEGREES = np.pi / 9  # 20 degrees

    def __init__(self):
        # used when calculating the angles of the LiDAR data
        self.radians_per_elem = None

    def preprocess_lidar(self, ranges):
        """ Preprocess the LiDAR scan array. Expert implementation includes:
            1.Setting each value to the mean over some window
            2.Rejecting high values (eg. > 3m)
        """
        self.radians_per_elem = (2 * np.pi) / len(ranges)
        # we won't use the LiDAR data from directly behind us
        proc_ranges = np.array(ranges[135:-135])
        # sets each value to the mean over a given window
        proc_ranges = np.convolve(proc_ranges, np.ones(self.PREPROCESS_CONV_SIZE), 'same') / self.PREPROCESS_CONV_SIZE
        proc_ranges = np.clip(proc_ranges, 0, self.MAX_LIDAR_DIST)
        return proc_ranges

    def find_max_gap(self, free_space_ranges):
        """ Return the start index & end index of the max gap in free_space_ranges
            free_space_ranges: list of LiDAR data which contains a 'bubble' of zeros
        """
        # mask the bubble
        masked = np.ma.masked_where(free_space_ranges == 0, free_space_ranges)
        # get a slice for each contigous sequence of non-bubble data
        slices = np.ma.notmasked_contiguous(masked)
        max_len = slices[0].stop - slices[0].start
        chosen_slice = slices[0]
        # I think we will only ever have a maximum of 2 slices but will handle an
        # indefinitely sized list for portablility
        for sl in slices[1:]:
            sl_len = sl.stop - sl.start
            if sl_len > max_len:
                max_len = sl_len
                chosen_slice = sl
        return chosen_slice.start, chosen_slice.stop

    def find_best_point(self, start_i, end_i, ranges):
        """Start_i & end_i are start and end indices of max-gap range, respectively
        Return index of best point in ranges
        Naive: Choose the furthest point within ranges and go there
        """
        # do a sliding window average over the data in the max gap, this will
        # help the car to avoid hitting corners
        averaged_max_gap = np.convolve(ranges[start_i:end_i], np.ones(self.BEST_POINT_CONV_SIZE),
                                    'same') / self.BEST_POINT_CONV_SIZE
        return averaged_max_gap.argmax() + start_i

    def get_angle(self, range_index, range_len):
        """ Get the angle of a particular element in the LiDAR data and transform it into an appropriate steering angle
        """
        lidar_angle = (range_index - (range_len / 2)) * self.radians_per_elem
        steering_angle = lidar_angle / 2
        return steering_angle
    
    def velocity_table(self, steering_angle, best_point_length):
        """ The speed is determined by two parameters.  
            The higher the best point length, the higher the speed.  
            The larger the steering angle value, the smaller the speed.
            The velocity table is a heuristic.
        Return : speed
        """
        input_angle = abs(steering_angle)
        
        # point의 거리가 25m 이상일 때
        if best_point_length >= 25:

            if input_angle < self.ONE_DEGREE:
                speed = 22
            elif input_angle >= self.ONE_DEGREE and input_angle < self.TWO_DEGREES:
                speed = 17
            elif input_angle >= self.TWO_DEGREES and input_angle < self.FIVE_DEGREES:
                speed = 13
            elif input_angle >= self.FIVE_DEGREES and input_angle < self.TEN_DEGREES:
                speed = 12
            else:
                speed = 8

        # point의 거리가 20m 이상일 때 25m 이내일 때
        elif best_point_length >= 20 and best_point_length < 25:

            if input_angle < self.ONE_DEGREE:
                speed = 17
            elif input_angle >= self.ONE_DEGREE and input_angle < self.TWO_DEGREES:
                speed = 15
            elif input_angle >= self.TWO_DEGREES and input_angle < self.FIVE_DEGREES:
                speed = 10
            elif input_angle >= self.FIVE_DEGREES and input_angle < self.TEN_DEGREES:
                speed = 9
            else:
                speed = 8
        
        # point의 거리가 15m 이상일 때 20m 이내일 때
        elif best_point_length >= 15 and best_point_length < 20:

            if input_angle < self.ONE_DEGREE:
                speed = 15
            elif input_angle >= self.ONE_DEGREE and input_angle < self.TWO_DEGREES:
                speed = 12
            elif input_angle >= self.TWO_DEGREES and input_angle < self.FIVE_DEGREES:
                speed = 10
            elif input_angle >= self.FIVE_DEGREES and input_angle < self.TEN_DEGREES:
                speed = 8
            elif input_angle >= self.TEN_DEGREES and input_angle < self.FIFTEEN_DEGREES:
                speed = 6
            elif input_angle >= self.FIFTEEN_DEGREES and input_angle < self.TWENTY_DEGREES:
                speed = 6
            else:
                speed = 6
        
        # point의 거리가 10m 이상일 때 15m 이내일 때
        elif best_point_length >= 10 and best_point_length < 15:

            if input_angle < self.ONE_DEGREE:
                speed = 14
            elif input_angle >= self.ONE_DEGREE and input_angle < self.TWO_DEGREES:
                speed = 10.5
            elif input_angle >= self.TWO_DEGREES and input_angle < self.FIVE_DEGREES:
                speed = 10
            elif input_angle >= self.FIVE_DEGREES and input_angle < self.TEN_DEGREES:
                speed = 9
            elif input_angle >= self.TEN_DEGREES and input_angle < self.FIFTEEN_DEGREES:
                speed = 7
            elif input_angle >= self.FIFTEEN_DEGREES and input_angle < self.TWENTY_DEGREES:
                speed = 7
            else:
                speed = 7
        
        # point의 거리가 5m 이상일 때 10m 이내일 때
        elif best_point_length >= 5 and best_point_length < 10:

            if input_angle < self.ONE_DEGREE:
                speed = 12
            elif input_angle >= self.ONE_DEGREE and input_angle < self.TWO_DEGREES:
                speed = 11
            elif input_angle >= self.TWO_DEGREES and input_angle < self.FIVE_DEGREES:
                speed = 10.5
            elif input_angle >= self.FIVE_DEGREES and input_angle < self.TEN_DEGREES:
                speed = 9
            elif input_angle >= self.TEN_DEGREES and input_angle < self.FIFTEEN_DEGREES:
                speed = 8.5
            elif input_angle >= self.FIFTEEN_DEGREES and input_angle < self.TWENTY_DEGREES:
                speed = 7.5
            else:
                speed = 7.5
        
        # 5m 이내일 때
        else:

            if input_angle < self.ONE_DEGREE:
                speed = 10
            elif input_angle >= self.ONE_DEGREE and input_angle < self.TWO_DEGREES:
                speed = 9
            elif input_angle >= self.TWO_DEGREES and input_angle < self.FIVE_DEGREES:
                speed = 8
            elif input_angle >= self.FIVE_DEGREES and input_angle < self.TEN_DEGREES:
                speed = 7
            elif input_angle >= self.TEN_DEGREES and input_angle < self.FIFTEEN_DEGREES:
                speed = 6
            elif input_angle >= self.FIFTEEN_DEGREES and input_angle < self.TWENTY_DEGREES:
                speed = 6
            else:
                speed = 6
    
        return speed

    def process_lidar(self, ranges):
        """ Process each LiDAR scan as per the Follow Gap algorithm & publish an AckermannDriveStamped Message
        """
        proc_ranges = self.preprocess_lidar(ranges)
        # Find closest point to LiDAR 가장 가까운 Lidar 위치
        closest = proc_ranges.argmin()

        # Eliminate all points inside 'bubble' (set them to zero)
        min_index = closest - self.BUBBLE_RADIUS
        max_index = closest + self.BUBBLE_RADIUS
        if min_index < 0: min_index = 0
        if max_index >= len(proc_ranges): max_index = len(proc_ranges) - 1
        proc_ranges[min_index:max_index] = 0

        # Find max length gap
        gap_start, gap_end = self.find_max_gap(proc_ranges)

        # Find the best point in the gap
        best = self.find_best_point(gap_start, gap_end, proc_ranges)
        
        # Publish Drive message
        steering_angle = self.get_angle(best, len(proc_ranges))
        speed = self.velocity_table(steering_angle, proc_ranges[best])
        # print('1. best point lengh : ', proc_ranges[best])
        # print('2. speed : ',speed)
        # print('3. Steering angle in degrees: {}'.format((steering_angle / (np.pi / 2)) * 90))
        return speed, steering_angle


class StupidDriver:
    '''
    0 deg is forward, 90 is left, -90 is right
    '''
    def process_lidar(self, ranges):
        # if avg dist of -10 to 10 degrees is greater than 2m, forward
        # else if left is clear, left
        # else right
        forward = np.mean(ranges[0:10] + ranges[-10:])
        left = np.mean(ranges[80:100])
        right = np.mean(ranges[260:280])
        print(forward, left, right)
        if forward > 2.0:
            return 5.0, 0.0
        elif left > right:
            return 2.0, 1.0
        else:
            return 2.0, -1.0


class GapFollower:
    BUBBLE_RADIUS = 160 // (1080//360)
    PREPROCESS_CONV_SIZE = 3
    BEST_POINT_CONV_SIZE = 80
    MAX_LIDAR_DIST = 3000000
    STRAIGHTS_SPEED = 8.0 # 8.0
    CORNERS_SPEED = 5.0 # 5.0
    STRAIGHTS_STEERING_ANGLE = np.pi / 18  # 10 degrees

    def __init__(self):
        # used when calculating the angles of the LiDAR data
        self.radians_per_elem = None

    def preprocess_lidar(self, ranges):
        """ Preprocess the LiDAR scan array. Expert implementation includes:
            1.Setting each value to the mean over some window
            2.Rejecting high values (eg. > 3m)
        """
        self.radians_per_elem = (2 * np.pi) / len(ranges)
        # we won't use the LiDAR data from directly behind us
        proc_ranges = np.array(ranges)# np.array(ranges[135:-135])
        # sets each value to the mean over a given window
        proc_ranges = np.convolve(proc_ranges, np.ones(self.PREPROCESS_CONV_SIZE), 'same') / self.PREPROCESS_CONV_SIZE
        proc_ranges = np.clip(proc_ranges, 0, self.MAX_LIDAR_DIST)
        return proc_ranges

    def find_max_gap(self, free_space_ranges):
        """ Return the start index & end index of the max gap in free_space_ranges
            free_space_ranges: list of LiDAR data which contains a 'bubble' of zeros
        """
        # mask the bubble
        masked = np.ma.masked_where(free_space_ranges == 0, free_space_ranges)
        # get a slice for each contigous sequence of non-bubble data
        slices = np.ma.notmasked_contiguous(masked)
        max_len = slices[0].stop - slices[0].start
        chosen_slice = slices[0]
        # I think we will only ever have a maximum of 2 slices but will handle an
        # indefinitely sized list for portablility
        for sl in slices[1:]:
            sl_len = sl.stop - sl.start
            if sl_len > max_len:
                max_len = sl_len
                chosen_slice = sl
        return chosen_slice.start, chosen_slice.stop

    def find_best_point(self, start_i, end_i, ranges):
        """Start_i & end_i are start and end indices of max-gap range, respectively
        Return index of best point in ranges
        Naive: Choose the furthest point within ranges and go there
        """
        # do a sliding window average over the data in the max gap, this will
        # help the car to avoid hitting corners
        averaged_max_gap = np.convolve(ranges[start_i:end_i], np.ones(self.BEST_POINT_CONV_SIZE),
                                       'same') / self.BEST_POINT_CONV_SIZE
        return averaged_max_gap.argmax() + start_i

    def get_angle(self, range_index, range_len):
        """ Get the angle of a particular element in the LiDAR data and transform it into an appropriate steering angle
        """
        lidar_angle = (range_index - (range_len / 2)) * self.radians_per_elem
        steering_angle = lidar_angle / 2
        return steering_angle

    def process_lidar(self, ranges):
        """ Process each LiDAR scan as per the Follow Gap algorithm & publish an AckermannDriveStamped Message
        """
        proc_ranges = self.preprocess_lidar(ranges)
        # Find closest point to LiDAR
        closest = proc_ranges.argmin()

        # Eliminate all points inside 'bubble' (set them to zero)
        min_index = closest - self.BUBBLE_RADIUS
        max_index = closest + self.BUBBLE_RADIUS
        print(min_index, max_index, len(proc_ranges))
        if min_index < 0: min_index = 0
        if max_index >= len(proc_ranges): max_index = len(proc_ranges) - 1
        proc_ranges[min_index:max_index] = 0

        # Find max length gap
        gap_start, gap_end = self.find_max_gap(proc_ranges)

        # Find the best point in the gap
        best = self.find_best_point(gap_start, gap_end, proc_ranges)
        

        # Publish Drive message
        steering_angle = self.get_angle(best, len(proc_ranges))
        if abs(steering_angle) > self.STRAIGHTS_STEERING_ANGLE:
            speed = self.CORNERS_SPEED
        else:
            speed = self.STRAIGHTS_SPEED
        print('Steering angle in degrees: {}'.format((steering_angle / (np.pi / 2)) * 90))
        return speed, steering_angle


# drives straight ahead at a speed of 5
class SimpleDriver:

    def process_lidar(self, ranges):
        speed = 5.0
        steering_angle = 0.0
        return speed, steering_angle


# drives toward the furthest point it sees
class AnotherDriver:

    def process_lidar(self, ranges):
        # the number of LiDAR points
        NUM_RANGES = len(ranges)
        # angle between each LiDAR point
        ANGLE_BETWEEN = 2 * np.pi / NUM_RANGES
        # number of points in each quadrant
        NUM_PER_QUADRANT = NUM_RANGES // 4

        # the index of the furthest LiDAR point (NOT) (ignoring the points behind the car)
        # max_idx = np.argmax(ranges[NUM_PER_QUADRANT:-NUM_PER_QUADRANT]) + NUM_PER_QUADRANT
        max_idx = np.argmax(ranges) # + NUM_PER_QUADRANT
        # some math to get the steering angle to correspond to the chosen LiDAR point
        steering_angle = max_idx * ANGLE_BETWEEN - (NUM_RANGES // 2) * ANGLE_BETWEEN
        speed = 5.0

        return speed, steering_angle


class DisparityExtender:
    CAR_WIDTH = 0.31
    # the min difference between adjacent LiDAR points for us to call them disparate
    DIFFERENCE_THRESHOLD = 2.
    SPEED = 5.
    # the extra safety room we plan for along walls (as a percentage of car_width/2)
    SAFETY_PERCENTAGE = 300.

    def preprocess_lidar(self, ranges):
        """ Any preprocessing of the LiDAR data can be done in this function.
            Possible Improvements: smoothing of outliers in the data and placing
            a cap on the maximum distance a point can be.
        """
        # remove quadrant of LiDAR directly behind us
        eighth = int(len(ranges) / 8)
        return np.array(ranges[eighth:-eighth])

    def get_differences(self, ranges):
        """ Gets the absolute difference between adjacent elements in
            in the LiDAR data and returns them in an array.
            Possible Improvements: replace for loop with numpy array arithmetic
        """
        differences = [0.]  # set first element to 0
        for i in range(1, len(ranges)):
            differences.append(abs(ranges[i] - ranges[i - 1]))
        return differences

    def get_disparities(self, differences, threshold):
        """ Gets the indexes of the LiDAR points that were greatly
            different to their adjacent point.
            Possible Improvements: replace for loop with numpy array arithmetic
        """
        disparities = []
        for index, difference in enumerate(differences):
            if difference > threshold:
                disparities.append(index)
        return disparities

    def get_num_points_to_cover(self, dist, width):
        """ Returns the number of LiDAR points that correspond to a width at
            a given distance.
            We calculate the angle that would span the width at this distance,
            then convert this angle to the number of LiDAR points that
            span this angle.
            Current math for angle:
                sin(angle/2) = (w/2)/d) = w/2d
                angle/2 = sininv(w/2d)
                angle = 2sininv(w/2d)
                where w is the width to cover, and d is the distance to the close
                point.
            Possible Improvements: use a different method to calculate the angle
        """
        angle = 2 * np.arcsin(width / (2 * dist))
        num_points = int(np.ceil(angle / self.radians_per_point))
        return num_points

    def cover_points(self, num_points, start_idx, cover_right, ranges):
        """ 'covers' a number of LiDAR points with the distance of a closer
            LiDAR point, to avoid us crashing with the corner of the car.
            num_points: the number of points to cover
            start_idx: the LiDAR point we are using as our distance
            cover_right: True/False, decides whether we cover the points to
                         right or to the left of start_idx
            ranges: the LiDAR points

            Possible improvements: reduce this function to fewer lines
        """
        new_dist = ranges[start_idx]
        if cover_right:
            for i in range(num_points):
                next_idx = start_idx + 1 + i
                if next_idx >= len(ranges): break
                if ranges[next_idx] > new_dist:
                    ranges[next_idx] = new_dist
        else:
            for i in range(num_points):
                next_idx = start_idx - 1 - i
                if next_idx < 0: break
                if ranges[next_idx] > new_dist:
                    ranges[next_idx] = new_dist
        return ranges

    def extend_disparities(self, disparities, ranges, car_width, extra_pct):
        """ For each pair of points we have decided have a large difference
            between them, we choose which side to cover (the opposite to
            the closer point), call the cover function, and return the
            resultant covered array.
            Possible Improvements: reduce to fewer lines
        """
        width_to_cover = (car_width / 2) * (1 + extra_pct / 100)
        for index in disparities:
            first_idx = index - 1
            points = ranges[first_idx:first_idx + 2]
            close_idx = first_idx + np.argmin(points)
            far_idx = first_idx + np.argmax(points)
            close_dist = ranges[close_idx]
            num_points_to_cover = self.get_num_points_to_cover(close_dist,
                                                               width_to_cover)
            cover_right = close_idx < far_idx
            ranges = self.cover_points(num_points_to_cover, close_idx,
                                       cover_right, ranges)
        return ranges

    def get_steering_angle(self, range_index, range_len):
        """ Calculate the angle that corresponds to a given LiDAR point and
            process it into a steering angle.
            Possible improvements: smoothing of aggressive steering angles
        """
        lidar_angle = (range_index - (range_len / 2)) * self.radians_per_point
        steering_angle = np.clip(lidar_angle, np.radians(-90), np.radians(90))
        return steering_angle

    def _process_lidar(self, ranges):
        """ Run the disparity extender algorithm!
            Possible improvements: varying the speed based on the
            steering angle or the distance to the farthest point.
        """
        self.radians_per_point = (2 * np.pi) / len(ranges)
        proc_ranges = self.preprocess_lidar(ranges)
        differences = self.get_differences(proc_ranges)
        disparities = self.get_disparities(differences, self.DIFFERENCE_THRESHOLD)
        proc_ranges = self.extend_disparities(disparities, proc_ranges,
                                              self.CAR_WIDTH, self.SAFETY_PERCENTAGE)
        steering_angle = self.get_steering_angle(proc_ranges.argmax(),
                                                 len(proc_ranges))
        speed = self.SPEED
        return speed, steering_angle

    def process_observation(self, ranges, ego_odom):
        return self._process_lidar(ranges)
