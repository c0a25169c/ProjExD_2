import os
import random
import sys
import pygame as pg
import time

WIDTH, HEIGHT = 1100, 650
os.chdir(os.path.dirname(os.path.abspath(__file__)))


def gameover(screen: pg.Surface) -> None:
    """
    引数：Surface
    戻り値：None
    """
    blackout = pg.Surface((WIDTH,HEIGHT))  # ブラックアウト
    blackout.fill((0, 0, 0))
    blackout.set_alpha(200)  # 透明度

    font = pg.font.Font(None, 80)  # ゲームオーバー文字
    text = font.render("Game Over", True,(255, 255, 255))
    text_rct = text.get_rect(center=(WIDTH//2, HEIGHT//2))

    kk8_img = pg.transform.rotozoom(pg.image.load("fig/8.png"), 0, 1)  # 泣いているこうかとん
    kk8_rct1 = kk8_img.get_rect(center=(WIDTH//2 + 200, HEIGHT//2))
    kk8_rct2 = kk8_img.get_rect(center=(WIDTH//2 - 200, HEIGHT//2))

    screen.blit(blackout, (0, 0))
    screen.blit(text, text_rct)
    screen.blit(kk8_img, kk8_rct1)
    screen.blit(kk8_img, kk8_rct2)
    pg.display.update()
    time.sleep(5)


def check_bound(rct: pg.Rect) -> tuple[bool,bool]:
    """
    引数：こうかとんRect or 爆弾Rect
    戻り値：判定結果タプル（横判定結果、縦判定結果）
    Ttue OR False
    """
    yoko, tate = True, True
    if rct.left < 0 or WIDTH < rct.right:  # 横判定
        yoko = False
    if rct.top < 0 or HEIGHT < rct.bottom:  # 縦判定
        tate = False
    return yoko, tate


def get_kk_imgs() -> dict[tuple[int,int],pg.Surface]:
    """
    移動量タプルと対応するこうかとん画像Surfaceの辞書を返す関数
    戻り値: 移動量タプルをキー、画像Surfaceを値とした辞書
    """
    img = pg.transform.rotozoom(pg.image.load("fig/3.png"), 0, 0.9)
    img_flip = pg.transform.flip(img, True, False) 

    return {
        (0, 0): img,  # キー押下なし
        (-5, 0): img,  # 左
        (+5, 0): img_flip,  # 右

        (0, -5): pg.transform.rotozoom(img, -90, 1.0),        # 上
        (0, +5): pg.transform.rotozoom(img, +90, 1.0),       # 下

        (-5, -5): pg.transform.rotozoom(img, -45, 1.0),       # 左上
        (-5, +5): pg.transform.rotozoom(img, +45, 1.0),      # 左下

        (+5, -5): pg.transform.rotozoom(img_flip, +45, 1.0), # 右上
        (+5, +5): pg.transform.rotozoom(img_flip, -45, 1.0),  # 右下
    }


def init_bb_imgs() -> tuple[list[pg.Surface], list[int]]:
    '''
    爆弾の拡大画像リストと加速度リストを生成する関数
    戻り値：bb_imgs (list[Surface]):半径10～100の爆弾Surfaceを10段階で格納したリスト
    bb_accs (list[int]):加速度(1～10)のリスト
    '''
    bb_imgs = []
    bb_accs = [a for a in range(1, 11)]

    for r in range(1, 11):
        bb_img = pg.Surface((20*r, 20*r))
        bb_img.set_colorkey((0, 0, 0))
        pg.draw.circle(bb_img, (255, 0, 0), (10*r, 10*r), 10*r)
        bb_imgs.append(bb_img)
    return bb_imgs, bb_accs

def main():
    pg.display.set_caption("逃げろ！こうかとん")
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    bg_img = pg.image.load("fig/pg_bg.jpg")  

    # こうかとんの初期化
    kk_imgs = get_kk_imgs()
    kk_img = kk_imgs[(0, 0)]  # 左向き
    kk_rct = kk_img.get_rect()
    kk_rct.center = 300, 200

    # 爆弾の初期化
    bb_imgs, bb_accs = init_bb_imgs()
    bb_img = pg.Surface((20,20))  # 爆弾用のSurface
    pg.draw.circle(bb_img,(255,0,0),(10,10),10)  # 赤丸半径10
    bb_img.set_colorkey((0,0,0))
    bb_rct = bb_img.get_rect()  # 爆弾Rect
    bb_rct.centerx = random.randint(0,WIDTH)  # 横初期座標
    bb_rct.centery = random.randint(0,HEIGHT)  # 縦初期座標
    vx, vy = +5, +5

    clock = pg.time.Clock()
    tmr = 0
    

    DELTA={
        pg.K_UP:(0,-5),#上
        pg.K_DOWN:(0,+5),#下
        pg.K_LEFT:(-5,0),#左
        pg.K_RIGHT:(+5,0),#右
    }

    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT: 
                return
        if kk_rct.colliderect(bb_rct):  # こうかとん　爆弾　重なったら
            gameover(screen)
            return
        screen.blit(bg_img, [0, 0]) 

        key_lst = pg.key.get_pressed()
        sum_mv = [0, 0]
        #if key_lst[pg.K_UP]:
        #   sum_mv[1] -= 5
        #if key_lst[pg.K_DOWN]:
        #    sum_mv[1] += 5
        #if key_lst[pg.K_LEFT]:
        #    sum_mv[0] -= 5
        #if key_lst[pg.K_RIGHT]:
        #    sum_mv[0] += 5
        for key, mv in DELTA.items():
            if key_lst[key]:
                sum_mv[0] += mv[0]#横移動量
                sum_mv[1] += mv[1]#縦移動量
        direction = (sum_mv[0], sum_mv[1])
        kk_img = kk_imgs[direction]  # こうかとん切り替え

        kk_rct.move_ip(sum_mv)
        if check_bound(kk_rct) != (True,True):
            kk_rct.move_ip(-sum_mv[0],-sum_mv[1])#動きをキャンセル
        screen.blit(kk_img,kk_rct)
        
        #bb_rct.move_ip(vx, vy)
        yoko, tate = check_bound(bb_rct)
        if not yoko:
            vx *= -1
        if not tate:
            vy *= -1

    
        idx = min(tmr // 500, 9) # tmrの値に応じて段階を決定(0～9)
        # 加速した速度
        avx = vx * bb_accs[idx]
        avy = vy * bb_accs[idx]

        bb_img = bb_imgs[idx] # 爆弾の画像を拡大版に差し替え
        bb_rct.width = bb_img.get_width()
        bb_rct.height = bb_img.get_height()

        bb_rct.move_ip(avx, avy)


        screen.blit(kk_img, kk_rct)
        screen.blit(bb_img, bb_rct)
        pg.display.update()
        tmr += 1
        clock.tick(50)


if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()
