import os


class Config:
    project_path = os.getcwd()

    camera_key_img_path = os.path.join(project_path, "Photo", "CameraPhoto", "Key")
    camera_origin_img_path = os.path.join(project_path, "Photo", "CameraPhoto", "Take")

    logo_key_path = os.path.join(project_path, "Photo", "Logo", "Key")
    logo_logo_path = os.path.join(project_path, "Photo", "Logo", "Logo")




