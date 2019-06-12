# imports
from Klasses import Lcd, ServoMotor
from RPi import GPIO
from subprocess import check_output
import time
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_socketio import SocketIO, emit
from mfrc522 import SimpleMFRC522
from database.DP1Database import Database
from threading import Thread, Timer
from smbus import SMBus
from datetime import datetime, time as Time


GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

lcd = Lcd.Lcd(16, 12, 25, 24, 23, 26, 19, 13, 6, 5, 0)
servo = ServoMotor.ServoMotor(18)
reader = SimpleMFRC522()

servo.set_angle(5)
time.sleep(1)

ips = check_output(['hostname', '--all-ip-addresses'])
iplist = str(ips).split(" ")
iplist[0] = iplist[0].replace("b'", "")
lcd.schrijf_zin("IP:" + iplist[0])

buzzer_pin = 4
GPIO.setup(buzzer_pin, GPIO.OUT)


def is_time_between(begin_time, end_time, check_time=None):
    # If check time is not given, default to current UTC time
    check_time = check_time or datetime.utcnow().time()
    if begin_time < end_time:
        return check_time >= begin_time and check_time <= end_time
    else: # crosses midnight
        return check_time >= begin_time or check_time <= end_time


def buzz(pitch, duration):  # create the function "buzz" and feed it the pitch and duration)
    period = 1.0 / pitch  # in physics, the period (sec/cyc) is the inverse of the frequency (cyc/sec)
    delay = period / 2  # calcuate the time for half of the wave
    cycles = int(duration * pitch)  # the number of waves to produce is the duration times the frequency

    for i in range(cycles):  # start a loop from 0 to the variable "cycles" calculated above
        GPIO.output(buzzer_pin, True)  # set pin 4 to high
        time.sleep(delay)  # wait with pin 18 high
        GPIO.output(buzzer_pin, False)  # set pin 4 to low
        time.sleep(delay)  # wait with pin 18 low


def init_gpio_in(pin):
    GPIO.setup(pin, GPIO.IN)
    print("pin {0} succesvol geinitialiseerd".format(pin))


def init_gpio_out(pin):
    GPIO.setup(pin, GPIO.OUT)
    print("pin {0} succesvol geinitialiseerd".format(pin))


def show_status():
    status = MagnetDetect.status_magnet()
    socketio.emit('hall_magnet', {'status': status})
    Timer(1, show_status).start()


class MagnetDetect(Thread):
    def __init__(self, hallpinlock, hallpindoor):
        Thread.__init__(self)  # Geef deze klasse door naar de parent Thread
        self.daemon = True  # Zet hem in de achtergrond

        self.hallLock = hallpinlock
        self.hallDoor = hallpindoor
        init_gpio_in(self.hallLock)
        init_gpio_in(self.hallDoor)
        GPIO.add_event_detect(self.hallDoor, GPIO.FALLING, callback=self.close_door)
        GPIO.add_event_detect(self.hallLock, GPIO.FALLING, callback=self.magneet_detect)
        self.start()  # Start de aparte thread

    @staticmethod
    def magneet_detect(hall):
        row_inserted = conn.set_data("INSERT INTO SensorenHistoriek(DatumTijd, Sensor) VALUES (CURRENT_TIMESTAMP, 2)")
        if int(row_inserted) > 0:
            print("Magnet detect stored in database")

    @staticmethod
    def open_door():
        time.sleep(1)
        servo.set_angle(70)
        time.sleep(1)

    @staticmethod
    def close_door(self):
        MagnetDetect.magneet_detect(" ")
        time.sleep(1)
        servo.set_angle(5)
        time.sleep(1)

    @staticmethod
    def status_magnet():
        return GPIO.input(21)

    def run(self):
        while True:
            time.sleep(5)


class BadgeCheck(Thread):
    def __init__(self, readerobj):
        Thread.__init__(self)  # Geef deze klasse door naar de parent Thread
        self.daemon = True  # Zet hem in de achtergrond
        self.start()  # Start de aparte thread
        self.badge = 0

        self.reader = readerobj

    @staticmethod
    def badge_check(badgenr):
        with app.app_context():
            return conn.get_data("SELECT * FROM Badges WHERE Badge = %s", str(badgenr))

    def print_read(self):
        self.badge = self.reader.read()
        if len(self.badge_check(self.badge[0])) != 0:
            print("deur opent")
            MagnetDetect.open_door()
            time.sleep(1)
            row_inserted = conn.set_data("INSERT INTO SensorenHistoriek(DatumTijd, Sensor) VALUES (CURRENT_TIMESTAMP , %s)", 3)
            if int(row_inserted) > 0:
                print("Badge logged in database")

    def run(self):
        try:
            start_time = time.time()
            while True:

                # your code
                elapsed_time = time.time() - start_time
                if elapsed_time > 5:
                    self.print_read()
                    start_time = time.time()

        finally:
            print("Bye!")


class MotionCheck(Thread):  # Parent van Thread

    def __init__(self):
        Thread.__init__(self)  # Geef deze klasse door naar de parent Thread
        self.daemon = True  # Zet hem in de achtergrond

        self.led = 17
        self.pir = 20

        init_gpio_in(self.pir)
        init_gpio_out(self.led)
        self.licht_uit()
        self.start()  # Start de aparte thread

    def licht_aan(self):
        GPIO.output(self.led, GPIO.HIGH)

    def licht_uit(self):
        GPIO.output(self.led, GPIO.LOW)

    def motion_detect(self, pir):
        row_inserted = conn.set_data("INSERT INTO SensorenHistoriek(DatumTijd, Sensor) VALUES (CURRENT_TIMESTAMP, 1)")
        if int(row_inserted) > 0:
            print("Motion stored in database")

        date = str(datetime.now())
        socketio.emit('pirMotion', {'tijd': date})

        if is_time_between(Time(4, 00), Time(22, 00)):
            print("test")
            self.licht_aan()
            time.sleep(5)
            self.licht_uit()
            time.sleep(2.5)

    def run(self):  # Dit wordt gerunt door self.start().
        #  de run functie niet zelf starten. je moet de effectieve thread starten

        time.sleep(2)
        print("ready")

        try:

            GPIO.add_event_detect(self.pir, GPIO.RISING, callback=self.motion_detect)
            while True:
                time.sleep(0.2)
        except KeyboardInterrupt:
            print("Bye!")
            GPIO.cleanup()


class KeypadModule(Thread):
    I2CADDR = 0x20  # valid range is 0x20 - 0x27

    PULUPA = 0x0F  # PullUp enable register base address
    PULUPB = 0xF0  # PullUp enable register base address

    # Keypad Keycode matrix
    KEYCODE = [['1', '2', '3'],  # KEYCOL0
               ['4', '5', '6'],  # KEYCOL1
               ['7', '8', '9'],  # KEYCOL2
               ['*', '0', '#']]  # KEYCOL3

    # Decide the row
    DECODE = [0, 0, 0, 0, 0, 0, 0, 3, 0, 0, 0, 2, 0, 1, 0, 0]

    # initialize I2C comm, 1 = rev2 Pi, 0 for Rev1 Pi
    i2c = SMBus(1)

    # initialize the keypad class
    def __init__(self, addr):
        Thread.__init__(self)  # Geef deze klasse door naar de parent Thread
        self.daemon = True  # Zet hem in de achtergrond
        self.I2CADDR = addr
        self.status = 0
        self.pin = ""
        global lcd
        global servo
        lcd.go_2nd_row()
        self.start()

    @staticmethod
    def lcd_instruction(value):
        for i in range(0, value):
            lcd.stuur_instructie(0b0000010000)

    def restart(self):
        lcd.schrijf_zin("pwd: ____")
        self.lcd_instruction(4)
        self.status = 0
        self.pin = ""

    # get a keystroke from the keypad
    def getch(self):
        time.sleep(0.1)
        self.i2c.write_byte(self.I2CADDR, self.PULUPA)
        row = self.i2c.read_byte(self.I2CADDR)
        if (row) != 0b1111:
            self.i2c.write_byte(self.I2CADDR, self.PULUPB)
            col = self.i2c.read_byte(self.I2CADDR) >> 4
            row = self.DECODE[row]
            col = self.DECODE[col]
            return self.KEYCODE[row][col]

    def run(self):
        self.restart()
        while True:
            time.sleep(0.05)
            ch = self.getch()
            if str(ch) != "None":
                if len(self.pin) != 3:
                    if self.status == 0:
                        self.pin += ch
                        lcd.schrijf_letter(ch)
                        self.status = 1
                else:
                    self.pin += ch
                    self.lcd_instruction(8)
                    antw_db = conn.get_data("SELECT * FROM Pincodes WHERE Code = %s AND Geactiveerd = 1", str(self.pin))
                    if len(antw_db) != 0:
                        # row_inserted = conn.set_data("INSERT INTO PinHistoriek(Code, LaatstGebruikt) VALUES (%s)", self.badge[0])
                        # if int(row_inserted) > 0:
                        #     print("Badge stored in database")
                        lcd.schrijf_zin("Opening... ")
                        self.lcd_instruction(11)
                        buzz(1500, 0.05)
                        time.sleep(0.05)
                        buzz(1500, 0.05)
                        MagnetDetect.open_door()
                        conn.set_data("UPDATE Pincodes SET Geactiveerd = %s WHERE Code = %s", [0, self.pin])
                        antw_db = conn.get_data("SELECT * FROM PinHistoriek WHERE Code = %s", self.pin)
                        if len(antw_db) != 0:
                            conn.set_data("UPDATE PinHistoriek SET LaatstGebruikt = CURRENT_TIMESTAMP WHERE Code = %s",
                                          self.pin)
                        else:
                            conn.set_data("INSERT INTO PinHisoriek(Code, LaatstGebruikt) VALUES (%s, CURRENT_TIMESTAMP )",
                                          self.pin)
                        self.restart()
                    else:
                        lcd.schrijf_zin("Wrong Code...  ")
                        self.lcd_instruction(15)
                        buzz(300, 0.5)
                        time.sleep(0.5)
                        # time.sleep(5)
                        lcd.schrijf_zin(".              ")
                        self.lcd_instruction(15)
                        time.sleep(0.05)
                        self.restart()
            else:
                self.status = 0


KeypadModule(0x38)


# Start app


app = Flask(__name__)
CORS(app)
socketio = SocketIO(app)

conn = Database(app=app, user='mct', password='mct', db='projectI')


MagnetDetect(21, 27)
show_status()

# MotionCheck()
BadgeCheck(reader)


endpoint = '/api/project'


@app.route("/")
def hello_world():
    return "Hello!"


@app.route("/pir-sensor", methods=['GET'])
def pir_sensor_log():
    if request.method == 'GET':
        return jsonify(conn.get_data("SELECT DatumTijd FROM SensorenHistoriek WHERE Sensor = 1 ORDER BY DatumTijd DESC LIMIT 1")), 200


@app.route("/hall-sensor", methods=['GET'])
def hall_sensor_log():
    if request.method == 'GET':
        return jsonify(conn.get_data("SELECT DatumTijd FROM SensorenHistoriek WHERE Sensor = 2 ORDER BY DatumTijd DESC LIMIT 1")), 200


@app.route("/pincodes_actief", methods=['GET'])
def pincodes_actief():
    if request.method == 'GET':
        return jsonify(conn.get_data("SELECT Code FROM Pincodes WHERE Geactiveerd = 1 ORDER BY LaatstGeactiveerd DESC")), 200


@app.route("/pincodes_beschik", methods=['GET'])
def pincodes_beschik():
    if request.method == 'GET':
        return jsonify(conn.get_data("SELECT Code FROM Pincodes WHERE Geactiveerd = 0 ORDER BY RAND() LIMIT 10")), 200


@app.route("/pincodes_change/<pin>/<status>", methods=['PUT'])
def pincodes_change(pin, status):
    if request.method == "PUT":
        if status == 1:
            conn.set_data("UPDATE Pincodes SET Geactiveerd = %s, LaatsGeactiveerd = CURRENT_TIMESTAMP WHERE Code = %s",
                          [status, pin])
        else:
            conn.set_data("UPDATE Pincodes SET Geactiveerd = %s WHERE Code = %s", [status, pin])
        return jsonify(pin=pin), 200


@app.route("/login", methods=['GET'])
def login_check():
    user = request.form['user']
    ww = request.form['ww']
    if request.method == 'GET':
        return jsonify(conn.get_data("SELECT AdminID FROM Admins WHERE GebruikersNaam = %s AND Wachtwoord = %s"), [user, ww]), 200


@socketio.on("connect")
def connecting():
    socketio.emit("connected")
    print("Connection with client established")


@socketio.on("open_lock")
def open_lock():
    MagnetDetect.open_door()
    time.sleep(1)


@socketio.on("hall_control")
def control_status():
    socketio.emit("hall_magnet", {'status': MagnetDetect.status_magnet()})


# Start app
if __name__ == '__main__':
    socketio.run(app, host="0.0.0.0", port=5000)
