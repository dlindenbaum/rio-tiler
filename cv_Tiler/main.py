import rasterio
from rasterio.warp import transform_bounds
from rasterio.io import DatasetReader

from rio_tiler import utils as rio_utils
from rio_tiler.errors import TileOutsideBounds
from rio_tiler import main as rio_main
from cv_Tiler import utils as cv_utils




def tile_utm_source(src, ll_x, ll_y, ur_x, ur_y, indexes=None, tilesize=256, nodata=None, alpha=None, dst_crs='epsg:4326'):
    """
    Create UTM tile from any images.

    Attributes
    ----------
    source : rasterio.Dataset
    tile_x : int
        Mercator tile X index.
    tile_y : int
        Mercator tile Y index.
    tile_z : int
        Mercator tile ZOOM level.
    indexes : tuple, int, optional (default: (1, 2, 3))
        Bands indexes for the RGB combination.
    tilesize : int, optional (default: 256)
        Output image size.
    nodata: int or float, optional
        Overwrite nodata value for mask creation.
    alpha: int, optional
        Overwrite alpha band index for mask creation.


    Returns
    -------
    data : numpy ndarray
    mask: numpy array

    """

    wgs_bounds = transform_bounds(
        *[src.crs, dst_crs] + list(src.bounds), densify_pts=21)

    indexes = indexes if indexes is not None else src.indexes
    tile_bounds = (ll_x, ll_y, ur_x, ur_y)
    if not cv_utils.tile_exists_utm(wgs_bounds, tile_bounds):
        raise TileOutsideBounds(
            'Tile {}/{}/{}/{} is outside image bounds'.format(ll_x, ll_y, ur_x, ur_y))

    return cv_utils.tile_read_utm(src,
                                  tile_bounds,
                                  tilesize,
                                  indexes=indexes,
                                  nodata=nodata,
                                  alpha=alpha,
                                  dst_crs=dst_crs)



def tile_utm(source, ll_x, ll_y, ur_x, ur_y, indexes=None, tilesize=256, nodata=None, alpha=None, dst_crs='epsg:4326'):
    """
    Create UTM tile from any images.

    Attributes
    ----------
    address : str
        file url or rasterio.Dataset.
    tile_x : int
        Mercator tile X index.
    tile_y : int
        Mercator tile Y index.
    tile_z : int
        Mercator tile ZOOM level.
    indexes : tuple, int, optional (default: (1, 2, 3))
        Bands indexes for the RGB combination.
    tilesize : int, optional (default: 256)
        Output image size.
    nodata: int or float, optional
        Overwrite nodata value for mask creation.
    alpha: int, optional
        Overwrite alpha band index for mask creation.


    Returns
    -------
    data : numpy ndarray
    mask: numpy array

    """

    if isinstance(source, DatasetReader):

        return tile_utm_source(source,
                               ll_x,
                               ll_y,
                               ur_x,
                               ur_y,
                               indexes=indexes,
                               tilesize=tilesize,
                               nodata=nodata,
                               alpha=alpha,
                               dst_crs=dst_crs)



    else:
        with rasterio.open(source) as src:

            return tile_utm_source(src,
                                   ll_x,
                                   ll_y,
                                   ur_x,
                                   ur_y,
                                   indexes=indexes,
                                   tilesize=tilesize,
                                   nodata=nodata,
                                   alpha=alpha,
                                   dst_crs=dst_crs)




def get_chip(address, ll_x, ll_y, xres, yres, downSampleRate):
    """ Get Chip From Image

    :param address:
    :param ll_x:
    :param ll_y:
    :param xres:
    :param yres:
    :param downSampleRate:
    :return:

    """



