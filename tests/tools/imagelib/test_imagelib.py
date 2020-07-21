import pytest
import os
import tempfile

from PIL import Image
from jumpscale.loader import j


def test_resize():
    old_tmp_dir = tempfile.mkdtemp()
    img = Image.new("RGB", (6000, 3000), color="red")
    old_img_path = os.path.join(old_tmp_dir, "red.png")
    img.save(old_img_path)
    new_tmp_dir = tempfile.mkdtemp()
    new_img_path = os.path.join(new_tmp_dir, "red.png")
    assert j.tools.imagelib.resize(old_img_path, new_img_path) == "True"


def test_resize_images_in_dir():
    old_tmp_dir = tempfile.mkdtemp()
    new_tmp_dir = tempfile.mkdtemp()
    red_img = Image.new("RGB", (6000, 3000), color="red")
    green_img = Image.new("RGB", (6000, 3000), color="green")
    blue_img = Image.new("RGB", (6000, 3000), color="blue")
    old_red_path = os.path.join(old_tmp_dir, "red.png")
    old_green_path = os.path.join(old_tmp_dir, "green.png")
    old_blue_path = os.path.join(old_tmp_dir, "blue.png")
    red_img.save(old_red_path)
    green_img.save(old_green_path)
    blue_img.save(old_blue_path)
    dic = {}
    dic[old_blue_path] = dic[old_green_path] = dic[old_red_path] = "True"
    img_dict = j.tools.imagelib.resize_images_in_dir(old_tmp_dir, new_tmp_dir)
    assert dic == img_dict
