import time
from Common import config, image_analysis, camera_operate, keying, m_serial, adb_timer, debug_log
import os
from Common.device_check import DeviceCheck

import sys

log = debug_log.MyLog()

conf = config.Config()
analysis = image_analysis.Analysis()
camera = camera_operate.Camera()
key_ing = keying.KeyPhoto()
t_ser = m_serial.SerialD()
device_check = DeviceCheck("3TP0110TB20222800005")


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
    # 先对设备的时间进行修改，使用网络时间，方便看log
    # 图片处理相关
    origin_logo_logo_img = os.path.join(conf.logo_logo_path, "Logo1.png")
    origin_logo_key_img = os.path.join(conf.logo_key_path, "Key3.png")
    # 需要在前端先删除存留的失败照片,调试的时候先在这里删除
    failed_img_path = os.path.join(conf.camera_key_img_path, "Failed.png")
    if os.path.exists(failed_img_path):
        os.remove(failed_img_path)

    flag = 0
    # log.info("====================================")
    # time.sleep(3)
    # log.info("==================================")

    while True:
        flag += 1
        log.info("********************%d******************************" % flag)
        print("********************%d******************************" % flag)
        time.sleep(1)

    # while True:
    #     flag += 1
    #     # 上下电启动
    #     t_ser.loginSer("COM56")
    #     t_ser.send_ser_disconnect_cmd()
    #     time.sleep(1)
    #     t_ser.send_ser_connect_cmd()
    #
    #     if check_adb_online_with_thread("3TP0110TB20222800005"):
    #         if check_boot_complete_with_thread("3TP0110TB20222800005", timeout=120):
    #             print("设备完全启动")
    #         else:
    #             print("设备无法完全启动， 请检查！！！！")
    #
    #         # 拍照
    #         time.sleep(60)
    #         origin_camera_path = os.path.join(conf.camera_origin_img_path, "Origin.png")
    #         if os.path.exists(origin_camera_path):
    #             os.remove(origin_camera_path)
    #         camera.take_photo(origin_camera_path)
    #         # 抠图
    #         camera_key_img_path = os.path.join(conf.camera_key_img_path, "Key3.png")
    #         if os.path.exists(camera_key_img_path):
    #             os.remove(camera_key_img_path)
    #         key_ing.save_key_photo(origin_camera_path, camera_key_img_path)
    #
    #         # 对比抠图/原图 origin_camera_path, origin_logo_logo_img
    #         percent = analysis.get_similarity(origin_logo_key_img, camera_key_img_path)
    #         if percent > 95:
    #             os.rename(camera_key_img_path, failed_img_path)
    #             # 捕捉前半个钟的log
    #             device_check.logcat(60)
    #             break
    #         t_ser.logoutSer()
    #     else:
    #         t_ser.loginSer("COM56")
    #         t_ser.send_ser_connect_cmd()
    #         time.sleep(1)
    #
    #         if check_adb_online_with_thread("3TP0110TB20222800005"):
    #             print("设备adb无法起来无法启动")
    #             # 比对黑暗图片
    #             pass
    #     time.sleep(5)
