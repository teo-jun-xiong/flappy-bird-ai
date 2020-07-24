# AI Aces Flappy Bird

## Preface
This mini-project serves as a fun introduction to artificial intelligence (AI) for me, and mainly uses Python and the NEAT module.

## Fitness Function

Birds (and the neurons) gain fitness if they:
- Progress through the game
- Pass through a pipe successfully, without collision

Birds (and the neurons) gain fitness if they:
- Collide into a pipe

The collision between birds and pipes are determined using `pygame.mask.from_surface`, which allows the top and bottom points of overlap to be determined, if any. This makes the collision pixel-accurate, compared to generating boxes around the (non-rectangular) bird models.

<div>Icons made by <a href="https://www.flaticon.com/authors/freepik" title="Freepik">Freepik</a> from <a href="https://www.flaticon.com/" title="Flaticon">www.flaticon.com</a></div>

