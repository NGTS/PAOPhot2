from astropy.table import Table
from astropy.io import fits 
import numpy as np 


def make_TIC_target_catalogue(tic_id, reference_image, reference_catalogue):
    print('making target catalogue for {:} using reference image {:} and reference catalogue {:}'.format(tic_id, tic_id, reference_image, reference_catalogue))
    frame = fits.open(reference_image)[0]
    reference_catalogue = Table.read(reference_catalogue)

    ###############################################################
    # Get target RA, dec, Tmag, G mag
    ###############################################################
    idx_target = np.where(reference_catalogue['tic_id']==tic_id)[0][0]
    ra, dec, Tmag, Gmag = reference_catalogue['ra_deg'][idx_target], reference_catalogue['dec_deg'][idx_target], reference_catalogue['Tmag'][idx_target], reference_catalogue['GAIAmag'][idx_target],

    ###############################################################
    # Sort catalogue out
    ###############################################################
    reference_catalogue_mask = (reference_catalogue['on_chip']==1) & (reference_catalogue['blended']==False) & (reference_catalogue['objType']=='STAR') & (reference_catalogue['lumclass']=='DWARF') & (reference_catalogue['Dilution_Tmag_AP3.0']< 0.1) 

    i = 1
    while True:
        if len(reference_catalogue_mask[reference_catalogue_mask & (np.abs(reference_catalogue['Tmag'] - Tmag) < (i*0.5))]) < 100:
            i *=2
        else : 
            reference_catalogue = reference_catalogue[reference_catalogue_mask & (np.abs(reference_catalogue['Tmag'] - Tmag) < (i*0.5))]
            print('Found {:,} comparison stars within Delta Tmag = {:.2f}'.format(len(reference_catalogue), i*0.5))
            break

    return reference_catalogue