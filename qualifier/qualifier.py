from pathlib import Path

import numpy as np
from PIL import Image



def valid_input(image_size: tuple[int, int], tile_size: tuple[int, int], ordering: list[int]) -> bool:
    """
    Return True if the given input allows the rearrangement of the image, False otherwise.
    
    The tile size must divide each image dimension without remainders, and `ordering` must use each input tile exactly
    once.
    """

    # Checking if there are any repeated values in the provided ordering
    if len(set(ordering)) != len(ordering):
        return False
    
    # Checking whether the image can be divided according to the provided tile_size
    if (image_size[0] % tile_size[0] == 0 and image_size[1] % tile_size[1] == 0):
        cols = image_size[0] / tile_size[0]
        rows = image_size[1] / tile_size[1]
        
        # Checking if the image can be divided according to the provided ordering
        if cols*rows % len(ordering) == 0 :
            return True
        else:
            return False
    else:
        return False

 
def rearrange_tiles(image_path: str, tile_size: tuple[int, int], ordering: list[int], out_path: str) -> None:
    """
    Rearrange the image.

    The image is given in `image_path`. Split it into tiles of size `tile_size`, and rearrange them by `ordering`.
    The new image needs to be saved under `out_path`.

    The tile size must divide each image dimension without remainders, and `ordering` must use each input tile exactly
    once. If these conditions do not hold, raise a ValueError with the message:
    "The tile size or ordering are not valid for the given image".
    """
    
    # Reading the image from the given path and getting meta data of the image
    image = Image.open(image_path)
    image_size = image.size
    cols = image_size[0] / tile_size[0]
    rows = image_size[1] / tile_size[1]
    image_mode = image.mode
    
    # Checking if the given image is valid for the processing
    valid = valid_input(image.size, tile_size, ordering)
    if not valid:
        raise ValueError('The tile size or ordering are not valid for the given image')

    # Splitting the image according to the given tile size
    parts = split_image_with_tile(image, tile_size)
    
    # Re-arranging the image according to the given ordering
    final_image = join_parts(parts, ordering, rows, cols, image_mode)
    
    # Saving the image to the given output path
    final_image.save(out_path)


def split_image_with_tile(image: Image, tile_size: tuple[int, int]) ->  list[Image]:
    """Splits image into parts according to the given tile size.

    Args:
        image (Image): The image read from the given path
        tile_size (tuple): Tile size given in the input

    Returns:
        list: Parts of the given image 
    """
        
    width, height = image.size
    tile_width, tile_height = tile_size

    parts = []
    for y in range(0, height, tile_height):
        for x in range(0, width, tile_width):
            left = x
            upper = y
            right = x + tile_width
            lower = y + tile_height

            part = image.crop((left, upper, right, lower))
            parts.append(part)

    return parts
    
def join_parts(parts: list[Image], order: list[int], rows: int, cols: int, image_mode: str) -> Image:
    """Re-arranges the parts of the given image and returns a final image

    Args:
        parts (list): List of tile parts
        order (list): List containing the given ordering
        rows (int): Number of rows for the new image
        cols (int): Number of columns for the new image
        image_mode (str): Mode of the new image

    Returns:
        Image: New image after the re-arranging process
    """    
    part_width, part_height = parts[0].size
    
    width = int(cols * part_width)
    height = int(rows * part_height)
    joined_image = Image.new(image_mode, (width, height))

    for idx, part_idx in enumerate(order):
        part = parts[part_idx] 

        col_idx = int(idx % cols)
        row_idx = int(idx // cols)

        left = col_idx * part_width
        upper = row_idx * part_height

        joined_image.paste(part, (left, upper))

    return joined_image

    
# if __name__ == '__main__':    
#     image_path = Path("images", 'pydis_logo_scrambled.png')
#     order_path = Path('images', 'pydis_logo_order.txt')
#     with open(order_path, 'r') as file:
#         ordering = file.readlines()
#         ordering = list(map(int, ordering))
#     output = rearrange_tiles(image_path, (256, 256), ordering, 'output_image.png')
