<p align="center">
  <img src="https://github.com/Balx13/Potatix_Engine/blob/main/logo/PotatixEngine_logo1024px.png" alt="PotatixEngine_logo" width="256">
</p>

<h1 align="center">Potatix Engine</h1>
<h4 align="center"><a href="https://github.com/Balx13/Potatix_Engine">github</a></h4>
<p align="center"><em>English version</em></p>

## About the project
### Hungarian-developed free and open source adaptive chess engine 🇭🇺

This chess engine is adaptive, which means it looks for the best move based on your opponent's playing style. \
This adaptive style is built into most NNUEs, but my engine still uses a manual evaluator, so it takes much more "lifelike" steps.

> This engine is still in the alpha stage and is written in Python, so it is quite slow. Future plans include rewriting it in Rust to improve performance. \
> Currently, it is a hobby project, but I plan to turn it into a competitive engine in the future.

## Files
### The file distribution for the current version of the Potatix Engine is as follows:
 * README.md - The file you are reading now
 * LICENCE.txt - Potatix ​​Engine License Terms.
 * google571f1ff7b4dfe5a2.html - This file is there so that the Google search engine, Microsoft Bing and other search engines can index this repository.
 * /logo - The logo of the Potatix Engine in different resolutions
 * /engine - This folder contains the chess engine source code.

## Usage
### 1.) How to build
1. Install [Git](https://git-scm.com)
2. Install [Python](https://www.python.org)
3. Clone this repository with this command: `https://github.com/Balx13/Potatix_Engine.git`
4. Install Pyinstaller and python-chess with this command: `pip install pyinstaller chess`
5. Run this command:
* Linux/MacOS: `pyinstaller --onefile --name PotatixEngine --icon=logo/PotatixEngine_logo128px.png --add-data "engine:engine" engine/main.py`
* Windows: `pyinstaller --onefile --name PotatixEngine --icon=logo/PotatixEngine_logo128px.png --add-data "engine;engine" engine/main.py`
7. The build will appear in the *dist* folder!

### 2.) How to use with GUI
> This process is different for each GUI, in this example we will use a GUI called arena
1. Go to *engines -> install new engine...*
2. Browse engine build
3. Click the **"open"** button
4. In the pop-up menu, click *"ok"* or *"yes"*

## Contributing
If you would like to contribute to the project or have found a bug, please open a **Pull request** or an **Issue**. \
**Thanks!**

The 'Potatix Engine' should not be confused with 'Potato Engine' or 'Potatix'.

**Author:** Balázs André
> Future plans: Once a larger community has formed, I plan to relicense the engine under GPL-3 to allow broader usage while protecting the source code.

<div align="center">
  
<p align="center"><em>Magyar verzió</em></p>

</div>

## A porjektről
### Magyar fejlesztésű ingyenes és nyílt forráskódú adaptív sakkmotor 🇭🇺

Ez a sakkmotor adaptív, ami azt jelenti, hogy az ellenfele játékstílusához igazodva keresi a legjobb lépést. \
Ez az adaptív stílus a legtöbb NNUE-be be van tanítva, de az én motorom még kézi értékelőt használ, így sokkal "élethűbb" lépéseket lép.

> Ez a motor még alfa fázisban van Pythonban, így nagyon lassú. A jövőbeli tervek között szerepel, hogy átírom Rust nyelvbe a motor felgyorsítása érdekében. \
> Jelenleg hobbi projekt, de a jövőben tervezem, hogy versenymotorrá alakítom.

## Fájlok
### A Potatix ​​Engine jelenlegi verziójának fájlelosztása a következő:
 * README.md - Ezt a féjlt olvasod most
 * LICENCE.txt - A Potatix Engine licencfeltételei
 * google571f1ff7b4dfe5a2.html - Ez a fájl azért van, hogy a Google keresőmotor, a Microsoft Bing és más keresőmotorok ki tudják indexelni ezt a repository-t.
 * logo - A Potatix Engine logója különböző felbontásban
 * /engine - Ez a mappa tartalmazza a sakkmotor forráskódját.

## Használat
### 1.) Hogyan buildeld
1. Telepítsd a [Git](https://git-scm.com)-et
2. Telepítsd a [Python](https://www.python.org)-t
3. Klónozd ezt a repository-t ezzel a paranccsal: `https://github.com/Balx13/Potatix_Engine.git`
4. Telepítsd a Pyinstaller-t és a python-chess-t ezzel a paranccsal: `pip install pyinstaller chess`
5. Futtasd ezt a parancsot:
* Linux/MacOS: `pyinstaller --onefile --name PotatixEngine --icon=logo/PotatixEngine_logo128px.png --add-data "engine:engine" engine/main.py`
* Windows: `pyinstaller --onefile --name PotatixEngine --icon=logo/PotatixEngine_logo128px.png --add-data "engine;engine" engine/main.py`
7. A build ezután megjelenik a  *dist* mappában!

### 2.) Hogyan használd GUI-val:
> Ez a folyamat minden GUI  esetében más, ebben a példában az arena nevű GUI-t fogjuk használni.
1. Menj az  *engines -> install new engine...* fülre
2. Tallózd a motor buildjét
3. Kattints az **"open"** gombra
4. A megjelenő menüben kattints az *"ok"* vagy *"yes"* gombra

## Hozzájárulás
Ha szeretnél hozzájárulni a projekthez, kérlek nyiss egy **Pull request**-et vagy egy **Issue**-t. \
**Köszönöm!**

A "Potatix Engine" név nem összekeverendő a "Potato Engine"-vel vagy a "Potatix"-xal.

**Szerző:** Balázs André
> Jövőbeli terv: Amint nagyobb közösség alakul, a motor GPL-3 licencre váltását tervezem, hogy szélesebb körben lehessen használni, miközben a forráskód védve marad.
