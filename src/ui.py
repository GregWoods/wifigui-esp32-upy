from machine import Pin, I2C, Timer
import utime
import ssd1306

    # Don't write code for multiple buttons until I have multiple buttons!
    # Don't write code for double-click until I need a double-click!

class UI:

    _btn = ""

    _btn_on_ticks = 0
    _button_irq_count = 0
    _button_history = 0
    _button_last_tick = 0

    _start_pressed_millis = 0
    _keypress_timer = ""
    
    _is_click = False
    _is_press = False
    _is_long_press = False
    _keyup_reset = True

    screen = ""

    def update_button_state(self, timer):       
        #check button state, and store it in button_history, restrict it to the 
        #  last 8 reads
        self._button_history = ((self._button_history << 1) | self._btn.value()) & 0xFF


    def __init__(self, oled, btn, timer, keypress_period):
        self.screen = Screen(oled)
        self._btn = btn
        timer.init(period = keypress_period, mode = Timer.PERIODIC, callback = self.update_button_state)
        self._keypress_timer = timer


    #--------------------------------------------------------------------------
    #These are the ones we care about in the UI
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

    def _key_down_event(self):
        # detects the start of a button press
        #   we mask out 3 bits in the middle which we don't care about (they could be bouncy)
        #   then compare to a off/on transition
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
            self._start_pressed_millis = utime.ticks_ms()
            self._is_click = False
            self._is_press = False
            self._is_long_press = False
            self._keyup_reset = True

        if self._key_up_event():
            self._is_click = False
            self._is_press = False
            self._is_long_press = False

            press_duration = utime.ticks_diff(utime.ticks_ms(), self._start_pressed_millis)

            if press_duration < 700:
                self._is_click = True

            if press_duration > 7000:
                self._is_long_press = True  

        if self._key_is_down():
            press_duration = utime.ticks_diff(utime.ticks_ms(), self._start_pressed_millis)
            #we need a key_up event between each Press
            if press_duration > 700 and self._keyup_reset == True:
                self._is_press = True    
                self._keyup_reset = False






#----------------------------------------------------------------------------------------------------

class UiRowType():
    menu = 0
    info = 1
    line = 2
    bottom = 3

#----------------------------------------------------------------------------------------------------

class Row:
    text = ""
    on_press = ""
    menu_type = ""

    def __init__ (self, text, onpress, menutype = UiRowType.menu):
        self.text = text
        self.on_press = onpress
        self.menu_type = menutype

#----------------------------------------------------------------------------------------------------

class Screen:
    oled = ""

    content = []
    selected_idx = 0

    row_height = 10
    row_offset = 2   


    def __init__ (self, oled : ssd1306):
        self.oled = oled
        self.set_first_selectable_idx()

    # adds or amends a row of text to the screen content
    def add_row(self, text, on_press = False, menu_type=UiRowType.menu):
        self.content.append(Row(text, on_press, menu_type))

    def _row_position(self, row_idx):
        return ((row_idx) * self.row_height) + self.row_offset

    def show(self, animate = True, preserve_selected_idx = False):
        if not preserve_selected_idx:
            self.set_first_selectable_idx()

        #render and show the screen
        for idx, uirow in enumerate(self.content):
            text_color = 1
            bg_color = 0  

            if self.selected_idx == idx:
                # invert colors
                text_color = 0
                bg_color = 1

            rowposition = self._row_position(idx)
            if UiRowType.bottom == uirow.menu_type:
                rowposition = self.oled.height - self.row_height

            self.oled.fill_rect(0, rowposition - self.row_offset, self.oled.width, self.row_height, bg_color)
            truncated_text = uirow.text[0:15]
            print(truncated_text)
            self.oled.text(uirow.text, 0, rowposition, text_color)
            # slow down the drawing a little to give a little animation to make it clearer when the screen changes
            #  and move oled.show() into the loop (inefficient, as the screen is redrawn multiple times, but it allows this animation)
            if (animate):
                utime.sleep_ms(50)
                self.oled.show()
        #For some screen refreshes, such as toggling items, we need to refresh as fast as possible
        if (animate == False):
            self.oled.show()


    def clear(self):
        #clear array of screen items
        self.content.clear()
        self.oled.fill(0)


    # used in the main loop
    def navigate_menu(self):
        self.set_next_selectable_idx()
        self.show(animate = False, preserve_selected_idx=True)


    def set_first_selectable_idx(self):
        self.selected_idx = self._get_selectable_idx(0)

    def set_next_selectable_idx(self):
        idx = self._inc_idx(self.selected_idx)
        self.selected_idx = self._get_selectable_idx(idx)        



    def _get_selectable_idx(self, idx):
        cnt = len(self.content)
        while(cnt > 0 ):   
            # if there is an on_press defined for this row, it is selectable, so exit
            if self.content[idx].on_press:
                break   
            idx = self._inc_idx(idx)
        return idx        

    def _inc_idx(self, idx):
        idx += 1
        if idx >= len(self.content):
            idx = 0
        return idx
        
    def call_current_row_method(self):
        self.content[self.selected_idx].on_press()


