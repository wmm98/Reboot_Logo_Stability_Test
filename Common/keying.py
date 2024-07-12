from PIL import Image
import rembg


class KeyPhoto:
    def save_key_photo(self, orig_path, new_path):
        img = Image.open(orig_path)
        img_bg_remove = rembg.remove(img)
        img_bg_remove.save(new_path)
