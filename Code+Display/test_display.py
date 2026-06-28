from HD44780 import HD44780 as LCD

from machine import Pin, Timer
import time

#         C0   C1   C2   C3
keys = [['1', '2', '3', 'D'], # R0
        ['4', '5', '6', '?'], # R1
        ['7', '8', '9', '-'], # R2
        ['*', '0', '#', 'Y']] # R3

# Pin connections left to right
row_pins = [4, 5, 6, 7]
col_pins = [0, 1, 2, 3]

cols = []  # Creat empty lists
rows = []

# Set up rows and columns
# Rows are OUTPUTS / Cols are INPUTS
for x in range(0,4):
    # Rows are OUTPUTs which we set HIGH or LOW
    rows.append(Pin(row_pins[x], Pin.OUT))
    rows[x].value(0) # Set LOW = 0V
    
    # Columns are INPUTS with internal PULL_DOWNS
    cols.append(Pin(col_pins[x], Pin.IN, Pin.PULL_DOWN))


def write_lcd(line1, line2, mode="center"):
    if mode == "center":
        display.set_line(0)
        display.set_string(line1.center(16))
        display.set_line(1)
        display.set_string(line2.center(16))
    else:
#         display.clear()
        display.set_line(0)
        display.set_string(line1)
        display.set_line(1)
        display.set_string(line2)

# Function to scan for a key press  - Returns the character pressed  
def scan():
    scanning = True
    while scanning:     # Until key pressed - blocking!
        for row in range(4):
            for col in range(4): 
                rows[row].high()     # Equivalent to .value(1)   
                if cols[col].value() == 1:
                    scanning = False # Terminate looping
                    k = keys[row][col] # Read character from grid
                    time.sleep(0.3) # Debounce                   
            rows[row].low()          # Equivalent to .value(0) 
#     led.value(1)        # Flash LED to indicate key pressed
#     time.sleep(0.1)
#     led.value(0)
    return k            # Supply values to calling code

code = ''
display = LCD()
display.init()
write_lcd("Enter Code", ''+ code)

rcode = '1234'
while True:
    ch = scan()
    code += ch 
    if ch == 'D':
        code = code[:-1]
        code = code[:-1]
    if ch == 'Y':
        code = code[:-1]
        write_lcd("Enter Code", ''+ code)
        if code == rcode:
            write_lcd('Correct' , '')
            break
        else:
            write_lcd('Inncorrect' , 'Press any key')
            scan()
            code = ''
    
    write_lcd("Enter Code", ''+ code)
