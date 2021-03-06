# To avoid OpenBLAS error
import os
os.environ['OPENBLAS_NUM_THREADS'] = '1'

from setuptools import setup, Extension

setup(
    name = 'PAOPhot2',
    version = '1.0',
    description = 'Package for the analysis and reduction of NGTS photometry in realtime.',
    url = None,
    author = 'Samuel Gill',
    author_email = 'samuel.gill@warwick.ac.uk',
    license = 'GNU',
    packages=['PAOPhot2'],
    package_dir={'PAOPhot2': 'src/PAOPhot2'},
    #package_data={'spec1d': ['data/gr5_-4_ref_spectra.dat', 'data/gr5_-4_ref_lines.dat']},
    #package_data={'tessffiextract': ['data/*.csv']},
    scripts=['Utils/reduce_action', 'Utils/find_best_comparisons', 'Utils/make_photometry_catalogue', 'Utils/postprocess_action', 'Utils/photpack', 'Utils/photpackstack',
            'Utils/process_night', 'Utils/process_night_wrapper', 'Utils/check_object' , 'Utils/paophottls', 'Utils/ngtscut'],
    #install_requires=['numba']
)