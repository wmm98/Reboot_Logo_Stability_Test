if __name__ == '__main__':
    import time
    from Common import config, image_analysis, camera_operate, keying, m_serial
    import os
    conf = config.Config()
    analysis = image_analysis.Analysis()
    camera = camera_operate.Camera()
    key_ing = keying.KeyPhoto()
    t_ser = m_serial.SerialD()

    # 图片处理相关
    origin_logo_img = os.path.join(conf.logo_key_path, "Key2.png")

    f = open("data.txt", "w+")

    flag = 0
    while True:
        flag += 1
        # 上下电启动
        t_ser.loginSer("COM27")
        t_ser.send_ser_disconnect_cmd()
        time.sleep(1)
        t_ser.send_ser_connect_cmd()
        time.sleep(70)

        # 拍照
        origin_camera_path = os.path.join(conf.camera_origin_img_path, "Origin.png")
        if os.path.exists(origin_camera_path):
            os.remove(origin_camera_path)
        camera.take_photo(origin_camera_path)
        # 抠图
        camera_key_img_path = os.path.join(conf.camera_key_img_path, "Key.png")
        if os.path.exists(camera_key_img_path):
            os.remove(camera_key_img_path)
        key_ing.save_key_photo(origin_camera_path, camera_key_img_path)

        # 对比抠图
        percent = analysis.get_similarity(origin_logo_img, camera_key_img_path)

        t_ser.logoutSer()
        t_f = open("data.txt", "a")
        t_f.write(str(percent) + "\n")
        t_f.close()







