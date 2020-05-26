import os
from PIL import Image


def get_list_files(dir_name):
    """returns a list of directories for all image files in a root folder

    Arguments:
        dir_name (str) : the directory of the root folder

    Returns:
        all_files (list) : the list of directories for all files in the root folder
    """
    # create a list of file and sub directories
    # names in the given directory
    files_list = os.listdir(dir_name)
    all_files = list()
    # Iterate over all the entries
    for entry in files_list:
        # Create full path
        full_path = os.path.join(dir_name, entry)
        # If entry is a directory then get the list of files in this directory
        if os.path.isdir(full_path):
            all_files = all_files + get_list_files(full_path)
        else:
            path_split = os.path.splitext(full_path)
            if path_split[1] in [".jpg", ".jpeg", ".png"]:
                all_files.append(full_path)

    return all_files


def get_image(path):
    """returns an PIL.Image object by path
    
    Arguments:
        path (string) : the image path
    
    Returns:
        PIL.Image object
    """
    return Image.open(path)


def resize(path, pathnew, width=1024):
    """resize an image 
    
    Arguments:
        path (string) : the path of the image will be resized
        pathnew (string) : the path of new resized image
    
    Keyword Arguments:
        width (int) : the width of the new image , hieght is depending on it
    
    Returns:
        (string) : True if image resized successfully or the exception message if not
    """
    im = get_image(path)
    xnew = width
    x, y = im.size
    ynew = int(float(y) / (float(x) / float(xnew)))
    imnew = im.resize((xnew, ynew), Image.ANTIALIAS)
    try:
        imnew.save(pathnew)
        return "True"
    except Exception as e:
        return str(e)


def resize_images_in_dir(folder, foldernew, width=1024):
    """resize images in folder
    
    Arguments:
        folder (string) : the path of the root folder in which images will be resized
        foldernew (string) : the path of the folder in which new images will be stored
    
    Keyword Arguments:
        width (int) : the width of the new images , hieght is depending on it
    
    Returns:
        (dict) : a dict with img path as key and its statue as value
            statue : True if image resized successfully or the exception message if not
    """
    img_list = get_list_files(folder)
    print(img_list)
    img_statue = {}
    for img in img_list:
        statue = resize(img, os.path.join(foldernew, os.path.basename(img)), width=width)
        img_statue[img] = statue
    return img_statue
