import spacy, pyphen, glob, os, numpy as np, pandas as pd
from wordfreq import top_n_list, zipf_frequency
from lexical_diversity import lex_div as ld
nlp=spacy.load('en_core_web_sm'); DIC=pyphen.Pyphen(lang='en_US')
def syl(w): return max(1,len(DIC.positions(w))+1)
TOP={n:set(top_n_list('en',n)) for n in (2000,3000,5000)}
def feats(doc):
    sents=[s for s in doc.sents if any(t.is_alpha for t in s)]
    toks=[t for t in doc if t.is_alpha]
    words=[t.lower_ for t in toks]
    nonprop=[t for t in toks if t.pos_!='PROPN']
    cov={f'cov{n//1000}k':np.mean([(t.lower_ in TOP[n]) or (t.lemma_.lower() in TOP[n]) for t in nonprop]) for n in TOP}
    content=[t for t in nonprop if t.pos_ in('NOUN','VERB','ADJ','ADV')]
    text=doc.text
    return dict(n_words=len(toks),mean_sent_len=len(toks)/len(sents),
        noun_per_1k=1000*sum(t.pos_=='NOUN' for t in toks)/len(toks),
        passive_per_1k=1000*sum(t.dep_ in('nsubjpass','auxpass') and t.dep_=='auxpass' for t in doc)/len(toks),
        mtld=ld.mtld(words), FRE=206.835-1.015*len(toks)/len(sents)-84.6*np.mean([syl(w) for w in words]), FKGL=0.39*len(toks)/len(sents)+11.8*np.mean([syl(w) for w in words])-15.59,
        content_zipf_mean=np.mean([zipf_frequency(t.lemma_.lower(),'en') for t in content]),
        rare_content_pct=100*np.mean([zipf_frequency(t.lemma_.lower(),'en')<3.5 for t in content]), **cov)
def window(doc,n=360):
    out=[];c=0
    for s in doc.sents:
        out.append(s.text); c+=sum(t.is_alpha for t in s)
        if c>=n: break
    return ' '.join(out)
rows=[]
base=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','Texts')
for f in sorted(glob.glob(base+'/*/*.txt')):
    book=f.split('/')[-2]; txt=open(f,encoding='utf-8',errors='replace').read()
    doc=nlp(txt); r=dict(book=book,text=os.path.basename(f)[:-4],version='full',**feats(doc)); rows.append(r)
    if book!='Panhellenics': rows.append(dict(book=book,text=r['text'],version='first360',**feats(nlp(window(doc)))))
F=pd.DataFrame(rows); F.to_csv('results/own_features.csv',index=False); print(F.groupby(['book','version']).mean(numeric_only=True).T.round(3))
