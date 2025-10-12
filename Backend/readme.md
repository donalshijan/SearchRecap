#  Run
    uvicorn Backend.main:app --host 0.0.0.0 --port 8000

To check if other devices can discover backend visit http://192.168.0.42:8000/docs from that device.

If you want to kill the server process and ctrl + c didn't work, then look for it's process id

    ps aux | grep uvicorn

and then kill it by

    kill -9 pid