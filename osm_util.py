import math


def osm_calc_scale(lat):

    print("Calculating scale for latitude: " + str(lat))
    rad_lat = math.radians(lat)

    lat_term_a = 111132.92
    lat_term_b = 559.82 * math.cos(2 * rad_lat)
    lat_term_c = 1.175 * math.cos(4 * rad_lat)
    lat_term_d = 0.0023 * math.cos(6 * rad_lat)
    print(f"{lat_term_a} {lat_term_b} {lat_term_c} {lat_term_d}")
    lat_scale = lat_term_a - lat_term_b + lat_term_c - lat_term_d

    lon_term_a = 111412.84 * math.cos(rad_lat)
    lon_term_b = 93.5 * math.cos(3 * rad_lat)
    lon_term_c = 0.118 * math.cos(5 * rad_lat)
    print(f"{lon_term_a} {lon_term_b} {lon_term_c}")
    lon_scale = lon_term_a - lon_term_b + lon_term_c

    print(f"Lat m per degree: {lat_scale} Lon m per degree: {lon_scale}")
    return lat_scale, lon_scale