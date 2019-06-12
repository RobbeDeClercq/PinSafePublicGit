from RPi import GPIO
import time


class ServoMotor:
    def __init__(self, par_pin):
        self.__pin = par_pin
        GPIO.setup(par_pin, GPIO.OUT)
        self.servomotor = GPIO.PWM(self.__pin,50)
        self.servomotor.start(0)

    def set_angle(self, angle):
        # servo angle tussen 0 en 180 graden
        if not 0 <= angle <= 180:
            raise ValueError('Servo angle must be between 0 and 180 degrees')

        duty = angle / 18 + 2
        GPIO.output(self.__pin, True)
        self.servomotor.ChangeDutyCycle(duty)
        time.sleep(1)
        GPIO.output(self.__pin, False)
        self.servomotor.ChangeDutyCycle(0)

    @staticmethod
    def value_to_angle(value):
        # zet de waarde van 1023 bits op naar 180 graden max
        return value /1023 * 180

    def __del__(self):
        self.servomotor.stop()
