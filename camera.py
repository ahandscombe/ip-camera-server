import threading, time, ffmpeg, json, sys
import shared, export

class main(threading.Thread):
   def __init__(self, url, daysToKeep):
      super(main, self).__init__()
      self.daemon = True
      self.url = url
      self.daysToKeep = daysToKeep
   def run(self):

      self.prevCaptureDay = shared.dayOfWeek()

      # Main FFMPEG Process
      def operate(self):
         while True:
            # Only want to record until midnight so that each day ends up in its respective folder
            captureSeconds = shared.getTimestampMidnight()
            # Get day of week and place hls/dash segments in correct folder
            captureDay = shared.dayOfWeek()

            # If false then it is a new day so clean up recordings and run other end of day things
            if self.prevCaptureDay != captureDay:
               shared.cleanRecordingsOnStart(self.name, captureDay,  self.daysToKeep)
               self.prevCaptureDay = captureDay

               # Generate final timelapse
               export.timelapsePreviousDay(self.name)

            print("Starting")

            command = (
                        ffmpeg
                        .input(self.url, rtsp_transport='tcp', stimeout='20000000', use_wallclock_as_timestamps=1, fflags='+genpts')
                        .output('data/%s/days/%s/stream.mpd' % (self.name, captureDay), vcodec='copy', an=None, format='dash', seg_duration=2, window_size=86400, extra_window_size=2, hls_playlist=1, remove_at_exit=0)
                        # ts segment output for moment
                        .global_args('-f', 'segment')
                        .global_args('-codec', 'copy')
                        .global_args('-segment_time', '1')
                        .global_args('-strftime', '1')
                        .global_args('data/%s/moment/parts/%%M-%%S.ts'% (self.name))
                        # timelapse
                        .global_args('-r', '60')
                        .global_args('-filter:v', 'setpts=0.0006944444444*PTS')
                        .global_args('-vcodec','libx264')
                        .global_args('-crf','30')
                        .global_args('-preset','slow')
                        .global_args('-an')
                        .global_args('data/%s/timelapses/parts/%s.ts'% (self.name, shared.nowDateString()))
                     )
            process = command.run_async(pipe_stdin=True, quiet=False)

            while True:
               if process.poll() == None:
                  # If process is still running, check the current time against captureSeconds to see if it should end
                  if shared.compareTimestampMidnight(captureSeconds):
                     # True so it is a new day, end the process safely
                     print("New Day")
                     process.communicate(str.encode("q"))
                     time.sleep(3)
                     process.terminate()
                     break
               else:
                  # Not running may have ended in error or completed with success, so restart
                  print("not Running")
                  time.sleep(10)
                  break
               time.sleep(1)

            print('Restart %s'% (shared.nowDateString()))

      #Create file structure
      shared.createStructure(self.name)

      #Starting a new recording so clean out folder, can't continue previous recordings even if on same day
      shared.cleanRecordingsOnStart(self.name, self.prevCaptureDay, self.daysToKeep)

      operate(self)
