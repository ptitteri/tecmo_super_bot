import platform

def mac_windows_path_convert(local_publish_path):
    if platform.platform().lower().find('macos') != -1:
        local_publish_path = local_publish_path.replace('\\', '/')
    elif platform.platform().lower().find('windows') != -1:
        local_publish_path = local_publish_path.replace('/', '\\')

    return local_publish_path