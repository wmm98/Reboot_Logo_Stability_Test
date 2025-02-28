import os


class Config:

    # 调试环境
    # # 调试环境
    # project_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # project_outside_path = project_path
    # print("**********************************")
    # print("project_path: ", project_path)
    # print("project_outside_path: ", project_outside_path)

    # # 正式路径
    project_path = os.path.dirname((os.path.dirname(os.path.abspath(__file__))))
    project_outside_path = os.getcwd()
    print("**********************************")
    print("project_path: ", project_path)
    print("project_outside_path: ", project_outside_path)

    photo_path = os.path.join(project_outside_path, "Photo")

    camera_photo_path = os.path.join(photo_path, "CameraPhoto")
    camera_photo_take_path = os.path.join(camera_photo_path, "Take")
    camera_photo_key_path = os.path.join(camera_photo_path, "Key")

    logo_path = os.path.join(photo_path, "Logo")
    logo_logo_base_path = os.path.join(logo_path, "Logo")
    logo_key_base_path = os.path.join(logo_path, "Key")

    camera_key_img_path = os.path.join(camera_photo_path, "Key")
    camera_origin_img_path = os.path.join(camera_photo_path, "Take")
    #
    # logo_key_path = os.path.join(project_path, "Photo", "Logo", "Key")
    logo_logo_path = os.path.join(logo_logo_base_path, "Logo.png")

    log_base_path = os.path.join(project_outside_path, "Log")

    debug_base_path = os.path.join(log_base_path, "Debug")
    debug_log_path = os.path.join(debug_base_path, "debug_log.txt")

    logcat_base_path = os.path.join(log_base_path, "Logcat")

    system_failed_log_path = os.path.join(logcat_base_path, "failed_logcat.txt")

    flag_file_path = os.path.join(project_path, "UI", "flag.txt")
    config_file_path = os.path.join(project_path, "UI", "config.ini")


    logo_take_path = os.path.join(logo_logo_base_path, "Logo.png")
    logo_key_path = os.path.join(logo_key_base_path, "Key.png")
    camera_key_path = os.path.join(camera_photo_key_path, "Key.png")
    camera2_key_path = os.path.join(camera_photo_key_path, "Key", "Key2.png")


    # failed_logcat.txt
    adb_log_path = os.path.join(logcat_base_path, "failed_logcat.txt")
    failed_image_key_path = os.path.join(camera_photo_key_path, "Failed.png")






