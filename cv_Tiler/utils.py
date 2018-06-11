"""cv_tiler.utils: utility functions."""


import numpy as np
import rasterio
from rasterio.vrt import WarpedVRT
from rasterio.enums import Resampling
from rasterio.io import DatasetReader
from rio_tiler.errors import (RioTilerError,
                              InvalidFormat,
                              InvalidLandsatSceneId,
                              InvalidSentinelSceneId,
                              InvalidCBERSSceneId)

from shapely.geometry import box

from PIL import Image

# Python 2/3
try:
    from urllib.request import urlopen
except ImportError:
    from urllib2 import urlopen


def utm_getZone(longitude):
    """Calculate UTM Zone from Longitude

    Attributes:
    ___________
    longitude: float of longitude (Degrees.decimal degrees)

    Returns:
    _______
    out: int
        returns UTM Zone number
    """
    return (int(1+(longitude+180.0)/6.0))

def utm_isNorthern(latitude):
    """Calculate UTM North/South from Latitude

    Attributes:
    ___________
    latitude: float of latitude (Deg.decimal degrees)

    Returns:
    _______
    out: int
        returns UTM Zone number
    """

    if (latitude < 0.0):
        return "S"
    else:
        return "N"


def calculate_UTM_EPSG(latitude, longitude, epsgStart={"N":"EPSG:326", "S":"EPSG:327"}):
    """Calculate UTM North/South from Latitude

    Attributes:
    ___________
    latitude: float, latitude (Deg.decimal degrees)
    longitude: float, of longitude (Degrees.decimal degrees)
    epsgStart: dict, dictionary for precursor for UTM Zone EPSG (Default is WGS84)

    Returns:
    _______
    out: str
        returns UTM Zone EPSG
    """

    utmZone = utm_getZone(longitude)
    utmDirection = utm_isNorthern(latitude)

    return "{}{}".format(epsgStart[utmDirection], str(utmZone))

def tile_read_utm(source, bounds, tilesize, indexes=[1], nodata=None, alpha=None, dst_crs='EPSG:3857'):
    """Read data and mask

    Attributes
    ----------
    source : str or rasterio.io.DatasetReader
        input file path or rasterio.io.DatasetReader object
    bounds : tuple, (w, s, e, n) bounds in dst_csrs
    tilesize : Output image size
    indexes : list of ints or a single int, optional, (default: 1)
        If `indexes` is a list, the result is a 3D array, but is
        a 2D array if it is a band index number.
    nodata: int or float, optional (defaults: None)
    alpha: int, optional (defaults: None)
        Force alphaband if not present in the dataset metadata

    dst_crs: str, optional (defaults: "EPSG:3857" (Web Mercator)
        Determine output path


    Returns
    -------
    out : array, int
        returns pixel value.
    """
    w, s, e, n = bounds

    if alpha is not None and nodata is not None:
        raise RioTilerError('cannot pass alpha and nodata option')

    if isinstance(indexes, int):
        indexes = [indexes]

    out_shape = (len(indexes), tilesize, tilesize)

    vrt_params = dict(
        dst_crs=dst_crs,
        resampling=Resampling.bilinear,
        src_nodata=nodata,
        dst_nodata=nodata)

    if isinstance(source, DatasetReader):
        with WarpedVRT(source, **vrt_params) as vrt:
            window = vrt.window(w, s, e, n, precision=21)
            data = vrt.read(window=window,
                            boundless=True,
                            resampling=Resampling.bilinear,
                            out_shape=out_shape,
                            indexes=indexes)

            if nodata is not None:
                mask = np.all(data != nodata, axis=0).astype(np.uint8) * 255
            elif alpha is not None:
                mask = vrt.read(alpha, window=window,
                                out_shape=(tilesize, tilesize),
                                boundless=True,
                                resampling=Resampling.bilinear)
            else:
                mask = vrt.read_masks(1, window=window,
                                      out_shape=(tilesize, tilesize),
                                      boundless=True,
                                      resampling=Resampling.bilinear)
    else:
        with rasterio.open(source) as src:
            with WarpedVRT(src, **vrt_params) as vrt:
                window = vrt.window(w, s, e, n, precision=21)
                data = vrt.read(window=window,
                                boundless=True,
                                resampling=Resampling.bilinear,
                                out_shape=out_shape,
                                indexes=indexes)

                if nodata is not None:
                    mask = np.all(data != nodata, axis=0).astype(np.uint8) * 255
                elif alpha is not None:
                    mask = vrt.read(alpha, window=window,
                                    out_shape=(tilesize, tilesize),
                                    boundless=True,
                                    resampling=Resampling.bilinear)
                else:
                    mask = vrt.read_masks(1, window=window,
                                          out_shape=(tilesize, tilesize),
                                          boundless=True,
                                          resampling=Resampling.bilinear)

    return data, mask

def tile_exists_utm(boundsSrc, boundsTile):
    """"Check if suggested tile is within bounds

    'bounds = (w, s, e, n)'
    'box( minx, miny, maxx, maxy)'

    :param bounds:

    :return:
    """


    boundsSrcBox = box(boundsSrc)
    boundsTileBox = box(boundsTile)

    return boundsSrcBox.intersects(boundsTileBox)





