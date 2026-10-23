import pandas as pd, numpy as np
from scipy import stats
from statsmodels.stats.multitest import multipletests
F=pd.read_csv('results/own_features.csv'); E=F[F.book=='Panhellenics']
cols=['mean_sent_len','noun_per_1k','passive_per_1k','mtld','FRE','FKGL','content_zipf_mean','rare_content_pct','cov2k','cov3k','cov5k']
def g(a,b):
    sp=np.sqrt(((len(a)-1)*a.var()+(len(b)-1)*b.var())/(len(a)+len(b)-2)); return (b.mean()-a.mean())/sp
for v in ['full','first360']:
    S=F[(F.book!='Panhellenics')&(F.version==v)]; rows=[]
    for c in cols:
        rows.append(dict(index=c,school=S[c].mean(),exam=E[c].mean(),g=g(S[c],E[c]),p_mw=stats.mannwhitneyu(E[c],S[c]).pvalue,p_welch=stats.ttest_ind(E[c],S[c],equal_var=False).pvalue))
    R=pd.DataFrame(rows); R['q_BH_mw']=multipletests(R.p_mw,method='fdr_bh')[1]
    print('\n== school',v,'vs exam'); print(R.round(3).to_string(index=False))
# agreement between own features and Coh-Metrix
A=pd.read_csv('data/cohmetrix_appA.csv'); M=A.merge(F[F.version=='full'],on=['book','text'])
for x,y in [('DESSL','mean_sent_len'),('RDFRE','FRE'),('RDFKGL','FKGL'),('WRDNOUN','noun_per_1k'),('DRPVAL','passive_per_1k'),('LDVOCD','mtld'),('RDL2','cov5k'),('RDL2','content_zipf_mean')]:
    print(x,y,round(stats.spearmanr(M[x],M[y])[0],2))
