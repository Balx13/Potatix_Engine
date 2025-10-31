<p align="center">
  <img src="https://github.com/Balx13/Potatix_Engine/raw/main/potatix_logo.png" alt="PotatixEngine_logo" width="256">
</p>

<h1 align="center">Potatix Engine</h1>
<h4 align="center"><a href="https://github.com/Balx13/Potatix_Engine">github</a></h4>
<p align="center"><em>English version</em></p>


## Hungarian-developed free and open source chess engine 🇭🇺
> This engine is still in the alpha stage and is written in Python, so it is quite slow. Future plans include rewriting it in Rust to improve performance. \
> Currently, it is a hobby project, but I plan to turn it into a competitive engine in the future.

## Usage
### 1.) How to build
1. Install [Git](https://git-scm.com)
2. Install [Python](https://www.python.org)
3. Clone this repository with this command: `git clone https://github.com/Balx13/Potato_bot.git`
4. Install Pyinstaller and python-chess with this command: `pip install pyinstaller chess`
5. Run this command: `pyinstaller --onefile --name MyEngine main.py adaptive_style.py config.py evulate.py move_ordering.py quiescence.py search.py stop_event.py time_manager.py transposition_table.py UCI.py`
6. The build will appear in the *dist* folder!

### 2.) How to use with GUI
> This process is different for each GUI, in this example we will use a GUI called arena
1. Go to *engines -> install new engine...*
2. Browse engine build
3. Click the **"open"** button
4. In the pop-up menu, click *"ok"* or *"yes"*

## Contributing
If you would like to contribute to the project or have found a bug, please open a **Pull request** or an **Issue**. \
**Thanks!**

**Author:** Balázs André
> Future plans: Once a larger community has formed, I plan to relicense the engine under GPL-3 to allow broader usage while protecting the source code.

<div align="center">
  
<p align="center"><em>Magyar verzió</em></p>

</div>

## Magyar fejlesztésű ingyenes és nyílt forráskódú sakkmotor 🇭🇺
> Ez a motor még alfa fázisban van Pythonban, így nagyon lassú. A jövőbeli tervek között szerepel, hogy átírom Rust nyelvbe a motor felgyorsítása érdekében. \
> Jelenleg hobbi projekt, de a jövőben tervezem, hogy versenymotorrá alakítom.

## Használat
### 1.) Hogyan buildeld
1. Telepítsd a [Git](https://git-scm.com)-et
2. Telepítsd a [Python](https://www.python.org)-t
3. Klónozd ezt a repository-t ezzel a paranccsal: `git clone https://github.com/Balx13/Potato_bot.git`
4. Telepítsd a Pyinstaller-t és a python-chess-t ezzel a paranccsal: `pip install pyinstaller chess`
5. Futtasd ezt a parancsot: `pyinstaller --onefile --name MyEngine main.py adaptive_style.py config.py evulate.py move_ordering.py quiescence.py search.py stop_event.py time_manager.py transposition_table.py UCI.py`
6. A build ezután megjelenik a  *dist* mappában!

### 2.) Hogyan használd GUI-val:
> Ez a folyamat minden GUI  esetében más, ebben a példában az arena nevű GUI-t fogunk használni.
1. Menj az  *engines -> install new engine...* fülre
2. Tallózd a motor buildjét
3. Kattints az **"open"** gombra
4. A megjelenő menüben kattints az *"ok"* vagy *"yes"* gombra

## Hozzájárulás
Ha szeretnél hozzájárulni a projekthez, kérlek nyiss egy **Pull request**-et vagy egy **Issue**-t. \
**Köszönöm!**

**Szerző:** Balázs André
> Jövőbeli terv: Amint nagyobb közösség alakul, a motor GPL-3 licencre váltását tervezem, hogy szélesebb körben lehessen használni, miközben a forráskód védve marad.
