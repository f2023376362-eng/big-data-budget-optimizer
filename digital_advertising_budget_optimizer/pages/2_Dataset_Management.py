"""
Page 2: Dataset Management
Synthetic data generator (10K, 100K, 1M, 10M), external CSV/Excel uploader,
column mapping validator, data cleaner, dataset preview, and SQLite sync.
"""

import os
from pathlib import Path
import streamlit as st
import pandas as pd
from src.data_generator import AdvertisingDataGenerator, get_default_dataset_path
from src.data_validation import DatasetValidator
from src.data_cleaning import DataCleaner
from src.database import DatabaseManager
import config

st.title("💾 Dataset Management & Quality Control")

# Tab navigation
tab_gen, tab_upload, tab_clean, tab_preview = st.tabs([
    "🎲 Generate Synthetic Data",
    "📤 Upload External Dataset",
    "🧹 Data Validation & Cleaning",
    "🔍 Active Dataset Preview",
])

# ----------------- TAB 1: SYNTHETIC DATA GENERATION -----------------
with tab_gen:
    st.markdown("### Generate Realistic Multi-Platform Advertising Data")
    st.caption("Generates data across Facebook, Instagram, Google, TikTok, and YouTube with business constraints.")

    col_size, col_action = st.columns([2, 1])
    with col_size:
        size_choice = st.selectbox(
            "Select Dataset Volume:",
            options=[10_000, 100_000, 1_000_000, 10_000_000],
            format_func=lambda x: f"{x:,} records" + (" (Recommended for Benchmarking)" if x == 100_000 else " (Large Scale / Chunked)" if x >= 1_000_000 else ""),
            index=0,
        )

    with col_action:
        st.write("")
        st.write("")
        generate_btn = st.button("🚀 Generate Dataset", type="primary", use_container_width=True)

    if size_choice == 10_000_000:
        st.warning(
            "⚠️ **10 Million Records Notice:** To prevent RAM exhaustion, this dataset is streamed in 50k row chunks "
            "directly to disk using high-efficiency CSV streaming. File size ~850MB."
        )

    if generate_btn:
        progress_bar = st.progress(0.0)
        status_text = st.empty()
        status_text.text(f"Starting chunked generation for {size_choice:,} records...")

        generator = AdvertisingDataGenerator()
        target_path = get_default_dataset_path(size_choice)

        def update_progress(current, total):
            pct = min(current / total, 1.0)
            progress_bar.progress(pct)
            status_text.text(f"Generated {current:,} / {total:,} records ({pct*100:.1f}%)...")

        target_path = generator.generate_dataset_to_file(
            total_records=size_choice,
            output_filepath=target_path,
            chunk_size=50_000,
            progress_callback=update_progress,
        )

        progress_bar.progress(1.0)
        status_text.text("Generation complete! Loading active memory preview...")

        # Load into active session state
        load_limit = min(size_choice, 500_000)
        active_df = pd.read_csv(target_path, nrows=load_limit)
        st.session_state["active_df"] = active_df
        st.session_state["dataset_name"] = f"Synthetic Dataset ({size_choice:,} records on disk)"

        file_size_mb = os.path.getsize(target_path) / (1024 * 1024)
        st.success(
            f"✅ Successfully created **{target_path.name}** ({file_size_mb:.2f} MB)! "
            f"Active dataset updated ({len(active_df):,} records loaded into workspace)."
        )

# ----------------- TAB 2: UPLOAD EXTERNAL DATASET -----------------
with tab_upload:
    st.markdown("### Upload External Advertising Data")
    st.caption("Upload marketing exports in CSV or Excel format. The system will auto-detect equivalent column names.")

    uploaded_file = st.file_uploader("Upload CSV or Excel file:", type=["csv", "xlsx", "xls"])
    if uploaded_file is not None:
        try:
            if uploaded_file.name.endswith(".csv"):
                df_upload = pd.read_csv(uploaded_file)
            else:
                df_upload = pd.read_excel(uploaded_file)

            st.write(f"**Loaded File:** `{uploaded_file.name}` ({len(df_upload):,} rows, {len(df_upload.columns)} columns)")

            validator = DatasetValidator()
            val_report = validator.validate(df_upload)

            # Show Column Mapping
            mapping, missing = validator.detect_column_mapping(df_upload.columns.tolist())
            st.markdown("#### 🔗 Detected Column Mappings")
            map_cols = st.columns(3)
            for idx, (std, orig) in enumerate(mapping.items()):
                with map_cols[idx % 3]:
                    st.caption(f"**{std}** ⬅️ `{orig}`")

            if missing:
                st.error(
                    f"❌ **Validation Failed:** Missing essential advertising columns: `{', '.join(missing)}`. "
                    f"The optimizer requires impressions, clicks, spend, conversions, and revenue to compute ROI."
                )
            else:
                st.success("✅ **Schema Verified:** All essential advertising metrics are present!")
                if st.button("📥 Set as Active Dataset", type="primary"):
                    st.session_state["active_df"] = df_upload
                    st.session_state["dataset_name"] = f"Uploaded File: {uploaded_file.name}"
                    st.rerun()

        except Exception as e:
            st.error(f"Error reading file: {str(e)}")

# ----------------- TAB 3: VALIDATION & CLEANING -----------------
with tab_clean:
    st.markdown("### Data Quality & Cleaning Engine")
    curr_df = st.session_state.get("active_df")

    if curr_df is not None:
        validator = DatasetValidator()
        report = validator.validate(curr_df)

        st.markdown("#### 📋 Quality Health Audit")
        s1, s2, s3, s4 = st.columns(4)
        s1.metric("Total Records", f"{report['summary']['total_rows']:,}")
        s2.metric("Null Cells", f"{report['summary']['null_cells']:,}")
        s3.metric("Duplicates", f"{report['summary']['duplicate_rows']:,}")
        s4.metric("Logical Anomalies", f"{report['summary']['invalid_metric_rows']:,}")

        if report["warnings"]:
            with st.expander("⚠️ Identified Data Quality Warnings", expanded=True):
                for w in report["warnings"]:
                    st.write(f"- {w}")

        st.markdown("#### 🛠️ Automated Cleaning Action")
        st.write("Click below to rectify bound violations (e.g. Clicks > Impressions), deduplicate, and impute nulls:")

        if st.button("🧹 Clean Active Dataset Now", type="primary"):
            cleaner = DataCleaner()
            cleaned_df, clean_summary = cleaner.clean(curr_df)
            st.session_state["active_df"] = cleaned_df
            st.success(
                f"✅ Cleaning complete! Deduplicated {clean_summary['duplicates_removed']} rows, "
                f"rectified {clean_summary['clicks_clamped']} clicks violations, and "
                f"clamped {clean_summary['conversions_clamped']} conversion violations."
            )
            st.rerun()

        st.markdown("---")
        st.markdown("#### 🗄️ Sync Active Dataset to SQLite Database")
        st.caption("Populate normalized SQLite database tables with active records for SQL exploration.")
        if st.button("💾 Insert Records into Database"):
            with st.spinner("Inserting records into SQLite..."):
                db = DatabaseManager()
                # Insert up to 25k records for responsive SQLite querying
                to_insert = curr_df.head(25_000)
                inserted = db.insert_advertising_records(to_insert)
                st.success(f"✅ Successfully inserted {inserted:,} records into SQLite `advertising.db`!")

# ----------------- TAB 4: ACTIVE DATASET PREVIEW -----------------
with tab_preview:
    st.markdown("### Active Dataset Preview & Download")
    curr_df = st.session_state.get("active_df")

    if curr_df is not None:
        mem_mb = curr_df.memory_usage(deep=True).sum() / (1024 * 1024)
        st.info(f"**Dataset Name:** {st.session_state.get('dataset_name')} | **Memory Usage:** {mem_mb:.2f} MB | **Rows:** {len(curr_df):,} | **Columns:** {len(curr_df.columns)}")

        st.dataframe(curr_df.head(50), use_container_width=True)

        csv_data = curr_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="⬇️ Download Processed Dataset (CSV)",
            data=csv_data,
            file_name="digital_advertising_processed.csv",
            mime="text/csv",
        )
    else:
        st.info("No active dataset in memory.")

