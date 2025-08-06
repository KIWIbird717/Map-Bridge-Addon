import re


def validate_coordinates(coord_string):
    """
    Validate coordinates in Google Earth format
    """
    if not coord_string:
        return False, "Обязательное поле"

    # Паттерн для координат: 43°43'25"N 10°23'49"E
    pattern = r'^(\d{1,2})°(\d{1,2})\'(\d{1,2})\"([NS])\s+(\d{1,3})°(\d{1,2})\'(\d{1,2})\"([EW])$'
    match = re.match(pattern, coord_string.strip())

    if not match:
        return False, "Неверный формат. Используйте: 43°43'25\"N 10°23'49\"E"

    # Извлекаем значения
    lat_deg, lat_min, lat_sec, _lat_dir, lon_deg, lon_min, lon_sec, _lon_dir = match.groups()

    # Проверяем диапазоны
    lat_deg, lat_min, lat_sec = int(lat_deg), int(lat_min), int(lat_sec)
    lon_deg, lon_min, lon_sec = int(lon_deg), int(lon_min), int(lon_sec)

    if lat_deg > 90 or lat_min >= 60 or lat_sec >= 60:
        return False, "Неверные значения широты"

    if lon_deg > 180 or lon_min >= 60 or lon_sec >= 60:
        return False, "Неверные значения долготы"

    return True, ""
