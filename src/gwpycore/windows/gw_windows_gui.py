import ctypes


def set_windows_wallpaper(filepath):
    SPI_SETDESKWALLPAPER = 20
    image_path = str(filepath).strip()
    ctypes.windll.user32.SystemParametersInfoW(SPI_SETDESKWALLPAPER, 0, image_path, 0)


__all__ = [
    "set_windows_wallpaper",
]
