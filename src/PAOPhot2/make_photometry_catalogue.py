from astropy.table import Table, vstack
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
    target_row = reference_catalogue[idx_target]
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

    # Finally, let's see if out target made the cut - after all, we want photometry for it.
    if tic_id in reference_catalogue['tic_id']:
        # its in. Lets put it at the start
        print('Target made the cut')
        idx_target = np.where(reference_catalogue['tic_id']==tic_id)[0][0]
        reference_catalogue.remove_row(idx_target) # remove it so we can sort by delta T mag
    else : print('Target did not made the cut, adding it now')
    reference_catalogue = reference_catalogue[np.argsort(np.abs(np.array(reference_catalogue['Tmag']-Tmag)))]
    reference_catalogue = vstack((Table(target_row), reference_catalogue)) # makes sure target is at top


    return reference_catalogue

'''
reference_image = 'NG0451-5357_811_IMAGE81120200928041553.fits'
reference_catalogue = 'NG0451-5357_811_IMAGE81120200928041553_reference_catalogue.fits'


phot_table = make_TIC_target_catalogue(259592689, reference_image, reference_catalogue)
import matplotlib.pyplot as plt
plt.plot(np.arange(len(phot_table)), np.abs(phot_table['Tmag'] - phot_table['Tmag'][0])) 
plt.show()
'''