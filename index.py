import threading, time
import shared, export, camera, web

setup = [
   {"cameraID":"exmaple", "rtsp":"rtsp://192.168.0.186:554/...", "daysToKeep": 5}
]

webThread = web.main()
webThread.daemon = True
webThread.start()

def request_handler(req):
   shared.handledCameras.append(req["cameraID"]) 
   cameraThread = camera.main(req["rtsp"], req["daysToKeep"])
   cameraThread.name = req["cameraID"]
   cameraThread.daemon = True
   cameraThread.start()

for x in setup:
   request_handler(x)

while True:
   time.sleep(10)
   for x in shared.handledCameras:
      shared.tidyMoment(x)