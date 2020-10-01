
from astropy.coordinates import EarthLocation
import astropy.units as u
from astropy.time import TimeDelta, Time


olat = -24.615662
olon = -70.391089
elev = 2433.
NGTS_location = EarthLocation(lat=olat*u.deg,
                            lon=olon*u.deg,
                            height=elev*u.m)

def convert_MJD(MJD, hjd_corr_sec, bjd_corr_sec):
        time_jd = Time(MJD, format="mjd", scale='utc', location=NGTS_location)
        time_bary = time_jd.tdb + TimeDelta(bjd_corr_sec*u.sec)
        time_helio = time_jd.utc + TimeDelta(hjd_corr_sec*u.sec) 
        return time_jd, time_bary, time_helio