#!/usr/bin/env python
# coding: utf-8

# In[1]:


import requests
import pandas as pd
import io
import tweepy
import json
import datetime
import statsmodels.api as sm
import numpy as np
import matplotlib.pyplot as plt


# # Gather Data

# In[2]:


#twitter archive
tweets = pd.read_csv('twitter-archive-enhanced.csv')


# In[3]:


#tweet image predictions
image_url = requests.get('https://d17h27t6h515a5.cloudfront.net/topher/2017/August/599fd2ad_image-predictions/image-predictions.tsv').content
image_raw = pd.read_csv(io.StringIO(image_url.decode('utf-8')),sep='\t', header=0)


# In[4]:


#get all the identifiers to query twitter api
join = pd.merge(tweets, image_raw, on = 'tweet_id',how = 'outer')


# In[5]:


identifiers = join['tweet_id'].values

#twitter json object file
f=open("tweet_json.txt", "w")
for identifier in identifiers:
    try:
        tweet = api.get_status(identifier, tweet_mode='extended')
        json.dump(tweet._json,f)
        f.write('\n')
        print('success')
    except:
        print('failure')
        continue
f.close()
# In[6]:


with open('tweet_json.txt','r') as f:
    content = f.readlines()


# In[7]:


data = {}
for item in content:
    d = json.loads(item)
    data[d['id']] = (d['retweet_count'],d['favorite_count'])


# In[8]:


tdf = pd.DataFrame.from_dict(data,orient='index',columns=['retweets','likes'])
tdf['ID'] = tdf.index
tdf = tdf.reset_index(drop=True)


# # Assess Data

# In[9]:


## tweets visual


# In[10]:


tweets.head()


# In[11]:


tweets['retweeted_status_id'].unique()


# **Quality Issue #1 Some observations are retweets. If the tweet has a retweeted status id, it is a retweet and should be removed from the dataset.** 

# In[12]:


tweets['in_reply_to_status_id'].unique()


# **Quality Issue #2 Some observations are replies. Observations with a in_reply_to_status_id is a reply and should be omitted from the dataset.** 

# In[13]:


## tweets programmatic


# In[14]:


tweets.dtypes


# In[15]:


type(tweets['timestamp'][0])


# **Quality Issue #3: Timestamp needs to be converted to a date time object in order to be manipulated**

# In[16]:


tweets[['doggo','floofer','pupper','puppo']].head()


# **Tidy Issue #1 The dog type should be a single column**

# **Quality Issue #4 Some dogs are listed as None for the above categories**

# In[17]:


tweets['rating_numerator'].unique()


# In[18]:


tweets['rating_denominator'].unique()


# **Quality Issue #5 The denominators are not consistent**

# In[19]:


tweets['name'].unique()


# **Quality Issue #6 The name variable has strange values such as "a" or "his" or "old". It is difficult to decifer if these are real names, typos, or whatnot**

# In[20]:


tweets['source'].unique()


# **Quality Issue #7 The important information in the source variable is buried inside a url. This should be extracted for clean data**

# In[21]:


## image visual


# In[22]:


image_raw


# **Quality Issue #8 Not all images are dogs** 

# In[23]:


## image programmatic


# In[24]:


image_raw.shape


# In[25]:


image_raw.dtypes


# In[26]:


image_raw['p1'].nunique()


# In[27]:


image_raw.groupby('p1').count()


# In[28]:


## api visual


# In[29]:


tdf.head()


# **Tidy Issue #2: The name for the id column should be consistent across all three dataframes because they identify the same type of object**

# In[30]:


## api programmatic


# In[31]:


tdf.dtypes


# # Clean Data

# In[32]:


#make copies of original data
tweets_original = tweets.copy()
images_original = image_raw.copy()
tdf_original = tdf.copy()


# **Quality Issue #1**

# In[33]:


#Define
#Some tweets are retweets
tweets['retweeted_status_id'].unique()


# In[34]:


#Code
#remove retweets
tweets = tweets[pd.isnull(tweets['retweeted_status_id'])]


# In[35]:


#Test
#verify that tweets with retweet status are removed
tweets.retweeted_status_id.unique() #only nan


# In[36]:


#Code
#remove retweet columns
tweets = tweets.drop(['retweeted_status_id','retweeted_status_user_id','retweeted_status_timestamp'],axis=1)


# In[37]:


#verify that retweet columns are dropped
tweets.head()


# **Quality Issue #2**

# In[38]:


#Define
#Some tweets are replies
tweets['in_reply_to_status_id'].unique()


# In[39]:


#code
#remove tweets with reply status
tweets = tweets[pd.isnull(tweets['in_reply_to_status_id'])]


# In[40]:


#test
#verify that replies are removed
tweets['in_reply_to_status_id'].unique()


# In[41]:


#code
#drop reply columns
tweets = tweets.drop(['in_reply_to_status_id','in_reply_to_user_id'],axis=1)


# In[42]:


tweets.head()


# **Quality Issue #3**

# In[43]:


#Define
#time stamp is string but should be date time object
type(tweets['timestamp'][0])


# In[44]:


#code
#convert to timestamp
tweets['timestamp'] = tweets['timestamp'].apply(lambda x: datetime.datetime.strptime(x,'%Y-%m-%d %H:%M:%S +0000'))


# In[45]:


#test
type(tweets['timestamp'][0])


# **Tidy Issue #1**

# In[46]:


#Define
#The dog type should be a column so the dummy variables need to be aggregated into a single column
tweets['doggo'].unique()
tweets['floofer'].unique()
tweets['pupper'].unique()
tweets['puppo'].unique()


# In[47]:


#code & test for tidy issue 1 is combined with quality issue 4


# **Quality Issue #4**

# In[48]:


#Define
#many dogs are not classified as a type ie doggo, floofer, etc
tweets[(tweets['doggo'] == 'None') & (tweets['floofer'] == 'None') & (tweets['pupper'] == 'None') & (tweets['puppo'] == 'None')].count()


# In[49]:


def f(row):
    val = 'None'
    count = 0
    if row['doggo'] == 'doggo':
        val = 'doggo'
        count +=1
    if row['floofer'] == 'floofer':
        val = 'floofer'
        count +=1
    if row['pupper'] == 'pupper':
        val = 'pupper'
        count +=1
    if row['puppo'] == 'puppo':
        val = 'puppo'
        count +=1
    if count > 1:
        val = 'multiple'
    if count == 0:
        val = 'not specified'
    return val


# In[50]:


#Code for tidy issue 1 and quality issue 4
#Make a single column
tweets['type'] = tweets.apply(f, axis=1)


# In[51]:


#drop other dummy variables
tweets = tweets.drop(['doggo','floofer','pupper','puppo'],axis=1)


# In[52]:


#Test 
#anything that was none has been changed to not specified
tweets['type'].unique()


# **Quality Issue #5**

# In[53]:


#Define
#The twitter denominator column does not have consistent values 
tweets.groupby('rating_denominator').count()


# In[54]:


#Code
#since majority is 10, drop other values
tweets = tweets[tweets['rating_denominator']==10]


# In[55]:


#test
tweets.groupby('rating_denominator').count() #shows that there are not denominators other than 10


# In[56]:


#Test
#display a few rows
tweets.head()


# **Quality Issue #6**

# In[57]:


#Define
#Some dog names have weird values such as "a", "his", or "old"
tweets['name'].unique()


# In[58]:


#Code
#drop values that dont begin with a capital letter, aka a proper noun
tweets = tweets[tweets['name'].apply(lambda x: x[0].isupper())==True]


# In[59]:


#test
#all nouns are proper, inproper nouns are dropped
tweets['name'].apply(lambda x: x[0].isupper()).unique()


# **Quality Issue #7** 

# In[60]:


#Define
#Source URL clunky. real information is embedded in URL
tweets['source'].unique()


# In[61]:


#code
def splitUrl(string):
    x = string.split('>')
    x = x[1].split('<')
    return x[0]


# In[62]:


tweets['source'] = tweets['source'].apply(lambda x: splitUrl(x))


# In[63]:


#Test
tweets['source'].unique()


# **Quality issue #8**

# In[64]:


#Define
#Not all the images are dogs.
image_raw[image_raw['p1_dog']==False]


# In[65]:


#Code
#Keep observations where at least one prediction is a dog
image_raw = image_raw[(image_raw['p1_dog'] == True) | (image_raw['p2_dog'] == True) | (image_raw['p3_dog'] == True)]


# In[66]:


#Test
#tweets without dogs were dropped
image_raw[(image_raw['p1_dog'] == False) & (image_raw['p2_dog'] == False) & (image_raw['p3_dog'] == False)]


# **Tidy Issue #2**

# In[67]:


#Define
#The id column should be named the same for each data table
tweets.columns


# In[68]:


tdf.columns


# In[69]:


#code
tdf = tdf.rename(index=str,columns={'ID':'tweet_id'})


# In[70]:


#test
tdf.columns


# ## Merge Dataframes

# In[71]:


archive = pd.merge(tweets, image_raw, on = 'tweet_id',how = 'inner')


# In[72]:


archive = pd.merge(archive, tdf, on = 'tweet_id',how = 'inner')


# In[73]:


archive.head()


# In[74]:


archive.to_csv('twitter_archive_master.csv',index=False)


# # Analyze Data

# In[75]:


archive.groupby(['source']).count() #iphone is the most popular source


# **Insight #1 The primary source for twitter is Twitter for iPhone.**

# In[76]:


archive['rating_numerator'].mean()


# **Insight #2 The average rating for dogs is 11.1 / 10.** 

# In[77]:


archive.nlargest(1,'retweets')


# **Insight #3 Stephen the chihuahua is the most retweeted dog**

# In[85]:


archive.nlargest(1,'likes')


# **Insight #4 A puppo lakeland terrier is the most "liked" dog.** 

# In[79]:


archive['intercept']=1


# In[80]:


archive.head()


# In[81]:


model = sm.OLS(archive['likes'],archive[['retweets','intercept','rating_numerator']]).fit()


# In[82]:


model.summary()


# **Insight #5 For each additional retweet, likes increase by 2.66. For each unit change in rating numerator, likes increase by 404.** 

# In[83]:


archive['rating_numerator'].hist(bins=50)


# Visualization #1

# In[84]:


plt.scatter(archive['retweets'], archive['likes'], s=50, c='blue', alpha=0.5)
plt.title('Likes vs Retweets')
plt.xlabel('Retweets')
plt.ylabel('Likes')
plt.show()


# In[ ]:




