# Pi
Curent Things that could break:
- userlocation is not a SENSORID ws_server.py ln 25 

This is the code for our Pi, Its job is to :
- recieve sensor data over websockets and cache it
- talk to a RESTful API which will archive the sensor data
- talk to a websockets server to forward liveData if recieved a message
- call RESTful API on a websocket message
