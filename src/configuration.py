import json
import uio


class ConfigManager:

    current = ""

    def __init__(self):
        self.load_config()

    def load_config(self):
        f = uio.open('settings.json', 'r')
        self.current = json.loads(f.read())
        f.close()
        print("Config Loaded")
        print(self.current['wifi']['currentAP'])


    def save_config(self):
        f = open('settings.json', 'w')
        f.write(json.dumps(self.current))
        f.close()


    #Convenience getters & setters for various config settings
    def get_wifi_enabled(self):
        return self.current['wifi']['enabled']


    def set_wifi_enabled(self, value):
        self.current['wifi']['enabled'] = value
        self.save_config()

    #not the right place for this
    def get_wifi_state_text(self):
        wifi_text_state = "[off]"
        if self.get_wifi_enabled():
            wifi_text_state = "[on]"
        return wifi_text_state

    def get_saved_AP_by_name(self, AP_name):
        # AP_name parameter may be a bytearray, if it has come from wlan.scan()
        APs = list(filter(lambda ap: ap['ssid'] == AP_name, self.current['wifi']['savedAPs']))
        if len(APs) > 1:
            print("That is odd! More than one Access Point with the name '", AP_name, "'")
        if len(APs) == 0:
            print("No saved AP called '", AP_name, "'")
            return {"ssid" : "", "password" : ""}
        print("Matching AP: ", APs[0])
        return APs[0]

    def get_current_AP(self):
        current_AP_name = self.current['wifi']['currentAP']
        ap = self.get_saved_AP_by_name(current_AP_name)
        return ap

    def is_AP_saved(self, AP_name):
        APs = list(filter(lambda ap: ap['ssid'] == AP_name, self.current['wifi']['savedAPs']))
        return len(APs) == 1

    def set_current_AP(self, value):
        self.current['wifi']['currentAP'] = value
        self.save_config()

