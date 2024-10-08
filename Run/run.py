import time
from Common import image_analysis, camera_operate, keying, m_serial, adb_timer, debug_log
import os
from Common.device_check import DeviceCheck
import configparser
from Common.config import Config

conf = Config()
log = debug_log.MyLog()
analysis = image_analysis.Analysis()
cnns = image_analysis.CNNsAnalysis()
camera = camera_operate.Camera()
key_ing = keying.KeyPhoto()
t_ser = m_serial.SerialD()
configpar = configparser.ConfigParser()
configpar.read(conf.config_file_path)


# 检查adb在线
def check_adb_online_with_thread(device, timeout=90):
    adb_checker = adb_timer.ADBChecker(device, timeout)
    if configpar.get('Config', "is_usb") == "1":
        log.info("选了USB")
        adb_checker.usb = True
        adb_checker.usb_relay = int(configpar.get('Config', "usb_config").split("_")[1])

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
    device_check = DeviceCheck(configpar.get('Config', "device_name"))

    # 确认二部机器adb btn 开
    device_check.adb_btn_open()
    # 先对设备的时间进行修改，使用网络时间，方便看log
    # ?
    # 图片处理相关
    origin_logo_logo_img = os.path.join(conf.logo_logo_path, "Logo.png")
    origin_logo_key_img = os.path.join(conf.logo_key_path, "Key.png")
    # 需要在前端先删除存留的失败照片,调试的时候先在这里删除
    failed_img_path = os.path.join(conf.camera_key_img_path, "Failed.png")
    if os.path.exists(failed_img_path):
        os.remove(failed_img_path)

    flag = 0
    log.info("*************开关机卡logo测试开始****************")
    # 用例说明
    """
    1 适配器开关机（适配器闭合开路开关机）
    2 适配器/电池+电源按键--正常关机（指令关机）
    3 适配器/电池+电源按键--异常关机（适配器开路关机）
    """

    # interval = [i*2 for i in range(1, 100)]
    # 获取cases
    try:
        cases = configpar.get('Config', "cases").split(",")
        if len(cases) == 1:
            while True:
                flag += 1
                # 上下电启动
                try:
                    t_ser.loginSer(configpar.get('Config', "COM"))
                except Exception as e:
                    # log.error("串口已经被占用， 请检查！！！")
                    log.error(str(e))
                    break
                log.info("关机")
                if configpar.get('Config', "cases") == "1":
                    num = int(configpar.get('Config', "adapter_config").split("_")[1])
                    t_ser.open_relay(num)
                    log.info("适配器开路")
                    time.sleep(1)
                    device_check.restart_adb()
                    if device_check.device_is_online():
                        raise Exception("设备关机失败，请接线是否正确！！！")
                    t_ser.close_relay(num)
                    log.info("适配器通路")
                elif configpar.get('Config', "cases") == "2":
                    # 关机
                    device_check.device_shutdown()
                    time.sleep(10)
                    device_check.restart_adb()
                    if device_check.device_is_online():
                        raise Exception("指令设备关机失败，请检查！！！")
                    log.info("指令关机")
                    # 开机
                    num = int(configpar.get('Config', "power_button_config").split("_")[1])
                    t_ser.open_relay(num)
                    log.info("按下电源按键")
                    time.sleep(int(configpar.get('Config', 'button_boot_time')))
                    t_ser.close_relay(num)
                    log.info("松开电源按键")
                # 适配器异常下电
                elif configpar.get('Config', "cases") == "3":
                    num_adapter_power = int(configpar.get('Config', "adapter_power_config").split("_")[1])
                    num_power_button = int(configpar['Config']["power_button_config"].split("_")[1])
                    # 断开适配器/电池
                    t_ser.open_relay(num_adapter_power)
                    log.info("电池/适配器开路")
                    time.sleep(1)
                    device_check.restart_adb()
                    if device_check.device_is_online():
                        raise Exception("设备关机失败，请检查接线是否正确！！！")
                    # 闭合适配器 / 电池
                    t_ser.close_relay(num_adapter_power)
                    log.info("电池/适配器通路")
                    # 按下电源按键开机
                    time.sleep(1)
                    t_ser.open_relay(num_power_button)
                    log.info("按下电源健")
                    time.sleep(int(configpar.get('Config', 'button_boot_time')))
                    t_ser.close_relay(num_power_button)
                    log.info("松开电源按键")
                device_check.restart_adb()
                log.info("正在开机，请等...")
                if check_adb_online_with_thread(configpar.get('Config', "device_name")):
                    if check_boot_complete_with_thread(configpar.get('Config', "device_name"), timeout=120):
                        log.info("设备完全启动")
                    else:
                        log.info("设备无法完全启动, 请检查!!!")
                        if configpar['Config']["only_boot_config"] == "1":
                            log.error("当前认为复现了卡logo情景，请检查！！！")
                            time.sleep(3)
                            break
                else:
                    log.error("没检测到设备在线!!!")
                    if configpar['Config']["only_boot_config"] == "1":
                        log.error("当前认为复现了卡logo情景，请检查！！！")
                        time.sleep(3)
                        break
                if configpar['Config']["only_boot_config"] == "0":
                    # 拍照
                    time.sleep(60)
                    # time.sleep(interval[flag])
                    origin_camera_path = os.path.join(conf.camera_origin_img_path, "Origin.png")
                    # 双屏情况
                    origin_camera2_path = os.path.join(conf.camera_origin_img_path, "Origin2.png")
                    if os.path.exists(origin_camera_path):
                        os.remove(origin_camera_path)
                    if os.path.exists(origin_camera2_path):
                        os.remove(origin_camera2_path)

                    # 单双屏情况
                    if configpar['Config']["double_screen_config"] == "1":
                        camera.take_photo(origin_camera_path, camera_id=1)
                        log.info("镜头2拍照完成")
                        # 抠图
                        log.info("抠图中， 请等待")
                        camera2_key_img_path = os.path.join(conf.camera_key_img_path, "Key2.png")
                        if os.path.exists(camera2_key_img_path):
                            os.remove(camera2_key_img_path)
                        key_ing.save_key_photo(origin_camera_path, camera2_key_img_path)
                        log.info("抠图完成")

                        score2 = cnns.generateScore(origin_logo_key_img, camera2_key_img_path)
                        log.info("当前相似度分数为：%s" % str(score2))
                        if score2 < 75:
                            log.error("当前认为复现了卡logo情景，请检查！！！")
                            if device_check.device_is_online():
                                log.info("设备在线")
                                device_check.logcat(int(configpar.get('Config', 'logcat_duration')) * 60)
                                log.info("成功捕捉了%s 分钟 adb log" % configpar.get('Config', 'logcat_duration'))
                                log.info("任务结束")
                            else:
                                log.info("设备不在线")
                                log.info("任务结束")
                            time.sleep(3)
                            break

                    camera.take_photo(origin_camera_path)
                    log.info("镜头1拍照完成")
                    # 抠图
                    log.info("抠图中， 请等待")
                    camera_key_img_path = os.path.join(conf.camera_key_img_path, "Key.png")
                    if os.path.exists(camera_key_img_path):
                        os.remove(camera_key_img_path)
                    key_ing.save_key_photo(origin_camera_path, camera_key_img_path)
                    log.info("抠图完成")

                    score = cnns.generateScore(origin_logo_key_img, camera_key_img_path)
                    log.info("当前相似度分数为：%s" % str(score))
                    if score < 75:
                        log.error("当前认为复现了卡logo情景，请检查！！！")
                        if device_check.device_is_online():
                            log.info("设备在线")
                            device_check.logcat(int(configpar.get('Config', 'logcat_duration')) * 60)
                            log.info("成功捕捉了%s 分钟 adb log" % configpar.get('Config', 'logcat_duration'))
                            log.info("任务结束")
                        else:
                            log.info("设备不在线")
                            log.info("任务结束")
                        time.sleep(3)
                        break
                else:
                    time.sleep(60)

                t_ser.logoutSer()
                log.info("*******************压测完成%d次********************" % flag)
                time.sleep(3)
    except Exception as e:
        log.info(str(e))

    log.info("停止压测.")
