# IP Camera Server

Python and FFMPEG based RTSP to HLS/MPEG-Dash web server

## Overview
* RTSP stream URL as input
* HLS and MPEG-Dash live output
* Timelapse creation
* Save output as JPEGs (frame)
* Record short clips as both MP4 and Gif (moment)

## Installation
```
pip install ffmpeg-python
pip install flask
```

## Usage:
### Flask HTTP Server
* Default port is 6478

### Input
* Within `index.py` edit setup list with a RTSP stream URL:
````
{"cameraID":"example", "rtsp":"rtsp://192.168.0.186:554/...", "daysToKeep": 5}
````
* `cameraID`: will be the reference for this input
* `rtsp`: url of the RTSP stream
* `daysToKeep`: the number of previous HLS and MPEG day streams that should be kept


### HLS and MPEG-Dash
* Handled in day streams
   * At the end of each day a new stream/playlist will be started
   * Allows for rewinding through current day
* Keep the recordings of up to six full previous days
   * stream for current day is called today
   * For other days it is the number of the weekday: e.g. 0 = Monday ... 6 = Sunday
   * All segments and playlists are deleted automatically when not required
* HLS stream
   * Today stream accessed via (cameraID should be replaced with the one provided in `index.py`): 
      ````
      http://127.0.0.1:6478/[cameraID]/stream/today/playlist.m3u8
      ````
   * Previous day streams:
      ````
      http://127.0.0.1:6478/[cameraID]/stream/[weekday number]/playlist.m3u8
      ````
* Dash stream
   * Today stream:
      ````
      http://127.0.0.1:6478/[cameraID]/stream/today/playlist.m3u8
      ````
   * Previous day streams:
      ````
      http://127.0.0.1:6478/[cameraID]/stream/[weekday number]/playlist.m3u8
      ````

### Timelapse
* Each day is turned into a MP4 video with a duration of 60 seconds approximately
* Generated with the live feed and is viewable only after the day has completed
* List of available timelapses as JSON can be requested:
   ````
   http://127.0.0.1:6478/[cameraID]/timelapse/
   ````
* To view a specific timelapse:
   ````
   http://127.0.0.1:6478/[cameraID]/timelapse/[year]/[month]/[day]
   ````

### Frame
* Outputs a JPEG image upon request
* To generate and request a frame:
   ````
   http://127.0.0.1:6478/[cameraID]/frame/
   ````

### Moment
* Allows for the simultaneous generation of short GIFs and MP4s that show what happened in the up to 20 seconds before the request was made
* The moment creation can be delayed up to 10 seconds beyond the time of the request. This allows for the event being captured to be in the middle of the clip rather than at the end. It shows what happened before and what happened after.
* Each MP4 is saved for later viewing whereas the GIF is overwritten with each generation request
* To generate a moment with a length of 5 seconds and no delay:
   ````
   http://127.0.0.1:6478/[cameraID]/moment/generate/
   ````
* To generate a moment with specific length (integer inclusive of 4 and 20) and delay (integer inclusive of 0 and 10):
   ````
   http://127.0.0.1:6478/[cameraID]/moment/generate/[length]/[delay]
   ````
* To retrieve the generated GIF:
   ````
   http://127.0.0.1:6478/[cameraID]/moment/gif
   ````
* List of available moments as JSON can be requested:
   ````
   http://127.0.0.1:6478/[cameraID]/moment/list
   ````
* To view a specific timelapse:
   ````
   http://127.0.0.1:6478/[cameraID]/moment/list/[year]/[month]/[day]/[hour]/[minute]/[second]
   ````