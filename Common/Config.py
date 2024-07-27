import os


class Config:
    project_path = path_dir = str(os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir)))

    camera_key_img_path = os.path.join(project_path, "Photo", "CameraPhoto", "Key")
    camera_origin_img_path = os.path.join(project_path, "Photo", "CameraPhoto", "Take")

    logo_key_path = os.path.join(project_path, "Photo", "Logo", "Key")
    logo_logo_path = os.path.join(project_path, "Photo", "Logo", "Logo")
    debug_log_path = os.path.join(project_path, "Log", "Debug", "debug_log.txt")
    system_failed_log_path = os.path.join(project_path, "Log", "Logcat", "failed_logcat.txt")
    flag_file_path = os.path.join(project_path, "UI", "flag.txt")
    config_file_path = os.path.join(project_path, "UI", "config.ini")






