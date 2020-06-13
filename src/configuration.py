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
        print(self.current)
        print(self.current['wifi'])
        print(self.current['wifi']['currentAP']['ssid'])


    def save_config(self):
        f = open('settings.json', 'w')
        f.write(json.dumps(self.current))
        f.close()


    #Convenience getters & setters for various config settings
    def get_wifi_enabled(self):
        return self.current['wifi']['enabled']


    def set_wifi_enabled(self, value):
        self.current['wifi']['enabled'] = value


    def get_wifi_state_text(self):
        wifi_text_state = "[off]"
        if self.get_wifi_enabled():
            wifi_text_state = "[on]"
        return wifi_text_state
