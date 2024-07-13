import cv2
from skimage.metrics import structural_similarity as ssim


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
            cv2.imwrite('../Camera/output_image3.jpg', image2)

        # cv2.imshow('Resized Image 1', image1)
        # cv2.imshow('Original Image 2', image2)

        # 将图片转换为灰度图像
        gray_image1 = cv2.cvtColor(image1, cv2.COLOR_BGR2GRAY)
        gray_image2 = cv2.cvtColor(image2, cv2.COLOR_BGR2GRAY)

        # 计算 SSIM
        ssim_index, _ = ssim(gray_image1, gray_image2, full=True)

        # 将 SSIM 转换为相似度百分比
        similarity_percentage = ssim_index * 100
        print(type(similarity_percentage))
        # 打印相似度百分比
        print(f"图片相似度百分比: {similarity_percentage:.2f}%")

        # cv2.waitKey(0)
        # cv2.destroyAllWindows()
        return float(similarity_percentage)
