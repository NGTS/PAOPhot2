"""
General database functions for process

Any functions that interact with the database should go here
"""
# To avoid OpenBLAS error
import os
os.environ['OPENBLAS_NUM_THREADS'] = '1'

from contextlib import contextmanager
from collections import defaultdict
import pymysql
from astropy.table import Table 
import numpy as np
import os, sys 

PAOPhot_paths = {'PAOPhot2_path' : '/home/ops/dev/PAOPhot2',
              'PAOPhot2_data_path' : '/ngts/staging/archive/PAOPhot2',
              'refcatpipe2_path' : '/home/ops/dev/refcatpipe2',
              'WCSPhotpipe_path'  : '/home/ops/dev/WCSPhotPipe',
              'NGTSDilution_path' : '/home/ops/dev/NGTSDilution'}

# pylint: disable=invalid-name

@contextmanager
def open_db(host='10.2.5.32', db='ngts_ops',
            user='ops', cur_class='list'):
    """
    Reusable database connection manager
    """
    if cur_class == 'list':
        with pymysql.connect(host=host,
                             db=db,
                             user=user) as cur:
            yield cur
    else:
        with pymysql.connect(host=host,
                             db=db,
                             user=user,
                             cursorclass=pymysql.cursors.DictCursor) as cur:
            yield cur

def is_action_ready_to_reduce(action_id):
    """
    sanity check the action_ids against
    action_summary_log.

    Possible action status in action_sumary_log are:
       1. aborted
       2. completed
       3. ignored
       4. pending
       5. started

    If an action was completed | aborted:
       1. We want to reduce these partial or complete actions
       2. Add the row to the quick_reduction table
       3. Create a job file for the correct das
       4. Submit the job file with qsub

    If an action was ignored:
       1. There is no data as nothing happend

    If an action is pending | started:
       1. There is an issue, this shouldn't happen
       2. The night should be over by this point

    A final case is when actions are dropped. In this
    case even the entry in action_list is missing. They
    can obviously be skipped too
    """

    qry = """
        SELECT status
        FROM action_summary_log
        WHERE action_id = %s
        """
    with open_db(cur_class='dict') as cur:
        cur.execute(qry, (action_id,))
        result = cur.fetchone()

    if result is None:
        ready = False
    else:
        if result['status'] in ['aborted', 'completed']:
            ready = True
        else:
            ready = False
    return ready







def get_action_info(action_id):
    """
    Get action info for scheduling reductions

    By this point we know we have an action in
    the action_summary_log table
    """
    qry = """
        SELECT asl.action_id, asl.field, sfi.ra_target_deg, sfi.dec_target_deg,
        al.camera_id, hwn.das_id
        FROM action_summary_log AS asl
        LEFT JOIN scheduler_field_info AS sfi ON asl.field = sfi.field
        LEFT JOIN action_list AS al ON asl.action_id = al.action_id
        LEFT JOIN ngts_hwlog.hw_now AS hwn ON al.camera_id = hwn.camera_id
        WHERE asl.action_id=%s;
    """
    qry_args = (action_id,)
    with open_db(cur_class='dict') as cur:
        cur.execute(qry, qry_args)
        result = cur.fetchone()
    return result 


def get_actions_for_field(field):
    qry = 'select * from action_summary_log where actual_start_utc like "{:}%" AND action_type="observeField";'.format(night)
    with open_db(cur_class='dict') as cur:
        cur.execute(qry)
        result = cur.fetchall()
    return result

def get_actions_for_night(night):
    qry = 'select * from action_summary_log where night="{:}" AND action_type="observeField";'.format(night)
    with open_db(cur_class='dict') as cur:
        cur.execute(qry)
        result = cur.fetchall()
    return result


def get_images_information_for_action(action_id):
    qry = 'select * from raw_image_list where action_id={:} AND image_class="SCIENCE" and image_type="IMAGE";'.format(action_id)
    with open_db(cur_class='dict') as cur:
        cur.execute(qry)
        result = cur.fetchall()
    return result

def get_image_information(image_id):
    qry = 'select * from raw_image_list where image_id={:};'.format(image_id)
    with open_db(cur_class='dict') as cur:
        cur.execute(qry)
        result = cur.fetchall()
    return result


def get_autoguider_information(field, camera_id):
    qry = 'select * from autoguider_refimage WHERE field="{:}" AND camera_id={:};'.format(field, camera_id)
    with open_db(cur_class='dict') as cur:
        cur.execute(qry)
        result = cur.fetchone()
    return result



def get_ticid_from_toi(TOI_ID):
    TOI_ID = int(TOI_ID)
    datafile =  '{:}/TOI_data/TOI-data.csv'.format(PAOPhot_paths['PAOPhot2_data_path']) 
    if not os.path.isfile(datafile):
        print('Unable to find {:}'.format(datafile))
        return -99
    
    # Load the table
    t = Table.read(datafile, format='csv')

    # look for out TOI
    idxs = np.argwhere(np.array(t['TOI'], dtype=int)==TOI_ID)
    if idxs[0].shape[0]==0:
        print('TOI-{:} is not in {:}'.format(TOI_ID, datafile))
        return -99 
    else : return int(t['TIC ID'][idxs[0][0]])


def get_actions_for_field(field):
    qry = 'select * from action_summary_log where field="{:}" and (status="completed" OR status="aborted");'.format(field)
    with open_db(cur_class='dict') as cur:
        cur.execute(qry)
        result = cur.fetchone()
    return result