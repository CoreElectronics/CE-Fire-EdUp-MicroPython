'''
This example demonstrates how to access one parameter from the "data" dictionary
You can also assign a value to a location in the dictionary eg.
data['humidity'] = 50.0
Will overwrite the user-input with a constant value

https://www.w3schools.com/python/python_dictionaries.asp
'''

# Initialise the simulation and select the Model and Slope
from firedup import *

firedup.model = 'button grass'
firedup.slope_degrees = 3


while True:
    # Collect Environmental and Fuel Conditions from the user inputs
    data = firedup.collect_data()
    
    
    # Print a message if the temperature is too hot.
    print(data['temperature'], '°C') # optional: show the data
    if data['temperature'] > 30:
        print('Conditions are hot, ensure you stay hydrated!')
    
    
    
    # Run the simulation using model, slope, environmental and fuel data
    # Calculates the Fire Behaviour Index, which is then used to choose a Fire Danger Rating
    fire_danger_rating = firedup.calculate_rating(data)
    
#     print("FBI:", firedup.FBI)

    firedup.update_display()
    
    sleep_ms(100)
    