import numpy as np

def convertFluxToMags(lightcurve, error):
    """
    Convert normalised lightcurve to differential
    magnitudes + errors
    Parameters
    ----------
    lightcurve : array-like
        Target lightcurve in normalized flux
    error : array-like
        Error on lightcurve
    Returns
    -------
    mag : array-like
        Target lightcurve converted to differential
        magnitudes
    magg_err : array-like
        Error on mag
    Raises
    ------
    None
    """
    mag = -2.5*np.log10(lightcurve)
    mag_err = (2.5/np.log(10))*(error/np.abs(lightcurve))
    return mag, mag_err