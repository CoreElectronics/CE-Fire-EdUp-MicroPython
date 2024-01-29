import os
import sys
from machine import I2C, Pin

# perform initial scan of connected devices
diagnostic_i2c = I2C(0, sda=Pin(8), scl=Pin(9))
connected_devices = diagnostic_i2c.scan()

def file_exists(filename):
    try:
        os.stat(filename)
        return True
    except OSError:
        return False

failed_import_string = "Couldn't find {} - make sure it is uploaded to your Pico and try again"

filename = "PiicoDev_Unified.py"
if file_exists(filename):
    from PiicoDev_Unified import sleep_ms
else:
    print(failed_import_string.format(filename))
    sys.exit()

filename = "enhanced_display.py"
if file_exists(filename):
    from enhanced_display import Enhanced_Display
else:
    print(failed_import_string.format(filename))
    
filename = "PiicoDev_Buzzer.py"
if file_exists(filename):
    from PiicoDev_Buzzer import PiicoDev_Buzzer
else:
    print(failed_import_string.format(filename))

filename = "PiicoDev_Potentiometer.py"
if file_exists(filename):
    from PiicoDev_Potentiometer import PiicoDev_Potentiometer
else:
    print(failed_import_string.format(filename))
    
filename = "PiicoDev_TMP117.py"
if file_exists(filename):
    from PiicoDev_TMP117 import PiicoDev_TMP117
else:
    print(failed_import_string.format(filename))

TMP117_base_address = 0x48

from time import ticks_ms


# The Fire-EdUp model names and associated FBI weighting
models = {'button grass':         1.00,
          'spinifex grasslands':  1.10,
          'grasslands':           1.15,
          'grassy woodlands':     1.20,
          'mallee-heaths':        1.25,
          'wet eucalypt forests': 1.30,
          'shrublands':           1.40,
          'pine plantations':     1.45,
          'dry eucalypt forests': 1.50}

# Creates a list of the key names in a bullet-list format
def dict_keys_to_string(dictionary):
    result = ""
    for key in dictionary.keys():
        result += f"\n• {key}"
    return result


class Firedup:
    def FBI_to_rating(self, fbi):
        if fbi < 12: return 'no rating'
        if fbi < 24: return 'moderate'
        if fbi < 50: return 'high'
        if fbi < 100: return 'extreme'
        return 'catastrophic'

    def show_fire_danger(self, rating):
        assert rating in ["no rating", "moderate", "high", "extreme", "catastrophic"], f"Got '{rating}'. Valid ratings are: 'no rating', 'moderate', 'high', 'extreme', or 'catastrophic'"
        self.display.fill(0)
        if rating == "no rating": self.display.load_pbm('no-rating.pbm', 1)
        elif rating == 'moderate': self.display.load_pbm('moderate.pbm', 1)
        elif rating == 'high': self.display.load_pbm('high.pbm', 1)
        elif rating == 'extreme': self.display.load_pbm('extreme.pbm', 1)
        elif rating == 'catastrophic': self.display.load_pbm('catastrophic.pbm', 1)
        self.display.show()
        
    def fire_behaviour_index(self, data):
        '''FBI is calculated using a predefined model. The value of FBI informs the Fire Danger Rating'''
        # Debugging
#         print(f'{self.temperature.value:3.0f}, {self.humidity.value:3.0f}, {self.wind.value:3.0f}, {self.fuel.value:4.2f}, {self.moisture.value:3.0f}')
        
        # normalise inputs and apply weighting
        norm_temperature = 0.60 * data['temperature'] / self.temperature.maximum
        norm_humidity = 0.60 - 0.6 * data['humidity'] / self.humidity.maximum # scale inverted. less humididty -> more risk
        norm_wind = 0.60 * data['wind'] / self.wind.maximum
        norm_fuel = 100 * data['fuel'] / self.fuel.maximum
        norm_moisture = 0.60 - 0.6 * data['moisture'] / self.moisture.maximum # scale inverted. less moisture -> more risk
#         print(f'{norm_temperature:3.0f}, {norm_humidity:3.0f}, {norm_wind:3.0f}, {norm_fuel:4.2f}, {norm_moisture:3.0f}')
        return self._model_weight * self._slope_weight * norm_fuel * (norm_temperature + norm_humidity + norm_wind + norm_moisture)
    
    @property
    def model(self):
        return self._model_name
    @model.setter
    def model(self, value):
        input_string_lower = value.lower()

        # Check if the lowercased input string is a key in the models dictionary
        if input_string_lower in models:
            # Assign the model's key (original format) to a new variable
            matched_model_key = next(key for key, value in models.items() if key.lower() == input_string_lower)
            self._model_name = matched_model_key
            self._model_weight = models[input_string_lower]
        else:
            raise ValueError(f"Invalid model name provided: '{value.lower()}'\nValid models are: \n" + dict_keys_to_string(models))
        
    def create_model(self, name, weight):
        if not isinstance(name, str):
            raise TypeError("in create_model(name, weight) -> 'name' must be a string")
        if not isinstance(weight, (int, float)):
            raise TypeError("in create_model(name, weight) -> 'weight' must be a number")
        self._model_name = name
        self._model_weight = weight
    
    @property
    def model_weight(self):
        return self._model_weight
    @model_weight.setter
    def model_weight(self, value):
        self._model_name = 'Unnamed Model'
        self._model_weight = value

    
    
    @property
    def slope_degrees(self):
        return self._slope_degrees
    @model.setter
    def slope_degrees(self, value):
        assert -90 <= value <= 90, ".slope_degrees must be between -90.0 and 90.0"
        self._slope_degrees = value
        self._slope_weight = 1 + 0.5 * abs(value)/90
    
    
    def calculate_rating(self, data):
        self.display_mode = "rating"
        force_update = False
        screen_mode_timeout = 2000
        
        # Look for changes in slider values
        difference_threshold = 0.5
        
        if abs(data['temperature'] - self.last_value["temperature"]) > difference_threshold:
            self.time_of_last_change["temperature"] = ticks_ms()
            
        if abs(data['humidity'] - self.last_value["humidity"]) > difference_threshold:
            self.time_of_last_change["humidity"] = ticks_ms()
            
        if abs(data['wind'] - self.last_value["wind"]) > difference_threshold:
            self.time_of_last_change["wind"] = ticks_ms()
            
        if abs(data['fuel'] - self.last_value["fuel"]) > difference_threshold:
            self.time_of_last_change["fuel"] = ticks_ms()
            
        if abs(data['moisture'] - self.last_value["moisture"]) > difference_threshold:
            self.time_of_last_change["moisture"] = ticks_ms()
        
        # Which was changed most recently?
        most_recently_changed = max(self.time_of_last_change, key=self.time_of_last_change.get)
        if abs(ticks_ms() - self.time_of_last_change[most_recently_changed]) < screen_mode_timeout:
            self.display_mode = "value"        
        
        # If slider has changed recently, update it's displayed value
        if abs(ticks_ms() - self.time_of_last_change["temperature"]) < screen_mode_timeout:
            self.last_value["temperature"] = data['temperature']
        if most_recently_changed == 'temperature':
            self.live_value = data['temperature']
            self.live_unit = ' degC'
            
        if abs(ticks_ms() - self.time_of_last_change["humidity"]) < screen_mode_timeout:
            self.last_value["humidity"] = data['humidity']
        if most_recently_changed == 'humidity':
            self.live_value = data['humidity']
            self.live_unit = ' %RH'
            
            
        if abs(ticks_ms() - self.time_of_last_change["wind"]) < screen_mode_timeout:
            self.last_value["wind"] = data['wind']
        if most_recently_changed == 'wind':
            self.live_value = data['wind']
            self.live_unit = ' km/h'
            
            
        if abs(ticks_ms() - self.time_of_last_change["fuel"]) < screen_mode_timeout:
            self.last_value["fuel"] = data['fuel']
        if most_recently_changed == 'fuel':
            self.live_value = data['fuel']
            self.live_unit = ' t/ha'
            
            
        if abs(ticks_ms() - self.time_of_last_change["moisture"]) < screen_mode_timeout:
            self.last_value["moisture"] = data['moisture']
        if most_recently_changed == 'moisture':
            self.live_value = data['moisture']
            self.live_unit = ' %'
            if self.live_value > 19.5:
                self.live_value = 20
                self.live_unit = "+" + self.live_unit
        
        fbi = self.fire_behaviour_index(data)
        self.FBI = round(fbi)
        rating = self.FBI_to_rating( fbi )
        
        # Display the changing value
        if self.display_mode == "value":
            self.display.fill(0)
            self.display.select_font('digits-30')
            self.live_value = round(self.live_value)
            self.display.text(f'{self.live_value}', 0, 0)
            self.display.select_font('text-16')
            self.display.text(f'{self.live_unit}', 65, 14)
            self.display.text(f'FBI: {fbi:.0f}', 0,  48)
            self.display.show()
            
            
        # Timeout the value display
        if all( abs(ticks_ms() - value) > screen_mode_timeout for value in self.time_of_last_change.values()):
            force_update = True
            self.display_mode = "rating"
        else:
            force_update = False
        
        
        if self.display_mode == "rating" and rating is not self.last_rating or force_update: #save updating the display every loop (slow)
            self.show_fire_danger( rating )
            
        if self.last_rating != rating:
            self._rating_has_changed = True
        else:
            self._rating_has_changed = False
        self.last_rating = rating
        return rating
        
    def tone(self, frequency, duration):
        self.buzzer.tone(frequency, duration)
        
    def collect_data(self, use_temperature_sensor = False):
        if use_temperature_sensor:
            if TMP117_base_address in connected_devices:
                temp = self.temperature_sensor.readTempC() # read the sensor
            else:
                print("Could not find a temperature sensor. Is it connected?")
                temp = 0
                sys.exit()
        else:
            temp = self.temperature.value # read the slide-pot as normal
            
        data = {"temperature": round(temp,1),
                "humidity":    round(self.humidity.value,1),
                "wind":  round(self.wind.value,1),
                "fuel":   round(self.fuel.value,1),
                "moisture": round(self.moisture.value,1)
                }
        return data
    
    def update_display(self):
        pass
    
    def rating_has_changed(self):
        temp = self._rating_has_changed
        self._rating_has_changed = False
        return temp
        
        
    def __init__(self):
        self.display = Enhanced_Display()
        self.display.load_fonts(['digits-30', 'text-16'])
        
        # Initialise the potentiometers with scales that match the printed labels
        self.temperature = PiicoDev_Potentiometer(id=[0,0,0,0], minimum=0, maximum=51)
        self.humidity = PiicoDev_Potentiometer(id=[0,0,0,1], minimum=0, maximum=100)
        self.wind = PiicoDev_Potentiometer(id=[0,0,1,0], minimum=0, maximum=118)
        self.fuel = PiicoDev_Potentiometer(id=[0,1,0,0], minimum=0, maximum=100)
        self.moisture = PiicoDev_Potentiometer(id=[1,0,0,0], minimum=0, maximum=20)
        self.buzzer = PiicoDev_Buzzer()
        self.temperature_sensor = PiicoDev_TMP117()
        
        
        self._model_name = None
        self._model_weight = 1
        self._slope_weight = 1
        self.last_rating = None
        self._rating_has_changed = False
        self.display_mode = "rating"
        self.time_of_last_change = {
            "temperature": 0,
            "humidity": 0,
            "wind": 0,
            "fuel": 0,
            "moisture": 0
            }
        
        self.last_value = {
            "temperature": self.temperature.value,
            "humidity": self.humidity.value,
            "wind": self.wind.value,
            "fuel": self.fuel.value,
            "moisture": self.moisture.value
            }

        
firedup = Firedup()
last_rating = None # used to detect a change in rating