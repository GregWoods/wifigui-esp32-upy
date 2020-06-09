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
    
def nothing():
    print("Back")

def main_menu():
    ui.clear()
    ui.row("WiFi <off>", turn_wifi_on)
    ui.row("<back>", nothing)
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
