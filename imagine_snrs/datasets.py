import numpy as np
from astropy.io import fits

import astropy.units as u
import matplotlib.pyplot as plt

import imagine as img
import imagine_datasets as img_data


__all__ = ['SNR_DA530_I', 'SNR_DA530_Q','SNR_DA530_U']

class _SNR_DA530_base(img.observables.ImageDataset):
    def __init__(self):

        filename = '../data/{}_DA530.fits'.format(self._STOKES_PARAMETER)
        hdu = fits.open(filename)[0]
        data = hdu.data[0,0].T
        header = hdu.header
        frequency = header['OBSFREQ']*u.Hz

        val_min = {}
        val_max = {}
        val_arr = {}
        delta = {}

        for i in (1, 2):
            i = str(i)

            q = header['CTYPE' + i]
            n_pix = header['NAXIS' + i]
            ref_pos = header['CRPIX' + i]
            ref_val = header['CRVAL' + i]
            delta[q] = header['CDELT' + i]

            val_min[q] = ref_val - delta[q]*(ref_pos-1)
            val_max[q] = ref_val + delta[q]*(n_pix - ref_pos)
            val_arr[q] = np.arange(val_min[q], val_max[q] + delta[q]/2, delta[q]) - ref_val

        super().__init__(data, 'sync',
                       lon_min=val_min['GLON-CAR'],
                       lon_max=val_max['GLON-CAR'],
                       lat_min=val_min['GLAT-CAR'],
                       lat_max=val_max['GLAT-CAR'],
                       object_id='SNR G093.3+06.9',
                       error=None, cov=None,
                       frequency=frequency,
                       tag=self._STOKES_PARAMETER)


class SNR_DA530_I(_SNR_DA530_base):
    _STOKES_PARAMETER = 'I'


class SNR_DA530_U(_SNR_DA530_base):
    _STOKES_PARAMETER = 'U'


class SNR_DA530_Q(_SNR_DA530_base):
    _STOKES_PARAMETER = 'Q'
