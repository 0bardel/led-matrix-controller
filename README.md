# led-matrix-controller
Memory-efficient WS2812B led matrix controller. Very hastily put together for a one-off cosplay project.


The project's goal was to display GIF animations on a small-resolution WS2812B led matrix display. 
 
Given the limited SRAM memory of Atmega328p,
individual GIF animations are stored and loaded from PROGMEM.
 
GIFs were created in https://www.piskelapp.com/ webapp and converted to relevant C data arrays with Python.
 
Given the time constraints, development was stopped as soon as desired result was achieved.
No cleanup was done. **The code is very much spaghetti.**
