import time
from Common import config, image_analysis, camera_operate, keying, m_serial, adb_timer, debug_log
import os
from Common.device_check import DeviceCheck
import configparser


# 检查adb在线
def check_adb_online_with_thread(device, timeout=90):
    adb_checker = adb_timer.ADBChecker(device, timeout)
    adb_checker.start_check()

    # Wait until timeout or ADB is found
    start_time = time.time()
    while time.time() - start_time < timeout:
        if adb_checker.result:
            adb_checker.timeout_handler()
            return True
        time.sleep(1)
    return False


# 检查adb在线
def check_boot_complete_with_thread(device, timeout=120):
    adb_checker = adb_timer.ADBChecker(device, timeout)
    adb_checker.start_check(boot=True)

    # Wait until timeout or ADB is found
    start_time = time.time()
    while time.time() - start_time < timeout:
        if adb_checker.result:
            adb_checker.timeout_handler()
            return True
        time.sleep(1)
    return False


if __name__ == '__main__':
    config = configparser.ConfigParser()
    config.read('config.ini')
    log = debug_log.MyLog()
    conf = config.Config()
    analysis = image_analysis.Analysis()
    camera = camera_operate.Camera()
    key_ing = keying.KeyPhoto()
    t_ser = m_serial.SerialD()
    device_check = DeviceCheck(config.get('Config', "device_name"))
    # 先对设备的时间进行修改，使用网络时间，方便看log
    # 图片处理相关
    origin_logo_logo_img = os.path.join(conf.logo_logo_path, "Logo.png")
    origin_logo_key_img = os.path.join(conf.logo_key_path, "Key.png")
    # 需要在前端先删除存留的失败照片,调试的时候先在这里删除
    failed_img_path = os.path.join(conf.camera_key_img_path, "Failed.png")
    if os.path.exists(failed_img_path):
        os.remove(failed_img_path)

    log.info("****************开始测试*****************")
    flag = 0
    log.info("*************开关卡logo测试开始****************")
    # 用例说明
    """
    1 适配器开关机用例
    2 适配器+电源按键--正常关机（指令关机）
    3 适配器+电源按键--异常关机（适配器开路关机）
    4 电池+电源按键--正常关机（指令关机）
    5 电池+电源按键--异常关机（电池开路关机）
    """

    interval = [i * 4 for i in range(1, 100)]
    while True:
        flag += 1
        # 上下电启动
        try:
            t_ser.loginSer(config.get('Config', "COM"))
        except Exception as e:
            log.error("串口已经被占用， 请检查！！！")
            log.error(str(e))
            break
        # 如果为1路继电器，则为断适配器开关机，适配器常闭状态
        if config.get('Config', "relay_type") == "is_1_relay":
            if config.get('Config', "adapter_config") == "relay_1":
                t_ser.open_first_relay()
                time.sleep(1)
                t_ser.close_first_relay()
            elif config.get('Config', "adapter_config") == "relay_2":
                t_ser.open_second_relay()
                time.sleep(1)
                t_ser.close_second_relay()
            elif config.get('Config', "battery_config") == "relay_3":
                t_ser.open_third_relay()
                time.sleep(1)
                t_ser.close_third_relay()
            else:
                t_ser.open_fourth_relay()
                time.sleep(1)
                t_ser.close_fourth_relay()
        else:
            # 4路继电器
            # 适配器+电源按键， 适配器常闭，电源按键常开
            if int(config.get('Config', "is_adapter")) and int(config.get('Config', "is_power_button")) and \
                    not int(config.get('Config', "is_battery")) and not int(config.get('Config', "is_usb")):
                pass

        t_ser.send_ser_disconnect_cmd()
        time.sleep(1)
        t_ser.send_ser_connect_cmd()
        if not t_ser.confirm_ser_connected():
            break
        log.info("正在开机，请等...")
        time.sleep(interval[flag])
        if check_adb_online_with_thread(config.get('Config', "device_name")):
            if check_boot_complete_with_thread(config.get('Config', "device_name"), timeout=120):
                log.info("设备完全启动")
            else:
                log.info("设备无法完全启动, 请检查!!!")

        # 拍照
        # time.sleep(60)
        origin_camera_path = os.path.join(conf.camera_origin_img_path, "Origin.png")
        if os.path.exists(origin_camera_path):
            os.remove(origin_camera_path)
        camera.take_photo(origin_camera_path)
        log.info("拍照完成")
        # 抠图
        log.info("抠图中， 请等待")
        camera_key_img_path = os.path.join(conf.camera_key_img_path, "Key.png")
        if os.path.exists(camera_key_img_path):
            os.remove(camera_key_img_path)
        key_ing.save_key_photo(origin_camera_path, camera_key_img_path)
        log.info("抠图完成")
        # 对比抠图/原图 origin_camera_path, origin_logo_logo_img
        # percent = analysis.get_similarity(origin_logo_key_img, camera_key_img_path)
        # log.info("样本logo和测试logo相似度为%s%%" % str(percent))
        # 对比距离值：
        distance = analysis.get_images_distance(origin_logo_key_img, camera_key_img_path)
        # if distance:
        log.info("两张图片之间的距离值为： %s" % str(distance))
        threshold = 8  # 可以根据需要调整阈值
        if distance > threshold:
            log.info("当前测试认为复现卡logo, 请检查设备!!!")
            # break

        # if percent < 95:
        #     # os.rename(camera_key_img_path, failed_img_path)
        #     log.info("当前测试认为复现卡logo, 请检查设备!!!")
        #     # 捕捉前半个钟的log
        #     device_check.logcat(60)
        #     break
        t_ser.logoutSer()
        log.info("*******************压测完成%d次********************" % flag)
        time.sleep(3)

    # thread.join()
    log.info("停止压测.")
