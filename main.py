import os
from PIL import Image


def get_size_format(b, factor=1024, suffix="B"):
    """
    Scale bytes to its proper byte format
    e.g:
        1253656 => '1.20MB'
        1253656678 => '1.17GB'
    """
    for unit in ["", "K", "M", "G", "T", "P", "E", "Z"]:
        if b < factor:
            return f"{b:.2f}{unit}{suffix}"
        b /= factor
    return f"{b:.2f}Y{suffix}"


# To check if image is transparent
def has_transparency(img):
    if img.info.get("transparency", None) is not None:
        return True
    if img.mode == "P":
        transparent = img.info.get("transparency", -1)
        for _, index in img.getcolors():
            if index == transparent:
                return True
    elif img.mode == "RGBA":
        extrema = img.getextrema()
        if extrema[3][0] < 255:
            return True

    return False


def compress_img(images, new_size_ratio=None, quality=90, width=None, height=None, to_jpg=True, save_to=None):
    images = images.split()

    for image_name in images:
        # load the image to memory
        img = Image.open(image_name)
        # print the original image shape
        print("[*] Image shape:", img.size)
        # get the original image size in bytes
        image_size = os.path.getsize(image_name)
        # print the size before compression/resizing
        print("[*] Size before compression:", get_size_format(image_size))

        if has_transparency(img):
            to_jpg = False

        if new_size_ratio:
            if new_size_ratio < 1.0:
                # if resizing ratio is below 1.0, then multiply width & height with this ratio to reduce image size
                img = img.resize((int(img.size[0] * new_size_ratio), int(img.size[1] * new_size_ratio)),
                                 Image.ANTIALIAS)
                # print new image shape
                print("[+] New Image shape:", img.size)
            elif width and height:
                # if width and height are set, resize with them instead
                img = img.resize((width, height), Image.ANTIALIAS)
                # print new image shape
                print("[+] New Image shape:", img.size)
        # split the filename and extension
        filename, ext = os.path.splitext(image_name)

        filename_without_path = filename.split("\\")[-1]

        if save_to:
            filename = f"{save_to}\\{filename_without_path}"

        # make new filename appending _compressed to the original file name

        if to_jpg:
            # change the extension to JPEG
            new_filename = f"{filename}_compressed.jpg"
        else:
            # retain the same extension of the original image
            new_filename = f"{filename}_compressed{ext}"

        try:
            # save the image with the corresponding quality and optimize set to True
            img.save(new_filename, quality=quality, optimize=True)
        except OSError:
            # convert the image to RGB mode first
            img = img.convert("RGB")
            # save the image with the corresponding quality and optimize set to True
            img.save(new_filename, quality=quality, optimize=True)
        print("[+] New file saved:", new_filename)
        # get the new image size in bytes
        new_image_size = os.path.getsize(new_filename)
        # print the new size in a good format
        print("[+] Size after compression:", get_size_format(new_image_size))
        # calculate the saving bytes
        saving_diff = new_image_size - image_size
        # print the saving percentage
        print(f"[+] Image size change: {saving_diff / image_size * 100:.2f}% of the original image size.")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Simple Python script for compressing and resizing images")
    parser.add_argument("image", help="Target image to compress and/or resize")
    parser.add_argument("-j", "--to-jpg", action="store_true", help="Whether to convert the image to the JPEG format")
    parser.add_argument("-q", "--quality", type=int, help="Quality ranging from a minimum of 0 (worst) to a maximum of 95 (best). Default is 90")
    parser.add_argument("-r", "--resize-ratio", type=float, help="Resizing ratio from 0 to 1, setting to 0.5 will multiply width & height of the image by 0.5. Default is 1.0")
    parser.add_argument("-w", "--width", type=int, help="The new width image, make sure to set it with the `height` parameter")
    parser.add_argument("-hh", "--height", type=int, help="The new height for the image, make sure to set it with the `width` parameter")
    parser.add_argument("-st", "--save-to", type=str, help="Where to save your compressed images")
    args = parser.parse_args()
    # print the passed arguments
    print("="*50)
    print("[*] Image:", args.image)
    print("[*] To JPEG:", args.to_jpg)
    print("[*] Quality:", args.quality)
    print("[*] Resizing ratio:", args.resize_ratio)
    if args.width and args.height:
        print("[*] Width:", args.width)
        print("[*] Height:", args.height)
    print("="*50)
    # compress the image
    compress_img(args.image, args.resize_ratio, args.quality, args.width, args.height, args.to_jpg, args.save_to)
