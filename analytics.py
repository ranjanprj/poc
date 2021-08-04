import numpy as np
from io import BytesIO
import pandas as pd
import seaborn as sns

import io
import base64
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def histo():
    np.random.seed(19680801)

    # example data
    mu = 100  # mean of distribution
    sigma = 15  # standard deviation of distribution
    x = mu + sigma * np.random.randn(437)

    num_bins = 50

    fig, ax = plt.subplots()

    # the histogram of the data
    n, bins, patches = ax.hist(x, num_bins, density=True)

    # add a 'best fit' line
    y = ((1 / (np.sqrt(2 * np.pi) * sigma)) *
        np.exp(-0.5 * (1 / sigma * (bins - mu))**2))
    ax.plot(bins, y, '--')
    ax.set_xlabel('Smarts')
    ax.set_ylabel('Probability density')
    ax.set_title(r'Histogram of IQ: $\mu=100$, $\sigma=15$')

    # Tweak spacing to prevent clipping of ylabel
    fig.tight_layout()
    # plt.show()
    buffer = BytesIO()
    plt.savefig(buffer, format="png")
    plt.close()
    return buffer


def bias_detection(df, target):
    # sns.countplot(df[target])
    # return pd.DataFrame(df[target].value_counts())

    datadict = {}
    

    datadict['plot'] = sns.countplot(df[target])
    datadict['target_counts'] = pd.DataFrame(df[target].value_counts())
    dlist = datadict['target_counts'].values
    bol = all(i == dlist[0] for i in dlist)
    if bol == True:
        datadict['result'] = 'Non Biased'
    else:
        datadict['result'] = 'Biased'
    datadict['target_counts'] = datadict['target_counts'].to_html(classes='table table-dark')

   
    bytes_image = io.BytesIO()
    plt.savefig(bytes_image, format='png')
    bytes_image.seek(0)
    pic_hash = base64.b64encode(bytes_image.read()).decode('utf8')

    datadict['plot'] = pic_hash

    return datadict
   
def missing_values_detection(df):
    return pd.DataFrame(round(((df.isnull().sum()/len(df.index))*100),1)).to_html(classes='table table-dark')


