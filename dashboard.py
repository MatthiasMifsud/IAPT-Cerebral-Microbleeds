import pandas as pd
import numpy as np
import streamlit as st
from utils import config as cf
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import scipy.ndimage as ndimage
from utils.helpers import load_eval_data, nifti_loader, pmap_loader, classify, slice_renderer

st.set_page_config(
    page_title="Interactive Exploration Dashboard",
    layout='wide',
    initial_sidebar_state="expanded"
)

# init
if 'selected_sub' not in st.session_state:
    st.session_state.selected_sub = None
if 'last_df_selection' not in st.session_state:
    st.session_state.last_df_selection = []
if "main_table_key" not in st.session_state:
    st.session_state["main_table_key"] = {"selection": {"rows": []}}

# caching
@st.cache_data(show_spinner=False) # no reload
def get_eval_data():
    return load_eval_data()

@st.cache_data(show_spinner=False)
def load_nifti(path: Path):
    return nifti_loader(path)

@st.cache_data(show_spinner=False)
def load_pmap(path: Path):
    return pmap_loader(path)

def sync_to_table():
    new_sub = st.session_state.sub_selector
    st.session_state.selected_sub = new_sub
    
    sub_list = list(df['subject_id'].unique())
    if new_sub in sub_list:
        row_idx = sub_list.index(new_sub)
        st.session_state["main_table_key"] = {"selection": {"rows": [row_idx]}}
        st.session_state.last_df_selection = [row_idx]

with st.spinner("Loading the Data..."):
    df = get_eval_data()

if "main_table_key" in st.session_state:
    current_table_selection = st.session_state["main_table_key"].get("selection", {}).get("rows", [])
    
    if current_table_selection != st.session_state.last_df_selection:
        st.session_state.last_df_selection = current_table_selection
        
        if current_table_selection:
            selected_row_idx = current_table_selection[0]
            new_sub_id = df.iloc[selected_row_idx]["subject_id"]
            
            st.session_state.selected_sub = new_sub_id
            st.session_state.sub_selector = new_sub_id

st.markdown("""
<div class="dash-header">
    <h1>Interactive Exploration Dashboard</h1>
    <span class="badge">Cerebral Microbleed Detection</span><br></br>
</div>
""", unsafe_allow_html=True)

tab_names = ["Per-Subject Viewer", "Dataset Summary", "Analytics"]
tab1, tab2, tab3 = st.tabs(tab_names)

with tab1:
    st.write("")
    c1, c2, c3, c4 = st.columns([1, 1, 0.5, 2], gap="medium")
    
    with c1:
        if not df.empty:
            sub_list = list(df['subject_id'].unique())

            if st.session_state.selected_sub not in sub_list:
                st.session_state.selected_sub = sub_list[0] # goes to valdo 101
            
            current_index = sub_list.index(st.session_state.selected_sub) 
            
            sub_id = st.selectbox(
                "**Select Subject**", 
                sub_list,
                index=current_index,
                key="sub_selector",
                on_change=sync_to_table # tab2 updater
            )
            st.session_state.selected_sub = sub_id

        else:
            st.warning(f"No volume files found.")
            sub_id = "None"
    
    with c2:
        axis_map = {"Axial (Y)": 2, "Sagittal (Z)": 0, "Coronal (X)": 1}
        options = list(axis_map.items())
        labels = [k for k, _ in options]
        
        axis_label = st.segmented_control(
            "**Viewing Axis**",
            options=labels,
            default=labels[0],
            selection_mode="single",
            required=True
        )
        
        if axis_label is None:
            axis_label = labels[0]
        
        axis = dict(options)[axis_label]
    
    with c3: 
        options_map = {"On": True, "Off": False}
        options = list(options_map.keys())
        toggle_seg = st.segmented_control(
            "**Segmentation**",
            options=options,
            default=options[0],
            selection_mode="single",
            required=True,
        )

        if toggle_seg is None:
            toggle_seg = options[0]
        
        seg = options_map[toggle_seg]

    with c4:
        threshold = st.slider(
            "**Probability slider**", 
            min_value=0.1, max_value=1.0, step=0.01, value=0.5,
            help="Applies for the .npz probability maps", disabled=not seg)
        
    st.divider()

    # loading all required files
    vol_path = cf.T2S_VOLUMES_PATH / f"{sub_id}{cf.T2S_EXT}"
    lbl_path = cf.GT_LABELS_PATH / f"{sub_id}{cf.NIFTI_EXT}"
    pred_path = cf.PRED_PATH / f"{sub_id}{cf.NIFTI_EXT}"
    prob_path = cf.PMAP_PATH / f"{sub_id}{cf.PMAP_EXT}"
    
    files_exist = all(path.exists() for path in [vol_path, lbl_path, pred_path, prob_path])
    
    # handling
    if not files_exist:
        missing = [p for p in [vol_path, lbl_path, pred_path, prob_path] if not p.exists()]
        missing_list = "\n".join(
            f"- '{'/'.join(file.parts[-3:])}'" for file in missing
        )
        st.error(f"**Missing files for subject {sub_id}:**\n{missing_list}")    

    else:
        with st.spinner(f"Loading files for subject {sub_id}"):
            t2s, t2s_zooms = load_nifti(vol_path)
            gt_lbl, _ = load_nifti(lbl_path)
            pmap = load_pmap(prob_path)

        col_img, col_stats = st.columns([1.4, 1], gap="large")
 
        with col_img:
            n_slices = t2s.shape[axis]
            mid = n_slices // 2
            slice_idx = st.slider("**Slice**", 0, n_slices-1, mid, key="slice_slider")

            tp_mask, fp_mask, fn_mask, tp, fp, fn = classify(pmap, gt_lbl, threshold)

            fig = slice_renderer(
                t2s, 
                tp_mask, fp_mask, fn_mask, 
                slice_idx, axis, t2s_zooms, seg
            )
            st.pyplot(fig, width='stretch')
            plt.close(fig)
    
        with col_stats:
            st.markdown(f"### {sub_id}")
            st.caption(f"**Threshold** {threshold:.2f} | **Slice** {slice_idx}/{n_slices-1}")
            st.divider()

            # sensitivity
            if (tp + fn) == 0:
                sensitivity = 1.0 if fp == 0 else 0.0
            else:
                sensitivity = tp / (tp + fn)

            # precision
            if (tp + fp) == 0:
                precision = 1.0 if (tp + fn) == 0 else 0.0
            else:
                precision = tp / (tp + fp)

            # f1
            if (precision + sensitivity) > 0:
                f1 = 2 * precision * sensitivity / (precision + sensitivity)
            else:
                f1 = 0.0

            # Detection metrics section
            st.markdown("**Detection Metrics**")
            m1, m2, m3 = st.columns(3)
            m1.metric("True Positives", tp)
            m2.metric("False Positives", fp)
            m3.metric("False Negatives", fn)

            gt_count = int(ndimage.label((gt_lbl > 0).astype(int))[1])
            pred_count = int(ndimage.label((pmap >= threshold).astype(int))[1])

            st.info(f"GT microbleeds: **{gt_count}** | Predicted: **{pred_count}**")
            st.divider()

            with st.container(border=True):
                st.subheader("Performance Metrics")
   
                st.write(f"**F1 Score:** {f1:.2f}")
                st.progress(f1)
                st.write("Sensitivity:", f"{sensitivity:.2f}")
                st.progress(sensitivity)
                st.write(f"**Precision:** {precision:.2f}")
                st.progress(precision)

with tab2:
    disp_df = df.copy()
    disp_df.rename(columns={
        "subject_id" : "Subject ID",
        "sensitivity": "Sensitivity",
        "false_positives": "False Positives",
        "f1_score": "F1 Score",
        "dice":"Dice",
        "num_gt_microbleeds": "GT Count",
        "num_pred_microbleeds": "Predicted Count"
    }, inplace=True)

    disp_df = disp_df[[
        "Subject ID",
        "F1 Score",
        "Sensitivity",
        "Dice",
        "False Positives",
        "GT Count",
        "Predicted Count"
    ]]

    st.subheader("Evaluation Dataset")
    selection = st.dataframe(
        disp_df,
        selection_mode='single-row',
        width='stretch',
        hide_index=True,
        key="main_table_key",
        on_select='rerun',
        height=400,
        column_config={
            "Subject ID": st.column_config.TextColumn("Subject ID", width="medium"),
            "Sensitivity": st.column_config.ProgressColumn(
                "Sensitivity", format="%.3f", min_value=0, max_value=1),
            "F1 Score": st.column_config.ProgressColumn(
                "F1 Score", format="%.3f", min_value=0, max_value=1),
            "Dice": st.column_config.ProgressColumn(
                "Dice", format="%.3f", min_value=0, max_value=1),
            "False Positives": st.column_config.NumberColumn("False Positives", format="%d"),
            "GT Count": st.column_config.NumberColumn("GT Count", format="%d"),
            "Predicte Count": st.column_config.NumberColumn("Predicted Count", format="%d"),
        },
    )

    st.divider()
    st.subheader("Evaluation Overview")
    numeric_cols = disp_df.select_dtypes(include=np.number).columns
    agg = disp_df[numeric_cols].mean()

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("F1 Score (Avg)", f"{agg['F1 Score']:.3f}")
    k2.metric("Sensitivity (Avg)", f"{agg['Sensitivity']:.3f}")
    k3.metric("Dice (Avg)", f"{agg['Dice']:.3f}")
    k4.metric("False Positives (Avg)", f"{agg['False Positives']:.1f}")

with tab3:
    st.subheader("Dataset-Level Analytics")
    
    col_hist, col_bar = st.columns(2)

    with col_hist:
        st.markdown("**Microbleed Counts per Subject**")
        # Histogram showing the distribution of bleed counts
        fig_hist, ax_hist = plt.subplots()
        ax_hist.hist(df['num_gt_microbleeds'], bins=max(10, df['num_gt_microbleeds'].max()), color='#4682B4', edgecolor='white')
        ax_hist.set_xlabel("Number of Microbleeds")
        ax_hist.set_ylabel("Frequency (Subjects)")
        st.pyplot(fig_hist)

    with col_bar:
        st.markdown("**Subject F1 Performance (Worst to Best)**")
        # sorted F1 scores
        f1_sorted = df[['subject_id', 'f1_score']].sort_values(by='f1_score')
        st.bar_chart(f1_sorted, x='subject_id', y='f1_score', color='#ff4b4b')

    st.divider()
    
    # Extra Analytics: Scatter plot of GT vs Predicted
    st.markdown("**Predicted vs Ground Truth Counts**")
    st.scatter_chart(df, x='num_gt_microbleeds', y='num_pred_microbleeds', size=20)