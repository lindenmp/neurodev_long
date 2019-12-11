#!/usr/bin/env python
# coding: utf-8

# # Preamble

# In[1]:


import os, sys, glob
import seaborn as sns
import pandas as pd
import numpy as np
import statsmodels.api as sm
import scipy as sp
from scipy import stats
import matplotlib.pyplot as plt


# In[2]:


sys.path.append('/Users/lindenmp/Dropbox/Work/ResProjects/NormativeNeuroDev_Longitudinal/code/func/')
from proj_environment import set_proj_env
from func import update_progress


# In[3]:


exclude_str = 't1Exclude'
parc_str = 'schaefer'
parc_scale = 400
parcel_names, parcel_loc, drop_parcels, num_parcels, yeo_idx, yeo_labels = set_proj_env(exclude_str = exclude_str,
                                                                            parc_str = parc_str, parc_scale = parc_scale)


# ### Setup output directory

# In[15]:


print(os.environ['MODELDIR'])
if not os.path.exists(os.environ['MODELDIR']): os.makedirs(os.environ['MODELDIR'])


# ## Load train/test .csv and setup node .csv

# In[5]:


df = pd.read_csv(os.path.join(os.environ['MODELDIR'], 'df_pheno.csv'))
df.set_index(['bblid', 'scanid', 'timepoint'], inplace = True)

print(df.shape)


# In[6]:


df.head()


# In[7]:


metrics = ('ct',)


# In[8]:


# output dataframe
ct_labels = ['ct_' + str(i) for i in range(num_parcels)]
df_node = pd.DataFrame(index = df.index, columns = ct_labels)

print(df_node.shape)


# ## Load in cortical thickness data

# In[9]:


CT = np.zeros((df.shape[0], num_parcels))

for (i, (index, row)) in enumerate(df.iterrows()):
    full_path = glob.glob(os.path.join(os.environ['CTDIR'], str(index[0]), '*' + str(index[1]), os.environ['CT_FILE_NAME']))[0]
    ct = np.loadtxt(full_path)
    CT[i,:] = ct
    
df_node.loc[:,ct_labels] = CT


# In[10]:


df_node.head()


# Save out brain feature data before any nuisance regression

# In[11]:


df_node.to_csv(os.path.join(os.environ['MODELDIR'], 'df_node_base.csv'))


# ### Nuisance regression

# Regress out nuisance covariates. For cortical thickness, we regress out whole brain volume as well as average rating of scan quality from Roalf et al. 2018 NeuroImage.
# 
# We also used a mixed linear model for nuisance regression (instead of a simple OLS) to account for dependency in some of the data

# In[12]:


nuis = ['mprage_antsCT_vol_TBV', 'averageManualRating']
df_nuis = df.loc[:,nuis]
df_nuis = sm.add_constant(df_nuis)

for i, col in enumerate(df_node.columns):
    update_progress(i/df_node.shape[1])
    mdl = sm.MixedLM(df_node.loc[:,col], df_nuis, groups = df.reset_index()['bblid']).fit()
    y_pred = mdl.predict(df_nuis)
    df_node.loc[:,col] = df_node.loc[:,col] - y_pred
update_progress(1)


# In[13]:


df_node.head()


# ## Save out

# In[14]:


df_node.to_csv(os.path.join(os.environ['MODELDIR'], 'df_node_clean.csv'))
