import machine
from machine import Pin, I2C, Timer
from micropython import kbd_intr
import network
import utime
import ssd1306

from button import Button
from menu_ui import Menu

# from configuration import ConfigManager
import configuration
from keyboard import Keyboard


GPIO25 = 25
OLED_SCL = 4
OLED_SDA = 5
screen_i2c_address = 0x3c

screen_width = 128
screen_height = 64

current_screen = ""
screen_type = "menu"    #"keyboard"

wlan = network.WLAN(network.STA_IF)
connecting = False
connected = False

config = configuration.ConfigManager()



def cancel_connecting():
    global connecting
    connecting = False
    wlan.disconnect()
    main_menu()

def connecting_screen():
    global current_screen, screen_type
    current_screen = "connecting_screen"
    screen_type = "menu"
    menu.clear()
    menu.add_row("Connecting...")
    menu.add_row("Cancel", cancel_connecting)
    menu.show()


def connect_wifi():
    global wlan, connecting, connected, config
    global current_screen

    currentAP = config.get_current_AP()
    ssid = currentAP['ssid']
    password = currentAP['password']
    wifi_enabled = config.current['wifi']['enabled']

    wlan.active(wifi_enabled)

    if wifi_enabled and ssid != "" and password != "":
        #print("Wifi enabled, SSID and Password are SET")
        if wlan.isconnected():
            print("Wifi is CONNECTED!")
            connecting = False
            #connection_attempt = 0
            connected = True
            print('network config:', wlan.ifconfig())

            main_menu(animate=False)
        else:
            # This way is cancellable with button press, as it works along with the main loop
            #print("Wifi is NOT connected!")
            if not connecting:
                #print("Starting connection: ", ssid, ", ", password)
                # we only "connect" once, and then wait in the main loop
                #   alternative is to try connecting, but then we'd need to pause without
                #      blocking keyboard input
                wlan.connect(ssid, password)
                connecting = True

                if current_screen != "connecting_Screen":
                    connecting_screen()

            else:
                print("waiting for connection")
            #    utime.sleep_ms(200)

            connected = False
#Testing!
def press3():
    print("Press 3")
def press4():
    print("Press 4")
def press5():
    print("Press 5")
def press6():
    print("Press 6")
def press7():
    print("Press 7")

#------------------------------------------------
#UI Menus

# create one global UiScreen, and reuse it.





def toggle_wifi():
    global current_screen, screen_type, config, connected
    current_screen = "main_menu"
    screen_type = "menu"
    print(current_screen)
    if config.get_wifi_enabled():
        config.set_wifi_enabled(False)
        connected = False
        main_menu(animate=False)
    else:
        config.set_wifi_enabled(True)
        connect_wifi()


def show_keyboard():
    global kbd_intr
    global screen_type
    screen_type = "keyboard"
    kb.show()


def kb_callback(text):
    print("kb_callback: " + text)

    main_menu()
    

def main_menu(animate=True, preserve_selected_idx=False):
    print("main_menu")
    global current_screen, screen_type, config

    # if we just came from main_menu, keep the currently selected menu row
    preserve_selected_idx = (current_screen == "main_menu")

    current_screen = "main_menu"
    screen_type = "menu"

    menu.clear()
    #menu.add_row("test ", change_access_point)
    menu.add_row("WiFi " + config.get_wifi_state_text(), toggle_wifi)
    menu.add_row(config.current['wifi']['currentAP'], change_access_point)
    menu.add_row("Keyboard", show_keyboard)

    menu.add_row("Test 1 ", toggle_wifi)

    #if connected:
    #    menu.add_row(wlan.ifconfig()[0], menu_type = UiRowType.bottom)
    menu.show(animate, preserve_selected_idx)

def forget_current_AP():
    global current_screen
    current_screen = "forget_current_AP"
    print(current_screen)


def select_ap(ap_idx):
    global config
    global access_points
    print("selected AP:", ap_idx)

    #save the AP
    selected_AP = access_points[ap_idx]
    AP_name = selected_AP[0].decode()
    config.set_current_AP(AP_name)

    if config.is_AP_saved(AP_name):
        connect_wifi()
    else:
        input_wifi_password()


def input_wifi_password():
    global current_screen, screen_type
    current_screen = "wifi_password"
    screen_type = "keyboard"
    print("input_wifi_password")
    kb = Keyboard(oled, kb_callback)
    kb.show()

access_points = []

def choose_another_network():
    global current_screen, screen_type
    global wlan
    global access_points
    current_screen = "choose_another_network"
    screen_type = "menu"
    print(current_screen)

    #temporary "scanning" menu, so the user knows their button Press worked
    menu.clear()
    menu.add_row("Scanning...")
    menu.show()

    access_points = wlan.scan() #blocks for a couple of seconds
    print(access_points)
    menu.clear()
    for idx, ap in enumerate(access_points):
        menu.add_row(ap[0], lambda tmp=idx: select_ap(tmp))
    menu.add_row("Back", change_access_point)
    menu.show()


def change_access_point():
    global current_screen, screen_type, config
    current_screen = "change_access_point"
    screen_type = "menu"
    menu.clear()
    menu.add_row("Forget " + config.current['wifi']['currentAP'], forget_current_AP)
    menu.add_row("Choose another", choose_another_network)
    menu.add_row("Back", main_menu)
    menu.show()



print("---------------------------------------------")
print("start...")
print("---------------------------------------------")
print("")
print("")
print(machine.freq()/1000000)


# Dependencies for Button and Screen classes
i2c = I2C(scl=Pin(OLED_SCL), sda=Pin(OLED_SDA))
oled = ssd1306.SSD1306_I2C(screen_width, screen_height, i2c, screen_i2c_address)
btn = Pin(GPIO25, Pin.IN, Pin.PULL_DOWN)    #Temp value because we can't declare a type. The real setup is in init
# sample keypresses every 4ms (with 8bits of history = 32ms to detect and debounce a valid press and release event)
timer = Timer(0)

MAX_ROWS = 5
ROW_HEIGHT = int(screen_height / MAX_ROWS)

button = Button(btn, timer)
menu = Menu(oled, ROW_HEIGHT)
kb = Keyboard(oled, kb_callback)


main_menu(animate=False)
#connect_wifi() #disable to speed up testing


while True:
    # some OO magic would be useful here

    button.process_button()

    if screen_type == "menu":
        #interupts constantly set the state of the last press
        if button.is_clicked():
            menu.navigate_menu()
            print("Click")
        if button.is_pressed():
            print("Press")
            menu.call_current_row_method()
        if button.is_long_pressed():
            print("Very long press")


    elif screen_type == "keyboard":
        #interupts constantly set the state of the last press
        if button.is_clicked():
            kb.next_key()
        if button.is_pressed():     #rename to long_clicked
            kb.select_current_key()
        #if button.is_long_pressed():
        #    print("Very long press")
        #    kb.start_keyrepeat()


    if connecting and not connected:
        connect_wifi()

    utime.sleep_ms(10)
    