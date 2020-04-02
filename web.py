from flask import render_template, Flask, send_from_directory, abort, json #sudo python3 -m pip install flask
import threading, os
from pathlib import Path
import shared, export

class main(threading.Thread):
   def __init__(self):
      super(main, self).__init__()
      self.daemon = True
   def run(self):

      app = Flask(__name__)

      @app.after_request
      def add_header(response):
         response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
         response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
         response.headers['Pragma'] = 'no-cache'
         response.headers['Expires'] = '0'
         response.headers['Access-Control-Allow-Origin'] = '*'
         return response

      @app.route('/<string:id>/stream/<string:day>/<string:filename>')
      def streamToday(id, day, filename):
         loc = None

         if day == 'today':
            loc = 'data/%s/days/%s' % (id, shared.dayOfWeek())         
         elif day == '0':
            loc = 'data/%s/days/0' % (id)
         elif day == '1':
            loc = 'data/%s/days/1' % (id)
         elif day == '2':
            loc = 'data/%s/days/2' % (id)
         elif day == '3':
            loc = 'data/%s/days/3' % (id)
         elif day == '4':
            loc = 'data/%s/days/4' % (id)
         elif day == '5':
            loc = 'data/%s/days/5' % (id)
         elif day == '6':
            loc = 'data/%s/days/6' % (id)
         else:
            abort(404)

         if filename == 'playlist.m3u8':
            # HLS Playlist Request
            if Path('%s/media_0.m3u8' % (loc)).is_file():
               return send_from_directory(loc, filename='media_0.m3u8')
            else:
               abort(404)         
         elif filename == 'playlist.mpd':
            # Dash Playlist Request
            if Path('%s/stream.mpd' % (loc)).is_file():
               return send_from_directory(loc, filename='stream.mpd')
            else:
               abort(404)
         else:
            # HLS or Dash Segment Request
            if Path('%s/%s' % (loc, filename)).is_file():
               return send_from_directory(loc, filename=filename)
            else:
               abort(404)

      @app.route('/<string:id>/frame')
      def frame(id):
         if export.jpg(id):
            return send_from_directory(directory='data/%s' % (id), filename='frame.jpg')   
         else:
            abort(404)


      @app.route('/<string:id>/moment/generate/', defaults={'delay': 0, 'length': 5})
      @app.route('/<string:id>/moment/generate/<int:length>', defaults={'delay': 0})
      @app.route('/<string:id>/moment/generate/<int:length>/<int:delay>')
      def moment_generate(id, length, delay):
         if export.moment(id, False, length, delay):
            return send_from_directory(directory='data/%s/moment' % (id), filename='moment.gif') 
         else:
            abort(404)

      @app.route('/<string:id>/moment/list/', defaults={'year': None, 'month': None, 'day': None, 'hour': None, 'minute': None, 'second': None})
      @app.route('/<string:id>/moment/list/<int:year>/<int:month>/<int:day>/<int:hour>/<int:minute>/<int:second>/')
      def moment_list(id, year, month, day, hour, minute, second):
         res = export.moment(id, True, False, False)
         if res != False:
            if year == None:
               items = []
               for x in os.listdir(res):
                  if x.endswith(".mp4"):
                     row = os.path.splitext(x)[0].split("-")
                     items.append([int(i) for i in row])

               response = app.response_class(
                  response=json.dumps(items),
                  status=200,
                  mimetype='application/json'
               )
               return response
            else:
               return send_from_directory(directory='data/%s/moment' % (id), filename='%s-%s-%s-%s-%s-%s.mp4' % (year, month, day, hour, minute, second)) 
         else:
            abort(404)

      @app.route('/<string:id>/moment/gif/')
      def moment_gif(id): 
         res = export.moment(id, True, False, False)
         if res != False:
            return send_from_directory(directory='data/%s/moment' % (id), filename='moment.gif') 
         else:
            abort(404)

      @app.route('/<string:id>/timelapse/', defaults={'year': None, 'month': None, 'day': None})
      @app.route('/<string:id>/timelapse/<int:year>/<int:month>/<int:day>/')
      def timelapse(id, year, month, day):
         if id in shared.handledCameras:

            if year == None:
               # Return a list of available timelapses
               items = []
               for x in os.listdir('data/%s/timelapses' % (id)):
                  if x.endswith(".mp4"):
                     row = os.path.splitext(x)[0].split("-")
                     items.append([int(i) for i in row])

               response = app.response_class(
                  response=json.dumps(items),
                  status=200,
                  mimetype='application/json'
               )
               return response

            else:
               # Return requested timelapse if it exists
               return send_from_directory(directory='data/%s/timelapses' % (id), filename='%s-%s-%s.mp4' % (year, month, day))
         else:
            abort(404)
         
      app.run(host='0.0.0.0', port=6478)