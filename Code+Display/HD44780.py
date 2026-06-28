# See : https://raphaelkabo.com/blog/pi-pico-hd44780/

# HD44780	Destination	Function
# 1 (Vss)	Ground (0V)	Powers the HD44780's processor
# 2 (Vdd)	5V	Powers the HD44780's processor
# 3 (V0)	Ground via a 1K resistor*	LCD contrast control: high for nothing, low for aggressive white squares that hate you
# 4 (RS)	Pi Pico GP16 (pin 21)	Register Select. High to send data, low to send instructions (like 'clear screen').
# 5 (R/W)	Ground	Read/write toggle. I've kept it permanently tied low since we only ever output to the display.
# 6 (E)	Pi Pico GP17 (pin 22)	Enable signal. Makes the thing do the stuff.
# 11, 12, 13, 14 (DB4-DB7)	Pi Pico GP18, GP19, GP20, GP21 (pins 24-27)	Data pins. We send data through them!
# 15 (BLA)	5V	Backlight LED anode.
# 16 (BLK)	Ground (0V)	Backlight LED cathode. I stuck a 220 ohm resistor in here to chill it out a bit.


from machine import Pin, Timer
import utime

# Almost entirely copied from micropython-lcd by wjdp
# https://github.com/wjdp/micropython-lcd
class HD44780(object):
    # Pinout, change within or outside class for your use case
    PINS = [16, 17, 18, 19, 20, 21]
    # Pin names, don't change
    PIN_NAMES = ['RS','E','D4','D5','D6','D7']

    # Dict of pins
    pins = {}

    # Pin mode, push-pull control
    PIN_MODE = Pin.OUT

    # Define some device constants
    LCD_WIDTH = 16    # Maximum characters per line
    # Designation of T/F for character and command modes
    LCD_CHR = True
    LCD_CMD = False

    LINES = {
        0: 0x80, # LCD RAM address for the 1st line
        1: 0xC0, # LCD RAM address for the 2nd line
        # Add more if desired
    }

    # Timing constants
    E_PULSE = 1
    E_DELAY = 1

    def init(self):
        # Initialise pins
        for pin, pin_name in zip(self.PINS, self.PIN_NAMES):
            self.pins['LCD_'+pin_name] = Pin(pin, self.PIN_MODE)
        # Initialise display
        self.lcd_byte(0x33,self.LCD_CMD)
        self.lcd_byte(0x32,self.LCD_CMD)
        self.lcd_byte(0x28,self.LCD_CMD)
        self.lcd_byte(0x0C,self.LCD_CMD)
        self.lcd_byte(0x06,self.LCD_CMD)
        self.lcd_byte(0x01,self.LCD_CMD)

    def clear(self):
        # Clear the display
        self.lcd_byte(0x01,self.LCD_CMD)

    def set_line(self, line):
        # Set the line that we're going to print to
        self.lcd_byte(self.LINES[line], self.LCD_CMD)

    def set_string(self, message):
        # Pad string out to LCD_WIDTH
        m_length = len(message)
        if m_length < self.LCD_WIDTH:
            short = self.LCD_WIDTH - m_length
            blanks=str()
            for i in range(short):
                blanks+=' '
            message+=blanks
        for i in range(self.LCD_WIDTH):
            self.lcd_byte(ord(message[i]), self.LCD_CHR)

    def lcd_byte(self, bits, mode):
        # Send byte to data pins
        # bits = data
        # mode = True  for character
        #        False for command

        self.pin_action('LCD_RS', mode) # RS

        # High bits
        self.pin_action('LCD_D4', False)
        self.pin_action('LCD_D5', False)
        self.pin_action('LCD_D6', False)
        self.pin_action('LCD_D7', False)
        if bits&0x10==0x10:
            self.pin_action('LCD_D4', True)
        if bits&0x20==0x20:
            self.pin_action('LCD_D5', True)
        if bits&0x40==0x40:
            self.pin_action('LCD_D6', True)
        if bits&0x80==0x80:
            self.pin_action('LCD_D7', True)

        # Toggle 'Enable' pin
        self.udelay(self.E_DELAY)
        self.pin_action('LCD_E', True)
        self.udelay(self.E_PULSE)
        self.pin_action('LCD_E', False)
        self.udelay(self.E_DELAY)

        # Low bits
        self.pin_action('LCD_D4', False)
        self.pin_action('LCD_D5', False)
        self.pin_action('LCD_D6', False)
        self.pin_action('LCD_D7', False)
        if bits&0x01==0x01:
            self.pin_action('LCD_D4', True)
        if bits&0x02==0x02:
            self.pin_action('LCD_D5', True)
        if bits&0x04==0x04:
            self.pin_action('LCD_D6', True)
        if bits&0x08==0x08:
            self.pin_action('LCD_D7', True)

        # Toggle 'Enable' pin
        self.udelay(self.E_DELAY)
        self.pin_action('LCD_E', True)
        self.udelay(self.E_PULSE)
        self.pin_action('LCD_E', False)
        self.udelay(self.E_DELAY)

    def udelay(self, us):
        # Delay by us microseconds, set as function for portability
        utime.sleep_ms(us)

    def pin_action(self, pin, high):
        # Pin high/low functions, set as function for portability
        if high:
            self.pins[pin].value(1)
        else:
            self.pins[pin].value(0)