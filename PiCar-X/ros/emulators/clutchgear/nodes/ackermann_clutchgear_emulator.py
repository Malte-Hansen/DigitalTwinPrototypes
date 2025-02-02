#!/usr/bin/env python3
# Copyright 2021 Alexander Barbie
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from typing import Union
import rospy
from picarx.emulators.clutchgear import AbstractClutchGearEmulator
from std_msgs.msg import Float64
import math
import argparse

class Options(object):

    def __init__(self, argv):
        parser = argparse.ArgumentParser()
        parser.add_argument(
            "name", type=str, help="The RS232 device the simulator should send data to, e.g., /dev/com0")
        parser.add_argument(
            "pwm_pin", type=str, help="The interval in which a line in the file should be read.")
        parser.add_argument(
            "i2c_port", type=str, help="The interval in which a line in the file should be read.")

        self.args = parser.parse_args(argv)

    def get_args(self):
        return vars(self.args)

class AckermannClutchGearEmulator(AbstractClutchGearEmulator):
    
    def __init__(self, name: str, pwm_pin: str, i2c_port: str, frequency: int = 50):
        super(AckermannClutchGearEmulator, self).__init__(pwm_pin, i2c_port)
        self.name = name
        self.frequency = frequency
        self.left_steer = None
        self.right_steer = None
        self.wheel_base = None
        self.wheel_track = None

    def angle_inside_wheel(self, angle):
        alpha_inside = math.atan(self.wheel_base / (self.turning_radius(angle) - self.wheel_track/2))
        return alpha_inside

    def angle_outside_wheel(self, angle):
        alpha_outside = math.atan(self.wheel_base / (self.turning_radius(angle) + self.wheel_track/2))
        return alpha_outside

    def turning_radius(self, angle):
        if angle == 0:
            return 0
        turning_radius = self.wheel_base / math.tan(math.radians(angle))
        return turning_radius

    def rotate(self, pulse_width):
        if pulse_width == 0: # this is required since SunFounder adds a constant > 0 in the pulse width calculation for the angle. Thus the pulse width of an angle is always > 0.
            return
        angle = self.pulse_width_to_angle(pulse_width)
        angle = 90 - angle if angle >= 90 else 90 - angle
        angle = angle

        inside_wheel = self.angle_inside_wheel(angle)
        outside_wheel = self.angle_outside_wheel(angle)

        if angle > 0:
            self.turn_left(inside_wheel, outside_wheel)
        elif angle < 0:
            self.turn_right(inside_wheel, outside_wheel)
        else:
            self.left_steer.publish(0)
            self.right_steer.publish(0)

    def turn_right(self, inside_wheel, outside_wheel):
        self.left_steer.publish(outside_wheel)
        self.right_steer.publish(inside_wheel)

    def turn_left(self, inside_wheel, outside_wheel):
        self.left_steer.publish(inside_wheel)
        self.right_steer.publish(outside_wheel)

    def stop(self):
        rospy.loginfo("Shutting Ackermann steering emulator down")

    def read_i2c_value(self):
        pulse_width = self.pwm_pin.register_channel.read()
        return pulse_width

    def start(self):
        rospy.init_node(self.name, anonymous=True)
        rospy.loginfo("Ackermann steering emulator initialized")
        rospy.on_shutdown(self.stop)
        self.left_steer = rospy.Publisher(rospy.get_param('~left_steer_topic'), Float64, queue_size=5)
        self.right_steer = rospy.Publisher(rospy.get_param('~right_steer_topic'), Float64, queue_size=5)
        self.wheel_base = float(rospy.get_param("~wheel_base"))
        self.wheel_track = float(rospy.get_param("~wheel_track"))
        frequency = rospy.Rate(50) # 50Hz
        while not rospy.is_shutdown():
            pulse_width = self.read_i2c_value()
            self.rotate(pulse_width)
            frequency.sleep()



if __name__ == '__main__':
    try:
        options = Options(rospy.myargv()[1:])
        clutchgear_emulator = AckermannClutchGearEmulator(options.args.name, options.args.pwm_pin, options.args.i2c_port)
        clutchgear_emulator.start()
    except rospy.ROSInterruptException:
        pass
