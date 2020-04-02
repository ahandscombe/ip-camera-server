import threading, time, ffmpeg, json, sys, shared, os, re
from shutil import copy
from datetime import datetime
from datetime import timedelta
from pathlib import Path

def jpg (name):
   # Update the frame jpg upon request
   # Latest file could be 32-57 or 32-58 as ts recording happens in two second segments
   # So get list of files in directory, sort them so most recent is index 0, then input index 1 into ffmpeg process

   items = os.listdir("data/%s/moment/parts" % (name))
   items.sort(reverse = True)

   try:
      (
         ffmpeg
         .input('data/%s/moment/parts/%s' % (name, items[1]))
         .output('data/%s/frame.jpg' % (name), f='image2', vframes='1')
         .global_args('-y')
         .run(capture_stdout=True, capture_stderr=True)
      )
      return True
   except ffmpeg.Error as e:
      print(e.stderr.decode(), file=sys.stderr)
      return False

def moment (name, directory, length, delay):
   # Generate a gif and mp4 for the specified camera.
   # Gif is saved always as moment.gif meaning that it is overwritten everytime
   # MP4 is saved always as year-month-day-hour-minute-second.mp4 meaning that each moment is kept
   # directory (bool) == return the directory where moments are kept
   # length (min 4 sec, max 20 secs) (1 second will be added to ensure length) == seconds that the replay should be
   # delay (0 = no delay, max 10 secs) == how long to wait before starting ffmpeg process, allows for capturing before and after the event

   if directory == True:
      if name in shared.handledCameras:
         return os.path.abspath('data/%s/moment' % (name))
      else:
         return False

   else:
      if length > 20:
         length = 20
      elif length < 4:
         length = 4

      if delay > 10:
         delay = 10

      items = os.listdir("data/%s/moment/parts" % (name))

      if len(items) >= (length + 1):

         if delay != 0:
            time.sleep(delay)

         # Retrieve list of dir again as delay may have changed its contents
         items = os.listdir("data/%s/moment/parts" % (name))
         items.sort(reverse = True)
         items.pop(0)

         filenames = []

         for i in range(length):
            filenames.insert(0,'data/%s/moment/parts/%s' % (name, items[i]))

         finalInput = 'concat:%s' % ('|'.join(filenames))

         now = datetime.now()
         videoName = '%s-%s-%s-%s-%s-%s' % (now.strftime("%Y"),now.strftime("%-m"),now.strftime("%-d"),now.strftime("%k"),now.strftime("%M"), now.strftime("%S"))

         try:
            (
               ffmpeg
               .input(finalInput)
               .output('data/%s/moment/moment.gif' % (name), f='gif')
               .global_args('-y')
               # MP4 Output
               .global_args('-vcodec', 'copy')
               .global_args('-an')
               .global_args('data/%s/moment/%s.mp4'% (name, videoName))
               .run(capture_stdout=True, capture_stderr=True)
            )
            return {"gif": os.path.abspath('data/%s/moment/moment.gif' % (name)), "mp4": os.path.abspath('../miro_data/monitor/%s/moment/%s.mp4'% (name, videoName)), "filename": [now.strftime("%Y"),now.strftime("%-m"),now.strftime("%-d"),now.strftime("%k"),now.strftime("%M"), now.strftime("%S")]}
         except ffmpeg.Error as e:
            print(e.stderr.decode(), file=sys.stderr)
            return False

      else:
         return False


def timelapsePreviousDay (name):
   # Concat the previous day timelapses into a single timelapse
   items = os.listdir("data/%s/timelapses/parts" % (name))

   t = datetime.now() - timedelta(days = 1)

   filenames = []

   for x in items:   
      # 2020-2-27-19-58-55.mp4
      if x.startswith('%s-%s-%s' % (t.strftime("%Y"), t.strftime("%-m"), t.strftime("%-d"))) and x.endswith(".ts"):
         # filenames.append(x)
         try:
            probe = ffmpeg.probe('data/%s/timelapses/parts/%s' % (name, x))

            if len(probe["streams"]) > 0:
               # Only add if the file contains stream data
               filenames.insert(0,'data/%s/timelapses/parts/%s' % (name, x))
         except ffmpeg.Error as e:
            print(e.stderr, file=sys.stderr)

   if len(filenames) > 0:

      filenames.sort()

      finalInput = 'concat:%s' % ('|'.join(filenames))

      try:
         (
            ffmpeg
            .input(finalInput)
            .output('data/%s/timelapses/%s-%s-%s.mp4' % (name, t.strftime("%Y"), t.strftime("%-m"), t.strftime("%-d")), vcodec='copy', an=None)
            .global_args('-y')
            .run(capture_stdout=True, capture_stderr=True)
         )
         
         # If was successful so delete original files
         for x in filenames:
            os.remove(x)
      except ffmpeg.Error as e:
         print(e.stderr.decode(), file=sys.stderr)
         return False