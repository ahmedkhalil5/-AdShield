import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO
import matplotlib.pyplot as plt 


st.set_page_config(page_title="Marketing Dashboard Pro", layout="wide")


st.markdown("""
<style>
    .reportview-container {
        background: #050404; /* لون خلفية فاتح ومريح */
    }
    .stMetric {
        background-color: #ffffff; /* خلفية بيضاء لكروت الأرقام */
        padding: 10px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);pip install mistralai
    }
</style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center; color: #1E88E5;'>🚀 Campaign Intelligence Dashboard</h1>", unsafe_allow_html=True)
st.markdown("---")


st.sidebar.header("📁 Data & Controls")
uploaded_file = st.sidebar.file_uploader("Upload Facebook CSV", type="csv")


st.sidebar.markdown("---")
st.sidebar.subheader("🎯 Filters")

if uploaded_file:
    data = pd.read_csv(uploaded_file)
    data.columns = [c.strip() for c in data.columns] 

    try:
       
        clicks_col = [c for c in data.columns if 'Clicks (all)' in c][0]
        spend_col = [c for c in data.columns if 'Amount spent' in c][0]
        imp_col = [c for c in data.columns if 'Impressions' in c][0]
        roas_col = [c for c in data.columns if 'ROAS' in c][0]
        campaign_col = "Campaign name" # ثابت في شيتات فيسبوك

        
        data["CTR %"] = (data[clicks_col] / data[imp_col]) * 100
        data["CPC"] = data[spend_col] / data[clicks_col]
        
        all_campaigns = data[campaign_col].unique().tolist()
        selected_campaigns = st.sidebar.multiselect("Select Campaigns", all_campaigns, default=all_campaigns)
        
        
        min_roas = float(data[roas_col].min())
        max_roas = float(data[roas_col].max())
        roas_range = st.sidebar.slider("Select ROAS Range", min_roas, max_roas, (min_roas, max_roas))

   
        filtered_data = data[
            (data[campaign_col].isin(selected_campaigns)) & 
            (data[roas_col] >= roas_range[0]) & 
            (data[roas_col] <= roas_range[1])
        ]

        # ---
        st.sidebar.markdown("---")
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            filtered_data.to_excel(writer, index=False, sheet_name='Filtered_Analysis')
        st.sidebar.download_button("📥 Download Filtered Report", data=output.getvalue(), file_name="Marketing_Analysis.xlsx")

        # --- --
        st.markdown("### 📌 Key Performance Indicators")
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("💰 Total Spend", f"{filtered_data[spend_col].sum():,.2f}")
        m2.metric("🖱️ Total Clicks", f"{filtered_data[clicks_col].sum():,.0f}")
        m3.metric("📈 Avg ROAS", f"{filtered_data[roas_col].mean():.2f}x")
        m4.metric("🎯 Avg CTR", f"{filtered_data['CTR %'].mean():.2f}%")

        st.markdown("---")

        # --- 
        st.markdown("### 📊 Visual Insights")
        c1, c2 = st.columns(2)
        
        with c1:
            #
            fig1 = px.bar(filtered_data, x=campaign_col, y=roas_col, 
                         title="ROAS by Campaign", 
                         color=roas_col, color_continuous_scale='Blues')
            fig1.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig1, use_container_width=True)
            
        with c2:
            
            fig2 = px.pie(filtered_data, values=spend_col, names=campaign_col, 
                         title="Budget Distribution", hole=0.3)
            st.plotly_chart(fig2, use_container_width=True)

       
        st.markdown("### 🔍 Detailed Data Analysis")
        
        styled_df = filtered_data[[campaign_col, spend_col, clicks_col, "CTR %", "CPC", roas_col]].style.background_gradient(subset=[roas_col], cmap="YlGn")
        st.dataframe(styled_df, use_container_width=True)

        if st.sidebar.checkbox("Show AI Summary"):
            st.markdown("---")
            st.markdown("### 🤖 AI Automated Insights")
            best_camp = filtered_data.loc[filtered_data[roas_col].idxmax()]
            summary = f"""
            * Your best performing campaign is **{best_camp[campaign_col]}** with a ROAS of **{best_camp[roas_col]:.2f}x**.
            * Average CPC across filtered campaigns is **{filtered_data['CPC'].mean():.2f}**.
            """
            st.write(summary)

    except Exception as e:
        st.error(f"Error: {e}")
else:
    st.info("👋 Welcome Ahmed! Please upload your CSV file in the sidebar.")