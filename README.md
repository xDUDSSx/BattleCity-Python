# Battle City 1985
## A clone game written in Python and Pyglet
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

*Semestral project for the BI-PYT class at Czech Technical University in Prague*

Goal of the project was to create a python clone of the action game BattleCity released in 1985 by Namco for the NES console.

# Running
Python (3.8.0+) and pyglet needs to be installed to run the game
```
pip install pyglet
```

Executable file is *run.py* in the *src* folder.
The game can then be started from the root folder with:
```
python src/run.py
```

# Controls
The player's tank is controlled using WSAD keys and SPACE to shoot.
Game level (stage) files are in the *src/stages* folder. The game automatically loads any files in the format:
stage<number>.<any extension> (stage9.txt for example)

# Screenshots
![BattleCity python clone](screenshots/1.PNG)
![BattleCity python clone](screenshots/2.PNG)
![BattleCity python clone](screenshots/3.PNG)
![BattleCity python clone](screenshots/4.PNG)
