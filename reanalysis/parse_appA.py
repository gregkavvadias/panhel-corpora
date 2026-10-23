import sys, pdfplumber, re, pandas as pd
rows={}; header=None; blocks=[]
with pdfplumber.open(sys.argv[1]) as p:
    lines=[]
    for i in range(66,74): lines+= (p.pages[i].extract_text() or '').split('\n')
for ln in lines:
    if ln.startswith('TextID'): header=ln.split()[1:]; continue
    m=re.match(r'\\Texts\\(.+?)\\(.+?)\.txt\s+(.*)',ln)
    if m and header:
        vals=[float(v) for v in m.group(3).split()]
        assert len(vals)==len(header),(ln,header)
        key=(m.group(1),m.group(2))
        rows.setdefault(key,{}).update(dict(zip(header,vals)))
df=pd.DataFrame.from_dict(rows,orient='index'); df.index.names=['book','text']
df=df.reset_index(); print(df.shape); print(df.isna().sum().sum()); print(df.columns.tolist())
df.to_csv('data/cohmetrix_appA.csv',index=False)
