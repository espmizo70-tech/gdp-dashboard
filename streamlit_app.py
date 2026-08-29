import streamlit as st
import pandas as pd
import plotly.express as px

# ضبط إعدادات الصفحة
st.set_page_config(page_title="GDP Dashboard", page_icon="📊", layout="wide")

st.title("📊 لوحة تحليل الناتج المحلي الإجمالي (GDP Dashboard)")
st.markdown("تحليل وتتبع نمو الناتج المحلي الإجمالي والدول الأكثر نمواً.")

# دالة تحميل البيانات مع التخزين المؤقت
@st.cache_data
def load_data():
    # تعديل اسم الملف حسب الملف الموجود داخل مجلد data/
    return pd.read_csv("data/gdp_data.csv")

try:
    df = load_data()

    # القائمة الجانبية لتصفية البيانات
    st.sidebar.header("🔍 خيارات التصفية")
    
    years = sorted(df['Year'].unique(), reverse=True)
    selected_year = st.sidebar.selectbox("اختر السنة", years)

    countries = st.sidebar.multiselect("اختر الدول للمقارنة", options=df['Country'].unique(), default=df['Country'].unique()[:5])

    # تصفية البيانات بناءً على التحديد
    df_year = df[df['Year'] == selected_year]
    df_filtered = df[df['Country'].isin(countries)]

    # 1. بطاقات المؤشرات الرئيسية (KPIs)
    col1, col2, col3 = st.columns(3)
    total_gdp = df_year['GDP'].sum()
    avg_gdp = df_year['GDP'].mean()
    top_country = df_year.loc[df_year['GDP'].idxmax()]['Country'] if not df_year.empty else "N/A"

    col1.metric("إجمالي الناتج العالمي", f"${total_gdp:,.0f}")
    col2.metric("متوسط الناتج لكل دولة", f"${avg_gdp:,.0f}")
    col3.metric("الأعلى ناتجاً هذا العام", top_country)

    st.markdown("---")

    # 2. رسم بياني لأعلى 10 دول في السنة المحددة
    col_chart1, col_chart2 = st.columns(2)

    with col_chart1:
        st.subheader(f"🏆 أعلى 10 دول لعام {selected_year}")
        top10 = df_year.sort_values(by="GDP", ascending=False).head(10)
        fig_bar = px.bar(
            top10, 
            x="Country", 
            y="GDP", 
            color="GDP", 
            color_continuous_scale="Viridis",
            labels={"GDP": "الناتج المحلي ($)", "Country": "الدولة"}
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    with col_chart2:
        st.subheader("📈 مسار النمو الزمني للدول المختارة")
        fig_line = px.line(
            df_filtered, 
            x="Year", 
            y="GDP", 
            color="Country",
            markers=True,
            labels={"GDP": "الناتج المحلي ($)", "Year": "السنة"}
        )
        st.plotly_chart(fig_line, use_container_width=True)

except Exception as e:
    st.info("💡 تأكد من رفع ملف البيانات `gdp_data.csv` داخل مجلد `data/` على GitHub ليشغل التطبيق البيانات المباشرة.")
