import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
import numpy as np

# Configuration
st.set_page_config(
    page_title="University Tuition Dashboard",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 0rem;
    }
    .metric-card {
    background-color: #f8f9fa;
    color: #000000;
    padding: 1rem;
    border-radius: 10px;
    border-left: 4px solid #1f77b4;
    }

    .stApp[data-theme="dark"] .metric-card {
        background-color: #4a4a4a;
        color: #ffffff;
        border-left: 4px solid #58a6ff;
    }
    
    /* Streamlit dark mode override */
    .stApp[data-theme="dark"] .metric-card {
        background-color: #4a4a4a;
        color: #ffffff;
        border-left: 4px solid #58a6ff;
    }
    
    .filter-section {
        background-color: #ffffff;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
    }
    
    /* Custom anchor heading for Data Visualization */
    #data-visualization {
        border-top: 2px solid #e1e4e8;
        padding-top: 2rem;
        margin-top: 2rem;
        font-size: 2rem;
        font-weight: 600;
        color: #1f77b4;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    #data-visualization svg {
        vertical-align: middle;
        margin-right: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# Load data
@st.cache_data
def load_data():
    try:
        with open('data/data_cleaning/output_with_tuition.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        df = pd.DataFrame(data)
        
        # Data cleaning and preparation
        df['tuition'] = pd.to_numeric(df['tuition'], errors='coerce')
        
        # Calculate total admission slots
        admission_columns = ['Round 1 Portfolio', 'Round 2 Quota', 'Round 3 Admission', 'Round 4 Direct Admission']
        df['total_admission'] = df[admission_columns].sum(axis=1, skipna=True)
        
        # Create tuition categories
        df['tuition_category'] = pd.cut(df['tuition'], 
                                       bins=[0, 15000, 30000, 50000, float('inf')],
                                       labels=['≤ 15,000 Baht', '15,001-30,000 Baht', 
                                              '30,001-50,000 Baht', '> 50,000 Baht'])
        
        # Use public_university field from JSON data
        df['university_type'] = df['public_university'].apply(lambda x: 'Public' if x else 'Private')
        
        return df
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return pd.DataFrame()

# Load the data
df = load_data()

if df.empty:
    st.error("Unable to load data. Please check the output_with_tuition.json file")
    st.stop()

# Header
st.markdown('<h1 class="main-header">University Tuition Analysis Dashboard</h1>', unsafe_allow_html=True)
st.markdown('<p style="text-align: center; font-size: 1.2rem; color: #666;">Analysis of Computer Engineering and AI Program Tuition Fees</p>', unsafe_allow_html=True)

# Page Navigation
st.sidebar.header("Navigation")
page = st.sidebar.radio("Select Page", ["Dashboard", "Data Table"], index=0)

# Sidebar Filters
st.sidebar.header("Filter Panel")

# Filter 1: Universities
universities = ['All'] + sorted(df['university'].unique().tolist())
selected_universities = st.sidebar.multiselect(
    "Select Universities",
    universities,
    default=['All']
)

# Filter 2: Program Type
program_types = ['All'] + sorted(df['program_type'].unique().tolist())
selected_program_type = st.sidebar.selectbox(
    "Program Type",
    program_types
)

# Filter 3: Field
fields = ['All'] + sorted(df['field'].unique().tolist())
selected_field = st.sidebar.selectbox(
    "Field of Study",
    fields
)

# Filter 4: Tuition Range
min_tuition = int(df['tuition'].min())
max_tuition = int(df['tuition'].max())
tuition_range = st.sidebar.slider(
    "Tuition Range (Baht)",
    min_tuition, max_tuition,
    (min_tuition, max_tuition),
    step=1000
)

# Filter 5: University Type
university_types = ['All', 'Public', 'Private']
selected_uni_type = st.sidebar.selectbox(
    "University Type",
    university_types
)

st.sidebar.markdown('</div>', unsafe_allow_html=True)

# Apply filters
filtered_df = df.copy()

if 'All' not in selected_universities:
    filtered_df = filtered_df[filtered_df['university'].isin(selected_universities)]

if selected_program_type != 'All':
    filtered_df = filtered_df[filtered_df['program_type'] == selected_program_type]

if selected_field != 'All':
    filtered_df = filtered_df[filtered_df['field'] == selected_field]

if selected_uni_type != 'All':
    filtered_df = filtered_df[filtered_df['university_type'] == selected_uni_type]

filtered_df = filtered_df[
    (filtered_df['tuition'] >= tuition_range[0]) & 
    (filtered_df['tuition'] <= tuition_range[1])
]

# Page Content
if page == "Dashboard":
    # Dashboard content
    # Summary Panel
    st.markdown("## Summary Statistics")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(f"""
            <div class="metric-card">
                <div>Total Programs</div>
                <div style="font-size: 1.75rem";>{len(filtered_df)}</div>
            </div>
            """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
            <div class="metric-card">
                <div>Average Tuition</div>
                <div style="font-size: 1.75rem";>{filtered_df['tuition'].mean():,.0f} Baht</div>
            </div>
            """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
            <div class="metric-card">
                <div>Lowest - Highest Tuition</div>
                <div style="font-size: 1.75rem";>{filtered_df['tuition'].max():,.0f} - {filtered_df['tuition'].min():,.0f} Baht</div>
            </div>
            """, unsafe_allow_html=True)

    # Dashboard Charts
    st.markdown("## Data Visualization")

    # Row 1: Tuition Distribution
    col1, = st.columns(1)

    with col1:
        st.subheader("Panel 1: Tuition Distribution")
        fig_hist = px.histogram(filtered_df, x='tuition', nbins=20, 
                               title="Histogram: Tuition Distribution",
                               labels={'tuition': 'Tuition (Baht)', 'count': 'Count'})
        fig_hist.update_layout(showlegend=False)
        st.plotly_chart(fig_hist, use_container_width=True)

    # Row 2: University Comparison
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Panel 2: University Comparison")
        # Top 15 universities by average tuition
        uni_avg = filtered_df.groupby('university')['tuition'].mean().sort_values(ascending=True).tail(15)
        
        # Create DataFrame for plotly
        uni_df = pd.DataFrame({
            'university': uni_avg.index,
            'average_tuition': uni_avg.values
        })
        
        fig_uni = px.bar(uni_df, x='average_tuition', y='university', orientation='h',
                         title="Average Tuition by University (Top 15)",
                         labels={'average_tuition': 'Average Tuition (Baht)', 'university': 'University'})
        fig_uni.update_layout(height=600)
        st.plotly_chart(fig_uni, use_container_width=True)

    with col2:
        st.subheader("Scatter Plot: Tuition vs Admission")
        fig_scatter = px.scatter(filtered_df, x='tuition', y='total_admission',
                                color='program_type', size='total_admission',
                                title="Relationship between Tuition and Total Admission",
                                labels={'tuition': 'Tuition (Baht)', 'total_admission': 'Total Admission'})
        st.plotly_chart(fig_scatter, use_container_width=True)

    # Row 3: Program Type Analysis
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Panel 3: Program Type Analysis")
        fig_violin = px.violin(filtered_df, x='program_type', y='tuition',
                              title="Violin Plot: Tuition Distribution by Program Type",
                              labels={'program_type': 'Program Type', 'tuition': 'Tuition (Baht)'})
        st.plotly_chart(fig_violin, use_container_width=True)

    with col2:
        st.subheader("Distribution by Price Range")
        tuition_cat_counts = filtered_df['tuition_category'].value_counts()
        fig_pie = px.pie(values=tuition_cat_counts.values, names=tuition_cat_counts.index,
                         title="Program Distribution by Price Range")
        st.plotly_chart(fig_pie, use_container_width=True)

    # Row 4: Field Analysis
    st.subheader("Panel 4: Field of Study Analysis")
    field_stats = filtered_df.groupby('field').agg({
        'tuition': ['mean', 'median', 'min', 'max', 'count']
    }).round(0)
    field_stats.columns = ['Average', 'Median', 'Minimum', 'Maximum', 'Program Count']

    fig_field = px.bar(field_stats, x=field_stats.index, y='Average',
                       title="Average Tuition by Field of Study",
                       labels={'x': 'Field of Study', 'Average': 'Average Tuition (Baht)'})
    st.plotly_chart(fig_field, use_container_width=True)

if page == "Data Table":
    # Data Table Page
    st.markdown("## Data Table Explorer")
    st.markdown("Select the columns you want to view and explore the complete dataset.")
    
    # Available columns with Thai descriptions
    column_descriptions = {
        # 'url': 'URL ลิงค์',
        'university': 'มหาวิทยาลัย',
        'faculty': 'คณะ',
        'field': 'สาขาวิชา',
        'program_name': 'ชื่อหลักสูตร (ไทย)',
        'program_name_en': 'ชื่อหลักสูตร (อังกฤษ)',
        'program_type': 'ประเภทหลักสูตร',
        'campus': 'วิทยาเขต',
        'Round 1 Portfolio': 'รอบที่ 1 Portfolio',
        'Round 2 Quota': 'รอบที่ 2 Quota',
        'Round 3 Admission': 'รอบที่ 3 Admission',
        'Round 4 Direct Admission': 'รอบที่ 4 Direct Admission',
        'tuition': 'ค่าเล่าเรียน (บาท)',
        'public_university': 'มหาวิทยาลัยของรัฐ',
        'total_admission': 'รวมจำนวนรับ (คำนวณ)'
    }
    
    # Column selection
    st.subheader("Column Selection")
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Available Columns:**")
        # Filter only columns that are in column_descriptions
        available_columns = [col for col in filtered_df.columns if col in column_descriptions]
        
        # Default selected columns
        default_columns = ['university', 'program_name', 'field', 'program_type', 'tuition', 'total_admission']
        
        selected_columns = st.multiselect(
            "Select columns to display:",
            available_columns,
            default=[col for col in default_columns if col in available_columns],
            format_func=lambda x: column_descriptions.get(x, x)
        )
    
    with col2:
        st.write("**Display Options:**")
        show_index = st.checkbox("Show row numbers", value=False)
        rows_per_page = st.selectbox("Rows per page:", [10, 25, 50, 100, 'All'], index=2)
        
        # Search functionality
        st.write("**Search & Filter:**")
        search_term = st.text_input("Search in data:", "")
    
    if selected_columns:
        # Create display dataframe
        display_df = filtered_df[selected_columns].copy()
        
        # Apply search filter
        if search_term:
            mask = display_df.astype(str).apply(lambda x: x.str.contains(search_term, case=False, na=False)).any(axis=1)
            display_df = display_df[mask]
        
        # Display statistics
        st.subheader("Data Summary")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Records", len(display_df))
        with col2:
            st.metric("Selected Columns", len(selected_columns))
        with col3:
            if 'tuition' in selected_columns:
                st.metric("Avg Tuition", f"{display_df['tuition'].mean():,.0f} ฿" if 'tuition' in display_df.columns else "N/A")
            else:
                st.metric("Universities", display_df['university'].nunique() if 'university' in display_df.columns else "N/A")
        with col4:
            if 'total_admission' in selected_columns:
                st.metric("Total Seats", f"{display_df['total_admission'].sum():,.0f}" if 'total_admission' in display_df.columns else "N/A")
            else:
                st.metric("Programs", len(display_df))
        
        # Pagination
        if rows_per_page != 'All':
            total_rows = len(display_df)
            total_pages = (total_rows - 1) // rows_per_page + 1
            
            if total_pages > 1:
                page_number = st.selectbox(f"Page (1-{total_pages}):", range(1, total_pages + 1))
                start_idx = (page_number - 1) * rows_per_page
                end_idx = start_idx + rows_per_page
                display_df = display_df.iloc[start_idx:end_idx]
        
        # Display the data table
        st.subheader(f"Data Table ({len(display_df)} records)")
        
        # Column name translation for display
        display_df_renamed = display_df.copy()
        column_rename_map = {col: column_descriptions.get(col, col) for col in display_df.columns}
        display_df_renamed.columns = [column_rename_map[col] for col in display_df.columns]
        
        st.dataframe(
            display_df_renamed,
            use_container_width=True,
            hide_index=not show_index
        )
        
        # Download options
        st.subheader("Download Data")
        col1, col2 = st.columns(2)
        
        with col1:
            json_data = display_df.to_json(orient='records', indent=2, force_ascii=False)
            st.download_button(
                label="Download as JSON",
                data=json_data,
                file_name=f"university_data_{'_'.join(selected_columns[:3])}.json",
                mime="application/json"
            )
        
        with col2:
            # Create Excel buffer
            from io import BytesIO
            buffer = BytesIO()
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                display_df.to_excel(writer, index=False, sheet_name='University Data')
            buffer.seek(0)
            
            st.download_button(
                label="Download as Excel",
                data=buffer,
                file_name=f"university_data_{'_'.join(selected_columns[:3])}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
    
    else:
        st.warning("Please select at least one column to display.")

# Footer (outside the page conditional)
st.markdown("---")
st.markdown("**Data Source:** TCAS University Programs | **Built with:** Streamlit + Plotly")