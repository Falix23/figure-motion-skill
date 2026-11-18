import os
os.environ['CUDA_VISIBLE_DEVICES']=''
import numpy as np,json
from pathlib import Path
X=np.eye(3)
Wq=np.array([[0.,1.],[2**.5,0.],[1.,1.]])
Wk=np.column_stack([np.log([.2,.5,.3]),np.zeros(3)])
Wv=np.array([[1.,0.],[0.,1.],[1.,1.]])
Q,K,V=X@Wq,X@Wk,X@Wv
scores=Q[1]@K.T/np.sqrt(2)
w=np.exp(scores-scores.max());w/=w.sum()
out=w@V
assert np.allclose(w,[.2,.5,.3]) and np.allclose(out,[.5,.8])
Path(__file__).with_name('toy_attention.json').write_text(json.dumps({'note':'教学构造的单头二维算例，不代表真实模型或因果解释','tokens':['我','爱','你'],'selected_query_position':1,'Q':Q.tolist(),'K':K.tolist(),'V':V.tolist(),'scores':scores.tolist(),'weights':w.tolist(),'output':out.tolist()},ensure_ascii=False,indent=2))
print('教学注意力：',w.tolist(),'→',out.tolist())
