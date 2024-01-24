'''
Similar to example 1
Here we extract the rating as a string eg. 'catastrophic', make a decision and perform some other task (beep)
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
   
    # Optional coding exercise, beep when Catastrophic state is entered (but don't beep continuously)
    if firedup.rating_has_changed():
        if fire_danger_rating == 'catastrophic':
            print('beep')
            firedup.tone(frequency = 262, duration = 200)

    sleep_ms(100)
    