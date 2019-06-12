from Klasses import ServoMotor
from RPi import GPIO
import pigpio
import time


GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

pi = pigpio.pi()

servo = ServoMotor.ServoMotor(18)
GPIO.setup(18, GPIO.OUT)
# buzzer_pin = 4
# GPIO.setup(buzzer_pin, GPIO.OUT)
#
# def buzz(pitch, duration):  # create the function "buzz" and feed it the pitch and duration)
#     period = 1.0 / pitch  # in physics, the period (sec/cyc) is the inverse of the frequency (cyc/sec)
#     delay = period / 2  # calcuate the time for half of the wave
#     cycles = int(duration * pitch)  # the number of waves to produce is the duration times the frequency
#
#     for i in range(cycles):  # start a loop from 0 to the variable "cycles" calculated above
#         GPIO.output(buzzer_pin, True)  # set pin 18 to high
#         time.sleep(delay)  # wait with pin 18 high
#         GPIO.output(buzzer_pin, False)  # set pin 18 to low
#         time.sleep(delay)  # wait with pin 18 low
#
#
# while True:  # start infinite loop
#     pitch_s = input("Enter Pitch (200 to 2000): ")  # ask the user to type in the pitch
#     pitch = float(pitch_s)  # convert user input to a floating decimal
#     duration_s = input("Enter Duration (seconds): ")  # ask the user to type in the duration
#     duration = float(duration_s)  # convert user input to a floating decimal
#     buzz(pitch, duration)  # feed the pitch and duration to the function, "buzz"


while True:
    # GPIO.output(buzzer, True)
    # time.sleep(0.002)
    # GPIO.output(buzzer, False)
    # time.sleep(0.002)
    # angle = input("Angle?")
    # if angle == "c":
    #     break
    # servo.set_angle(int(angle))
    # servo.set_angle(0)
    # time.sleep(2)
    # servo.set_angle(70)
    # time.sleep(2)

    print(time.daylight)
    time.sleep(2)

