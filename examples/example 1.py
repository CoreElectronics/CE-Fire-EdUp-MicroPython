'''
This is the simplest demonstration of the Fire-EdUp platform
User-inputs set the environmental and fuel conditions. FBI is calculated and a danger rating is displayed
'''

# Initialise the simulation and select the Model and Slope
from firedup import *

firedup.model = 'button grass'
firedup.slope_degrees = 3


while True:
    # Collect Environmental and Fuel Conditions from the user inputs
    data = firedup.collect_data()
    
    print(data) # optional: show the data
    
    # Run the simulation using model, slope, environmental and fuel data
    # Calculates the Fire Behaviour Index, which is then used to choose a Fire Danger Rating
    fire_danger_rating = firedup.calculate_rating(data)
    
#     print("FBI:", firedup.FBI)

    firedup.update_display()
    
    sleep_ms(100)
    