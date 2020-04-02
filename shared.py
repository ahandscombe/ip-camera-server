from datetime import datetime
from datetime import timedelta
from pathlib import Path
import re, os

debug = False

handledCameras = []

def dayOfWeek():
   today = datetime.now()
   return today.weekday()

def secondsUntilMidnight():
   now = datetime.now()
   # Add an extra 60 seconds to ensure that the time passes midnight
   return (((24 - now.hour - 1) * 60 * 60) + ((60 - now.minute - 1) * 60) + (60 - now.second) + 60)

def getTimestampMidnight():
   # Add an extra 20 seconds to ensure that the time passes midnight
   midnight = (int(datetime.timestamp(datetime.combine(datetime.now(), datetime.max.time())))+20)
   return midnight

def compareTimestampMidnight(value):
   # Provide the known midnight (captureSeconds) and this function determines if the current time is before or after that value
   now = (int(datetime.timestamp(datetime.now())))
   if value >= now:
      # Before value, so same day
      return False
   else:
      # After value, so new day
      return True

def todayDateString():
   now = datetime.now()
   return ('%s-%s-%s' % (now.year, now.month, now.day))
   
def nowDateString():
   now = datetime.now()
   return ('%s-%s-%s-%s-%s-%s' % (now.year, now.month, now.day, now.hour, now.minute, now.second))

def createStructure(name):
   Path("data/%s/days/0" % name).mkdir(parents=True, exist_ok=True) # Monday
   Path("data/%s/days/1" % name).mkdir(parents=True, exist_ok=True) # Tuesday
   Path("data/%s/days/2" % name).mkdir(parents=True, exist_ok=True) # Wednesday
   Path("data/%s/days/3" % name).mkdir(parents=True, exist_ok=True) # Thursday
   Path("data/%s/days/4" % name).mkdir(parents=True, exist_ok=True) # Friday
   Path("data/%s/days/5" % name).mkdir(parents=True, exist_ok=True) # Saturday
   Path("data/%s/days/6" % name).mkdir(parents=True, exist_ok=True) # Sunday
   Path("data/%s/timelapses/parts" % name).mkdir(parents=True, exist_ok=True)
   Path("data/%s/moment/parts" % name).mkdir(parents=True, exist_ok=True)

def cleanRecordingsOnStart(name, day, limit):
   # Deletes recording within the folder for the day provided and those days not covered by the limit
   # Also deletes all files within replay folder
   # Day is current day of week
   # Limit is how many days to keep, if 3 then the previous three days before the current will be kept, the other 3 days will be deleted

   allDays = [0,1,2,3,4,5,6]
   daysToKeep = []

   #Work out days to keep
   for i in range((day - limit), day):
      daysToKeep.append(allDays[i])

   #Get List of files in respective directories and then delete the files
   for i in allDays:
      if i not in daysToKeep:
         items = os.listdir("data/%s/days/%s" % (name, i))
         for x in items:
            os.remove("data/%s/days/%s/%s" % (name, i, x))

   replayItems = os.listdir("data/%s/moment/parts" % (name))
   for x in replayItems:
      os.remove("data/%s/moment/parts/%s" % (name, x))

def tidyMoment(name):
   # Removes ts files from the moment folder that are older than a minute

   replayItems = os.listdir("data/%s/moment/parts/" % (name))
   t = datetime.now() - timedelta(minutes = 2)

   for x in replayItems:   
      if re.search('%s-\d\d.ts' % (t.strftime("%M")),x) != None:
         os.remove("data/%s/moment/parts/%s" % (name, x))