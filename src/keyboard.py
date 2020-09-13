
class KbType:
    LOWER = 0
    UPPER = 1

class Keyboard:

    oled = ""
    ok_callback = ""
    
    kb_variant = KbType.LOWER
    selected_row_idx = 0
    selected_key_idx = 0
    text = ""


    def __init__(self, oled, callback):
        print("keyboard init")
        self.oled = oled
        self.ok_callback = callback

    #TODO: custom graphical characters for things like Shift, Return, Backspace
    # LATER: consider plain array instead of lists. Look into memoryview
    # en-UK
    keyboards = [
        [
            ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0'],
            ['q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p'],
            ['a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l', '#'],
            ['z', 'x', 'c', 'v', 'b', 'n', 'm', '[Del]'],
            ['[CAPS]', '[ Ok ]']
        ], [
            ['!', '"', '£', '$', '%', '^', '&', '*', '(', ')'],
            ['Q', 'Q', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P'],
            ['A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L', '@'],
            ['Z', 'X', 'C', 'V', 'B', 'N', 'M', '[Del]'],
            ['[Sym]', '[ Ok ]']
        ], [
            ['!', '"', '£', '$', '%', '^', '&', '*', '(', ')'],
            ['Q', 'Q', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P'],
            ['A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L', '@'],
            ['Z', 'X', 'C', 'V', 'B', 'N', 'M', '[Del]'],
            ['[Lower]', '[ Ok ]']
        ]
    ]


    def show(self):
        FONT_WIDTH = 8
        KEY_SPACING = 5
        ROW_HEIGHT = 10

        print("keyboard show")

        vert_position = 0
        text_color = 1

        self.oled.fill(0)
        vert_position = 0
        for row_idx, row in enumerate(self.keyboards[self.kb_variant]):
            horiz_posn = 0
            for col_idx, key in enumerate(row):
                key_text = str(key)

                key_width = len(key_text) * FONT_WIDTH

                text_color = 1
                bg_color = 0
                if row_idx == self.selected_row_idx and col_idx == self.selected_key_idx:
                    text_color = 0
                    bg_color = 1

                vert_position = ROW_HEIGHT * row_idx
                self.oled.fill_rect(horiz_posn, vert_position - 1, key_width, ROW_HEIGHT, bg_color)
                self.oled.text(key_text, horiz_posn, vert_position, text_color)

                horiz_posn += key_width + KEY_SPACING

        self.oled.text(self.text, 0, self.oled.height - ROW_HEIGHT, 1)
        self.oled.show()

#
    def next_key(self):
        print("next_key")
        kb = self.keyboards[self.kb_variant]  #std keyboard for now

        # This feels very un-pythonic
        self.selected_key_idx += 1
        keys_in_row = len(kb[self.selected_row_idx])
        if self.selected_key_idx >= keys_in_row:
            self.selected_key_idx = 0
            self.selected_row_idx += 1
            if self.selected_row_idx >= len(kb):
                self.selected_row_idx = 0
        self.show()


    def select_current_key(self):
        kb = self.keyboards[self.kb_variant]  #std keyboard for now
        key = kb[self.selected_row_idx][self.selected_key_idx]
        # handle special keys
        if len(key) == 1:
            self.text += key
        elif key == "[CAPS]" or key == "[Sym]" or key == "[Lower]":
            self.kb_variant += 1
            if self.kb_variant >= len(self.keyboards):
                self.kb_variant = 0
        elif key == "[Del]":
            self.text = self.text[:-1]
        elif key == "[ Ok ]":
            print("Finished text is: " + self.text)
            self.ok_callback(self.text)
            return
        else:
            print("UNKNOWN key:'" + key + "'")

        self.show()
        print(self.text)
