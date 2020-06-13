import machine
from machine import Pin, I2C, Timer
import network
import uio
import ujson as json
import utime
import ssd1306

from ui import UI, UiRowType, Screen
import configuration


GPIO25 = 25
OLED_SCL = 4
OLED_SDA = 5
screen_i2c_address = 0x3c

screen_width = 128
screen_height = 64

current_screen = ""

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
    global current_screen
    current_screen = "connecting_screen"
    ui.screen.clear()
    ui.screen.add_row("Connecting...")
    ui.screen.add_row("Cancel", cancel_connecting)
    ui.screen.show()

def connect_wifi():
    global wlan, connecting, connected, config
    global current_screen

    ssid = config.current['wifi']['currentAP']['ssid']
    password = config.current['wifi']['currentAP']['password']
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

            main_menu(animate = False)   
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
            
  
#------------------------------------------------    
#UI Menus

# create one global UiScreen, and reuse it.





def toggle_wifi():
    global current_screen, config, connected
    current_screen = "main_menu"       
    print(current_screen)
    if config.get_wifi_enabled():
        config.set_wifi_enabled(False)
        connected = False
        main_menu(animate = False)
    else:
        config.set_wifi_enabled(True)
        connect_wifi()
    

def change_access_point():
    global current_screen
    current_screen = "change_access_point"    
    print("Change Access Point")    
    

def main_menu(animate = True, preserve_selected_idx = False):
    global current_screen, config
    preserve_selected_idx = (current_screen == "main_menu")

    current_screen = "main_menu"
    ui.screen.clear()
    #ui.screen.add_row("test ", change_access_point)
    ui.screen.add_row("WiFi " + config.get_wifi_state_text(), toggle_wifi)
    ui.screen.add_row(config.current['wifi']['currentAP']['ssid'], change_access_point)
    if connected:
        ui.screen.add_row(wlan.ifconfig()[0], menu_type = UiRowType.bottom)
    ui.screen.show(animate, preserve_selected_idx)

def forget_current_AP():
    global current_screen
    current_screen = "forget_current_AP"    
    print(current_screen)

def choose_another_network():
    global current_screen
    current_screen = "choose_another_network"    
    print(current_screen)

def change_access_point():
    global current_screen, config, ui
    current_screen = "change_access_point"
    ui.screen.clear()
    ui.screen.add_row("Forget " + config.current['wifi']['currentAP']['ssid'], forget_current_AP)
    ui.screen.add_row("Choose another", choose_another_network)
    ui.screen.add_row("Back", main_menu)
    ui.screen.show()


print("---------------------------------------------")
print("start...")
print("---------------------------------------------")
print("")
print("")
print(machine.freq()/1000000)


# Dependencies for ui class
i2c = I2C(scl=Pin(OLED_SCL), sda=Pin(OLED_SDA))
oled = ssd1306.SSD1306_I2C(screen_width, screen_height, i2c, screen_i2c_address)
btn = Pin(GPIO25, Pin.IN, Pin.PULL_DOWN)    #Temp value because we can't declare a type. The real setup is in init
# sample keypresses every 4ms (with 8bits of history = 32ms to detect and debounce a valid press and release event)
timer = Timer(0)
KEYPRESS_PERIOD = 4

ui = UI(oled, btn, timer, KEYPRESS_PERIOD)

main_menu(animate = False)
connect_wifi()

while (True):
    #interupts constantly set the state of the last press
    ui.process_button()

    if ui.is_clicked():
        ui.screen.navigate_menu()
        print("Click")
    if ui.is_pressed():
        print("Press")
        ui.screen.call_current_row_method()
    if ui.is_long_pressed():
        print("Very long press")
    
    if connecting and not connected:
        connect_wifi()


    utime.sleep_ms(10)

