from machine import Pin, I2C, Timer
import ssd1306
import utime


width = 128
height = 64
i2c = 0x3c
oled = 0

last_button_press = 0   #0 = none, 1 = click, 2 = long press

_btn_on_ticks = 0
button_irq_count = 0
button_history = 0
button_last_tick = 0


#NO_UNHANDLED_BUTTON_PRESS = 0
#SHORT_PRESS = 1
#LONG_PRESS = 2


btn = Pin(25, Pin.IN, Pin.PULL_DOWN)    #Temp value because we can't declare a type. The real setup is in init

# Don't write code for multiple buttons until I have multiple buttons!
# Don't write code for double-click until I need a double-click!


start_pressed_millis = 0
 
_is_click = False
_is_press = False
_is_long_press = False
_keyup_reset = True

#These are the ones we care about in the UI
#  after reading the value, we reset to false. We assume that if its been read, it's been handled

def is_clicked():
    global _is_click
    if _is_click:
        _is_click = False
        return True
    else:
        return False

def is_pressed():
    global _is_press
    if _is_press:
        _is_press = False
        return True
    else:
        return False

def is_long_pressed():
    global _is_long_press
    if _is_long_press:
        _is_long_press = False
        return True
    else:
        return False


def _key_down_event():
    # detects the start of a button press
    #   we mask out 3 bits in the middle which we don't care about (they could be bouncy)
    #   then compare to a off/on transition
    global button_history
    pressed = False

    if (button_history & 0b11000111) == 0b00000111:
        pressed = True
        button_history = 0b11111111
    return pressed
    
def _key_up_event():
    global button_history
    released = False
    if (button_history & 0b11100011) == 0b11100000:
        released = True
        button_history = 0b00000000
    return released

def _key_is_down():
    global button_history
    return button_history == 0b11111111

def _key_is_up():
    global button_history
    return button_history == 0b00000000


def process_button():
    #this is run in the main loop
    #  keeps most of the work out of the interrupt handler
    global start_pressed_millis, _is_click, _is_press, _is_long_press, _keyup_reset

    if _key_down_event():
        start_pressed_millis = utime.ticks_ms()
        _is_click = False
        _is_press = False
        _is_long_press = False
        _keyup_reset = True

    if _key_up_event():
        _is_click = False
        _is_press = False
        _is_long_press = False

        press_duration = utime.ticks_diff(utime.ticks_ms(), start_pressed_millis)

        if press_duration < 700:
            _is_click = True

        if press_duration > 7000:
            _is_long_press = True  

    if _key_is_down():
        press_duration = utime.ticks_diff(utime.ticks_ms(), start_pressed_millis)
        #we need a key_up event between each Press
        if press_duration > 700 and _keyup_reset == True:
            _is_press = True    
            _keyup_reset = False









"""
## ignore this below here... old code based on interrupts. Cannot handle long press, double click etc

def btn_change(btn):
    if btn.value() == 1:
        btn_on(btn)
    else:
        btn_off(btn)

def btn_on(btn):
    global _btn_on_ticks
    _btn_on_ticks = utime.ticks_ms()
    #set a one-shot timer interrupt to detect the long press
    timer.init(period=4, mode=Timer.ONE_SHOT, callback=button_interrupt)

def btn_off(btn):
    global _btn_on_ticks
    global last_button_press
    global NO_UNHANDLED_BUTTON_PRESS, SHORT_PRESS, LONG_PRESS
    press_duration = utime.ticks_diff(utime.ticks_ms(), _btn_on_ticks) 
    if press_duration <= 30:
        last_button_press = NO_UNHANDLED_BUTTON_PRESS
        return
    if press_duration > 30 and press_duration < 200:
        last_button_press = SHORT_PRESS
        # navigate_menu()   #shouldn't really be doing this in the interupt handler. Keep it short!
        return
    if press_duration > 700:
        last_button_press = LONG_PRESS
 

"""
def init(screen_width, screen_height, i2c_address, scl_pin, sda_pin, button_gpio):
    global width, height, oled, btn
    width = screen_width
    height = screen_height

    i2c = I2C(scl=Pin(scl_pin), sda=Pin(5))
    oled = ssd1306.SSD1306_I2C(screen_width, screen_height, i2c, i2c_address)
    
    btn = Pin(button_gpio, Pin.IN, Pin.PULL_DOWN)
    #btn.irq(btn_change, Pin.IRQ_RISING | Pin.IRQ_FALLING)



def update_button_state(timer):
    ##button_irq_count helps us keep track of whether the interrupt has been handled
    #global button_irq_count
    #button_irq_count += 1 
    global btn
    
    #check button state, and store it in button_history, restrict it to the 
    #  last 8 reads
    global button_history
    button_history = ((button_history << 1) | btn.value()) & 0xFF


# just store 8 bits of history for start/end of a button push
# store max 32ms of history
# sample every 4ms
timer = Timer(0)
timer.init(period = 4, mode = Timer.PERIODIC, callback = update_button_state)



# oled coords: col, row

row_height = 10
row_offset = 2

class UiRow:
    def __init__ (self, text, on_press):
        self.text = text
        self.on_press = on_press


def _row_position(row_idx):
    global row_height, row_offset
    return ((row_idx) * row_height) + row_offset

content = []
selected_idx = 0

# adds or amends a row of text to the screen content
def row(text, callback):
    content.append(UiRow(text, callback))

def show():
    #render and show the screen
    global row_offset
    for idx, uirow in enumerate(content):
        text_color = 1
        bg_color = 0  
        if selected_idx == idx:
            text_color = 0
            bg_color = 1
        oled.fill_rect(0, _row_position(idx) - row_offset, width, row_height, bg_color)
        oled.text(uirow.text, 0, _row_position(idx), text_color)
    oled.show()

def clear():
    #clear array of screen items
    content.clear()
    oled.fill(0)


# used in the main loop
def navigate_menu():
    global selected_idx
    
    selected_idx += 1
    if selected_idx >= len(content):
        selected_idx = 0
    show()
