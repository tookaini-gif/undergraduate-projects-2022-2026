import argparse
from engine import Snake

def main():
    p=argparse.ArgumentParser(description='Keyboard snake: WASD/arrows, R restart, Esc exit')
    p.add_argument('--fps', type=int, default=10); a=p.parse_args()
    if not 1 <= a.fps <= 60: p.error('fps must be in 1..60')
    import pygame
    pygame.init(); screen=pygame.display.set_mode((600, 440)); clock=pygame.time.Clock()
    pygame.display.set_caption('Snake | Keyboard Edition'); font=pygame.font.Font(None, 26)
    game=Snake(); running=True
    keys={pygame.K_LEFT:(-1,0), pygame.K_a:(-1,0),pygame.K_RIGHT:(1,0),pygame.K_d:(1,0),pygame.K_UP:(0,-1),pygame.K_w:(0,-1),pygame.K_DOWN:(0,1),pygame.K_s:(0,1)}
    try:
        while running:
            direction=None
            for event in pygame.event.get():
                if event.type==pygame.QUIT: running=False
                elif event.type==pygame.KEYDOWN:
                    if event.key==pygame.K_ESCAPE: running=False
                    elif event.key==pygame.K_r: game.reset()
                    elif event.key in keys and direction is None: direction=keys[event.key]
            if not running: break
            game.step(direction); screen.fill((15,23,42))
            for i,(x,y) in enumerate(game.body): pygame.draw.rect(screen,(45,212,191) if i==0 else (20,130,120),(x*20,y*20,18,18),border_radius=4)
            if game.food: pygame.draw.circle(screen,(251,146,60),(game.food[0]*20+10,game.food[1]*20+10),7)
            label=f'Score: {game.score} | R: restart | Esc: exit'
            if game.over: label=('You won! ' if game.won else 'Game over. ')+label
            screen.blit(font.render(label,True,(230,237,246)),(10,410)); pygame.display.flip(); clock.tick(a.fps)
    finally: pygame.quit()

if __name__=='__main__': main()
