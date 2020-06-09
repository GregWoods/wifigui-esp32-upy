import machine
import network
import uio
import ujson as json
import ui
import utime
import json

GPIO25 = 25
OLED_SCL = 4
OLED_SDA = 5
ui.init(128, 64, 0x3c, OLED_SCL, OLED_SDA, GPIO25)

config = ""
#------------------------------------------------    

def load_config():
    global config
    f = uio.open('settings.json', 'r')
    config = json.loads(f.read())
    f.close()
    print(config)
    print(config['wifi'])
    print(config['wifi']['currentAP']['ssid'])

def save_config():
    global config
    f = open('settings.json', 'w')
    f.write(json.dumps(config))
    f.close()

#Convenience getters & setters for various config settings
def get_wifi_enabled():
    global config
    return config['wifi']['enabled']

def set_wifi_enabled(value):
    global config
    config['wifi']['enabled'] = value

def get_wifi_state_text():
    wifi_text_state = "[off]"
    if get_wifi_enabled():
        wifi_text_state = "[on]"
    return wifi_text_state

#------------------------------------------------    

current_screen = ""

def cancel_connecting():
    global connecting
    connecting = False
    main_menu()

def connecting_screen():
    global current_screen
    current_screen = "connecting_screen"
    ui.clear()
    ui.row("Connecting...", nothing)
    ui.row("Cancel", cancel_connecting)
    ui.selected_idx = 1
    ui.show()


wlan = network.WLAN(network.STA_IF)
connecting = False
connected = False


def connect_wifi():
    global wlan, config, connecting, connected
    global current_screen

    ssid = config['wifi']['currentAP']['ssid']
    password = config['wifi']['currentAP']['password']
    wifi_enabled = config['wifi']['enabled']

    wlan.active(wifi_enabled) 

    if wifi_enabled and ssid != "" and password != "":
        #print("Wifi enabled, SSID and Password are SET")
        if wlan.isconnected():
            print("Wifi is CONNECTED!")
            connecting = False
            connected = True
            print('network config:', wlan.ifconfig())    
        else:
            #print("Wifi is NOT connected!")
            if not connecting:
            #    print("Starting connection: ", ssid, ", ", password)

                wlan.connect(ssid, password)
                connecting = True
                if current_screen != "connecting_Screen":
                    connecting_screen()
                
            #else:
            #    print("waiting for connection")
            #    utime.sleep_ms(200)

            connected = False
            
            
            
#------------------------------------------------    
#UI Menus

def toggle_wifi():
    global current_screen
    current_screen = "toggle_wifi"       
    print(current_screen)
    if get_wifi_enabled():
        set_wifi_enabled(False)
        main_menu()
    else:
        set_wifi_enabled(True)
        connect_wifi()
        

def change_access_point():
    global current_screen
    current_screen = "change_access_point"    
    print("Change Access Point")    
    
def nothing():
    print("Back")

def main_menu(animate = True):
    global current_screen
    current_screen = "main_menu"
    ui.clear()
    ui.row("WiFi " + get_wifi_state_text(), toggle_wifi)
    ui.row(config['wifi']['currentAP']['ssid'], change_access_point)
    ui.show(animate)

def forget_current_AP():
    global current_screen
    current_screen = "forget_current_AP"    
    print(current_screen)

def choose_another_network():
    global current_screen
    current_screen = "choose_another_network"    
    print(current_screen)

def change_access_point():
    global current_screen
    current_screen = "change_access_point"
    ui.clear()
    ui.row("Forget " + config['wifi']['currentAP']['ssid'], forget_current_AP)
    ui.row("Choose another", choose_another_network)
    ui.row("Back", main_menu)
    ui.show()


#------------------------------------------


print("---------------------------------------------")
print("start...")
print("---------------------------------------------")
print("")
print("")
print(machine.freq()/1000000)
load_config()


main_menu()

while (True):
    #interupts constantly set the state of the last press
    ui.process_button()

    if ui.is_clicked():
        ui.navigate_menu()
        print("Click")
    if ui.is_pressed():
        print("Press")
        ui.call_current_row_method()
    if ui.is_long_pressed():
        print("Very long press")
    
    if connecting and not connected:
        connect_wifi()


    utime.sleep_ms(10)
