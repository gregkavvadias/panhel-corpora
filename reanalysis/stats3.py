import pandas as pd, numpy as np
from scipy import stats
from statsmodels.stats.multitest import multipletests
df=pd.read_csv('data/cohmetrix_appA.csv')
keys=['RDL2','RDFRE','RDFKGL','DESSL','LDVOCD','WRDNOUN','WRDCNCc','WRDIMGc','WRDMEAc','SMCAUSvp','DRPVAL']
rows=[]
for c in keys:
    g=[df[df.book==b][c].values for b in ['English 1','English 2','Panhellenics']]
    H,p=stats.kruskal(*g)
    p12=stats.mannwhitneyu(g[0],g[1]).pvalue
    rows.append(dict(index=c,E1_med=np.median(g[0]),E2_med=np.median(g[1]),Exam_med=np.median(g[2]),E1_M=g[0].mean(),E2_M=g[1].mean(),Exam_M=g[2].mean(),KW_p=p,E1vE2_p=p12))
R=pd.DataFrame(rows); R['KW_p_BH']=multipletests(R.KW_p,method='fdr_bh')[1]
print(R.round(3).to_string(index=False))
print('\nRDL2 range/SD by book'); print(df.groupby('book').RDL2.agg(['min','max','std','count']).round(2))
# power: detectable g at 80% power, n=28 vs 13, alpha .05 two-sided
from statsmodels.stats.power import TTestIndPower
print('\nMDES (80% power, a=.05):',round(TTestIndPower().solve_power(nobs1=28,ratio=13/28,alpha=.05,power=.8),2))
print('MDES with exam n=17 (2010-2026):',round(TTestIndPower().solve_power(nobs1=28,ratio=17/28,alpha=.05,power=.8),2))
# TOST-style: 90% CI for RDL2 mean diff (Welch)
a=df[df.book!='Panhellenics'].RDL2; b=df[df.book=='Panhellenics'].RDL2
d=b.mean()-a.mean(); se=np.sqrt(a.var()/len(a)+b.var()/len(b))
dof=se**4/((a.var()/len(a))**2/(len(a)-1)+(b.var()/len(b))**2/(len(b)-1))
print(f'RDL2 diff exam-school {d:.2f}, 90% CI [{d-stats.t.ppf(.95,dof)*se:.2f}, {d+stats.t.ppf(.95,dof)*se:.2f}], pooled SD {np.sqrt((a.var()*27+b.var()*12)/39):.2f}')
