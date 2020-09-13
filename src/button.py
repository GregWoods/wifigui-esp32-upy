from machine import Timer
import utime

    # Don't write code for multiple buttons until I have multiple buttons!
    # Don't write code for double-click until I need a double-click!


class Button:

    _btn = ""

    _btn_on_ticks = 0
    _button_irq_count = 0
    _button_history = 0
    _button_last_tick = 0

    _start_pressed_millis = 0
    _keypress_timer = ""
    last_key_repeat_millis = 0

    _is_click = False
    _is_press = False
    _is_long_press = False
    _keyup_reset = True

    press_duration = 0

    KEYPRESS_PERIOD = 4
    MAX_CLICK_DURATION = 200
    MAX_LONG_CLICK_DURATION = 1100
    KEYREPEAT_INTERVAL = 150

    # The interrupt handler
    def update_button_state(self, _timer):
        #check button state, and store it in button_history, restrict it to the
        #  last 8 reads
        self._button_history = ((self._button_history << 1) | self._btn.value()) & 0xFF


    def __init__(self, btn, timer):
        self._btn = btn
        timer.init(period=self.KEYPRESS_PERIOD, mode=Timer.PERIODIC, callback=self.update_button_state)
        self._keypress_timer = timer


    #--------------------------------------------------------------------------
    #These are state checks we care about in the UI
    #  after reading the value, we reset to false. We assume that if its been read, it's been handled

    # They are used in conjunction with process_button()

    def is_clicked(self):
        if self._is_click:
            self._is_click = False
            return True
        else:
            return False

    def is_pressed(self):
        if self._is_press:
            self._is_press = False
            return True
        else:
            return False

    def is_long_pressed(self):
        if self._is_long_press:
            self._is_long_press = False
            return True
        else:
            return False

    #--------------------------------------------------------------------------
    # Used internally by process_button to debounce the button

    def _key_down_event(self):
        # detects the start of a button press
        #   we mask out 3 bits in the middle which we don't care about (they could be bouncy)
        #   then compare to an off/on transition
        pressed = False
        if (self._button_history & 0b11000111) == 0b00000111:
            pressed = True
            self._button_history = 0b11111111
        return pressed


    def _key_up_event(self):
        released = False
        if (self._button_history & 0b11100011) == 0b11100000:
            released = True
            self._button_history = 0b00000000
        return released


    def _key_is_down(self):
        return self._button_history == 0b11111111


    def _key_is_up(self):
        return self._button_history == 0b00000000


    #--------------------------------------------------------------------------

    def process_button(self):
        #this is run in the main loop
        #  keeps most of the work out of the interrupt handler

        if self._key_down_event():
            print("key_down_event")
            self._start_pressed_millis = utime.ticks_ms()
            self._is_click = False
            self._is_press = False
            self._is_long_press = False
            self._keyup_reset = True
            self.last_key_repeat_millis = 0

        if self._key_up_event():
            print("key_up_event")
            self._is_click = False
            self._is_press = False
            self._is_long_press = False
            self.last_key_repeat_millis = 0

            self.press_duration = utime.ticks_diff(utime.ticks_ms(), self._start_pressed_millis)
            print(self.press_duration)
            if self.press_duration < self.MAX_CLICK_DURATION:
                self._is_click = True
            elif self.press_duration < self.MAX_LONG_CLICK_DURATION:
                self._is_press = True

            self.press_duration = 0

        if self._key_is_down():
            self.press_duration = utime.ticks_diff(utime.ticks_ms(), self._start_pressed_millis)

            if self.press_duration > self.MAX_LONG_CLICK_DURATION:  #and self._keyup_reset:
                self._is_press = False

                now = utime.ticks_ms()
                if now > self.last_key_repeat_millis + self.KEYREPEAT_INTERVAL:
                    print("key is down")
                    #call same function as "click"
                    self._is_click = True   #not sure this is the right way to do it
                    self.last_key_repeat_millis = now

