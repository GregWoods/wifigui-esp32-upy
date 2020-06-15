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


    def __init__(self, oled, btn, timer, rowheight, keypress_period):
        self.screen = Screen(oled, rowheight)
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
    menu_selected_idx = 0
    screen_top_idx = 0
    scroll_offset = 0

    _row_height = 8
    _row_offset = 2  # used to move text a few pixels down relative to the background box 

    max_rows = 0

    def __init__ (self, oled : ssd1306, rowheight):
        self._row_height = rowheight
        self.oled = oled
        self.set_first_selectable_idx()
        self.max_rows = int(self.oled.height / self._row_height)

    # adds or amends a row of text to the screen content
    def add_row(self, text, on_press = False, menu_type=UiRowType.menu):
        self.content.append(Row(text, on_press, menu_type))

    def _row_position(self, row_idx):
        return ((row_idx) * self._row_height) + self._row_offset


    def show(self, animate = True, preserve_selected_idx = False):
        self.buffer(animate, preserve_selected_idx)
        self.oled.show()


    #split off from show() so we can use buffer(), oled.scroll(), show()
    def buffer(self, animate = True, preserve_selected_idx = False):

        if not preserve_selected_idx:
            self.set_first_selectable_idx()
        
        #make sure the number of rows fits on screen
        #  if we have some spare vertical pixels after max_row, 
        #    populate it with the next row. It gives a visual indication there are more options

        #rows_to_show may be one more than max_rows

        rows_to_show = self.max_rows    # max_rows better named whole_visible_rows
        if self.oled.height % self._row_height > 0:
            rows_to_show += 1

        current_content = self.content[self.screen_top_idx : self.screen_top_idx + rows_to_show]
        screen_selected_idx = self.menu_selected_idx - self.screen_top_idx

        for idx, uirow in enumerate(current_content):
            text_color = 1
            bg_color = 0  

            if screen_selected_idx == idx:
                # invert colors
                text_color = 0
                bg_color = 1

            rowposition = self._row_position(idx)
            if UiRowType.bottom == uirow.menu_type:
                rowposition = self.oled.height - self._row_height

            self.oled.fill_rect(0, rowposition - self._row_offset, self.oled.width, self._row_height, bg_color)
            truncated_text = uirow.text[0:15]
            #print(truncated_text)
            self.oled.text(uirow.text, 0, rowposition, text_color)


    def clear(self):
        #clear array of screen items
        self.content.clear()
        self.oled.fill(0)


    # used in the main loop
    def navigate_menu(self):
        self.set_next_selectable_idx()
        self.set_screen_top_idx()
        self.show(animate = False, preserve_selected_idx=True)
              

    def set_screen_top_idx(self):
        if self.menu_selected_idx >= (self.screen_top_idx + self.max_rows):
            print("navigated of bottom of visible items")
            self.screen_top_idx += 1
        elif self.menu_selected_idx < self.screen_top_idx:
            print("navigated of bottom of entire menu. Looped back to the start")
            # scrolled off the bottom of the menu, move menu back to the top
            self.screen_top_idx = 0
            #additional loop needed here... if, due to non-selectable menu items, the next selectable menu item is off the bottom of the screen
            #  this is not a desirable menu layout, as it means some info items will always be scrolled out of view
            

    def set_first_selectable_idx(self):
        self.menu_selected_idx = self._get_selectable_idx(0)

    def set_next_selectable_idx(self):
        idx = self._inc_idx(self.menu_selected_idx)
        self.menu_selected_idx = self._get_selectable_idx(idx)        



    def _get_selectable_idx(self, idx):
        for _ in self.content:  
            # if there is an on_press defined for this row, it is selectable, so exit
            if self.content[idx].on_press:
                return idx   
            idx = self._inc_idx(idx)
        #if we get to the end of the for loop, nothing was selectable
        return -1        

    def _inc_idx(self, idx):
        idx += 1
        if idx >= len(self.content):
            idx = 0
        return idx
        
    def call_current_row_method(self):
        self.content[self.menu_selected_idx].on_press()


