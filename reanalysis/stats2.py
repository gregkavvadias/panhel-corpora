import pandas as pd, numpy as np
from scipy import stats
from statsmodels.stats.multitest import multipletests
df=pd.read_csv('data/cohmetrix_appA.csv'); df['grp']=np.where(df.book=='Panhellenics','exam','school')
idx=[c for c in df.columns if c not in('book','text','grp','RDL2')]
thesis_exam={'DESPC':.837,'CNCAll':.637,'DRNEG':.594,'WRDADV':.574,'LDVOCD':-.575,'DRNP':-.634,'DRPP':-.673,'WRDNOUN':-.919}
thesis_school={'DRVP':.453,'WRDNOUN':-.560,'WRDCNCc':-.438}
for g,th in [('school',thesis_school),('exam',thesis_exam)]:
    d=df[df.grp==g]; rows=[]
    for c in idx:
        r,p=stats.pearsonr(d[c],d.RDL2); rs,ps=stats.spearmanr(d[c],d.RDL2)
        rows.append(dict(index=c,r=r,p=p,rho=rs,p_rho=ps,thesis_r=th.get(c,np.nan)))
    R=pd.DataFrame(rows); R['p_BH']=multipletests(R.p,method='fdr_bh')[1]
    print(f'\n== {g} (n={len(d)})'); print(R.sort_values('p').round(3).head(12).to_string(index=False))
    R.to_csv(f'results/corr_{g}.csv',index=False)
print('\ncritical |r| p<.05: n=13',round(stats.t.ppf(.975,11)/np.sqrt(11+stats.t.ppf(.975,11)**2),3),' n=28',round(stats.t.ppf(.975,26)/np.sqrt(26+stats.t.ppf(.975,26)**2),3))
