import numpy as np
import streamlit as st
from utils import config as cf
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from utils.helpers import load_eval_data, nifti_loader, pmap_loader, classify, slice_renderer

st.markdown("""
    <style>
        body, html { font-size: 16px !important; }
        div[data-testid="metric-container"] { padding: 8px; }
        h1 { font-size: 40px !important; }
        h2 { font-size: 28px !important; }
        h3 { font-size: 22px !important; }
        .stMetricValue { font-size: 20px !important; }
        .stMetricLabel { font-size: 14px !important; }
    </style>
""", unsafe_allow_html=True)

st.set_page_config(
    page_title="Interactive Exploration Dashboard",
    layout='wide',
    initial_sidebar_state="expanded"
)

# ---- init ----
if 'selected_sub' not in st.session_state:
    st.session_state.selected_sub = None
if 'last_df_selection' not in st.session_state:
    st.session_state.last_df_selection = []
if "main_table_key" not in st.session_state:
    st.session_state["main_table_key"] = {"selection": {"rows": []}}


# ---- caching ----
@st.cache_data(show_spinner=False) # no reload
def get_eval_data():
    return load_eval_data()

@st.cache_data(show_spinner=False)
def load_nifti(path: Path):
    return nifti_loader(path)

@st.cache_data(show_spinner=False)
def load_pmap(path: Path):
    return pmap_loader(path)

@st.cache_data
def convert_for_download(df):
    return df.to_csv().encode("utf-8")

# ---- synching logic ---- 
def sync_to_table():
    new_sub = st.session_state.sub_selector
    st.session_state.selected_sub = new_sub
    
    sub_list = list(df['subject_id'].unique())
    if new_sub in sub_list:
        row_idx = sub_list.index(new_sub)
        st.session_state["main_table_key"] = {"selection": {"rows": [row_idx]}}
        st.session_state.last_df_selection = [row_idx]

def mask_metric(label, value, color):
    st.metric(label, value)

    st.markdown(
        f"""
        <div style="
            width: 50%;
            border-bottom: 2px solid {color};
            padding-bottom: 4px;
            margin-bottom: 8px;
        ">
        """,
        unsafe_allow_html=True
    )

    st.markdown("</div>", unsafe_allow_html=True)

with st.spinner("Loading the Data..."):
    df = get_eval_data()

# synching
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

tab_names = ["Per-Subject Viewer", "Dataset Summary", "Graph Analytics"]
tab1, tab2, tab3 = st.tabs(tab_names)

with tab1:
    st.write("")
    c1, c2, c3, c4 = st.columns([0.8, 1.2, 0.7, 2], gap="medium")
    
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
                on_change=sync_to_table, # tab2 updater
                help="Choose a subject ID to view"
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
            required=True,
            help="Select the viewing plane: `Axial` (top-down view), `Sagittal` (side view), or `Coronal` (front-to-back view)"
        )
        
        if axis_label is None:
            axis_label = labels[0]
        
        axis = dict(options)[axis_label]
    
    with c3: 
        options_map = {"Show": True, "Hide": False}
        options = list(options_map.keys())
        toggle_seg = st.segmented_control(
            "**Segmentation**",
            options=options,
            default=options[0],
            selection_mode="single",
            required=True,
            help="Toggle to `Show`/`Hide` the microbleed segmentation overlay on the brain scan"
        )

        if toggle_seg is None:
            toggle_seg = options[0]
        
        seg = options_map[toggle_seg]

    with c4:
        threshold = st.slider(
            "**Probability slider**", 
            min_value=0.1, max_value=1.0, step=0.01, value=0.5,
            help="Adjust the probability threshold for microbleed detection. Higher values require more confidence but may miss some microbleeds. Lower values detect more but may include false positives. (Only applies when segmentation is toggled on `Show`)", disabled=not seg)
        
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
            slice_idx = st.slider("**Slice**", 0, n_slices-1, mid, key=f"slice_slider_{sub_id}", help="Navigate through different slices of the brain scan along the selected viewing axis")

            tp_mask, fp_mask, fn_mask, tp, fp, fn, gt_count, pred_count = classify(pmap, gt_lbl, threshold)

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
            with m1:
                mask_metric("True Positives", tp, cf.TP_HEX)
            with m2:
                mask_metric("False Positives", fp, cf.FP_HEX)
            with m3:
                mask_metric("False Negatives", fn, cf.FN_HEX)

            st.markdown(f"""
                <div style="
                    background-color: rgba(109, 173, 190, 0.5);
                    color:#cedadb;
                    margin-top: 10px;
                    padding:10px 10px;
                    border-radius:6px;
                    text-align:center;
                ">
                GT microbleeds: <b>{gt_count}</b>\t|\tPredicted: <b>{pred_count}</b>
                </div>
                """, unsafe_allow_html=True
            )

            st.divider()

            with st.container(border=True):
                st.subheader("Performance Metrics", help="Evaluation metrics showing how well the detection model performs compared to ground truth annotations")
   
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

    st.subheader("Evaluation Overview", help="Average performance metrics across all subjects in the dataset")
    numeric_cols = disp_df.select_dtypes(include=np.number).columns
    agg = disp_df[numeric_cols].mean()

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("F1 Score (Avg)", f"{agg['F1 Score']:.3f}")
    k2.metric("Sensitivity (Avg)", f"{agg['Sensitivity']:.3f}")
    k3.metric("Dice (Avg)", f"{agg['Dice']:.3f}")
    k4.metric("False Positives (Avg)", f"{agg['False Positives']:.1f}")
    
    st.divider()

    st.subheader("Evaluation Dataset", help="Detailed performance metrics for each subject. Click any row to view that subject in the Per-Subject Viewer tab")
    selection = st.dataframe(
        disp_df,
        selection_mode='single-row',
        width='stretch',
        hide_index=True,
        key="main_table_key",
        on_select='rerun',
        height=400,
        column_config={
            "Subject ID": st.column_config.TextColumn("Subject ID", width="medium", help="Unique identifier for each subject/patient"),
            "Sensitivity": st.column_config.ProgressColumn(
                "Sensitivity", format="%.3f", min_value=0, max_value=1, help="Recall - How much microbleeds were actually dectected out of all microbleeds (TP / (TP + FN))"),
            "F1 Score": st.column_config.ProgressColumn(
                "F1 Score", format="%.3f", min_value=0, max_value=1, help="Overall detection accuracy (harmonic mean of precision and sensitivity) ((2 x Recall x Precision) / (Recall + Precision))"),
            "Dice": st.column_config.ProgressColumn(
                "Dice", format="%.3f", min_value=0, max_value=1, help="Dice coefficient: measure of overlap between predicted and actual microbleeds"),
            "False Positives": st.column_config.NumberColumn("False Positives", format="%d", help="Number of incorrect detections - areas identified as microbleeds that aren't actually there"),
            "GT Count": st.column_config.NumberColumn("GT Count", format="%d", help="Ground truth count: actual number of microbleeds annotated by medical experts"),
            "Predicted Count": st.column_config.NumberColumn("Predicted Count", format="%d", help="Number of microbleeds detected by the detection model")
        },
    )

    csv = convert_for_download(disp_df)

    st.download_button(
        label="Download CSV",
        data=csv,
        file_name="CMB_2DModel_Evaluation_Data.csv",
        mime="text/csv",
        icon=":material/download:",
        help="Click to downliad the dataframe"
    )

with tab3:    
    if not df.empty:
        st.subheader("Microbleed Counts Per-subject", help="Distribution showing how many subjects have different numbers of microbleeds")

        mb_counts = df['num_gt_microbleeds'].value_counts().sort_index()
        
        st.bar_chart(
            mb_counts, 
            x_label="Number of Microbleeds", 
            y_label="Number of Subjects",
            color="primary"
        )

        st.divider()
    
        st.subheader("F1 Score Per-subject", help="Individual performance scores for each subject, sorted by F1-Score (worse to best)")
        
        st.bar_chart(
            df[['subject_id', 'f1_score']], 
            x="subject_id", 
            y="f1_score", 
            x_label="Subject ID", 
            y_label="F1 Score",
            sort="f1_score",
            color="#ff4b4b"
        )      

    else:
        st.info("No data available to display analytics.")