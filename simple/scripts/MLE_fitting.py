import numpy as np
from statsmodels.base.model import GenericLikelihoodModel
from scipy.stats import norm
import pandas as pd
import xml.etree.ElementTree as ET


def _ll_ols(y, X, beta, sigma):
    mu = X.dot(beta)
    return norm(mu, sigma).logpdf(y).sum()


class MyOLS(GenericLikelihoodModel):
    def __init__(self, endog, exog, **kwds):
        super(MyOLS, self).__init__(endog, exog, **kwds)

    def nloglikeobs(self, params):
        sigma = params[-1]
        beta = params[:-1]
        ll = _ll_ols(self.endog, self.exog, beta, sigma)
        return -ll

    def fit(self, start_params=None, maxiter=10000, maxfun=5000, **kwds):
        # we have one additional parameter and we need to add it for summary
        self.exog_names.append('sigma')
        if start_params == None:
            # Reasonable starting values
            start_params = np.append(np.zeros(self.exog.shape[1]), .5)
        return super(MyOLS, self).fit(start_params=start_params,
                                      maxiter=maxiter, maxfun=maxfun,
                                      **kwds)


def get_travel_times(filename):
    tree = ET.parse(filename)
    root = tree.getroot()
    travel_times = []
    veh_num = []
    for i, tripinfo in enumerate(root):
        travel_times.append(float(tripinfo.attrib['duration']))
        veh_num.append(i)
    return travel_times, veh_num


if __name__=="__main__":
    y, x = get_travel_times('../output/tripinfo_2_to_4_0_500.xml')
    df = pd.DataFrame({'y':y, 'x':x})
    #df['constant'] = 1
    #sm_ols_manual = MyOLS(df.y,df[['constant','x']]).fit()
    #print(sm_ols_manual.summary())
    df.to_csv('disrupted.csv')