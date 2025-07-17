# File: Asir_app3_通用空間軌跡點位篩選可視化.py

import streamlit as st
import folium
from streamlit_folium import st_folium
import pandas as pd
import io
from datetime import datetime
import re

# --- Config ---
st.set_page_config(layout="wide", page_title="Asir_app3:通用空間軌跡點位篩選可視化")

# --- Sidebar 控制區 ---
with st.sidebar:
    st.title("Asir_app3: 通用空間軌跡點位篩選可視化 控制區")
    # 資料來源模式
    source_mode = st.radio("資料來源模式", ["維持原始資料", "使用含時間欄位新資料"])

    # 上傳及讀取資料
    if source_mode == "維持原始資料":
        data_file = st.file_uploader("上傳點位資料 (CSV 或 XLSX)", type=["csv", "xlsx"], key="orig")
        if not data_file:
            st.info("請先上傳原始點位資料。")
            st.stop()
        data_bytes = data_file.read()
        if data_file.name.lower().endswith('.xlsx'):
            xls = pd.ExcelFile(io.BytesIO(data_bytes))
            sheet = st.selectbox("選擇資料工作表", xls.sheet_names)
            df = xls.parse(sheet)
        else:
            encodings = ["utf-8", "cp950", "latin1"]
            enc = st.selectbox("CSV 編碼選擇", encodings, index=1)
            try:
                df = pd.read_csv(io.BytesIO(data_bytes), encoding=enc)
            except Exception:
                st.error("CSV 解碼失敗，請選擇正確編碼。")
                st.stop()
    else:
        data_file2 = st.file_uploader("上傳含時間欄位資料 (CSV 或 XLSX)", type=["csv", "xlsx"], key="time")
        if not data_file2:
            st.info("請先上傳含時間欄位的新資料。")
            st.stop()
        data_bytes = data_file2.read()
        if data_file2.name.lower().endswith('.xlsx'):
            xls = pd.ExcelFile(io.BytesIO(data_bytes))
            sheet = st.selectbox("選擇工作表", xls.sheet_names)
            df0 = xls.parse(sheet)
        else:
            encodings = ["utf-8", "cp950", "latin1"]
            enc = st.selectbox("CSV 編碼選擇", encodings, index=1)
            try:
                df0 = pd.read_csv(io.BytesIO(data_bytes), encoding=enc)
            except Exception:
                st.error("CSV 解碼失敗，請選擇正確編碼。")
                st.stop()
        # 驗證時間欄位並轉換
        if '時間' not in df0.columns:
            st.error("新資料需包含 '時間' 欄位。請改成這三個欄位名稱：gx, gy, 時間。")
            st.stop()
        def parse_roctime(x):
            if pd.isna(x):
                return pd.NaT
            s = str(x).strip()
            if re.fullmatch(r"\d+\.\d+", s) or isinstance(x, (int, float)):
                try:
                    return pd.to_datetime('1899-12-30') + pd.to_timedelta(float(x), unit='D')
                except:
                    return pd.NaT
            m = re.match(r"^(\d{2,4})/(\d{1,2})/(\d{1,2})[\sT](\d{1,2}):(\d{1,2}):(\d{1,2})$", s)
            if m:
                y, mo, d, hh, mi, ss = m.groups()
                year = int(y)
                if year < 1900:
                    year += 1911
                try:
                    return datetime(year, int(mo), int(d), int(hh), int(mi), int(ss))
                except:
                    return pd.NaT
            try:
                return pd.to_datetime(s)
            except:
                return pd.NaT
        df0['時間_dt'] = df0['時間'].apply(parse_roctime)
        df0['年月'] = df0['時間_dt'].dt.year * 100 + df0['時間_dt'].dt.month
        df0['星期'] = df0['時間_dt'].dt.weekday + 1
        df0['週期'] = df0['時間_dt'].dt.isocalendar().week
        hours = df0['時間_dt'].dt.hour.fillna(0).astype(int)
        df0['時段'] = hours.apply(lambda h: f"{(h//2)*2:02d}_{((h//2)*2+2)%24:02d}")
        df = df0.copy()

    # 通用欄位檢查：gx, gy, 時間
    if not {"gx", "gy", "時間"}.issubset(df.columns):
        st.error("資料需包含 gx, gy, 時間 三個欄位，請修改欄位名稱後再試。")
        st.stop()
    lon_col, lat_col = "gx", "gy"

    # 篩選 1 (AND 條件)
    st.subheader("🔹 篩選條件 1 (AND)")
    c1, v1 = st.columns([2, 2])
    with c1:
        cat1 = st.selectbox("分類欄位 1", [""] + df.columns.tolist(), key="cat1")
    with v1:
        vals1 = df[cat1].dropna().unique().tolist() if cat1 else []
        val1 = st.selectbox("分類值 1", [""] + vals1, key="val1")
    df1_source = df[df[cat1] == val1] if cat1 and val1 else pd.DataFrame(columns=df.columns)
    c12, v12 = st.columns([2, 2])
    with c12:
        cat1_2 = st.selectbox("分類欄位 1_2", [""] + df.columns.tolist(), key="cat1_2")
    with v12:
        vals12 = df1_source[cat1_2].dropna().unique().tolist() if cat1_2 else []
        val1_2 = st.selectbox("分類值 1_2", [""] + vals12, key="val1_2")

    # 篩選 2 (AND 條件)
    st.subheader("🔸 篩選條件 2 (AND)")
    c2, v2 = st.columns([2, 2])
    with c2:
        cat2 = st.selectbox("分類欄位 2", [""] + df.columns.tolist(), key="cat2")
    with v2:
        vals2 = df[cat2].dropna().unique().tolist() if cat2 else []
        val2 = st.selectbox("分類值 2", [""] + vals2, key="val2")
    df2_source = df[df[cat2] == val2] if cat2 and val2 else pd.DataFrame(columns=df.columns)
    c22, v22 = st.columns([2, 2])
    with c22:
        cat2_2 = st.selectbox("分類欄位 2_2", [""] + df.columns.tolist(), key="cat2_2")
    with v22:
        vals22 = df2_source[cat2_2].dropna().unique().tolist() if cat2_2 else []
        val2_2 = st.selectbox("分類值 2_2", [""] + vals22, key="val2_2")

    # 軌跡顯示
    st.markdown("---")
    show_traj1 = st.checkbox("顯示軌跡1 (紅線)", key="traj1")
    show_traj2 = st.checkbox("顯示軌跡2 (綠線)", key="traj2")

# --- 資料篩選 ---
if cat1 and val1:
    df1 = df[df[cat1] == val1]
    if cat1_2 and val1_2:
        df1 = df1[df1[cat1_2] == val1_2]
    df1 = df1.dropna(subset=[lat_col, lon_col])
else:
    df1 = pd.DataFrame(columns=df.columns)
if cat2 and val2:
    df2 = df[df[cat2] == val2]
    if cat2_2 and val2_2:
        df2 = df2[df2[cat2_2] == val2_2]
    df2 = df2.dropna(subset=[lat_col, lon_col])
else:
    df2 = pd.DataFrame(columns=df.columns)

all_points = pd.concat([df1, df2])

# --- 主畫面 ---
col_map, col_data = st.columns([2, 1])
with col_map:
    if not all_points.empty:
        m = folium.Map(location=[all_points[lat_col].mean(), all_points[lon_col].mean()], zoom_start=8)
        for _, row in df1.iterrows():
            folium.CircleMarker(
                location=[row[lat_col], row[lon_col]],
                radius=4, color='red', fill=True, fill_opacity=0.6
            ).add_to(m)
        for _, row in df2.iterrows():
            folium.CircleMarker(
                location=[row[lat_col], row[lon_col]],
                radius=4, color='green', fill=True, fill_opacity=0.6
            ).add_to(m)
        if show_traj1 and not df1.empty:
            coords1 = df1[[lat_col, lon_col]].values.tolist()
            folium.PolyLine(locations=coords1, color='red').add_to(m)
        if show_traj2 and not df2.empty:
            coords2 = df2[[lat_col, lon_col]].values.tolist()
            folium.PolyLine(locations=coords2, color='green').add_to(m)
        m.fit_bounds(all_points[[lat_col, lon_col]].values.tolist())
        title = f"Asir_app3: {cat1 or '-'}={val1 or '-'}"
        if cat1_2 and val1_2:
            title += f" AND {cat1_2}={val1_2}"
        title += f" (紅) & {cat2 or '-'}={val2 or '-'}"
        if cat2_2 and val2_2:
            title += f" AND {cat2_2}={val2_2}"
        title += " (綠)"
        m.get_root().html.add_child(folium.Element(f"<h4 style='text-align:center'>{title}</h4>"))
        st_folium(m, width=800, height=600)
    else:
        st.warning("無符合條件之點位，請調整篩選參數。")
with col_data:
    st.subheader("篩選結果資料")
    df1_display = df1.reset_index(drop=True)
    df2_display = df2.reset_index(drop=True)
    cond1_text = f"{cat1 or '-'}={val1 or '-'}"
    if cat1_2 and val1_2:
        cond1_text += f" AND {cat1_2}={val1_2}"
    st.markdown(f"**篩選 1**: {cond1_text}")
    st.dataframe(df1_display, use_container_width=True)
    cond2_text = f"{cat2 or '-'}={val2 or '-'}"
    if cat2_2 and val2_2:
        cond2_text += f" AND {cat2_2}={val2_2}"
    st.markdown(f"**篩選 2**: {cond2_text}")
    st.dataframe(df2_display, use_container_width=True)
