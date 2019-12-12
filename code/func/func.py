# Functions for project: NormativeNeuroDev_Longitudinal
# Linden Parkes, 2019
# lindenmp@seas.upenn.edu

from IPython.display import clear_output
import numpy as np
import scipy as sp
from scipy import stats
import pandas as pd

from statsmodels.stats import multitest

def get_cmap(which_type = 'qual1', num_classes = 8):
    # Returns a nice set of colors to make a nice colormap using the color schemes
    # from http://colorbrewer2.org/
    #
    # The online tool, colorbrewer2, is copyright Cynthia Brewer, Mark Harrower and
    # The Pennsylvania State University.

    if which_type == 'linden':
        cmap_base = np.array([[255,105,97],[97,168,255],[178,223,138],[117,112,179],[255,179,71]])
    elif which_type == 'pair':
        cmap_base = np.array([[124,230,199],[255,169,132]])
    elif which_type == 'qual1':
        cmap_base = np.array([[166,206,227],[31,120,180],[178,223,138],[51,160,44],[251,154,153],[227,26,28],
                            [253,191,111],[255,127,0],[202,178,214],[106,61,154],[255,255,153],[177,89,40]])
    elif which_type == 'qual2':
        cmap_base = np.array([[141,211,199],[255,255,179],[190,186,218],[251,128,114],[128,177,211],[253,180,98],
                            [179,222,105],[252,205,229],[217,217,217],[188,128,189],[204,235,197],[255,237,111]])
    elif which_type == 'seq_red':
        cmap_base = np.array([[255,245,240],[254,224,210],[252,187,161],[252,146,114],[251,106,74],
                            [239,59,44],[203,24,29],[165,15,21],[103,0,13]])
    elif which_type == 'seq_blu':
        cmap_base = np.array([[247,251,255],[222,235,247],[198,219,239],[158,202,225],[107,174,214],
                            [66,146,198],[33,113,181],[8,81,156],[8,48,107]])
    elif which_type == 'redblu_pair':
        cmap_base = np.array([[222,45,38],[49,130,189]])
    elif which_type == 'yeo17':
        cmap_base = np.array([[97,38,107], # VisCent
                            [194,33,39], # VisPeri
                            [79,130,165], # SomMotA
                            [44,181,140], # SomMotB
                            [75,148,72], # DorsAttnA
                            [23,116,62], # DorsAttnB
                            [149,77,158], # SalVentAttnA
                            [222,130,177], # SalVentAttnB
                            [75,87,61], # LimbicA
                            [149,166,110], # LimbicB
                            [210,135,47], # ContA
                            [132,48,73], # ContB
                            [92,107,131], # ContC
                            [218,221,50], # DefaultA
                            [175,49,69], # DefaultB
                            [41,38,99], # DefaultC
                            [53,75,158] # TempPar
                            ])
    elif which_type == 'yeo17_downsampled':
        cmap_base = np.array([[97,38,107], # VisCent
                            [79,130,165], # SomMotA
                            [75,148,72], # DorsAttnA
                            [149,77,158], # SalVentAttnA
                            [75,87,61], # LimbicA
                            [210,135,47], # ContA
                            [218,221,50], # DefaultA
                            [53,75,158] # TempPar
                            ])

    if cmap_base.shape[0] > num_classes: cmap = cmap_base[0:num_classes]
    else: cmap = cmap_base

    cmap = cmap / 255

    return cmap


def update_progress(progress, my_str = ''):
    bar_length = 20
    if isinstance(progress, int):
        progress = float(progress)
    if not isinstance(progress, float):
        progress = 0
    if progress < 0:
        progress = 0
    if progress >= 1:
        progress = 1

    block = int(round(bar_length * progress))

    clear_output(wait = True)
    text = my_str + " Progress: [{0}] {1:.1f}%".format( "#" * block + "-" * (bar_length - block), progress * 100)
    print(text)


def get_synth_cov(df, cov = 'scanageYears', stp = 1):
    # Synthetic cov data
    X_range = [np.min(df[cov]), np.max(df[cov])]
    X = np.arange(X_range[0],X_range[1],stp)
    X = X.reshape(-1,1)

    return X


def run_corr(df_X, df_y, typ = 'spearmanr'):
    df_corr = pd.DataFrame(index = df_y.columns, columns = ['coef', 'p'])
    for i, row in df_corr.iterrows():
        if typ == 'spearmanr':
            df_corr.loc[i] = sp.stats.spearmanr(df_X, df_y[i])
        elif typ == 'pearsonr':
            df_corr.loc[i] = sp.stats.pearsonr(df_X, df_y[i])

    return df_corr


def get_fdr_p(p_vals):
    out = multitest.multipletests(p_vals, alpha = 0.05, method = 'fdr_bh')
    p_fdr = out[1] 

    return p_fdr


def get_fdr_p_df(p_vals):
    p_fdr = pd.DataFrame(index = p_vals.index,
                        columns = p_vals.columns,
                        data = np.reshape(get_fdr_p(p_vals.values.flatten()), p_vals.shape))

    return p_fdr


def mark_outliers(x, thresh = 3, c = 1.4826):
    my_med = np.median(x)
    mad = np.median(abs(x - my_med))/c
    cut_off = mad * thresh
    upper = my_med + cut_off
    lower = my_med - cut_off
    outliers = np.logical_or(x > upper, x < lower)
    
    return outliers


def perc_dev(Z, thr = 2.6, sign = 'abs'):
    if sign == 'abs':
        bol = np.abs(Z) > thr;
    elif sign == 'pos':
        bol = Z > thr;
    elif sign == 'neg':
        bol = Z < -thr;
    
    # count the number that have supra-threshold z-stats and store as percentage
    Z_perc = np.sum(bol, axis = 1) / Z.shape[1] * 100
    
    return Z_perc


def evd(Z, thr = 0.01, sign = 'abs'):
    m = Z.shape
    l = np.int(m[1] * thr) # assumes features are on dim 1, subjs on dim 0
    
    if sign == 'abs':
        T = np.sort(np.abs(Z), axis = 1)[:,m[1] - l:m[1]]
    elif sign == 'pos':
        T = np.sort(Z, axis = 1)[:,m[1] - l:m[1]]
    elif sign == 'neg':
        T = np.sort(Z, axis = 1)[:,:l]

    E = sp.stats.trim_mean(T, 0.1, axis = 1)
    
    return E

