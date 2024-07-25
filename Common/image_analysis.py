import cv2
from skimage.metrics import structural_similarity as ssim
from PIL import Image
import imagehash

"""
目前使用感知哈希算法比对两张图片的距离
"""


class Analysis:
    def __init__(self):
        pass

    def resize_image(sefl, image, size):
        """调整图像大小以匹配目标尺寸"""
        return cv2.resize(image, size, interpolation=cv2.INTER_AREA)

    def get_similarity(self, image1, image2):
        # 读取第一张图片
        image1 = cv2.imread(image1, cv2.IMREAD_COLOR)

        # 检查第一张图片是否成功读取
        if image1 is None:
            print("无法读取第一张图片")
            exit()

        # 读取第二张图片
        image2 = cv2.imread(image2, cv2.IMREAD_COLOR)

        # 检查第二张图片是否成功读取
        if image2 is None:
            print("无法读取第二张图片")
            exit()

        # 获取两张图片的尺寸
        size1 = image1.shape[1], image1.shape[0]
        size2 = image2.shape[1], image2.shape[0]

        # 调整第二张图片的大小以匹配第一张图片的尺寸
        if size1 != size2:
            image2 = self.resize_image(image2, size1)
            # cv2.imwrite('../Camera/output_image3.jpg', image2)

        # cv2.imshow('Resized Image 1', image1)
        # cv2.imshow('Original Image 2', image2)

        # 将图片转换为灰度图像
        gray_image1 = cv2.cvtColor(image1, cv2.COLOR_BGR2GRAY)
        gray_image2 = cv2.cvtColor(image2, cv2.COLOR_BGR2GRAY)

        # 计算 SSIM
        ssim_index, _ = ssim(gray_image1, gray_image2, full=True)
        # 将 SSIM 转换为相似度百分比
        similarity_percentage = ssim_index * 100
        return float(similarity_percentage)

    def calculate_phash(self, image_path):
        """
        计算图像的感知哈希值
        """
        img = Image.open(image_path)
        return imagehash.phash(img)

    def compare_images(self, image_path1, image_path2):
        """
        比较两张图片的感知哈希值
        """
        hash1 = self.calculate_phash(image_path1)
        hash2 = self.calculate_phash(image_path2)

        # 计算哈希值之间的汉明距离
        hash_distance = hash1 - hash2

        # 返回相似度（距离越小，图片越相似）
        return hash_distance

    def get_images_distance(self, image_path1, image_path2):
        # 比较两张图片
        distance = self.compare_images(image_path1, image_path2)
        # 判断图片是否相似（设定一个阈值）
        # threshold = 5  # 可以根据需要调整阈值
        # if distance < threshold:
        #     print("Images are similar")
        # else:
        #     print("Images are not similar")

        return distance

    # def calculate_dhash(self, image_path):
    #     """
    #     计算图像的差异哈希值
    #     """
    #     img = Image.open(image_path)
    #     # 使用 imagehash 库计算差异哈希值
    #     return imagehash.dhash(img)
    #
    # def compare_images(self, image_path1, image_path2):
    #     """
    #     比较两张图片的差异哈希值
    #     """
    #     hash1 = self.calculate_dhash(image_path1)
    #     hash2 = self.calculate_dhash(image_path2)
    #
    #     # 计算哈希值之间的汉明距离
    #     hash_distance = hash1 - hash2
    #
    #     # 返回相似度（汉明距离越小，图片越相似）
    #     return hash_distance
