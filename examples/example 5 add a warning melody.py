'''
Similar to example 2 but here we program a short melody
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
    
    firedup.update_display()
   
    # Optional coding exercise
    # beep once when entering Extreme danger
    # play a melody when entering Catastrophic danger
    # remix idea: research the frequencies that match musical notes and program a short melody
        
    if firedup.rating_has_changed():
        if fire_danger_rating == 'extreme':
            firedup.tone(frequency = 262, duration = 200) # play a single note
            sleep_ms(100)

        if fire_danger_rating == 'catastrophic':
            firedup.tone(frequency = 262, duration = 50) # play a sequence of notes
            sleep_ms(100)
            firedup.tone(frequency = 262, duration = 50)
            sleep_ms(100)
            firedup.tone(frequency = 262, duration = 50)
            sleep_ms(100)
            firedup.tone(frequency = 100, duration = 200)
            sleep_ms(200)

    
    