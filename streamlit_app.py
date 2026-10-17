import streamlit as st
import networkx as nx
import matplotlib.pyplot as plt
from collections import defaultdict

st.set_page_config(page_title="Hierholzer Algorithm Lab", page_icon="🔗", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Prompt:wght@300;400;500;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Prompt', sans-serif; }
.stApp { background: linear-gradient(135deg, #f5f8fc 0%, #edf7f6 100%); }
.hero { padding: 1.4rem 1.6rem; border-radius: 18px; color: #fff; background: linear-gradient(115deg,#173a5e,#087e83); margin-bottom: 1rem; }
.hero h1 { color: white; margin: 0; font-size: 2rem; }
.hero p { color: #d9f4f1; margin: .4rem 0 0; }
.metric { background: white; border: 1px solid #dce7ec; border-radius: 14px; padding: .8rem 1rem; }
.metric-label { color: #617985; font-size: .85rem; }
.metric-value { color: #173a5e; font-size: 1.7rem; font-weight: 700; }
div.stButton > button[kind="primary"] { background: #087e73; border-color: #087e73; }
</style>
<div class="hero"><h1>🔗 Hierholzer Algorithm Lab</h1><p>สร้างกราฟ ตรวจสอบ และหา Euler Path / Euler Circuit ทีละขั้นตอน</p></div>
""", unsafe_allow_html=True)


def make_sample_graph():
    graph = nx.MultiGraph()
    graph.add_nodes_from([f"V{i}" for i in range(1, 7)])
    edges = [("V1", "V2"), ("V1", "V3"), ("V2", "V3"), ("V2", "V4"),
             ("V2", "V5"), ("V3", "V4"), ("V3", "V5"), ("V4", "V5"),
             ("V4", "V6"), ("V5", "V6")]
    graph.add_edges_from(edges)
    return graph


def get_degree_map(graph):
    return {node: graph.degree(node) for node in graph.nodes}


def euler_status(graph):
    if graph.number_of_edges() == 0:
        return False, "เพิ่มเส้นเชื่อมอย่างน้อย 1 เส้นก่อน", []
    active_nodes = [node for node in graph.nodes if graph.degree(node) > 0]
    if not active_nodes or not nx.is_connected(graph.subgraph(active_nodes)):
        return False, "จุดยอดที่มีเส้นเชื่อมต้องอยู่ในส่วนกราฟที่เชื่อมต่อกัน", []
    odd_nodes = [node for node, degree in get_degree_map(graph).items() if degree % 2]
    if len(odd_nodes) == 0:
        return True, "กราฟนี้มี Euler Circuit", odd_nodes
    if len(odd_nodes) == 2:
        return True, "กราฟนี้มี Euler Path แบบเปิด", odd_nodes
    return False, f"ไม่มี Euler Path / Circuit เพราะมีจุดดีกรีคี่ {len(odd_nodes)} จุด", odd_nodes


def run_hierholzer(graph, start_node):
    # Use a unique edge ID so parallel edges are handled correctly.
    adjacency = defaultdict(list)
    edge_id = 0
    for u, v, _key in graph.edges(keys=True):
        adjacency[u].append((v, edge_id))
        adjacency[v].append((u, edge_id))
        edge_id += 1

    used_edges = set()
    stack = [start_node]
    route = []
    actions = []
    while stack:
        current = stack[-1]
        available = next(((neighbor, eid) for neighbor, eid in adjacency[current]
                          if eid not in used_edges), None)
        if available is not None:
            neighbor, eid = available
            used_edges.add(eid)
            stack.append(neighbor)
            actions.append(f"ใช้เส้นเชื่อมจาก {current} ไป {neighbor}")
        else:
            popped = stack.pop()
            route.append(popped)
            actions.append(f"ไม่มีเส้นเชื่อมที่เหลือจาก {popped} จึงเพิ่มจุดนี้เข้าคำตอบ")

    route.reverse()
    if len(used_edges) != graph.number_of_edges():
        return None
    return {
        "path": route,
        "actions": actions,
        "circuit": len(route) > 1 and route[0] == route[-1],
    }


def reset_solution():
    st.session_state.solution = None
    st.session_state.step = 0


if "graph" not in st.session_state:
    st.session_state.graph = make_sample_graph()
if "next_vertex_id" not in st.session_state:
    st.session_state.next_vertex_id = 7
if "start_vertex" not in st.session_state:
    st.session_state.start_vertex = "V1"
if "solution" not in st.session_state:
    st.session_state.solution = None
if "step" not in st.session_state:
    st.session_state.step = 0

graph = st.session_state.graph

st.markdown("### ตัวแก้ไขกราฟ")
actions_col = st.columns(4)
with actions_col[0]:
    if st.button("＋ เพิ่มจุดยอด", use_container_width=True):
        name = f"V{st.session_state.next_vertex_id}"
        while name in graph:
            st.session_state.next_vertex_id += 1
            name = f"V{st.session_state.next_vertex_id}"
        graph.add_node(name)
        st.session_state.next_vertex_id += 1
        reset_solution()
        st.rerun()
with actions_col[1]:
    if st.button("ล้างกราฟ", use_container_width=True):
        graph.clear()
        st.session_state.start_vertex = ""
        reset_solution()
        st.rerun()
with actions_col[2]:
    if st.button("โหลดกราฟตัวอย่าง", use_container_width=True):
        st.session_state.graph = make_sample_graph()
        st.session_state.next_vertex_id = 7
        st.session_state.start_vertex = "V1"
        reset_solution()
        st.rerun()
with actions_col[3]:
    if st.button("เริ่มดูขั้นตอนใหม่", use_container_width=True):
        st.session_state.step = 0
        st.rerun()

left, right = st.columns([1.35, 1], gap="large")
with left:
    st.markdown("### แผนภาพกราฟ")
    if graph.number_of_nodes() > 0:
        fig, ax = plt.subplots(figsize=(8, 5))
        fig.patch.set_facecolor("white")
        ax.set_facecolor("#f8fcfd")
        positions = nx.spring_layout(graph, seed=19)
        degree_map = get_degree_map(graph)
        odd_nodes = {node for node, degree in degree_map.items() if degree % 2}
        node_colors = ["#ffbf80" if node in odd_nodes else
                       "#76d9c5" if node == st.session_state.start_vertex else "#8fd3f0"
                       for node in graph.nodes]
        nx.draw_networkx_edges(graph, positions, ax=ax, edge_color="#607986", width=2,
                               connectionstyle="arc3,rad=0.08")
        nx.draw_networkx_nodes(graph, positions, ax=ax, node_color=node_colors, node_size=1050,
                               edgecolors="#176e8c", linewidths=1.5)
        nx.draw_networkx_labels(graph, positions, ax=ax, font_size=10, font_weight="bold",
                                font_color="#173a4a")
        ax.set_axis_off()
        st.pyplot(fig, use_container_width=True)
        plt.close(fig)
    else:
        st.info("กราฟยังว่างอยู่ เพิ่มจุดยอดและเส้นเชื่อมเพื่อเริ่ม")

    st.markdown("#### จัดการเส้นเชื่อม")
    nodes = list(graph.nodes)
    if len(nodes) >= 2:
        add1, add2, add3 = st.columns([1, 1, 1])
        with add1:
            from_node = st.selectbox("จุดต้นทาง", nodes, key="edge_from")
        with add2:
            to_options = [node for node in nodes if node != from_node]
            to_node = st.selectbox("จุดปลายทาง", to_options, key="edge_to")
        with add3:
            st.write("")
            st.write("")
            if st.button("＋ เพิ่มเส้น", use_container_width=True):
                graph.add_edge(from_node, to_node)
                reset_solution()
                st.rerun()

        if graph.number_of_edges() > 0:
            edge_records = list(graph.edges(keys=True))
            edge_labels = [f"{u} — {v} (เส้นที่ {i + 1})" for i, (u, v, _key) in enumerate(edge_records)]
            selected_edge = st.selectbox("เลือกเส้นที่จะลบ", edge_labels, key="delete_edge_select")
            if st.button("ลบเส้นที่เลือก"):
                u, v, key = edge_records[edge_labels.index(selected_edge)]
                graph.remove_edge(u, v, key)
                reset_solution()
                st.rerun()
    elif nodes:
        st.caption("ต้องมีจุดยอดอย่างน้อย 2 จุดเพื่อเพิ่มเส้นเชื่อม")

    if nodes:
        node_to_remove = st.selectbox("เลือกจุดยอดที่จะลบ", nodes, key="delete_node_select")
        if st.button("ลบจุดยอดที่เลือก"):
            graph.remove_node(node_to_remove)
            if st.session_state.start_vertex not in graph:
                st.session_state.start_vertex = next(iter(graph.nodes), "")
            reset_solution()
            st.rerun()

with right:
    st.markdown("### สรุปกราฟ")
    degree_map = get_degree_map(graph)
    odd_nodes = [node for node, degree in degree_map.items() if degree % 2]
    metric_cols = st.columns(3)
    for col, label, value in [(metric_cols[0], "จุดยอด", graph.number_of_nodes()),
                              (metric_cols[1], "เส้นเชื่อม", graph.number_of_edges()),
                              (metric_cols[2], "ดีกรีคี่", len(odd_nodes))]:
        with col:
            st.markdown(f'<div class="metric"><div class="metric-label">{label}</div>'
                        f'<div class="metric-value">{value}</div></div>', unsafe_allow_html=True)

    st.markdown("#### ดีกรีของจุดยอด")
    if degree_map:
        for node, degree in degree_map.items():
            marker = "🟠" if degree % 2 else "🔵"
            st.write(f"{marker} **{node}** — ดีกรี {degree} ({'คี่' if degree % 2 else 'คู่'})")
    else:
        st.caption("ยังไม่มีจุดยอดในกราฟ")

    valid, status_message, odd_nodes = euler_status(graph)
    if valid:
        st.success(status_message)
        st.caption(f"จุดดีกรีคี่: {', '.join(odd_nodes)}" if odd_nodes else "ทุกจุดมีดีกรีคู่")
    else:
        st.warning(status_message)

    if graph.number_of_nodes() > 0:
        node_options = list(graph.nodes)
        default_start = st.session_state.start_vertex if st.session_state.start_vertex in node_options else node_options[0]
        start_node = st.selectbox("จุดเริ่มต้น", node_options,
                                  index=node_options.index(default_start), key="start_vertex_select")
        st.session_state.start_vertex = start_node
        if st.button("▶ คำนวณด้วย Hierholzer", type="primary", use_container_width=True):
            valid, status_message, odd_nodes = euler_status(graph)
            active_nodes = [node for node in graph.nodes if graph.degree(node) > 0]
            if not valid:
                st.session_state.solution = None
                st.error(status_message)
            elif start_node not in active_nodes:
                st.session_state.solution = None
                st.error("เลือกจุดเริ่มต้นที่มีเส้นเชื่อม")
            elif len(odd_nodes) == 2 and start_node not in odd_nodes:
                st.session_state.solution = None
                st.error(f"กราฟนี้ต้องเริ่มจาก {odd_nodes[0]} หรือ {odd_nodes[1]}")
            else:
                st.session_state.solution = run_hierholzer(graph, start_node)
                st.session_state.step = 0
                st.rerun()

st.divider()
st.markdown("### ขั้นตอนการทำงานของอัลกอริทึม")
solution = st.session_state.solution
if solution:
    all_actions = solution["actions"]
    total_steps = len(all_actions)
    current_step = st.session_state.step
    st.progress(min(current_step / max(total_steps, 1), 1.0))
    step_cols = st.columns(4)
    with step_cols[0]:
        if st.button("← ก่อนหน้า", disabled=current_step <= 0, use_container_width=True):
            st.session_state.step -= 1
            st.rerun()
    with step_cols[1]:
        if st.button("ขั้นถัดไป →", disabled=current_step >= total_steps, use_container_width=True):
            st.session_state.step += 1
            st.rerun()
    with step_cols[2]:
        if st.button("แสดงทุกขั้น", use_container_width=True):
            st.session_state.step = total_steps
            st.rerun()
    with step_cols[3]:
        st.caption(f"ขั้นที่ {current_step} จาก {total_steps}")

    if current_step == 0:
        st.info("กด ‘ขั้นถัดไป’ เพื่อดูอัลกอริทึมทีละขั้น")
    else:
        st.info(f"ขั้นที่ {current_step}: {all_actions[current_step - 1]}")
        with st.expander("ดูขั้นตอนก่อนหน้าทั้งหมด", expanded=True):
            for index, action in enumerate(all_actions[:current_step], start=1):
                st.write(f"{index}. {action}")

    if current_step == total_steps:
        st.markdown("#### เส้นทางคำตอบ")
        st.success("Euler Circuit — วงจรออยเลอร์" if solution["circuit"] else "Euler Path — เส้นทางออยเลอร์")
        st.code(" → ".join(solution["path"]), language=None)
        st.caption(f"จำนวนเส้นเชื่อมที่ใช้: {graph.number_of_edges()}")
else:
    st.info("เมื่อกราฟผ่านเงื่อนไขแล้ว กด ‘คำนวณด้วย Hierholzer’ เพื่อดูคำตอบและขั้นตอน")

st.markdown("<div style='text-align:center;color:#6b818c;font-size:.8rem;padding:1rem'>"
            "Undirected multigraph · รองรับเส้นเชื่อมซ้ำ · ไม่รองรับ self-loop · ไม่มีระบบเกมหรือบันทึกถาวร"
            "</div>", unsafe_allow_html=True)
