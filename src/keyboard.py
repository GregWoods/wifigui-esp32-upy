
class KbType:
    LOWER = 0
    UPPER = 1

class Keyboard:

    oled = ""
    selected_row_idx = 4
    selected_key_idx = 0

    def __init__(self, oled):
        print("keyboard init")
        self.oled = oled

    #TODO: custom graphical characters for things like Shift, Return, Backspace
    # LATER: consider plain array instead of lists. Look into memoryview
    # en-UK
    kb = [
        [
            ['1','2','3','4','5','6','7','8','9','0'],    
            ['q','w','e','r','t','y','u','i','o','p'],
            ['a','s','d','f','g','h','j','k','l','#'],
            ['z','x','c','v','b','n','m',',','.','/'],
            [(0, '[Shift]'), (6, '[ Ok ]')]
        ],[
            ['!','"','£','$','%','^','&','*','(',')'],    
            ['Q','Q','E','R','T','Y','U','I','O','P'],
            ['A','S','D','F','G','H','J','K','L','@'],
            ['|','Z','X','C','V','B','N','M','?'],
            [(0, '[Shift]'), (6, '[ Ok ]')]
        ]
    ]


    #kb = [
    #    [
    #        ['1', '2','3','4','5','6','7','8','9','0','-','='],    
    #        ['q', 'w','e','r','t','y','u','i','o','p','[',']'],
    #        ['a', 's','d','f','g','h','j','k','l',';',"'",'#'],
    #        ["\\",'z','x','c','v','b','n','m',',','.','/'],
    #        ['[ Shift ]', '[  Ok  ]']
    #    ],
    #        ['!', '"','£','$','%','^','&','*','(',')','_','+'],    
    #        ['Q', 'Q','E','R','T','Y','U','I','O','P','{','}'],
    #        ['A', 'S','D','F','G','H','J','K','L',':',"@",'~'],
    #        ['|','Z','X','C','V','B','N','M','<','>','?'],
    #        ['[ Shift ]', '[  Ok  ]']
    #]    

    def show(self):
        FONT_WIDTH = 8
        KEY_SPACING = 13
        ROW_HEIGHT = 10
    
        print("keyboard show")

        self.oled.fill(0)
        kb_type = KbType.LOWER
        for row_idx, row in enumerate(self.kb[kb_type]):
            for col_idx, key in enumerate(row):
                horiz_posn = KEY_SPACING * col_idx
                key_text = str(key)
                key_width = KEY_SPACING
                if isinstance(key, tuple):
                    #special key, such as [ ok ] or [shift]
                    #  first item in the tuple is the number of characters across to position it
                    horiz_posn = KEY_SPACING * key[0]
                    key_text = key[1]
                    key_width = len(key_text) * FONT_WIDTH

                text_color = 1
                bg_color = 0
                if row_idx == self.selected_row_idx and col_idx == self.selected_key_idx:
                    text_color = 0
                    bg_color = 1     

                vert_position = ROW_HEIGHT * row_idx
                self.oled.fill_rect(horiz_posn, vert_position - 1, key_width, ROW_HEIGHT, bg_color)
                self.oled.text(key_text, horiz_posn, vert_position, text_color)
        self.oled.show()