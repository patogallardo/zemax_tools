import pandas as pd
import matplotlib.pyplot as plt
import glob
import numpy as np
import numba as nb
import os
import h5py

GRIDSIZE = 25

def get_fnumbers_given_vectors(ray1, ray2):
    '''Receives row objects ray1 and ray2, these must contain l,m,n
    coordinates.
    returns a f/#'''
    v1 = ray1[['l','m','n']].values[0]
    v2 = ray2[['l','m','n']].values[0]
    cos_theta = np.dot(v1, v2)
    return 0.5/np.tan(np.arccos(cos_theta))

def compare_fields(df1, df2):
    dif = df1[['hx_deg', 'hy_deg']].values - df2[['hx_deg', 'hy_deg']].values
    assert np.sum(dif**2) < 1e-16

def get_extreme_ray_dfs(df):
    df_cr = df.query('px==0 and py==0')
    df_xp = df.query('px==1 and py==0')
    df_xm = df.query('px==-1 and py==0')
    df_yp = df.query('px==0 and py==1')
    df_ym = df.query('px==0 and py==-1')

    compare_fields(df_cr, df_xp)
    compare_fields(df_cr, df_xm)
    compare_fields(df_cr, df_yp)
    compare_fields(df_cr, df_ym)
    
    return df_cr, df_xp, df_xm, df_yp, df_ym

def vignetted(df_cr, df_xp, df_xm, df_yp, df_ym):
    and_ = np.logical_and
    sel1 = df_cr.vignette_code.values == 0
    sel2 = df_xp.vignette_code.values == 0
    sel3 = df_xm.vignette_code.values == 0
    sel4 = df_yp.vignette_code.values == 0
    sel5 = df_ym.vignette_code.values == 0
    use = and_(and_(and_(and_(sel1, sel2), sel3), sel4), sel5)
    return use


def get_fnumber_for_a_given_direction(df1, df2):
    lmn = ['l','m','n']
    dot_p = np.sum(df1[lmn].values * df2[lmn].values, axis=1)
    fn = 0.5/np.tan(np.arccos(dot_p))
    return fn

def get_fnumbers_in_four_directions(df_cr, df_xp, df_xm, df_yp, df_ym):
    fn_xp = get_fnumber_for_a_given_direction(df_cr, df_xp)
    fn_xm = get_fnumber_for_a_given_direction(df_cr, df_xm)
    fn_yp = get_fnumber_for_a_given_direction(df_cr, df_yp)
    fn_ym = get_fnumber_for_a_given_direction(df_cr, df_ym)

    chief_ray_angle = np.rad2deg(np.arccos(df_cr.n.values))
    
    dont_use = np.logical_not(vignetted(df_cr, df_xp, df_xm, df_yp, df_ym))

    fn_xp[dont_use] = np.nan 
    fn_xm[dont_use] = np.nan
    fn_yp[dont_use] = np.nan
    fn_ym[dont_use] = np.nan
    chief_ray_angle[dont_use] = np.nan

    fnumbers = {'fn_xp': fn_xp,
                'fn_xm': fn_xm,
                'fn_yp': fn_yp,
                'fn_ym': fn_ym,
                'fn_av': 0.25*(fn_xp + fn_xm + fn_yp + fn_ym),
                'hx_deg': df_cr.hx_deg.values,
                'hy_deg': df_cr.hy_deg.values,
                'x_pos': df_cr.x_pos.values,
                'y_pos': df_cr.y_pos.values,
                'chief_ray_angle_deg': chief_ray_angle}
    df_fnumbers = pd.DataFrame(fnumbers)
    return df_fnumbers


def camnameFromKeyName(keyname):
    camname = keyname.split('_')[-1]
    return camname


def make_fnumber_hists(df_fn, keyname, show=True):
    sel = np.logical_not(np.isnan(df_fn.fn_av.values))
    plt.figure(figsize=[8, 4.5])
    plt.hist(df_fn.fn_yp.values[sel], 
             histtype='step', label='$f/\#_{y+}$', bins=40)
    plt.hist(df_fn.fn_ym.values[sel], 
             histtype='step', label='$f/\#_{y-}$', bins=40)
    plt.hist(df_fn.fn_xp.values[sel], 
             histtype='step', label='$f/\#_{x+}$', bins=40)
    plt.hist(df_fn.fn_xm.values[sel], 
             histtype='step', label='$f/\#_{x-}$', bins=40)
    
    av = np.percentile(df_fn.fn_av.values[sel], 50)
    av_m = av-np.percentile(df_fn.fn_av.values[sel], 50-34)
    av_p = np.percentile(df_fn.fn_av.values[sel], 50+34)-av

    
    plt.hist(df_fn.fn_av.values[sel], 
             histtype='step', lw=2, 
             label='$f/\#_{av}: %1.2f_{-%1.2f}^{+%1.2f}$' %(av, av_m, av_p),
             bins=40)
    plt.axvspan(av-av_m, av+av_p, color='C4', alpha=0.2)

    plt.legend(loc='upper right')

    camname = camnameFromKeyName(keyname)
    plt.title('Chief ray relative $f/\#$ %s' %camname)
    plt.xlabel('$f/\#$')
    plt.ylabel('count [-]')
    if show:
        plt.show()
    else:
        plt.savefig(os.path.join(out_folder, 
                                 'fnumber_hists_%s.png' %camname),
                    dpi=150)
        plt.close()




def make_fnumber_maps(df_fn, keyname, show=True):
    fig, ax = plt.subplots(2, 2, sharex='col', sharey='row', figsize=[10,8])
    data_id = [['fn_xp', 'fn_xm'], ['fn_yp', 'fn_ym']]
    camname = camnameFromKeyName(keyname)
    
    for i in range(2):
        for j in range(2):
            id = data_id[i][j]
            ax[i,j].set_title(id)
            hb = ax[i,j].hexbin(df_fn.x_pos, df_fn.y_pos, df_fn[id],
                                gridsize=GRIDSIZE)
            fig.colorbar(hb, ax=ax[i,j])
            if i==1:
                ax[i,j].set_xlabel('x$_{focal plane}$ [mm]')
            if j==0:
                ax[i,j].set_ylabel('y$_{focal plane}$ [mm]')
            ax[i,j].set_aspect('equal')
    fig.tight_layout()
    if show:
        plt.show()
    else:
        plt.savefig(os.path.join(out_folder, 
                                 'fnumber_xy_direction_maps_%s.png' % camname),
                    dpi=150)
    plt.close()
    
    plt.figure(figsize=[5.5, 4])
    plt.hexbin(df_fn.x_pos, df_fn.y_pos, df_fn['fn_av'], 
               gridsize=GRIDSIZE)
    plt.title('Average f/$\#$ (in x, y directions)')
    plt.xlabel('x$_{focal plane}$ [mm]')
    plt.ylabel('y$_{focal plane}$ [mm]')
    plt.axis('equal')
    plt.colorbar()
    if show:
        plt.show()
    else:
        plt.savefig(os.path.join(out_folder, 'fnumber_av_%s.png' % camname), 
                    dpi=150)
    plt.close()


def make_chief_angle_map(df_fn, keyname, show=False):
    camname = camnameFromKeyName(keyname)
    plt.figure(figsize=[5.5, 4])
    plt.hexbin(df_fn.x_pos, df_fn.y_pos, df_fn['chief_ray_angle_deg'],
               gridsize=GRIDSIZE)
    plt.title('Focal plane chief ray angle (90-$\\theta$)')
    plt.xlabel('x$_{focal plane}$ [mm]')
    plt.ylabel('y$_{focal plane}$ [mm]')
    plt.axis('equal')
    plt.colorbar()

    if not os.path.exists('./chief_ray'):
        os.mkdir('./chief_ray')
    if show:
        plt.show()
    else:
        plt.savefig(os.path.join('./chief_ray', 
                                 'chief_ray_angles_map_%s.png' %camname), 
                    dpi=150)
    plt.close()

def make_chief_angle_hist(df_fn, keyname, show=False):
    camname = camnameFromKeyName(keyname)

    plt.figure(figsize=[8, 4.5])
    chief_ray_angles = df_fn['chief_ray_angle_deg'].values
    sel = np.logical_not(np.isnan(chief_ray_angles))
    pct_50, pct_50p, pct_50m = np.percentile(chief_ray_angles[sel], 
                                             [50, 50-32, 50+32])
    sigma_p, sigma_m = pct_50p-pct_50, pct_50 - pct_50m
    plt.hist(chief_ray_angles[sel], bins=50, histtype='step',
             color='black', label='angle=$%1.2f^{+%1.2f}_{-%1.2f}$'%(
                                  pct_50, sigma_p, sigma_m))
    plt.axvline(pct_50, color='black', alpha=1)
    plt.axvline(pct_50p, color='black', alpha=0.3)
    plt.axvline(pct_50m, color='black', alpha=0.3)
    plt.legend()
    plt.title('Chief ray angles (90-$\\theta$)')
    plt.xlabel('chief ray angle [deg]')
    plt.ylabel('N')

    if not os.path.exists('./chief_ray'):
        os.mkdir('./chief_ray')
    if show:
        plt.show()
    else:
        plt.savefig(os.path.join('./chief_ray',
                                 'chief_ray_angles_hist_%s.png' % camname), 
                    dpi=150)
    plt.close()


def cleanup_df(df):
    groups = df.groupby(['hx_deg','hy_deg'])
    dfs = []
    
    for group in groups:
        if len(group[1]) == 5:
             dfs.append(group[1])
    df_toreturn = pd.concat(dfs, ignore_index=True)
    return df_toreturn

fnames = glob.glob('ray_db.hdf')
assert len(fnames) == 1
fname = fnames[0]

f = h5py.File('ray_db.hdf')
keys = f.keys()
keys = [key for key in keys if 'df' in key] # leave only the dfs for cameras
f.close()

out_folder = './fNumbers'
if not os.path.exists(out_folder):
    os.mkdir(out_folder)


for j in range(len(keys)):
    key = keys[j]
    df = pd.read_hdf(fname, key)
    max_field_pos = 0.385 # limit fields to sensical values
    df.query('hx_deg**2 + hy_deg**2 < %1.2f**2' %max_field_pos, 
             inplace=True)
    df.query('x_pos**2 + y_pos**2 < 65**2', inplace=True)
    df = cleanup_df(df) # removes rays if pupil not sampled correctly
    
    ########## Now run the analysis
    
    df_cr, df_xp, df_xm, df_yp, df_ym = get_extreme_ray_dfs(df)
    df_fnumbers = get_fnumbers_in_four_directions(df_cr, df_xp, df_xm, 
                                                  df_yp, df_ym)
    #plots below
    make_fnumber_hists(df_fnumbers, keyname=key, show=False)
    make_fnumber_maps(df_fnumbers, keyname=key, show=False)
    
    make_chief_angle_map(df_fnumbers, keyname=key)
    make_chief_angle_hist(df_fnumbers, keyname=key)
    
