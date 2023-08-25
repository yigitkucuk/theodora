## Theodora
A Chess Engine Enhanced with Transposition Tables, Move Ordering, Null Move Pruning, Aspiration Window, Alpha-Beta Pruning, Quiescence Search, and Opening Books.

### Strength

- I haven't yet had a chance to check the strength of the engine in objective measures, and haven't played against it myself yet, but I believe it to be stronger than what we call a club player.

- The books are quite strong and the engine plays according to theory for about 15 to 20 moves in the opening.

### Depth

- In the first version of the engine, it couldn't have gone behind depth 3.

- With the enchancements and improvements noted above, it can go behind depth 40 and quite possibly more in a relatively small time.

### Notes

- I developed this engine to better comprehend some concepts for the shogi engine that I will be building.

- I do not plan to develop a user interface for this engine, however, I will implement a terminal interface to play against it.

- I plan to develop a terminal interface for this engine to play against stronger engines such as Stockfish and Komodo.

- I will probably not be further developing this engine after I make one last improvement, that is, the migration from simplified evaluation function to an improved version of PeSTO's evaluation function. However, if I come across more improvements while looking onto the forums, I might bring in further developments.
  
- Huge shoutout to the [Chess Programming Wiki](https://www.chessprogramming.org/Main_Page).
