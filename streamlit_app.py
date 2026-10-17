import math
from collections import defaultdict

import networkx as nx
import plotly.graph_objects as go
import streamlit as st
from streamlit_plotly_events import plotly_events

st.set_page_config(page_title="Hierholzer's Algorithm", page_icon="🔗", layout="wide")
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Prompt:wght@300;400;500;600;700&display=swap');
/* Force readable contrast regardless of Streamlit Cloud's selected theme. */
html, body, [class*="css"], [data-testid="stAppViewContainer"],
[data-testid="stMain"], [data-testid="stMarkdownContainer"],
[data-testid="stWidgetLabel"], .stMarkdown, .stText, p, label, li,
[data-testid="stCaptionContainer"] {
  font-family:'Prompt',sans-serif !important;
  color:#173746 !important;
}
.stApp, [data-testid="stAppViewContainer"] {
  background:linear-gradient(135deg,#f4f9fc,#edf7f7) !important;
}
[data-testid="stHeader"] {background:rgba(244,249,252,.96) !important;}
.hero{background:linear-gradient(120deg,#123b5a,#087e83);padding:1.35rem 1.6rem;border-radius:18px;color:#ffffff !important;margin-bottom:1rem}
.hero h1{color:#ffffff !important;margin:0;font-size:2rem}.hero p{color:#e7fffb !important;margin:.35rem 0 0}
.kpi{background:#ffffff;border:1px solid #dbe7ed;border-radius:14px;padding:.85rem 1rem}
.kpi-label{color:#526b78 !important;font-size:.85rem}.kpi-value{color:#123b5a !important;font-size:1.8rem;font-weight:700}
/* Inputs, radio options, dropdowns, and buttons */
input, textarea, [data-baseweb="select"], [data-baseweb="input"],
[data-baseweb="select"] *, [data-baseweb="input"] *,
[data-testid="stRadio"] *, [data-testid="stSelectbox"] *,
[data-testid="stButton"] button, [data-testid="stAlert"] *,
[data-testid="stInfo"] *, [data-testid="stSuccess"] *,
[data-testid="stError"] *, [data-testid="stWarning"] * {
  color:#173746 !important;
}
[data-testid="stButton"] button {
  background:#ffffff !important; border:1px solid #9ab5c1 !important;
  border-radius:9px !important; font-weight:500 !important;
}
div.stButton>button[kind="primary"] {
  background:#078b76 !important; border-color:#078b76 !important; color:#ffffff !important;
}
[data-testid="stAlert"] {background:#ffffff !important;border:1px solid #d3e1e8 !important;}
[data-testid="stSelectbox"] svg, [data-baseweb="select"] svg {fill:#173746 !important;}
</style>
<div class="hero"><h1>◉ Hierholzer's Algorithm</h1><p>เครื่องมือสร้างกราฟและหา Euler Path / Euler Circuit</p></div>
""", unsafe_allow_html=True)

LETTERS = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")

def sample_graph():
    g = nx.MultiGraph()
    g.add_nodes_from(list("ABCDEF"))
    g.add_edges_from([("A","B"),("A","C"),("B","C"),("B","D"),("B","E"),("C","D"),("C","E"),("D","E"),("D","F"),("E","F")])
    return g

def sample_positions():
    return {"A":(130,120),"B":(300,80),"C":(220,250),"D":(460,210),"E":(390,380),"F":(620,370)}

def invalidate():
    st.session_state.solution = None
    st.session_state.step = 0

def next_name(g):
    return next((x for x in LETTERS if x not in g), None)

def degree_map(g):
    return {n:g.degree(n) for n in g.nodes}

def check_euler(g):
    if g.number_of_edges() == 0:
        return False, "เพิ่มเส้นเชื่อมอย่างน้อย 1 เส้นก่อน", []
    active = [n for n in g.nodes if g.degree(n) > 0]
    if not nx.is_connected(g.subgraph(active)):
        return False, "กราฟส่วนที่มีเส้นเชื่อมไม่เชื่อมต่อกัน", []
    odd = [n for n,d in degree_map(g).items() if d % 2]
    if len(odd) == 0:
        return True, "มี Euler Circuit (วงจรออยเลอร์)", odd
    if len(odd) == 2:
        return True, "มี Euler Path (เส้นทางออยเลอร์แบบเปิด)", odd
    return False, f"ไม่มี Euler Path / Circuit: มีจุดดีกรีคี่ {len(odd)} จุด", odd

def hierholzer(g, start):
    adj = defaultdict(list)
    edge_id = 0
    for u,v,k in g.edges(keys=True):
        adj[u].append((v,edge_id)); adj[v].append((u,edge_id)); edge_id += 1
    used=set(); stack=[start]; route=[]; actions=[]
    while stack:
        u=stack[-1]
        nxt=next(((v,eid) for v,eid in adj[u] if eid not in used),None)
        if nxt:
            v,eid=nxt; used.add(eid); stack.append(v); actions.append(f"เลือกเส้น {u} — {v} แล้วเดินไปยัง {v}")
        else:
            x=stack.pop(); route.append(x); actions.append(f"ไม่มีเส้นที่เหลือจาก {x} จึงนำ {x} เข้าลำดับคำตอบ")
    route.reverse()
    return {"path":route,"actions":actions,"circuit":len(route)>1 and route[0]==route[-1]} if len(used)==g.number_of_edges() else None

def make_chart(g, positions, selected_node, odd_nodes):
    fig = go.Figure()
    # Transparent grid markers make blank-area clicks detectable by Plotly.
    gx = list(range(0, 801, 12)); gy = list(range(0, 501, 12))
    fig.add_trace(go.Scatter(
        x=[x for x in gx for _ in gy], y=[y for _ in gx for y in gy],
        mode="markers", marker=dict(size=16, color="rgba(255,255,255,0.01)"),
        customdata=["__canvas__"]*(len(gx)*len(gy)), hoverinfo="skip", showlegend=False
    ))
    counts={}; offsets={}
    for u,v,k in g.edges(keys=True):
        pair=tuple(sorted((u,v))); idx=counts.get(pair,0); counts[pair]=idx+1; offsets[(u,v,k)]=idx
    for u,v,k in g.edges(keys=True):
        x1,y1=positions[u]; x2,y2=positions[v]
        pair=tuple(sorted((u,v))); total=counts[pair]; idx=offsets[(u,v,k)]
        dx=x2-x1; dy=y2-y1; length=max(math.hypot(dx,dy),1)
        off=(idx-(total-1)/2)*10; ox=-dy/length*off; oy=dx/length*off
        fig.add_trace(go.Scatter(x=[x1+ox,x2+ox],y=[y1+oy,y2+oy],mode="lines",
            line=dict(color="#506a79",width=2.5),hoverinfo="text",text=[f"{u} — {v}"]*2,showlegend=False))
    nodes=list(g.nodes)
    if nodes:
        colors=["#f8b56b" if n in odd_nodes else "#ffca77" if n==selected_node else "#8ed3f0" for n in nodes]
        fig.add_trace(go.Scatter(x=[positions[n][0] for n in nodes],y=[positions[n][1] for n in nodes],
            mode="markers+text",text=nodes,textposition="middle center",
            textfont=dict(size=16,color="#12333f",family="Arial Black"),
            marker=dict(size=42,color=colors,line=dict(color="#176e8c",width=2)),
            customdata=nodes,hovertemplate="จุดยอด %{customdata}<extra></extra>",showlegend=False))
    fig.update_layout(height=500,margin=dict(l=8,r=8,t=8,b=8),paper_bgcolor="white",plot_bgcolor="#f8fcfd",
        xaxis=dict(range=[0,800],visible=False,fixedrange=True),yaxis=dict(range=[0,510],visible=False,fixedrange=True,scaleanchor="x",scaleratio=1),
        clickmode="event+select",dragmode=False,showlegend=False)
    return fig

if "G" not in st.session_state: st.session_state.G=sample_graph()
if "positions" not in st.session_state: st.session_state.positions=sample_positions()
for key, value in [("start","A"),("solution",None),("step",0),("mode","เพิ่มจุดยอด"),("edge_first",None),("chart_version",0)]:
    if key not in st.session_state: st.session_state[key]=value
G=st.session_state.G
positions=st.session_state.positions

st.markdown("### ตัวแก้ไขกราฟ")
st.caption("โหมดเพิ่มจุดยอด: คลิกพื้นที่ว่าง · โหมดสร้างเส้นเชื่อม: คลิกจุดยอด 2 จุดตามลำดับ")
buttons=st.columns([1.3,1,1,1])
with buttons[0]:
    st.radio("โหมดการแก้ไข",["เพิ่มจุดยอด","สร้างเส้นเชื่อม"],horizontal=True,key="mode",label_visibility="collapsed")
with buttons[1]:
    if st.button("ล้างกราฟ",use_container_width=True):
        G.clear(); positions.clear(); st.session_state.start=""; st.session_state.edge_first=None; st.session_state.chart_version+=1; invalidate(); st.rerun()
with buttons[2]:
    if st.button("โหลดตัวอย่าง",use_container_width=True):
        st.session_state.G=sample_graph(); st.session_state.positions=sample_positions(); st.session_state.start="A"; st.session_state.edge_first=None; st.session_state.chart_version+=1; invalidate(); st.rerun()
with buttons[3]:
    if st.button("ยกเลิกเลือกจุด",use_container_width=True):
        st.session_state.edge_first=None; st.session_state.chart_version+=1; st.rerun()

left,right=st.columns([1.45,1],gap="large")
with left:
    st.markdown("### แผนภาพกราฟ")
    odd_now=[n for n,d in degree_map(G).items() if d%2]
    if st.session_state.mode=="สร้างเส้นเชื่อม":
        st.info(f"เลือกจุดแรกแล้ว: {st.session_state.edge_first} — คลิกจุดยอดที่สอง" if st.session_state.edge_first else "คลิกจุดยอดแรก แล้วคลิกจุดยอดที่สอง")
    else:
        st.info("คลิกพื้นที่ว่างเพื่อเพิ่มจุดยอดใหม่ ชื่อเรียง A, B, C, …, Z")
    events=plotly_events(make_chart(G,positions,st.session_state.edge_first,odd_now),click_event=True,select_event=False,hover_event=False,key=f"graph_click_{st.session_state.chart_version}",override_height=500)
    if events:
        ev=events[-1]
        node=ev.get("customdata")
        if isinstance(node,(list,tuple)): node=node[0] if node else None
        if st.session_state.mode=="เพิ่มจุดยอด":
            if node in G:
                st.warning(f"จุด {node} มีอยู่แล้ว คลิกพื้นที่ว่างเพื่อเพิ่มจุดยอด")
            else:
                name=next_name(G)
                if name is None:
                    st.warning("เพิ่มได้สูงสุด 26 จุดยอด ตั้งแต่ A ถึง Z")
                else:
                    x=float(ev.get("x",400)); y=float(ev.get("y",250))
                    G.add_node(name); positions[name]=(max(25,min(775,x)),max(25,min(485,y)))
                    if not st.session_state.start: st.session_state.start=name
                    st.session_state.edge_first=None; st.session_state.chart_version+=1; invalidate(); st.rerun()
        else:
            if node not in G:
                st.warning("โหมดสร้างเส้นเชื่อม: คลิกบนจุดยอดที่มีอยู่")
            elif st.session_state.edge_first is None:
                st.session_state.edge_first=node; st.session_state.chart_version+=1; st.rerun()
            elif node==st.session_state.edge_first:
                st.warning("เลือกจุดยอดคนละจุด (ไม่รองรับ self-loop)")
            else:
                G.add_edge(st.session_state.edge_first,node); st.session_state.edge_first=None
                st.session_state.chart_version+=1; invalidate(); st.rerun()
    st.caption("สีฟ้า = จุดยอดทั่วไป · สีส้ม = จุดดีกรีคี่ · สีเหลือง = จุดที่เลือก")
    if G.number_of_edges():
        edges=list(G.edges(keys=True)); labels=[f"{u} — {v} (เส้น {i+1})" for i,(u,v,k) in enumerate(edges)]
        chosen=st.selectbox("เส้นเชื่อมที่จะลบ",labels,key="edge_to_delete")
        if st.button("ลบเส้นที่เลือก"):
            u,v,k=edges[labels.index(chosen)]; G.remove_edge(u,v,k); invalidate(); st.session_state.chart_version+=1; st.rerun()
    if G.nodes:
        node_delete=st.selectbox("จุดยอดที่จะลบ",list(G.nodes),key="node_to_delete")
        if st.button("ลบจุดยอดที่เลือก"):
            G.remove_node(node_delete); positions.pop(node_delete,None)
            if st.session_state.start not in G: st.session_state.start=next(iter(G.nodes),"")
            st.session_state.edge_first=None; invalidate(); st.session_state.chart_version+=1; st.rerun()

with right:
    deg=degree_map(G); odd=[n for n,d in deg.items() if d%2]
    st.markdown("### ข้อมูลกราฟ"); k1,k2,k3=st.columns(3)
    for col,label,value in [(k1,"จุดยอด",G.number_of_nodes()),(k2,"เส้นเชื่อม",G.number_of_edges()),(k3,"ดีกรีคี่",len(odd))]:
        with col: st.markdown(f'<div class="kpi"><div class="kpi-label">{label}</div><div class="kpi-value">{value}</div></div>',unsafe_allow_html=True)
    st.markdown("#### ดีกรีของแต่ละจุดยอด")
    for n,d in deg.items(): st.write(f"{'🟠' if d%2 else '🔵'} **{n}** — ดีกรี {d} ({'คี่' if d%2 else 'คู่'})")
    ok,msg,odd=check_euler(G)
    if ok:
        st.success(msg); st.caption(f"จุดดีกรีคี่: {', '.join(odd)}" if odd else "ทุกจุดมีดีกรีคู่")
    else: st.error(msg)
    if G.nodes:
        choices=list(G.nodes); current=st.session_state.start if st.session_state.start in choices else choices[0]
        start=st.selectbox("จุดเริ่มต้น",choices,index=choices.index(current),key="start_select"); st.session_state.start=start
        if st.button("▶ หาเส้นทางด้วย Hierholzer",type="primary",use_container_width=True):
            ok,msg,odd=check_euler(G); active=[n for n in G.nodes if G.degree(n)>0]
            if not ok: st.session_state.solution=None; st.warning(msg)
            elif start not in active: st.session_state.solution=None; st.warning("เลือกจุดเริ่มต้นที่มีเส้นเชื่อม")
            elif len(odd)==2 and start not in odd: st.session_state.solution=None; st.warning(f"กราฟนี้ต้องเริ่มจาก {odd[0]} หรือ {odd[1]}")
            else: st.session_state.solution=hierholzer(G,start); st.session_state.step=0; st.rerun()

st.divider(); st.markdown("### ขั้นตอนการทำงานของ Hierholzer's Algorithm")
sol=st.session_state.solution
if sol:
    actions=sol["actions"]; total=len(actions); st.progress(st.session_state.step/max(total,1)); c=st.columns(4)
    with c[0]:
        if st.button("← ก่อนหน้า",disabled=st.session_state.step==0): st.session_state.step-=1; st.rerun()
    with c[1]:
        if st.button("ขั้นถัดไป →",disabled=st.session_state.step>=total): st.session_state.step+=1; st.rerun()
    with c[2]:
        if st.button("แสดงทั้งหมด"): st.session_state.step=total; st.rerun()
    with c[3]: st.caption(f"{st.session_state.step} / {total} ขั้นตอน")
    if st.session_state.step:
        st.info(f"ขั้นที่ {st.session_state.step}: {actions[st.session_state.step-1]}")
        for i,text in enumerate(actions[:st.session_state.step],1): st.write(f"{i}. {text}")
    else: st.info("กดขั้นถัดไปเพื่อเริ่มดูการทำงานทีละขั้น")
    if st.session_state.step==total:
        st.markdown("#### ผลลัพธ์สุดท้าย"); st.success("Euler Circuit — วงจรออยเลอร์" if sol["circuit"] else "Euler Path — เส้นทางออยเลอร์")
        st.code(" → ".join(sol["path"]),language=None); st.caption(f"เส้นเชื่อมที่ใช้ทั้งหมด: {G.number_of_edges()} เส้น")
else: st.info("เมื่อกราฟผ่านเงื่อนไขแล้ว กดปุ่มหาเส้นทางเพื่อแสดงคำตอบและขั้นตอน")
st.markdown('<div style="text-align:center;color:#6b818c;font-size:.8rem;padding:1rem">Undirected Multigraph · ชื่อจุดยอด A–Z · รองรับเส้นเชื่อมซ้ำ · ไม่รองรับ self-loop</div>',unsafe_allow_html=True)
