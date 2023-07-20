#!/usr/bin/env python
# coding: utf-8

# ## COMA ASAS-SN SkyPatrol Comet Ingest Pipeline
# 
# The pyasassn client allows users to query the ASAS-SN input catalog and retrieve light curves from our database. These light curves are subject to live updates as we are running continuous photometry on our nightly images.
# 
# 
# 
# ### ASAS-SN comets
# 
# Use the client.comets catalog to enumerate ASAS-SN comets

# In[19]:


#!pip install seaborn


# In[20]:


import os
import seaborn as sns

from pyasassn.client import SkyPatrolClient

client = SkyPatrolClient()
client.catalogs


# #### Comets Catalog
# 
# The __comets__ catalog contains the comet targets that are of interest to COMA. 

# In[21]:


client.catalogs.comets.head()


# #### The Master List
# 
# The __master_list__ contains __asas_sn_ids__ coordinates and catalog sources for all of our targets. All of our catalogs are cross-matched on the master list with a 2-arcsecond cone. 

# In[22]:


client.catalogs.master_list


# ### Random Curves 
# 
# For whatever reason, if you are interested in random targets from a given catalog, we can give you those too.

# In[23]:


client.random_sample(100, catalog="comets")


# ## Pick a comet from the list
# 
# -  417P is a periodic comet
# -  C/2020K1 is a long period comet
# -  P/2021L4 is a periodic comet

# In[24]:


comet_regexp = 'C/2017K2.*'
#comet_regexp = '417P.*'
#comet_regexp = 'C/2020K1.*'
#comet_regexp = 'P/2021L4.*'


# ### ADQL Queries
# 
# We have inculded a custom ADQL parser. That will allow users to query targets using this familiar SQL-like language. 
# Let's use ADQL to find all the observations of the comet we are interested in!
# 

# In[25]:


query = """
SELECT 
 name 
FROM comets
WHERE name REGEXP '%s'
"""
query = query %(comet_regexp)
client.adql_query(query)


# In[26]:


lcs = client.adql_query(query, download=True, threads=8)
lcs.data.describe()


# In[27]:


lcs.data.head()


# In[28]:


lcs.data.describe()


# In[29]:


t = lcs.data['jd']
m = lcs.data['mag']


# In[30]:


sns.scatterplot(data=lcs.data, x="jd", y="mag")


# In[31]:


sns.scatterplot(data=lcs.data, x="jd", y="mag_err")


# In[32]:


filtered = lcs.data[lcs.data['mag_err'] < 1] 
t = filtered['jd']
m = filtered['mag']


# In[33]:


sns.scatterplot(data=filtered, x="jd", y="mag").set(title='ASAS-SN: C/2017K2')


# #### Saving
# 
# Finally, we can save the individual light curve or the entire collection to .csv

# In[34]:


lcs['C/2017K2(PANSTARRS)MPC105544']


# In[35]:


lightcurve = lcs['C/2017K2(PANSTARRS)MPC105544']
lightcurve.save(filename="c-2017-k2.parq")


# In[36]:


save_dir = '/data'
#print(lcs.data['name'])
lcs.data['coma_id'] = lcs.data['name'].str.replace('/', '-')
for lc in lcs.itercurves():
    lc.meta['coma_id'] = lc.meta['name'].str.replace('/', '-')
#    #lc.meta.set_index('coma_id')

lcs.id_col = 'coma_id'
for lc in lcs.itercurves():
    #lc.meta.set_index('coma_id')
    file = lc.meta[lcs.id_col].values[0]
    #file = file.replace('/','-',1)
    print(file)


# In[48]:


print(lcs.id_col)
lcs.catalog_info['coma_id'] = lcs.catalog_info['name'].str.replace('/', '-')


# In[50]:


for key, data in lcs.data.groupby(lcs.id_col):
    print(key)
    source = lcs.catalog_info[lcs.id_col] == key
    meta = lcs.catalog_info[source]


# In[51]:


lcs.save(save_dir='/data')


# In[52]:


query = """
SELECT 
 name 
FROM comets
"""

client.adql_query(query)


# In[ ]:




