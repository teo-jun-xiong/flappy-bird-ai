import pygame
import neat
import time
import os
import random
pygame.font.init()

# pylint: disable=no-member
WIN_WIDTH = 500
WIN_HEIGHT = 800
GENERATION = 0

BIRD_IMGS = [pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird1.png"))), pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird2.png"))), pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird1.png")))]
PIPE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "pipe.png")))
BASE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "base.png")))
BG_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bg.png")))
 
STAT_FONT = pygame.font.SysFont("comicsans", 50)

class Bird:
    IMGS = BIRD_IMGS
    MAX_ROTATION = 25               # simulate bird "tilting" when moving up or down
    ROT_VELOCITY = 20               # speed of "tilt"
    ANIMATION_TIME = 5
    
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.tilt = 0               # bird is stationary initially
        self.tick_count = 0
        self.velocity = 0
        self.height = self.y
        self.img_count = 0          # to keep track of image displayed; allows animation
        self.img = self.IMGS[0]

    def jump(self):
        self.velocity = -10.5       # top-left corner of window is (0,0); negative velocity in the y-direction moves up
        self.tick_count = 0         # keeps track of when last jump occured
        self.height = self.y

    # called to move the bird between every frame
    def move(self):
        self.tick_count += 1

        displacement = self.velocity*self.tick_count + 1.5*self.tick_count**2 # actual distance moved when y is changed

        if displacement >= 16:                                                # (failsafe) terminal velocity
            displacement = 16

        if displacement < 0:
            displacement -=2

        self.y = self.y + displacement
        
        if displacement < 0 or self.y < self.height + 50:                     # check if bird is above initial position
            if self.tilt < self.MAX_ROTATION:                                 # prevent complete tilt backwards
                self.tilt = self.MAX_ROTATION
            
        else:                                                                 # if not moving upwards and not tilting upwards
            if self.tilt > -90:
                self.tilt -= self.ROT_VELOCITY

    def draw(self, win): 
        self.img_count += 1

        # shows different image depending on img_count; animates bird
        if self.img_count < self.ANIMATION_TIME:
            self.img = self.IMGS[0]
        elif self.img_count < self.ANIMATION_TIME*2:
            self.img = self.IMGS[1]
        elif self.img_count < self.ANIMATION_TIME*3:
            self.img = self.IMGS[2]
        elif self.img_count < self.ANIMATION_TIME*4:
            self.img = self.IMGS[1]
        elif self.img_count < self.ANIMATION_TIME*4 + 1:
            self.img = self.IMGS[0]
            self.img_count = 0
        
        if self.tilt <= -80:
            self.img = self.IMGS[1]
            self.img_count = self.ANIMATION_TIME*2

        # rotates the image around its center
        rotated_img = pygame.transform.rotate(self.img, self.tilt)
        new_rectangle = rotated_img.get_rect(center = self.img.get_rect(topleft = (self.x, self.y)).center)
        win.blit(rotated_img, new_rectangle.topleft)
    
    # used for identifying collisions
    def get_mask(self):
        return pygame.mask.from_surface(self.img)

class Pipe:
    GAP = 200
    VELOCITY = 5

    def __init__(self, x):
        self.x = x
        self.height = 0
        self.gap = 100

        self.top = 0
        self.bottom = 0
        self.PIPE_TOP = pygame.transform.flip(PIPE_IMG, False, True)
        self.PIPE_BOTTOM = PIPE_IMG 

        self.passed = False     # for collision
        self.set_height()
    
    def set_height(self):
        self.height = random.randrange(50, 450)
        self.top = self.height - self.PIPE_TOP.get_height()
        self.bottom = self.height + self.GAP

    def move(self):
        self.x -= self.VELOCITY

    def draw(self, win):
        win.blit(self.PIPE_TOP, (self.x, self.top))
        win.blit(self.PIPE_BOTTOM, (self.x, self.bottom))

    # checks if pipe and bird collide using masks
    def collide(self, bird):
        bird_mask = bird.get_mask()
        top_mask = pygame.mask.from_surface(self.PIPE_TOP)
        bottom_mask = pygame.mask.from_surface(self.PIPE_BOTTOM)

        top_offset = (self.x - bird.x, self.top - round(bird.y))
        bottom_offset = (self.x - bird.x, self.bottom - round(bird.y))

        bottom_point = bird_mask.overlap(bottom_mask, bottom_offset)
        top_point = bird_mask.overlap(top_mask, top_offset)

        if bottom_point or top_point:   # not NaN
            return True
        
        return False
 
class Base:
    VELOCITY = 5
    WIDTH = BASE_IMG.get_width()
    IMG = BASE_IMG

    def __init__(self, y):
        self.y = y

        # x1 represents the top left corner of the first base
        # x2 represents the top left corner of the second base, which is "out of the screen", directly after the first image
        self.x1 = 0
        self.x2 = self.WIDTH

    def move(self):
        self.x1 -= self.VELOCITY
        self.x2 -= self.VELOCITY

        # if either the first or the second image is "out of the screen", cycle them back to the end
        if self.x1 + self.WIDTH < 0:
            self.x1 = self.x2 + self.WIDTH

        if self.x2 + self.WIDTH < 0:
            self.x2 = self.x1 + self.WIDTH

    def draw(self, win):
        win.blit(self.IMG, (self.x1, self.y))
        win.blit(self.IMG, (self.x2, self.y))

# execute NEAT from config file    
def run(config_path):
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet, neat.DefaultStagnation, config_path)

    p = neat.Population(config) # generate population from config file
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)
    p.run(main, 50)

if __name__ == "__main__":
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir + "\config-feedforward.txt")
    run(config_path)

def draw_window(win, birds, pipes, base, score, generation):
    win.blit(BG_IMG, (0,0))
    
    for pipe in pipes:
        pipe.draw(win)

    # shows current score 
    text = STAT_FONT.render("Score: " + str(score), 1, (255, 255, 255))
    win.blit(text, (WIN_WIDTH - 10 - text.get_width(), 10))

    # shows current generation
    text = STAT_FONT.render("Generation: " + str(generation), 1, (255, 255, 255))
    win.blit(text, (10, 10))

    base.draw(win)

    for bird in birds:
        bird.draw(win)

    pygame.display.update()

def main(genomes, config):
    global GENERATION
    GENERATION += 1
    nets = []
    ge = []
    birds = []
    
    # initializes genomes
    for _, genome in genomes:
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        nets.append(net)
        birds.append(Bird(230, 350))
        genome.fitness = 0
        ge.append(genome)

    base = Base(730)
    pipes = [Pipe(700)]
    win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
    clock = pygame.time.Clock()
    
    score = 0
    run = True
    while run:
        clock.tick(30)

        # checks if the game has ended
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()

        pipe_index = 0

        # if the bird passes the second/subsequent pipe
        if len(birds) > 0:
            if len(pipes) > 1 and birds[0].x > pipes[0].x + pipes[0].PIPE_TOP.get_width():
                pipe_index = 1
        else:   # if no birds left, quit the game
            run = False
            break

        for i, bird in enumerate(birds):
            bird.move()
            ge[i].fitness += 0.01

            output = nets[i].activate((bird.y, abs(bird.y - pipes[pipe_index].height), abs(bird.y - pipes[pipe_index].bottom)))

            if output[0] > 0.5:
                bird.jump()

        add_pipe = False
        removed_pipes = []

        for pipe in pipes:
            for i, bird in enumerate(birds):
                if pipe.collide(bird):
                    ge[i].fitness -= 0.5
                    birds.pop(i)
                    nets.pop(i)
                    ge.pop(i)


                if not pipe.passed and pipe.x < bird.x:
                    pipe.passed = True
                    add_pipe = True

            # if pipe is completely out of the screen
            if pipe.x + pipe.PIPE_TOP.get_width() < 0:  
                removed_pipes.append(pipe)

            pipe.move()

        if add_pipe:
            score += 1

            # increases fitness for birds that pass through a pipe
            for genome in ge:
                genome.fitness += 2

            pipes.append(Pipe(600)) # adjusts how close the new pipe is created

        for pipe in removed_pipes:
            pipes.remove(pipe)

        for i, bird in enumerate(birds):
            # if bird has hit the ground, remove it, or bird is above the screen
            if bird.y + bird.img.get_height() >= 730 or bird.y < 0:
                birds.pop(i)
                nets.pop(i)
                ge.pop(i)

        base.move()
        draw_window(win, birds, pipes, base, score, GENERATION)
