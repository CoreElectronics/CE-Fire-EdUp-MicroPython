'''
You can create a new model by defining a name and a weight using firedup.create_model('name', weight)
For example
firedup.create_model("arctic ice-shelf", 0.05) # is very immune to fire risk
firedup.create_model("fireworks factory", 5) # is extremely sensitive to fire risk
'''

from firedup import *

# create_model accepts a (name, value)
# Create a new model and name it. A model's value is it's weighting when calculating FBI. Larger numbers are more sensitive.
firedup.create_model('strange new ecosystem', 1.23)

firedup.slope_degrees = 3

while True:
    # Collect Environmental and Fuel Conditions from the user-inputs
    data = firedup.collect_data()
    
    print(data)
    
    # Run the simulation using collected data, the selected model & slope
    # Calculates the Fire Behaviour Index, which is then used to choose a Fire Danger Rating
    fire_danger_rating = firedup.calculate_rating(data)
    
#     print("FBI:", firedup.FBI)
    firedup.update_display()
   
    sleep_ms(100)
    