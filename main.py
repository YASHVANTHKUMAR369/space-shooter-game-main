import pygame as p
import os
import time
import random
p.font.init()

WIDTH , HEIGHT = 700,710
WIN = p.display.set_mode((WIDTH, HEIGHT))

Red_Enemy= p.image.load(os.path.join("enemy1.png"))
Blue_Enemy = p.image.load(os.path.join("enemy2.png"))
Green_Enemy = p.image.load(os.path.join("enemy3.png"))
Ornage_Enemy = p.image.load(os.path.join("enemy4.png"))
Gray_Enemy = p.image.load(os.path.join("1.png"))

#player player
Player_player = p.image.load(os.path.join("enemy5.png"))

#laser
Player_laser = p.image.load(os.path.join("laser.png"))
Enemy_laser = p.image.load(os.path.join("laser1.png"))

#bg
BG = p.transform.scale(p.image.load(os.path.join("bg 1.png")),(WIDTH, HEIGHT))

class Laser:
    def __init__(self,x, y, img):
        self.x = x
        self.y = y
        self.img= img
        self.mask = p.mask.from_surface(self.img)

    def draw(self,window):
        window.blit(self.img,(self.x, self.y)) 

    def move(self,vel):
        self.y += vel

    def off_screen(self,height):
        return not (self.y <= height and self.y >= 0)

    def collision(self,obj):
        return collide(self,obj)          

class Ship:
    COOLDOWN = 30
    def __init__(self, x, y, health = 100):
        self.x = x
        self.y = y
        self.health = health
        self.player_img = None
        self.laser_img = None
        self.lasers = []
        self.cool_counter = 0

    def draw(self, window):
        window.blit(self.player_img,(self.x,self.y))
        for laser in self.lasers:
            laser.draw(window)
        for laser in self.lasers:
            laser.draw(window)


    def move_lasers(self, vel, obj):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            elif laser.collision(obj):
                obj.health -= 10
                self.lasers.remove(laser)            

    def cooldown(self):
        if self.cool_counter >= self.COOLDOWN:
            self.cool_counter = 0
        elif self.cool_counter > 0:
            self.cool_counter += 1
            
    def shoot(self):
        if self.cool_counter == 0:
            laser = Laser(self.x-1, self.y, self.laser_img)
            fire = Laser(self.x, self.y, self.laser_img)
            self.lasers.append(laser)  
            self.lasers.append(fire) 
            self.cool_counter = 1 
 

    def get_width(self):
        return self.player_img.get_width()

    def get_height(self):
        return self.player_img.get_height()


class Player(Ship):
    def __init__(self, x, y, health=100):
        super().__init__(x, y, health)
        self.player_img = Player_player
        self.laser_img = Player_laser
        self.mask = p.mask.from_surface(self.player_img)
        self.max_health = health

    def move_lasers(self, vel, objs):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            else:
                for obj in objs:
                    if laser.collision(obj):
                        objs.remove(obj)
                        self.lasers.remove(laser)    

    def draw(self, window):
        super().draw(window)
        self.healthbar(window)

    def healthbar(self,window):
        p.draw.rect(window,(255,0,0),(self.x, self.y + self.player_img.get_height() + 10, self.player_img.get_width(),7))
        p.draw.rect(window,(0,255,0),(self.x, self.y + self.player_img.get_height() + 10, self.player_img.get_width() * (self.health/self.max_health),7))
              

class Enemy(Ship):
    Color_Map = {
                "red":(Red_Enemy, Enemy_laser),
                "green":(Green_Enemy,Enemy_laser),
                "blue" :(Blue_Enemy,Enemy_laser),
                "orange":(Ornage_Enemy,Enemy_laser),
                "gray":(Green_Enemy,Enemy_laser)
                }
    
    def __init__(self, x, y, color, health=100): 
        super().__init__(x, y, health)
        self.player_img,self.laser_img = self.Color_Map[color]
        self.mask= p.mask.from_surface(self.player_img)

    def move(self,vel):
        self.y += vel

    def shoot(self):
        if self.cool_counter == 0:
            laser = Laser(self.x-20, self.y, self.laser_img)
            self.lasers.append(laser)   
            self.cool_counter = 1 

def collide(obj1, obj2):
    offset_x =obj2.x - obj1.x
    offset_y =obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask,(offset_x, offset_y)) != None

def main():
    run =  True
    FPS = 60
    clock = p.time.Clock()
    level = 1
    lives = 20
    player_vel = 10
    laser_vel= 20
    enemies = []
    wave = 5
    enemy_vel = 2
    main_font = p.font.SysFont("comicsans", 35)
    lost_font = p.font.SysFont("comicsans", 35)
    player = Player(300,500)
    lost= False
    lost_count = 0
    p.display.set_caption("space shooter.....")

    def redraw_window():
        WIN.blit(BG,(0,0))
        lives_label = main_font.render(F"Level:{lives}", 1,(255,255,255))
        level_label = main_font.render(F"Level:{level}", 1,(255,255,255))
    
        WIN.blit(lives_label,(10,10))
        WIN.blit(level_label, (WIDTH - level_label.get_width() - 10,10))
        
        for enemy in enemies:
            enemy.draw(WIN)
        player.draw(WIN)

        if lost:
            lost_label = lost_font.render("you lost!!...", 1, (255,255,255))
            WIN.blit(lost_label,(WIDTH/2 - lost_label.get_width()/2,350))
       
        p.display.update()

    while run:
        clock.tick(FPS)
        redraw_window()

        
        if lives <= 0 or player.health <= 0:
            lost = True
            lost_count += 1

        if lost:
            if lost_count > FPS * 5: 
                run = False
            else:
                continue
            
        if len(enemies) == 0:
            level += 1
            wave += 5
            for i in range(wave):
                enemy =Enemy(random.randrange(5,WIDTH-100), random.randrange(-1500,-100), random.choice(["red","blue","green","orange","gray"]))
                enemies.append(enemy)
        
        for event in p.event.get():
            if event.type == p.QUIT:
                run = False

        keys = p.key.get_pressed()
        if keys[p.K_LEFT] and player.x - player_vel > 0:
            player.x -= player_vel
        if keys[p.K_RIGHT] and player.x + player_vel + player.get_width() < WIDTH:
            player.x += player_vel
        if keys[p.K_UP] and player.y - player_vel > 0:
            player.y -= player_vel
        if keys[p.K_DOWN  ] and player.y + player_vel + player.get_height() + 15 < HEIGHT:
            player.y += player_vel    

        if keys[p.K_SPACE]:
            player.shoot() 

        
        for enemy in enemies[:]:
            enemy.move(enemy_vel)
            enemy.move_lasers(laser_vel, player)
            if random.randrange(0, 2*60) == 1:
                enemy.shoot()

            if collide(enemy,player):
                player.health -= 10
                enemies.remove(enemy)

            if enemy.y + enemy.get_height() > HEIGHT:
                lives -= 1
                enemies.remove(enemy)
        player.move_lasers(-laser_vel, enemies)        


def main_menu():
    title_font = p.font.SysFont("comicsans",40)  
    run = True
    while run:
        WIN.blit(BG,(0,0))
        title_label = title_font.render("press Mouse Button.....", 1,(170,175,130))
        WIN.blit(title_label,(WIDTH/2 - title_label.get_width()/2,350))
        p.display.update() 
        for event in p.event.get():
            if event.type == p.QUIT:
                run = False
            if event.type == p.MOUSEBUTTONDOWN:
                main()
    p.quit()            

main_menu()
