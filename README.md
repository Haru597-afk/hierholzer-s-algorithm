# Hierholzer Algorithm Lab

Streamlit app for Euler paths/circuits.

## Deploy
1. Upload `streamlit_app.py`, `requirements.txt`, and `README.md` to the repository root.
2. Set Streamlit Cloud Main file path to `streamlit_app.py`.
3. Reboot the app.

## Graph editor
- In `เพิ่มจุดยอด` mode, click empty canvas space to add A, B, C, ... Z.
- In `สร้างเส้นเชื่อม` mode, click two different vertices to connect them. Parallel edges are supported. Self-loops are not supported.
- `ล้างกราฟ` clears the graph; the next vertex starts again at A. Maximum 26 vertices.
