Real-time Flask
=====

This is a base Flask project that shows how to integrate real-time API requests using Socket.io.

Steps to get setup:
0) I would recommend using a virtual environment (setup is outside of the scope of this README.)
1) Install all of the packages from the requirements.txt:
pip install -r requirements.txt
2) At this point you can either run the project using gevent by running:
python website/website.py
3) Alternatively, you can use gunicorn with a command similar to this:
gunicorn --worker-class socketio.sgunicorn.GeventSocketIOWorker --pythonpath website website:app -b localhost:5000

Now you can connect multiple browser sessions to the website at http://localhost:5000/ and you should see news being updated in real-time!