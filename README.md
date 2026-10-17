# Hierholzer's Algorithm — Streamlit

This keeps the existing app layout, Euler validation, Hierholzer steps, and graph summary, adding click-based graph editing.

## Deploy
1. Upload `streamlit_app.py`, `requirements.txt`, and `README.md` to the repository root.
2. In Streamlit Community Cloud, set **Main file path** to `streamlit_app.py`.
3. Reboot the app.

## Click editing
- Choose **เพิ่มจุดยอด** and click an empty place on the graph to add a vertex.
- Choose **สร้างเส้นเชื่อม** and click two different existing vertices to connect them.
- Vertex labels use A–Z. After **ล้างกราฟ**, the next created vertex starts at A again.
- Parallel edges are supported; self-loops are not supported.
