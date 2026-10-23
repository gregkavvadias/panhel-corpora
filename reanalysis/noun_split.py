# Splits noun density into common (NOUN) vs proper (PROPN) nouns and relates each to RDL2
import spacy, glob, os, pandas as pd
from scipy import stats
nlp=spacy.load('en_core_web_sm'); rows=[]
base=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','Texts')
for f in sorted(glob.glob(base+'/*/*.txt')):
    d=nlp(open(f,encoding='utf-8',errors='replace').read()); t=[x for x in d if x.is_alpha]
    rows.append(dict(book=f.split('/')[-2],text=os.path.basename(f)[:-4],
        common=1000*sum(x.pos_=='NOUN' for x in t)/len(t),proper=1000*sum(x.pos_=='PROPN' for x in t)/len(t)))
M=pd.read_csv('data/cohmetrix_appA.csv').merge(pd.DataFrame(rows)); M.to_csv('results/nouns_split.csv',index=False)
M['exam']=M.book=='Panhellenics'
for e,d in M.groupby('exam'):
    print('exam' if e else 'school','common',round(d.common.mean(),1),'proper',round(d.proper.mean(),1))
    for c in ['WRDNOUN','common','proper']:
        r,p=stats.pearsonr(d[c],d.RDL2); print(f'   r(RDL2,{c})={r:.2f} p={p:.3f}')
print('Mann-Whitney proper p',stats.mannwhitneyu(M[M.exam].proper,M[~M.exam].proper).pvalue,'common p',stats.mannwhitneyu(M[M.exam].common,M[~M.exam].common).pvalue)
