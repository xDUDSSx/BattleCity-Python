import pyglet
from pyglet.gl import *
import os


class TextureManager:
    """
    Static manager object for texture loading
    """
    resources_path = None

    error = None
    bullet = None

    tank_player_1 = None
    tank_player_2 = None
    tank_standard_1 = None
    tank_standard_2 = None

    wall = None
    wall_bl = None
    wall_br = None
    wall_tr = None
    wall_tl = None

    wall_bl_damaged = None
    wall_br_damaged = None
    wall_tr_damaged = None
    wall_tl_damaged = None

    inwall = None
    bush = None

    exp_anim = None
    bling_seq = None

    debris1 = None
    debris2 = None
    debris3 = None
    debris_anim = None

    flag = None
    flag_damaged = None

    tank_icon = None

    @staticmethod
    def init(path: str):
        """
        :param path: Path to the resources directory
        """
        TextureManager.resources_path = path

    @staticmethod
    def load_texture(path: str):
        """
        :param path: Path to the resource relative to the resource directory
        """
        image = pyglet.image.load(TextureManager.resources_path + os.sep + path)
        return image

    @staticmethod
    def set_center_anchor(image):
        image.anchor_x = image.width // 2
        image.anchor_y = image.height // 2

    @staticmethod
    def load():
        """
        Loads all necessary game textures. Needs to be called before creating any entities.
        """
        TextureManager.tank_player_1 = TextureManager.load_texture("tank_player_1.png")
        TextureManager.tank_player_2 = TextureManager.load_texture("tank_player_2.png")
        TextureManager.tank_standard_1 = TextureManager.load_texture("tank_standard_1_w.png")
        TextureManager.tank_standard_2 = TextureManager.load_texture("tank_standard_2_w.png")

        TextureManager.set_center_anchor(TextureManager.tank_player_1)
        TextureManager.set_center_anchor(TextureManager.tank_player_2)
        TextureManager.set_center_anchor(TextureManager.tank_standard_1)
        TextureManager.set_center_anchor(TextureManager.tank_standard_2)

        TextureManager.error = TextureManager.load_texture("default48.png")

        TextureManager.wall = TextureManager.load_texture("wall48.png")
        TextureManager.wall_bl = TextureManager.load_texture("wall_bits/wall2_bl24.png")
        TextureManager.wall_br = TextureManager.load_texture("wall_bits/wall2_br24.png")
        TextureManager.wall_tr = TextureManager.load_texture("wall_bits/wall2_tr24.png")
        TextureManager.wall_tl = TextureManager.load_texture("wall_bits/wall2_tl24.png")

        TextureManager.wall_bl_damaged = TextureManager.load_texture("wall_bits/wall2_damaged_bl24.png")
        TextureManager.wall_br_damaged = TextureManager.load_texture("wall_bits/wall2_damaged_br24.png")
        TextureManager.wall_tr_damaged = TextureManager.load_texture("wall_bits/wall2_damaged_tr24.png")
        TextureManager.wall_tl_damaged = TextureManager.load_texture("wall_bits/wall2_damaged_tl24.png")

        TextureManager.inwall = TextureManager.load_texture("inwall24.png")
        TextureManager.bush = TextureManager.load_texture("bush24.png")

        # TODO: Export to a horizonzal strip and load with image grid
        exp1 = TextureManager.load_texture("explosion/exp1_48.png")
        exp2 = TextureManager.load_texture("explosion/exp2_48.png")
        exp3 = TextureManager.load_texture("explosion/exp3_48.png")
        exp4 = TextureManager.load_texture("explosion/exp4_48.png")
        exp5 = TextureManager.load_texture("explosion/exp5_48.png")
        exp6 = TextureManager.load_texture("explosion/exp6_48.png")

        explosion_anim_images = [exp1, exp2, exp3, exp4, exp5, exp6]
        TextureManager.exp_anim = pyglet.image.Animation.from_image_sequence(explosion_anim_images,
                                                                             duration=0.07,
                                                                             loop=False)

        bling = TextureManager.load_texture("bling.png")
        bling_images = pyglet.image.ImageGrid(bling, 1, 10)
        TextureManager.bling_seq = pyglet.image.Animation.from_image_sequence(bling_images,
                                                                              duration=0.035,
                                                                              loop=True)

        TextureManager.bullet = TextureManager.load_texture("bullet12.png")
        TextureManager.set_center_anchor(TextureManager.bullet)

        TextureManager.flag = TextureManager.load_texture("flag.png")
        TextureManager.flag_damaged = TextureManager.load_texture("flag_damaged.png")

        TextureManager.tank_icon = TextureManager.load_texture("tank_icon.png")
