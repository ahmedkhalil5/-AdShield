import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt

# محاولة استدعاء مكتبة Mistral بشكل آمن
try:
    from mistralai.client import MistralClient
    from mistralai.models.chat_completion import ChatMessage
    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False

# --- 1. إعدادات الصفحة ---
st.set_page_config(page_title="AD-SHIELD PRO: WAR ROOM", layout="wide")

# --- 2. التحقق من مفتاح الـ API ---
# الكود بيسحب المفتاح تلقائياً من الـ Secrets اللي إنت ضفتها في إعدادات Streamlit
if "MISTRAL_API_KEY" in st.secrets:
    MISTRAL_API_KEY = st.secrets["MISTRAL_API_KEY"]
else:
    # ده المفتاح اللي كان ظاهر في صورك، حطيته كاحتياط لو الـ Secrets مش مقروءة
    MISTRAL_API_KEY = "GQgcXZycQirade3Mk7ZN8C6yof7gykiD"

# تعريف الـ Client
if AI_AVAILABLE:
    client = MistralClient(api_key=MISTRAL_API_KEY)

# --- 3. تصميم واجهة البرنامج ---
st.title("⚡ AD-SHIELD: WAR ROOM")
st.markdown("### نظام تحليل الحملات الإعلانية المدعوم بالذكاء الاصطناعي")

# القائمة الجانبية لرفع الملفات
st.sidebar.header("📂 إدارة البيانات")
uploaded_file = st.sidebar.file_uploader("ارفع ملف نتائج الإعلانات (CSV)", type="csv")

if uploaded_file:
    # قراءة الملف
    df = pd.read_csv(uploaded_file)
    
    # تنظيف أسماء الأعمدة (مسح الفراغات وتحويلها لحروف صغيرة لضمان التعرف عليها)
    df.columns = [c.strip().lower() for c in df.columns]

    # --- 4. عرض البيانات الخام ---
    with st.expander("👁️ استعراض البيانات المرفوعة"):
        st.dataframe(df)

    # --- 5. قسم التحليلات الذكية (Performance Dashboard) ---
    st.divider()
    st.subheader("📊 Performance Dashboard")

    try:
        # محاولة التعرف على الأعمدة آلياً (لو الأسماء متغيرة في الملف)
        spend_col = [c for c in df.columns if 'spent' in c or 'cost' in c or 'صرف' in c][0]
        roas_col = [c for c in df.columns if 'roas' in c or 'return' in c or 'عائد' in c][0]
        name_col = [c for c in df.columns if 'campaign' in c or 'name' in c or 'اسم' in c][0]

        # عرض مؤشرات الأداء الرئيسية (KPIs)
        kpi1, kpi2, kpi3 = st.columns(3)
        kpi1.metric("Total Spend", f"${df[spend_col].sum():,.2f}")
        kpi2.metric("Avg ROAS", f"{df[roas_col].mean():.2f}x")
        kpi3.metric("Top Campaign", df.loc[df[roas_col].idxmax(), name_col])

        # --- 6. محرك القرارات (Scale vs Kill) ---
        st.divider()
        st.subheader("🚀 Decision Center (Scaling)")
        
        # تحديد هدف الـ ROAS المطلوب
        target_roas = st.slider("حدد الـ Target ROAS المطلوب للحكم على الحملات", 0.5, 10.0, 3.0)
        
        col_scale, col_kill = st.columns(2)
        
        with col_scale:
            st.success("✅ Scale These (الحملات الرابحة)")
            winners = df[df[roas_col] >= target_roas]
            if not winners.empty:
                st.write(winners[[name_col, roas_col, spend_col]])
            else:
                st.write("مفيش حملات محققة الهدف حالياً.")

        with col_kill:
            st.error("🛑 Kill/Optimize (الحملات الخاسرة)")
            losers = df[df[roas_col] < target_roas]
            if not losers.empty:
                st.write(losers[[name_col, roas_col, spend_col]])
            else:
                st.write("كل الحملات أداؤها ممتاز!")

        # --- 7. طلب تحليل تفصيلي من الذكاء الاصطناعي (Mistral AI) ---
        st.divider()
        st.subheader("🤖 AI Strategic Analysis")
        
        if st.button("اضغط هنا لتحليل البيانات بواسطة AI"):
            if not AI_AVAILABLE:
                st.error("مكتبة Mistral غير مثبتة في السيرفر. تأكد من ملف requirements.txt")
            else:
                with st.spinner("جاري إرسال البيانات للذكاء الاصطناعي..."):
                    # تجهيز ملخص للحملات لإرساله للـ AI
                    summary_data = df[[name_col, spend_col, roas_col]].to_string()
                    
                    prompt = f"""
                    أنت خبير إعلانات (Media Buyer) محترف. حلل البيانات التالية وقدم لي:
                    1. تحليل سريع للحملات الأفضل والأسوأ.
                    2. نصيحة محددة لزيادة الأرباح (Scaling Strategy) وتوزيع الميزانية.
                    
                    البيانات:
                    {summary_data}
                    """
                    
                    messages = [ChatMessage(role="user", content=prompt)]
                    response = client.chat(model="mistral-tiny", messages=messages)
                    st.info(response.choices[0].message.content)

        # --- 8. الرسوم البيانية ---
        st.divider()
        st.subheader("📈 Visual Performance Visualizer")
        fig = px.bar(df, x=name_col, y=spend_col, color=roas_col, 
                     title="توزيع الصرف مقابل العائد لكل حملة",
                     color_continuous_scale="RdYlGn",
                     labels={spend_col: "المبلغ المصروف", roas_col: "العائد (ROAS)"})
        st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        st.warning(f"⚠️ تنبيه: لم يتم العثور على أعمدة (Name, Spend, ROAS) بشكل صريح. تأكد من تسمية الأعمدة في ملف الإكسيل بشكل صحيح. الخطأ: {e}")

else:
    # رسالة ترحيبية تظهر في البداية
    st.info("👋 مرحباً بك في AD-SHIELD. من فضلك ارفع ملف الـ CSV من القائمة الجانبية لبدء الحرب!")
