import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg') 
from astropy.table import Table 
import numpy as np
from scipy.stats import sem

from astropy.time import Time



def lc_bin(time, flux, bin_width):
        '''
        Function to bin the data into bins of a given width. time and bin_width 
        must have the same units
        '''
        
        edges = np.arange(np.min(time), np.max(time), bin_width)
        dig = np.digitize(time, edges)
        time_binned = (edges[1:] + edges[:-1]) / 2
        flux_binned = np.array([np.nan if len(flux[dig == i]) == 0 else flux[dig == i].mean() for i in range(1, len(edges))])
        err_binned = np.array([np.nan if len(flux[dig == i]) == 0 else sem(flux[dig == i]) for i in range(1, len(edges))])
        time_bin = time_binned[~np.isnan(err_binned)]
        err_bin = err_binned[~np.isnan(err_binned)]
        flux_bin = flux_binned[~np.isnan(err_binned)]   
        
        return time_bin, flux_bin, err_bin


def plot_target_night(table, tic_id_target,fieldcam):
    # tic_id_target is TIC-XXX 
    tics = np.unique([i.split('_')[0] for i in table.colnames[3:] ])
    tics = np.delete(tics, np.where(tics==tic_id_target))

    # First, get the target flux 
    target_flux = np.array(table['{:}_Aper_flux_3'.format(tic_id_target)])
    target_flux_err = np.array(table['{:}_Aper_flux_3_err'.format(tic_id_target)])

    # Now get the comp flux and errors
    comp_flux = np.zeros(target_flux.shape[0])
    comp_flux_err = np.zeros(target_flux.shape[0])
    for i in range(tics.shape[0])[:] : 
        comp_flux = comp_flux + np.array(table['{:}_Aper_flux_3'.format(tics[i])])
        comp_flux_err = comp_flux_err + np.array(table['{:}_Aper_flux_3_err'.format(tics[i])])**2
    comp_flux_err = np.sqrt(comp_flux_err)

    # Work out the detrended flux and errors
    detrended_flux =  target_flux/comp_flux
    detrended_flux_err =  target_flux_err /comp_flux # np.sqrt(detrended_flux**2*((comp_flux_err**2) /  (comp_flux)**2))

    # Now work out a normalisation constant
    Nquarter = int(0.25*target_flux.shape[0])
    norm_constant = np.max([ np.median(detrended_flux[:Nquarter]),   np.median(detrended_flux[-Nquarter:])  ])
    detrended_flux = detrended_flux / norm_constant

    # establish time offset and other metrics
    time_offset = int(np.min(np.array(table['JD'])))
    rms = int(1e6*np.std(detrended_flux))

    f = plt.figure(figsize = (12,5))
    plt.errorbar(np.array(table['JD'])-time_offset, detrended_flux, yerr=detrended_flux_err/norm_constant, markersize=3, fmt='k.', ecolor='lightgrey', alpha = 0.3)



    # Now plot bin if needed 
    t_bin, f_bin, f_bin_err = lc_bin(np.array(table['JD']), detrended_flux, 0.5/24/6)
    plt.errorbar(t_bin-time_offset, f_bin, yerr=f_bin_err, markersize=3, fmt='k.', ecolor='k', alpha = 1)
    rms_5 = int(1e6*np.std(f_bin))

    tile_text = '{:} [{:}]\n{:}\nRMS = {:,} ppm [{:,} @ 5 min]'.format(tic_id_target,    Time(np.array(table['JD'])[0], format='jd').datetime.isoformat()[:10],fieldcam, rms, rms_5)
    plt.gca().set(xlabel='JD-{:,}'.format(time_offset), ylabel='Flux',title=tile_text)
    plt.grid()
    plt.tight_layout()

    # Finally, creat lightcurve structure to return 
    tmp = np.array([np.array(table['JD']), target_flux/comp_flux, target_flux_err /comp_flux ]).T
    return f, plt.gca() , Time(np.array(table['JD'])[0], format='jd').datetime.isoformat()[:10], tmp
