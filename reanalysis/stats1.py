import pandas as pd, numpy as np
from scipy import stats
from statsmodels.stats.multitest import multipletests
df=pd.read_csv('data/cohmetrix_appA.csv'); df['grp']=np.where(df.book=='Panhellenics','exam','school')
idx=[c for c in df.columns if c not in('book','text','grp')]
S=df[df.grp=='school']; E=df[df.grp=='exam']
rng=np.random.default_rng(1)
def hedges(a,b):
    na,nb=len(a),len(b); sp=np.sqrt(((na-1)*a.var(ddof=1)+(nb-1)*b.var(ddof=1))/(na+nb-2))
    return (b.mean()-a.mean())/sp*(1-3/(4*(na+nb)-9))
def boot_ci(a,b,B=5000):
    g=[hedges(rng.choice(a,len(a)),rng.choice(b,len(b))) for _ in range(B)]
    return np.percentile(g,[2.5,97.5])
out=[]
for c in idx:
    a,b=S[c].values,E[c].values
    t,pw=stats.ttest_ind(b,a,equal_var=False)
    U,pm=stats.mannwhitneyu(b,a,alternative='two-sided')
    g=hedges(a,b); lo,hi=boot_ci(a,b)
    rbc=2*U/(len(a)*len(b))-1  # rank-biserial, exam>school positive
    out.append(dict(index=c,school_M=a.mean(),exam_M=b.mean(),g=g,g_lo=lo,g_hi=hi,rbc=rbc,p_welch=pw,p_mw=pm,
                    shapiro_school=stats.shapiro(a).pvalue))
R=pd.DataFrame(out)
for p in ['p_welch','p_mw']:
    R[p+'_BH']=multipletests(R[p],method='fdr_bh')[1]
    R[p+'_holm']=multipletests(R[p],method='holm')[1]
pd.set_option('display.width',250); pd.set_option('display.max_columns',30)
print(R.round(3).to_string(index=False))
R.to_csv('results/group_comparisons.csv',index=False)
# length dependence within school texts
print('\nSpearman with DESWC within school texts:')
print(pd.Series({c:stats.spearmanr(S[c],S.DESWC)[0] for c in idx}).round(2).sort_values().to_string())
