import cv2


camera = cv2.VideoCapture(0)

# 设置曝光参数
camera.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0)  # 关闭自动曝光
camera.set(cv2.CAP_PROP_EXPOSURE, -8)  # 设置曝光值，具体数值需要根据摄像头和环境调整

# 设置摄像头的分辨率
camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

# 读取一帧图像（拍照）
ret, frame = camera.read()

# 检查图像是否成功读取
if not ret:
    print("无法从摄像头捕获图像")
else:
    # 保存图像到当前目录下，文件名为 photo.jpg
    cv2.imwrite('photo.jpg', frame)
    print("照片已保存为 photo.jpg")

# 释放摄像头资源
camera.release()