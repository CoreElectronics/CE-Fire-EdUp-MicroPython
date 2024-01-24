'''
Connect an optional precision temperature sensor and tell the .collect_data() method to use_temperature_sensor=True
This will override the user-input in favour of using a real sensor.
'''

from firedup import *

# Initialise the simulation and select the Model and Slope

firedup.model = 'button grass'
firedup.slope_degrees = 3

while True:
    # Collect data using a real precision temperature sensor instead of the user-input
    data = firedup.collect_data(use_temperature_sensor = True)
    
    print(data) # optional: show the data
    
    # Run the simulation using model, slope, environmental and fuel data
    # Calculates the Fire Behaviour Index, which is then used to choose a Fire Danger Rating
    fire_danger_rating = firedup.calculate_rating(data)
    
#     print("FBI:", firedup.FBI)

    firedup.update_display()
    
    sleep_ms(100)
    