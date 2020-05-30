# gui_forks_ft
Gui in `tkinter` for calculate fork feedthrough parameters

Migration from `Matlab` GUI to `Python` one.

# Logger

Log message has such `regex` pattern:

```regex
^([0-9]\w+-[0-9]\w-[0-9]\w\s[0-9]\w:[0-9]\w:[0-9]\w,[0-9]\w+)\s-\s([A-Z]\w+)\s-\s(.[a-z]\w+.)\s-\s(line:\s[0-9]\w+)\s-\s([\s\S]*)$
```

with a start pattern `^2`

Build to avoid `scipy` problems:
```
pyinstaller -F --paths e:\PycharmProjects\gui_forks_ft\venv\Lib\site-packages\scipy\.libs\ main_app.py
```
or add path to `pathex`
# Build a docker image
```
 sudo docker build -f Dockerfile --tag gui-forks-app .
```

# Run docker image under Ubuntu
To allow `tkinter` run:
```
sudo apt-get install x11-xserver-utils
xhost +
sudo docker run -v /tmp/.X11-unix:/tmp/.X11-unix -e DISPLAY=unix$DISPLAY --name my-app gui-forks-app

```
