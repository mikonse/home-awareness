# Home Awareness
This is a python project with the goal of performing simple home automation functions such as 
mqtt interfacing, light and audio control and simple presence detection.

It exposes its parameters and backend apis via a webserver under the url `/api`.

# Development
Simply `pip install -r requirements.txt`

Then `python __main__.py` to run. Unfortunately it must be executed with root priviledges, as the 
wifi tracking module will not work otherwise.