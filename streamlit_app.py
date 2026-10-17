import streamlit as st
import networkx as nx
import plotly.graph_objects as go
from streamlit_plotly_events import plotly_events
from collections import defaultdict
import math

st.set_page_config(page_title="Hierholzer Algorithm Lab", page_icon="🔗", layout="wide")
st.markdown("""<style>@import url('https://fonts.googleapis.com/css2?family=Prompt:wght@300;400;500;600;700&display=swap');html,body,[class*="css"]{font-family:'Prompt',sans-serif}.stApp{background:linear-gradient(135deg,#f5f8fc,#edf7f6)}.hero{padding:1.3rem 1.5rem;border-radius:18px;color:white;background:linear-gradient(115deg,#173a5e,#087e83);margin-bottom:1rem}.hero h1{color:white;margin:0}.hero p{color:#d9f4f1;margin:.4rem 0 0}.metric{background:white;border:1px solid #dce7ec;border-radius:14px;padding:.8rem 1rem}.metric-label{color:#617985;font-size:.85rem}.metric-value{color:#173a5e;font-size:1.7rem;font-weight:700}</style><div class="hero"><h1>🔗 Hierholzer Algorithm Lab</h1><p>คลิกสร้างจุดยอด เชื่อมจุดด้วยการคลิก และตรวจสอบ Euler Path / Euler Circuit</p></div>""",unsafe_allow_html=True)
LETTERS=list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
def sample():
 g=nx.MultiGraph(); g.add_nodes_from("ABCDEF"); g.add_edges_from([("A","B"),("A","C"),("B","C"),("B","D"),("B","E"),("C","D"),("C","E"),("D","E"),("D","F"),("E","F")]); return g
def samplepos(): return {"A":(170,100),"B":(360,80),"C":(250,250),"D":(510,230),"E":(430,400),"F":(650,390)}
def deg(g): return {n:g.degree(n) for n in g.nodes}
def status(g):
 if not g.number_of_edges(): return False,"เพิ่มเส้นเชื่อมอย่างน้อย 1 เส้นก่อน",[]
 active=[n for n in g if g.degree(n)>0]
 if not nx.is_connected(g.subgraph(active)): return False,"จุดยอดที่มีเส้นเชื่อมต้องอยู่ในส่วนกราฟที่เชื่อมต่อกัน",[]
 odd=[n for n,d in deg(g).items() if d%2]
 if len(odd)==0:return True,"กราฟนี้มี Euler Circuit",odd
 if len(odd)==2:return True,"กราฟนี้มี Euler Path แบบเปิด",odd
 return False,f"ไม่มี Euler Path / Circuit เพราะมีจุดดีกรีคี่ {len(odd)} จุด",odd
def solve(g,start):
 adj=defaultdict(list); eid=0
 for u,v,k in g.edges(keys=True): adj[u].append((v,eid)); adj[v].append((u,eid)); eid+=1
 used=set(); stack=[start]; route=[]; actions=[]
 while stack:
  cur=stack[-1]; item=next(((v,e) for v,e in adj[cur] if e not in used),None)
  if item:
   v,e=item; used.add(e); stack.append(v); actions.append(f"ใช้เส้นเชื่อมจาก {cur} ไป {v}")
  else:
   x=stack.pop(); route.append(x); actions.append(f"ไม่มีเส้นเชื่อมที่เหลือจาก {x} จึงเพิ่มจุดนี้เข้าคำตอบ")
 route.reverse()
 if len(used)!=g.number_of_edges(): return None
 return {"path":route,"actions":actions,"circuit":len(route)>1 and route[0]==route[-1]}
def reset(): st.session_state.solution=None; st.session_state.step=0
def nextname(g): return next((x for x in LETTERS if x not in g),None)
def chart(g,pos,selected,odd):
 fig=go.Figure(); counts={}; seen={}
 # Nearly invisible hit-target grid makes blank-canvas clicks register in Plotly.
 gx=list(range(0,801,16)); gy=list(range(0,521,16))
 fig.add_trace(go.Scatter(x=[x for x in gx for y in gy],y=[y for x in gx for y in gy],
  mode="markers",marker=dict(size=18,color="rgba(255,255,255,0.01)"),
  customdata=["__canvas__"]*(len(gx)*len(gy)),hoverinfo="skip",showlegend=False))
 for u,v,k in g.edges(keys=True):
  pair=tuple(sorted((u,v))); idx=counts.get(pair,0); counts[pair]=idx+1; seen[(u,v,k)]=idx
 for u,v,k in g.edges(keys=True):
  x1,y1=pos[u]; x2,y2=pos[v]; pair=tuple(sorted((u,v))); total=counts[pair]; idx=seen[(u,v,k)]; dx=x2-x1;dy=y2-y1;length=max(math.hypot(dx,dy),1); off=(idx-(total-1)/2)*9; ox=-dy/length*off;oy=dx/length*off
  fig.add_trace(go.Scatter(x=[x1+ox,x2+ox],y=[y1+oy,y2+oy],mode="lines",line=dict(color="#708794",width=3),hoverinfo="text",text=[f"{u} — {v}"]*2,showlegend=False))
 ns=list(g.nodes)
 if ns:
  colors=["#ffb45e" if n==selected else "#f7a6a6" if n in odd else "#77d9c5" for n in ns]
  fig.add_trace(go.Scatter(x=[pos[n][0] for n in ns],y=[pos[n][1] for n in ns],mode="markers+text",text=ns,textposition="middle center",textfont=dict(size=17,color="#173a4a",family="Arial Black"),marker=dict(size=42,color=colors,line=dict(color="#176e8c",width=2)),customdata=ns,hovertemplate="จุดยอด %{customdata}<extra></extra>",showlegend=False))
 fig.update_layout(height=520,margin=dict(l=10,r=10,t=10,b=10),paper_bgcolor="white",plot_bgcolor="#f8fcfd",xaxis=dict(range=[0,800],visible=False,fixedrange=True),yaxis=dict(range=[0,530],visible=False,fixedrange=True,scaleanchor="x",scaleratio=1),clickmode="event+select",dragmode=False,showlegend=False)
 return fig
if "graph" not in st.session_state: st.session_state.graph=sample()
if "positions" not in st.session_state: st.session_state.positions=samplepos()
for key,val in [("start_vertex","A"),("solution",None),("step",0),("edge_first",None),("canvas_key",0)]:
 if key not in st.session_state: st.session_state[key]=val
g=st.session_state.graph; pos=st.session_state.positions
st.markdown("### ตัวแก้ไขกราฟ")
st.caption("โหมดเพิ่มจุดยอด: คลิกพื้นที่ว่าง · โหมดสร้างเส้นเชื่อม: คลิกจุดยอด 2 จุดตามลำดับ")
c=st.columns([1.5,1,1,1])
with c[0]: mode=st.radio("โหมด",["เพิ่มจุดยอด","สร้างเส้นเชื่อม"],horizontal=True,key="mode",label_visibility="collapsed")
with c[1]:
 if st.button("ล้างกราฟ",use_container_width=True):
  st.session_state.graph=nx.MultiGraph();st.session_state.positions={};st.session_state.start_vertex="";st.session_state.edge_first=None;st.session_state.canvas_key+=1;reset();st.rerun()
with c[2]:
 if st.button("โหลดกราฟตัวอย่าง",use_container_width=True):
  st.session_state.graph=sample();st.session_state.positions=samplepos();st.session_state.start_vertex="A";st.session_state.edge_first=None;st.session_state.canvas_key+=1;reset();st.rerun()
with c[3]:
 if st.button("ยกเลิกเลือกจุด",use_container_width=True): st.session_state.edge_first=None;st.session_state.canvas_key+=1;st.rerun()
left,right=st.columns([1.4,1],gap="large")
with left:
 st.markdown("### แผนภาพกราฟ")
 odd_now=[n for n,d in deg(g).items() if d%2]
 if mode=="สร้างเส้นเชื่อม": st.info(f"เลือกจุดแรกแล้ว: {st.session_state.edge_first} — คลิกจุดยอดที่สอง" if st.session_state.edge_first else "คลิกจุดยอดแรก แล้วคลิกจุดยอดที่สอง")
 else: st.info("คลิกพื้นที่ว่างเพื่อเพิ่มจุดยอดใหม่ ชื่อจะเรียง A, B, C, …, Z")
 events=plotly_events(chart(g,pos,st.session_state.edge_first,odd_now),click_event=True,select_event=False,hover_event=False,key=f"graph_{st.session_state.canvas_key}",override_height=520)
 if events:
  ev=events[-1]; node=ev.get("customdata")
  if isinstance(node,(list,tuple)): node=node[0] if node else None
  if mode=="เพิ่มจุดยอด":
   if node in g: st.warning(f"จุด {node} มีอยู่แล้ว คลิกพื้นที่ว่างเพื่อเพิ่มจุดใหม่")
   else:
    name=nextname(g)
    if name is None: st.warning("เพิ่มได้สูงสุด 26 จุดยอด ตั้งแต่ A ถึง Z")
    else:
     g.add_node(name);pos[name]=(max(25,min(775,float(ev.get("x",400)))),max(25,min(505,float(ev.get("y",265)))))
     if not st.session_state.start_vertex: st.session_state.start_vertex=name
     reset();st.session_state.canvas_key+=1;st.rerun()
  else:
   if node not in g: st.warning("โหมดสร้างเส้นเชื่อม: คลิกบนจุดยอดที่มีอยู่")
   elif st.session_state.edge_first is None: st.session_state.edge_first=node;st.session_state.canvas_key+=1;st.rerun()
   elif node==st.session_state.edge_first: st.warning("เลือกจุดยอดคนละจุด (ไม่รองรับ self-loop)")
   else:
    g.add_edge(st.session_state.edge_first,node);st.session_state.edge_first=None;reset();st.session_state.canvas_key+=1;st.rerun()
 st.caption("เขียว = จุดปกติ · ส้ม = จุดที่เลือก · แดง = จุดดีกรีคี่")
 if g.number_of_edges():
  edges=list(g.edges(keys=True)); labels=[f"{u} — {v} (เส้นที่ {i+1})" for i,(u,v,k) in enumerate(edges)]; selected=st.selectbox("เลือกเส้นเชื่อมเพื่อลบ",labels,key="delete_edge")
  if st.button("ลบเส้นที่เลือก"):
   u,v,k=edges[labels.index(selected)];g.remove_edge(u,v,k);reset();st.session_state.canvas_key+=1;st.rerun()
 if g.nodes:
  dn=st.selectbox("เลือกจุดยอดเพื่อลบ",list(g.nodes),key="delete_node")
  if st.button("ลบจุดยอดที่เลือก"):
   g.remove_node(dn);pos.pop(dn,None)
   if st.session_state.start_vertex not in g: st.session_state.start_vertex=next(iter(g.nodes),"")
   st.session_state.edge_first=None;reset();st.session_state.canvas_key+=1;st.rerun()
with right:
 st.markdown("### สรุปกราฟ"); dm=deg(g); odd=[n for n,d in dm.items() if d%2]; metrics=st.columns(3)
 for col,label,value in [(metrics[0],"จุดยอด",g.number_of_nodes()),(metrics[1],"เส้นเชื่อม",g.number_of_edges()),(metrics[2],"ดีกรีคี่",len(odd))]:
  with col: st.markdown(f'<div class="metric"><div class="metric-label">{label}</div><div class="metric-value">{value}</div></div>',unsafe_allow_html=True)
 st.markdown("#### ดีกรีของจุดยอด")
 for n,d in dm.items(): st.write(f"{'🟠' if d%2 else '🔵'} **{n}** — ดีกรี {d} ({'คี่' if d%2 else 'คู่'})")
 valid,msg,odd_nodes=status(g)
 if valid: st.success(msg);st.caption(f"จุดดีกรีคี่: {', '.join(odd_nodes)}" if odd_nodes else "ทุกจุดมีดีกรีคู่")
 else: st.warning(msg)
 if g.nodes:
  opts=list(g.nodes); default=st.session_state.start_vertex if st.session_state.start_vertex in opts else opts[0]; start=st.selectbox("จุดเริ่มต้น",opts,index=opts.index(default),key="start_select");st.session_state.start_vertex=start
  if st.button("▶ คำนวณด้วย Hierholzer",type="primary",use_container_width=True):
   valid,msg,odd_nodes=status(g); active=[n for n in g if g.degree(n)>0]
   if not valid: st.session_state.solution=None;st.error(msg)
   elif start not in active: st.session_state.solution=None;st.error("เลือกจุดเริ่มต้นที่มีเส้นเชื่อม")
   elif len(odd_nodes)==2 and start not in odd_nodes: st.session_state.solution=None;st.error(f"กราฟนี้ต้องเริ่มจาก {odd_nodes[0]} หรือ {odd_nodes[1]}")
   else: st.session_state.solution=solve(g,start);st.session_state.step=0;st.rerun()
st.divider();st.markdown("### ขั้นตอนการทำงานของอัลกอริทึม"); sol=st.session_state.solution
if sol:
 actions=sol["actions"];total=len(actions);current=st.session_state.step;st.progress(min(current/max(total,1),1.0));cols=st.columns(4)
 with cols[0]:
  if st.button("← ก่อนหน้า",disabled=current<=0,use_container_width=True):st.session_state.step-=1;st.rerun()
 with cols[1]:
  if st.button("ขั้นถัดไป →",disabled=current>=total,use_container_width=True):st.session_state.step+=1;st.rerun()
 with cols[2]:
  if st.button("แสดงทุกขั้น",use_container_width=True):st.session_state.step=total;st.rerun()
 with cols[3]:st.caption(f"ขั้นที่ {current} จาก {total}")
 if current==0:st.info("กด ‘ขั้นถัดไป’ เพื่อดูทีละขั้น")
 else:
  st.info(f"ขั้นที่ {current}: {actions[current-1]}")
  with st.expander("ดูขั้นตอนก่อนหน้าทั้งหมด",expanded=True):
   for i,a in enumerate(actions[:current],1):st.write(f"{i}. {a}")
 if current==total:
  st.markdown("#### เส้นทางคำตอบ");st.success("Euler Circuit — วงจรออยเลอร์" if sol["circuit"] else "Euler Path — เส้นทางออยเลอร์");st.code(" → ".join(sol["path"]),language=None);st.caption(f"จำนวนเส้นเชื่อมที่ใช้: {g.number_of_edges()}")
else: st.info("เมื่อกราฟผ่านเงื่อนไขแล้ว กด ‘คำนวณด้วย Hierholzer’ เพื่อดูคำตอบ")
st.markdown("<div style='text-align:center;color:#6b818c;font-size:.8rem;padding:1rem'>ชื่อจุดยอดเรียง A–Z · รองรับเส้นเชื่อมซ้ำ · ไม่รองรับ self-loop</div>",unsafe_allow_html=True)
