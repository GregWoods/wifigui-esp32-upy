import machine
import ui
import utime

GPIO25 = 25
OLED_SCL = 4
OLED_SDA = 5
ui.init(128, 64, 0x3c, OLED_SCL, OLED_SDA, GPIO25)


#Top level WiFi menu
def turn_wifi_on():
    print("Turn ON Wifi")

def change_access_point():
    print("Change Access Point")    
    
def nothing():
    print("Back")

def main_menu():
    ui.clear()
    ui.row("WiFi [on]", turn_wifi_on)
    ui.row("MyAPName24", change_access_point)
    ui.row("Back", nothing)
    ui.show()

def forget_current_AP():
    print("Forget Current AP")

def choose_another_network():
    print("Choose another network")

def change_access_point():
    ui.clear()
    ui.row("Forget MyAPName24", forget_current_AP)
    ui.row("Choose another", choose_another_network)
    ui.row("Back", main_menu)
    ui.show()


print("start...")
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
    utime.sleep_ms(1)
