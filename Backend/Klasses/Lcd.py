from RPi import GPIO
import math
import time


class Functies:
    clear_display_and_cursor_home = 0x1
    cursor_home = 0x2
    display_on = 0x8
    all_display_on = 0xC
    cursur_on = 0xE
    cursur_blink = 0XF
    set_interface= 0x3F
    curser_2de_lijn = 0xBF


class Lcd:
    def __init__(self,rs,e,d0,d1,d2,d3,d4,d5,d6,d7,backlight):

        self.rs = rs
        self.e = e
        self.pinnen = [d0,d1,d2,d3,d4,d5,d6,d7]
        self.bl = backlight

        #init pinnen
        for pin in self.pinnen:
            GPIO.setup(pin,GPIO.OUT)

        GPIO.setup(self.rs, GPIO.OUT)
        GPIO.setup(self.e, GPIO.OUT)
        GPIO.setup(self.bl, GPIO.OUT)

        # init display
        self.stuur_instructie(Functies.set_interface)
        self.stuur_instructie(Functies.all_display_on)
        self.stuur_instructie(Functies.clear_display_and_cursor_home)

    def test_ldc(self):
        self.stuur_instructie(Functies.cursur_blink)


    def stuur_instructie(self,byte):
        GPIO.output(self.e, True)
        self.set_GPIO_bits(byte)
        GPIO.output(self.e, False)


    def stuur_teken(self,byte):
        GPIO.output(self.rs,True)
        GPIO.output(self.e, True)

        self.set_GPIO_bits(byte)

        GPIO.output(self.e, False)

        GPIO.output(self.rs,False)

    def stuur_zin(self,zin):
        lengte_zin = len(zin)

        if lengte_zin <= 16:
            self.schrijf_zin(zin)

        else:
            zin1 = zin[:16]
            zin2= zin[16:]
            self.schrijf_zin(zin1)
            self.stuur_instructie(Functies.curser_2de_lijn)

            self.schrijf_zin(zin2)

    def schrijf_zin(self,zin):
        while zin[0] == " ":
            zin = zin[1:]

        for i in range(len(zin)):
            letter = ord(zin[i])
            self.stuur_teken(letter)

    def clear_display(self):
        self.stuur_instructie(Functies.clear_display_and_cursor_home)

    def go_2nd_row(self):
        self.stuur_instructie(Functies.curser_2de_lijn)

    def set_GPIO_bits(self,byte):
        for i in range(8):
           GPIO.output(self.pinnen[i], bool(byte & (2**i)))

        time.sleep(0.002)

    def schrijf_letter(self,letter):
        self.stuur_teken(ord(letter))