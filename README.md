<p align="center">
  <img src="https://github.com/Balx13/Potatix_Engine/blob/main/logo/PotatixEngine_logo1024px.png" alt="PotatixEngine_logo" width="256">
</p>

<h1 align="center">Potatix Engine</h1>
<h4 align="center"><a href="https://github.com/Balx13/Potatix_Engine">github</a></h4>
<p align="center"><em>English version</em></p>

## About the project
### Hungarian-developed free and open source adaptive chess engine 🇭🇺

> This engine is still in the alpha stage and is written in Python, so it is quite slow. Future plans include rewriting it in Rust to improve performance. \
> Currently, it is a hobby project, but I plan to turn it into a competitive engine in the future.

## Current Features:
- Negamax algorithm with Alpha-Beta pruning
- Late Move Pruning and Late Move Reductions
- Null move pruning
- Transposition table
- Move ordering
- Quicksense
- UCI communication
- Basic evaluation
- Killer moves
- History heuristic
- Adaptive mode

## Limitations:
### Does not use...
- NNUE
- MTD(f) or PVS search algorithms
- multi-core parallelization
- bitboards

## Custom Developments:
1. **Adaptive Mode**


Most chess engines search for the best move assuming an ideal opponent.
The Potatix Engine, however, tries to exploit weaknesses in the opponent’s play.
For example, if the opponent weakens their king’s safety in the middlegame, Potatix Engine will start attacking.

- Status: Stable, but still under development.
- To work correctly, the position must be set using the `position startpos moves ...` command.

## Files
### The file distribution for the current version of the Potatix Engine is as follows:
 * README.md - The file you are reading now
 * LICENCE.txt - Potatix Engine License Terms.
 * google571f1ff7b4dfe5a2.html - This file is there so that the Google search engine, Microsoft Bing and other search engines can index this repository.
 * /logo - The logo of the Potatix Engine in different resolutions
 * /scr - This folder contains the chess engine source code.

## Usage
### 1.) How to build
1. Install [Git](https://git-scm.com)
2. Install [Python](https://www.python.org)
3. Clone this repository with this command: `git clone https://github.com/Balx13/Potatix_Engine.git`
4. Install Pyinstaller and python-chess with this command: `pip install pyinstaller chess`
5. Run this command:
* Linux/MacOS: `pyinstaller --onefile --name PotatixEngine --icon=logo/PotatixEngine_logo128px.png --add-data "scr:scr" scr/main.py`
* Windows: `pyinstaller --onefile --name PotatixEngine --icon=logo/PotatixEngine_logo128px.png --add-data "scr;scr" scr/main.py`
7. The build will appear in the *dist* folder!

### 2.) How to use with GUI
> This process is different for each GUI, in this example we will use a GUI called arena
1. Go to *engines -> install new engine...*
2. Browse engine build
3. Click the **"open"** button
4. In the pop-up menu, click *"ok"* or *"yes"*

### Opening Book Generation

The opening book used in this project was generated using:

- [**Lichess Elite Database**](https://database.nikonoel.fr), which contains high-level games used for training and reference.
- [**Stockfish 17.1**](https://github.com/official-stockfish/Stockfish) chess engine, used to evaluate positions and assign move scores.

**License:** The resulting opening book is released under the [CC BY-NC-SA 4.0 license](https://creativecommons.org/licenses/by-nc-sa/4.0/), allowing non-commercial use with attribution and share-alike requirements.

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

> Ez a motor még alfa fázisban van Pythonban, így nagyon lassú. A jövőbeli tervek között szerepel, hogy átírom Rust nyelvbe a motor felgyorsítása érdekében. \
> Jelenleg hobbi projekt, de a jövőben tervezem, hogy versenymotorrá alakítom.

## Jelenlegi Funkciók:
- Minimax algoritmus AlphaBeta vágással
- Late Move Pruning és Late Move Reductions
- Null move pruning
- Tranzpozíciós tábla
- Move ordering
- Quicksense
- UCI kommunikáció
- Kezdetleges értékelő
- Killer moves
- History heuristic
- Adaptív mód

## Korlátok:
### Nem használ...
- NNUE-t
- MTD(f) vagy PVS keresést
- multi-core párhuzamosítást
- bitboardokat

## Egyedi feljesztések:
1. **Adaptív mód**


A legtöbb sakkmotor úgy működik, hogy egy elméleti, tökéletes ellenfél ellen keresi a legjobb lépést.
A Potatix Engine ezzel szemben az ellenfél gyengeségeit próbálja kihasználni.
Például, ha az ellenfél a középjátékban gyengíti a király védelmét, a Potatix Engine támadásba lendül.

- Állapota: Stabil, de még fejlesztés alatt áll.
- A megfelelő működéshez a pozíciót a `position startpos moves ...` paranccsal kell átadni.

## Fájlok
### A Potatix Engine jelenlegi verziójának fájlelosztása a következő:
 * README.md - Ezt a féjlt olvasod most
 * LICENCE.txt - A Potatix Engine licencfeltételei
 * google571f1ff7b4dfe5a2.html - Ez a fájl azért van, hogy a Google keresőmotor, a Microsoft Bing és más keresőmotorok ki tudják indexelni ezt a repository-t.
 * logo - A Potatix Engine logója különböző felbontásban
 * /scr - Ez a mappa tartalmazza a sakkmotor forráskódját.

## Használat
### 1.) Hogyan buildeld
1. Telepítsd a [Git](https://git-scm.com)-et
2. Telepítsd a [Python](https://www.python.org)-t
3. Klónozd ezt a repository-t ezzel a paranccsal: `git clone https://github.com/Balx13/Potatix_Engine.git`
4. Telepítsd a Pyinstaller-t és a python-chess-t ezzel a paranccsal: `pip install pyinstaller chess`
5. Futtasd ezt a parancsot:
* Linux/MacOS: `pyinstaller --onefile --name PotatixEngine --icon=logo/PotatixEngine_logo128px.png --add-data "scr:scr" scr/main.py`
* Windows: `pyinstaller --onefile --name PotatixEngine --icon=logo/PotatixEngine_logo128px.png --add-data "scr;scr" scr/main.py`
7. A build ezután megjelenik a  *dist* mappában!

### 2.) Hogyan használd GUI-val:
> Ez a folyamat minden GUI  esetében más, ebben a példában az arena nevű GUI-t fogjuk használni.
1. Menj az  *engines -> install new engine...* fülre
2. Tallózd a motor buildjét
3. Kattints az **"open"** gombra
4. A megjelenő menüben kattints az *"ok"* vagy *"yes"* gombra

### Megnyitási könyv létrehozása

A projektben használt megnyitási könyvet a következő források felhasználásával hoztam létre:

- [**Lichess Elite Database**](https://database.nikonoel.fr), amely magas szintű játszmákat tartalmaz a tanuláshoz és referenciaként.
- [**Stockfish 17.1**](https://github.com/official-stockfish/Stockfish) sakkmotor, amelyet a pozíciók értékelésére és a lépések pontozására használtam.

**Licenc:** A megnyitási könyv a [CC BY-NC-SA 4.0 licenc](https://creativecommons.org/licenses/by-nc-sa/4.0) alatt került kiadásra, amely lehetővé teszi a nem kereskedelmi célú felhasználást, megköveteli a szerző feltüntetését és a share-alike szabályok betartását.

## Hozzájárulás
Ha szeretnél hozzájárulni a projekthez, kérlek nyiss egy **Pull request**-et vagy egy **Issue**-t. \
**Köszönöm!**

A "Potatix Engine" név nem összekeverendő a "Potato Engine"-vel vagy a "Potatix"-xal.

**Szerző:** Balázs André
> Jövőbeli terv: Amint nagyobb közösség alakul, a motor GPL-3 licencre váltását tervezem, hogy szélesebb körben lehessen használni, miközben a forráskód védve marad.
