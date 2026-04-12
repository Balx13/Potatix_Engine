<p align="center">
  <img src="https://github.com/Balx13/Potatix_Engine/blob/main/logo/PotatixEngine_logo1024px.png" alt="PotatixEngine_logo" width="256">
</p>

<h1 align="center">Potatix Engine</h1>
<h4 align="center"><a href="https://github.com/Balx13/Potatix_Engine">github</a></h4>
<p align="center"><em>English version</em></p>

## About the project
### Free and open-source chess engine


> This engine is still in the alpha stage and is written in Python, so it is quite slow. Future plans include rewriting it in Rust to improve performance. \
> Currently, it is a hobby project, but I plan to turn it into a competitive engine in the future.

## Current Features:
- Negamax algorithm with Alpha-Beta pruning
- Late Move Pruning and Late Move Reductions
- Null move pruning
- Transposition table
- Move ordering
- Quiescence
- UCI communication
- Basic evaluation
- Killer moves
- History heuristic
- Optening book
- Adaptive mode

## Limitations:
### Does not use...
- NNUE
- MTD(f) or PVS search algorithms
- multi-core parallelization
- bitboards

## Licenses:
- Everything about Potatix Engine — the source code, the source code, the logo, the name, and the documentation — is licensed under the GPLv3. \
You are free to use, copy, and modify it under the terms of the GPL. (see: LICENCE.txt)

## Custom Developments:
1. **Adaptive Mode**


Most chess engines search for the best move assuming an ideal opponent.
The Potatix Engine, however, tries to exploit weaknesses in the opponent’s play.
For example, if the opponent weakens their king’s safety in the middlegame, Potatix Engine will start attacking.

- Status: Alpha
- Adaptive mode is disabled by default
- To work correctly, the position must be set using the `position startpos moves ...` command.

## Files
### The file distribution for the current version of the Potatix Engine is as follows:
 * README.md - The file you are reading now
 * LICENCE.txt - Potatix Engine License Terms.
 * /logo - The logo of the Potatix Engine in different resolutions
 * /scr - This folder contains the chess engine source code.


### Opening Book Generation

The opening book used in this project was generated using:

- [**Lichess Elite Database**](https://database.nikonoel.fr), which contains high-level games used for training and reference.
- [**Stockfish**](https://github.com/official-stockfish/Stockfish) chess engine, used to evaluate positions and assign move scores.


## Contributing
If you would like to contribute to the project or have found a bug, please open a **Pull request** or an **Issue**. \
**Thanks!**

The 'Potatix Engine' should not be confused with 'Potato Engine' or 'Potatix'.

**Author:** Balázs André


<details>
<summary> Magyar verzió 🇭🇺</summary>

## A porjektről
### Ingyenes és nyílt forráskódú sakkmotor

> Ez a motor még alfa fázisban van Pythonban, így nagyon lassú. A jövőbeli tervek között szerepel, hogy átírom Rust nyelvbe a motor felgyorsítása érdekében. \
> Jelenleg hobbi projekt, de a jövőben tervezem, hogy versenymotorrá alakítom.

## Jelenlegi Funkciók:
- Negamax algoritmus AlphaBeta vágással
- Late Move Pruning és Late Move Reductions
- Null move pruning
- Tranzpozíciós tábla
- Move ordering
- Quiescence
- UCI kommunikáció
- Kezdetleges értékelő
- Killer moves
- History heuristic
- Megnyitási könyv
- Adaptív mód

## Korlátok:
### Nem használ...
- NNUE-t
- MTD(f) vagy PVS keresést
- multi-core párhuzamosítást
- bitboardokat

## Licencek:
- Minden, ami a Potatix Engine-hez tartozik — a forráskód, a brinális kód, a logó, a név és a dokumentáció — a GPLv3 alatt van. \
Szabadon használhatod, másolhatod és módosíthatod a GPL feltételei szerint. (lásd: LICENCE.txt)

## Egyedi feljesztések:
1. **Adaptív mód**


A legtöbb sakkmotor úgy működik, hogy egy elméleti, tökéletes ellenfél ellen keresi a legjobb lépést.
A Potatix Engine ezzel szemben az ellenfél gyengeségeit próbálja kihasználni.
Például, ha az ellenfél a középjátékban gyengíti a király védelmét, a Potatix Engine támadásba lendül.

- Állapota: Alfa
- Az Adaptív mód alaértelmezetten le van tiltva.
- A megfelelő működéshez a pozíciót a `position startpos moves ...` paranccsal kell átadni.

## Fájlok
### A Potatix Engine jelenlegi verziójának fájlelosztása a következő:
 * README.md - Ezt a féjlt olvasod most
 * LICENCE.txt - A Potatix Engine licencfeltételei
 * logo - A Potatix Engine logója különböző felbontásban
 * /scr - Ez a mappa tartalmazza a sakkmotor forráskódját.


### Megnyitási könyv létrehozása

A projektben használt megnyitási könyvet a következő források felhasználásával hoztam létre:

- [**Lichess Elite Database**](https://database.nikonoel.fr), amely magas szintű játszmákat tartalmaz a tanuláshoz és referenciaként.
- [**Stockfish**](https://github.com/official-stockfish/Stockfish) sakkmotor, amelyet a pozíciók értékelésére és a lépések pontozására használtam.


## Hozzájárulás
Ha szeretnél hozzájárulni a projekthez, kérlek nyiss egy **Pull request**-et vagy egy **Issue**-t. \
**Köszönöm!**

A "Potatix Engine" név nem összekeverendő a "Potato Engine"-vel vagy a "Potatix"-xal.

**Szerző:** Balázs André

</details>
