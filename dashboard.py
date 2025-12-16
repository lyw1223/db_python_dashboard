# streamlit run streamlit_dashboard/dashboard.py
from datetime import datetime, timedelta
from pathlib import Path
import pytz
import streamlit as st
import pandas as pd
import json
# import mariadb
import mysql.connector
import plotly.graph_objects as go
from plotly.subplots import make_subplots


st.set_page_config(
    layout="wide",
    page_title="Python Automation",
    page_icon="🔷"
)

# ------------------------------
# Data Load
# ------------------------------
@st.cache_data
def load_data():
    # Streamlit secrets에서 데이터베이스 연결 정보 가져오기
    db_config = {
        "host": st.secrets["db"]["host"],
        "user": st.secrets["db"]["user"],
        "password": st.secrets["db"]["password"],
        "database": st.secrets["db"]["database"],
        "port": st.secrets["db"]["port"]
    }
     # mysql.connector.connect()는 with 구문 지원 안하므로 명시적 close 필요
    conn = mysql.connector.connect(**db_config)
    try:        
        df_ai_table = pd.read_sql_query("SELECT job_id, token, date FROM `ai_response`", conn)
        df_model_create_table = pd.read_sql_query("SELECT * FROM `model_create`", conn)
        df_photo_upload_table = pd.read_sql_query("SELECT * FROM `photo_upload`", conn)

        # 날짜 컬럼 datetime 변환
        df_ai_table['date'] = pd.to_datetime(df_ai_table['date']).dt.date
        df_model_create_table['date'] = pd.to_datetime(df_model_create_table['date']).dt.date
        df_photo_upload_table['date'] = pd.to_datetime(df_photo_upload_table['date']).dt.date

        return df_ai_table, df_model_create_table, df_photo_upload_table
    finally:
        conn.close()        
 
df_ai_table, df_model_create_table, df_photo_upload_table = load_data()
df_ai_table_grouped = df_ai_table.groupby('date').agg({'token': ['sum', 'count']}).sort_index()
df_ai_table_grouped.columns = ['token_sum', 'count']
df_ai_table_grouped['cost'] = df_ai_table_grouped['count'] * 0.25
df_model_create_table = df_model_create_table.sort_values('date', ascending=False)


# ------------------------------
# 외부 파일 로드 (CSS, JavaScript)
# ------------------------------
BASE_DIR = Path(__file__).parent

css_file = BASE_DIR / "dashboard.css"
with open(css_file, "r", encoding="utf-8") as f:
    css_content = f.read()

js_file = BASE_DIR / "dashboard.js"
with open(js_file, "r", encoding="utf-8") as f:
    js_content = f.read()

st.markdown(f"<style>{css_content}</style>", unsafe_allow_html=True)
st.markdown(f"<script>{js_content}</script>", unsafe_allow_html=True)




header_col1, header_col2 = st.columns([8, 2])
with header_col1:
    st.markdown(f"""<div class="header-title">
        <img src="data:image/jpeg;base64,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" 
        style="width: 50px; height: 50px; border-radius: 50%;
        vertical-align: middle; margin-right: 10px;">
        SemiMarket Python Automation
    </div>""", unsafe_allow_html=True)

    if st.button("Data Reload",icon="🔄"): 
        st.cache_data.clear()
        st.rerun()

    # ------------------------------
    # daily, weekly, monthly 작업 내역
    # ------------------------------  
    
    
    daily_tab, weekly_tab, monthly_tab = st.tabs(["📊 daily 작업 내역", "🤖 weekly 작업 내역", "📷 monthly 작업 내역"])
    
    def calculate_period_stats(df_ai, df_model, df_photo, days_ago):
        """기간별 통계를 계산하는 함수
        
        Args:
            df_ai: AI 테이블 데이터프레임
            df_model: 모델 생성 테이블 데이터프레임
            df_photo: 사진 업로드 테이블 데이터프레임
            days_ago: 며칠 전부터 계산할지 (1: 금일, 7: 주간, 30: 월간)
        """
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days_ago-1)
        
        filtered_ai = df_ai[(df_ai['date'] >= start_date) & (df_ai['date'] <= end_date)]
        filtered_model = df_model[(df_model['date'] >= start_date) & (df_model['date'] <= end_date)]
        filtered_photo = df_photo[(df_photo['date'] >= start_date) & (df_photo['date'] <= end_date)]
        
        marketablity_count = len(filtered_ai)
        marketablity_tokens = filtered_ai['token'].sum() if not filtered_ai.empty else 0
        marketablity_cost = marketablity_count * 0.25
        model_create_count = len(filtered_model)
        sgno_count = len(filtered_photo)
        images_count = filtered_photo['count'].sum() if not filtered_photo.empty else 0
        
        return {
            'start_date': start_date,
            'end_date': end_date,
            'marketablity_count': marketablity_count,
            'marketablity_tokens': marketablity_tokens,
            'marketablity_cost': marketablity_cost,
            'model_create_count': model_create_count,
            'sgno_count': sgno_count,
            'images_count': images_count
        }
    
    def render_period_report(stats, period_name, icon):
        """기간별 보고서 렌더링"""
        with st.expander(f"{icon} {period_name} 작업 내역", expanded=False):
            st.markdown(f"""
            ### {stats['start_date']} ~ {stats['end_date']} {period_name} Summary
            """
            )
            st.markdown(f"""
            **Marketability Collector:**
            - AI 컨텐츠 업데이트: {stats['marketablity_count']:,} 건
            - Total Tokens: {stats['marketablity_tokens']:,}
            - Cost: $ {stats['marketablity_cost']:.2f}
            - Model: GPT5-Deep Research
            """
            )
            st.markdown(f"""
            **Model INFO Create:**
            - 모델 생성: {stats['model_create_count']:,} 건
            """
            )
            st.markdown(f"""
            **Photo Upload:**
            - SG NO: {stats['sgno_count']:,} 건
            - Upload Images: {stats['images_count']:,} 건
            """
            )
    
    with daily_tab:
        daily_stats = calculate_period_stats(df_ai_table, df_model_create_table, df_photo_upload_table, 1)
        render_period_report(daily_stats, "Daily", "📊")
    
    with weekly_tab:
        weekly_stats = calculate_period_stats(df_ai_table, df_model_create_table, df_photo_upload_table, 7)
        render_period_report(weekly_stats, "Weekly", "🤖")

    with monthly_tab:
        monthly_stats = calculate_period_stats(df_ai_table, df_model_create_table, df_photo_upload_table, 30)
        render_period_report(monthly_stats, "Monthly", "📷")

    

# 날짜 입력 영역
with header_col2:
    korea_tz = pytz.timezone('Asia/Seoul')
    today_korea = datetime.now(korea_tz).date()
    week_ago_korea = today_korea - timedelta(days=365)     # 초기 검색 기간 설정
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("시작 일", week_ago_korea)
    with col2:
        end_date = st.date_input("종료 일", today_korea)


    st.image('https://splusglobal-my.sharepoint.com/:i:/g/personal/lily_yang_surplusglobal_com/IQBLDyZWjgtqQ5Wzm8KmaTH5AUMGbHUlG7KGTR1SUzwJRgE?e=qFKWhb')


# 데이터 날짜 필터링
filtered = df_ai_table_grouped.loc[(df_ai_table_grouped.index >= start_date) & (df_ai_table_grouped.index <= end_date)]
filtered_model_create = df_model_create_table.loc[(df_model_create_table['date'] >= start_date) & (df_model_create_table['date'] <= end_date)]


# ------------------------------
# AI API 사용 건수 테이블 영역
# ------------------------------
api_df = pd.DataFrame()
total_tokens = 0
total_calls = 0
total_cost = 0.0

if not filtered.empty:
    api_df = filtered.copy()
    api_df.index.name = 'Date'
    api_df = api_df.reset_index().sort_values('Date', ascending=False)
    api_df.columns = ['Date', 'Total Tokens', 'API Calls', 'Cost ($)']
    total_tokens = int(api_df['Total Tokens'].sum())
    total_calls = int(api_df['API Calls'].sum())
    total_cost = api_df['Cost ($)'].sum()

st.subheader(f"AI 모델 컨텐츠 업데이트 집계: ({start_date} ~ {end_date})")
if not api_df.empty:
    st.dataframe(api_df, use_container_width=True)
else:
    st.info("기간 내 데이터가 없습니다.")

# ------------------------------
# AI API 요약 카드 영역
# ------------------------------
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown(f"""<div class="summary-card">
        <div class="summary-label">📊 API 사용 토큰 수</div>
                <div class="summary-value">{total_tokens:,}</div>
    </div>""", unsafe_allow_html=True)
with col2:
    st.markdown(f"""<div class="summary-card">
        <div class="summary-label">🔄 모델 컨텐츠 생성 건수</div>
                <div class="summary-value">{total_calls:,}</div>
    </div>""", unsafe_allow_html=True)
with col3:
    st.markdown(f"""<div class="summary-card">
        <div class="summary-label" title="API 사용 비용 = (요청 건수 * $0.25) 정확한 비용은 OpenAI 공식 홈페이지에서 확인 가능">💰 API 사용 비용</div>
        <div class="summary-value">$ {total_cost:,.0f}</div>
    </div>""", unsafe_allow_html=True)
st.markdown("---")

# ------------------------------
# Model Create 모델 생성 건수 테이블 영역
# ------------------------------

model_df = pd.DataFrame()

if not filtered_model_create.empty:    # 데이터가 있는 경우
    standard_col = 'standard_status' if 'standard_status' in filtered_model_create.columns else 'standard'
    # 날짜별 그룹화 및 집계
    model_create_grouped = filtered_model_create.groupby('date').agg({
        'model_id': 'count',
        standard_col: lambda x: (x == 1).sum() if standard_col in filtered_model_create.columns else 0
    }).reset_index()
    
    model_create_grouped.columns = ['Date', 'Total Count', 'Standardized']
    model_create_grouped['Non-Standardized'] = model_create_grouped['Total Count'] - model_create_grouped['Standardized']
    model_create_grouped = model_create_grouped.sort_values('Date', ascending=False)
    
    model_df = model_create_grouped
       

st.subheader(f"신규 모델생성, 정형화 집계: ({start_date} ~ {end_date})")
if not model_df.empty:
    st.dataframe(model_df, use_container_width=True)
    # ------------------------------
    # Model Create 요약 카드 영역
    # ------------------------------
    total_models = int(model_df['Total Count'].sum())
    total_standardized = int(model_df['Standardized'].sum())
    total_non_standardized = total_models - total_standardized
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(f"""<div class="summary-card">
            <div class="summary-label">신규 모델 생성</div>
            <div class="summary-value">{total_models:,}</div>
        </div>""", unsafe_allow_html=True)
    with col2:
        st.markdown(f"""<div class="summary-card">
            <div class="summary-label"><img src="https://img.icons8.com/?size=48&id=D9RtvkuOe31p&format=png" 
            style="width: 20px; height: 20px; border-radius: 50%;
            vertical-align: middle; margin-right: 5px;"> 정형화</div>
            <div class="summary-value">{total_standardized:,}</div>
        </div>""", unsafe_allow_html=True)
    with col3:
        st.markdown(f"""<div class="summary-card">
            <div class="summary-label">비정형화</div>
            <div class="summary-value">{total_non_standardized:,}</div>
        </div>""", unsafe_allow_html=True)
    st.markdown("---")
else:
    st.info("기간 내 데이터가 없습니다.")
    total_models = 0
    total_standardized = 0
    total_non_standardized = 0
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""<div class="summary-card">
                <div class="summary-label">📦 자동화 모델 생성 건수</div>
                <div class="summary-value">{total_models:,}</div>
        </div>""", unsafe_allow_html=True)
    with col2:
        st.markdown(f"""<div class="summary-card">
            <div class="summary-label"><img src="https://img.icons8.com/?size=48&id=D9RtvkuOe31p&format=png" 
            style="width: 20px; height: 20px; border-radius: 50%;
            vertical-align: middle; margin-right: 5px;"> 정형화</div>
                <div class="summary-value">{total_standardized:,}</div>
        </div>""", unsafe_allow_html=True)
    with col3:
        st.markdown(f"""<div class="summary-card">
            <div class="summary-label">⏳ 비정형화</div>
                <div class="summary-value">{total_non_standardized:,}</div>
        </div>""", unsafe_allow_html=True)
    st.markdown("---")




# ------------------------------
# Photo Upload 사진 업로드 건수 테이블 영역
# ------------------------------
photo_upload_df = pd.DataFrame()
total_photo_upload = 0
total_photo_upload_sgno = 0
total_photo_upload_web_open_chk = 0

filtered_photo_upload = df_photo_upload_table.loc[(df_photo_upload_table['date'] >= start_date) & (df_photo_upload_table['date'] <= end_date)]

if not filtered_photo_upload.empty:
    photo_upload_df = filtered_photo_upload.groupby('date').agg({'count': 'sum', 'sgno': 'count', 'web_open_chk': 'sum'}).reset_index()    
    photo_upload_df.columns = ['Date','Total Count', 'Total sgno', 'Total Web Open Chk']
    photo_upload_df['Date'] = pd.to_datetime(photo_upload_df['Date']).dt.date
    photo_upload_df['Total sgno'] = photo_upload_df['Total sgno'].astype(int)
    photo_upload_df['Total Count'] = photo_upload_df['Total Count'].astype(int)
    photo_upload_df = photo_upload_df.sort_values('Date', ascending=False)
    total_photo_upload = int(photo_upload_df['Total Count'].sum())
    total_photo_upload_sgno = int(photo_upload_df['Total sgno'].sum())
    total_photo_upload_web_open_chk = int(photo_upload_df['Total Web Open Chk'].sum())

st.subheader(f"OneDrive Photo Upload 집계: ({start_date} ~ {end_date})")
if not photo_upload_df.empty:
    st.dataframe(photo_upload_df, use_container_width=True)
else:
    st.info("기간 내 데이터가 없습니다.")

# ------------------------------
# Photo Upload 요약 카드 영역
# ------------------------------
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown(f"""<div class="summary-card">
        <div class="summary-label">이미지 업로드 총 건수</div>
        <div class="summary-value">{total_photo_upload:,}</div>
    </div>""", unsafe_allow_html=True)
with col2:
    st.markdown(f"""<div class="summary-card">
        <div class="summary-label">상품 수량(SG NO)</div>
        <div class="summary-value">{total_photo_upload_sgno:,}</div>
    </div>""", unsafe_allow_html=True)
with col3:
    st.markdown(f"""<div class="summary-card">
        <div class="summary-label">Web Open <img src="https://img.icons8.com/?size=48&id=9fp9k4lPT8us&format=png" style="width: 20px; height: 20px; border-radius: 50%;
        vertical-align: middle; margin-right: 5px;"></div>
        <div class="summary-value">{total_photo_upload_web_open_chk:,}</div>
    </div>""", unsafe_allow_html=True)
st.markdown("---")







# ------------------------------
# 차트 섹션
# ------------------------------
tab1, tab2, tab3 = st.tabs(["📊 마켓터빌리티", "🤖 모델생성", "📷 이미지 업로드"])

# 마켓터빌리티 차트
with tab1:
    if not api_df.empty:
        chart_df_ai = api_df.copy()
        chart_df_ai['Date'] = pd.to_datetime(chart_df_ai['Date'])
        
        fig = make_subplots(
            rows=2, cols=1,
            subplot_titles=('API 사용 & 토큰 사용량', 'API Cost($)'),
            vertical_spacing=0.15,
            row_heights=[1, 1]
        )
        
        # API Calls 바 차트
        fig.add_trace(
            go.Bar(
                x=chart_df_ai['Date'],
                y=chart_df_ai['API Calls'],
                name='API 사용',
                marker_color='#10B981',
                opacity=0.8
            ),
            row=1, col=1
        )
        
        # Tokens 라인
        fig.add_trace(
            go.Scatter(
                x=chart_df_ai['Date'],
                y=chart_df_ai['Total Tokens'],
                name='토큰 사용량',
                mode='lines+markers',
                line=dict(color='#3A7BFF', width=3),
                marker=dict(size=8, color='#3A7BFF'),
                yaxis='y2'
            ),
            row=1, col=1
        )
        
        # Cost 바 차트
        fig.add_trace(
            go.Bar(
                x=chart_df_ai['Date'],
                y=chart_df_ai['Cost ($)'],
                name='Cost($)',
                marker_color='#FF6B6B',
                opacity=0.8
            ),
            row=2, col=1
        )
        
        fig.update_layout(
            height=600,
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(family="Arial", size=12),
            hovermode='x unified'
        )
        
        fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(0,0,0,0.1)', row=1, col=1)
        fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(0,0,0,0.1)', row=2, col=1)
        fig.update_yaxes(title_text="API 사용 건수", showgrid=True, gridwidth=1, gridcolor='rgba(0,0,0,0.1)', row=1, col=1)
        fig.update_yaxes(title_text="API 사용 비용 ($)", showgrid=True, gridwidth=1, gridcolor='rgba(0,0,0,0.1)', row=2, col=1)
        fig.update_yaxes(title_text="토큰 사용량", overlaying='y', side='right', row=1, col=1)
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("기간 내 데이터가 없습니다.")

# 모델생성 차트
with tab2:
    if not model_df.empty:
        chart_df_model = model_df.copy()
        chart_df_model['Date'] = pd.to_datetime(chart_df_model['Date'])
        
        fig = go.Figure()
        
        # Total Count 바 차트
        fig.add_trace(go.Bar(
            x=chart_df_model['Date'],
            y=chart_df_model['Total Count'],
            name='모델 생성',
            marker_color='#3A7BFF',
            opacity=0.8
        ))
        
        # Standardized 바 차트
        fig.add_trace(go.Bar(
            x=chart_df_model['Date'],
            y=chart_df_model['Standardized'],
            name='정형화',
            marker_color='#10B981',
            opacity=0.8
        ))
        
        # Non-Standardized 바 차트
        fig.add_trace(go.Bar(
            x=chart_df_model['Date'],
            y=chart_df_model['Non-Standardized'],
            name='비정형화',
            marker_color='#F59E0B',
            opacity=0.8
        ))
        
        fig.update_layout(
            title='모델 생성 건수 추이',
            xaxis_title='Date',
            yaxis_title='건수',
            height=500,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(family="Arial", size=10),
            hovermode='x unified',
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            barmode='group'
        )
        
        fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(0,0,0,0.1)')
        fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(0,0,0,0.1)')
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("기간 내 데이터가 없습니다.")

# 이미지 업로드 차트
with tab3:
    if not photo_upload_df.empty:
        chart_df_photo = photo_upload_df.copy()
        chart_df_photo['Date'] = pd.to_datetime(chart_df_photo['Date'])
        
        fig = go.Figure()
        
        # Total Count 바 차트
        fig.add_trace(go.Bar(
            x=chart_df_photo['Date'],
            y=chart_df_photo['Total Count'],
            name='이미지 업로드',
            marker_color='#3A7BFF',
            opacity=0.8
        ))
        
        # Total sgno 바 차트
        fig.add_trace(go.Bar(
            x=chart_df_photo['Date'],
            y=chart_df_photo['Total sgno'],
            name='상품 수량(SG NO)',
            marker_color='#10B981',
            opacity=0.8
        ))
        
        # Web Open Chk 바 차트
        fig.add_trace(go.Bar(
            x=chart_df_photo['Date'],
            y=chart_df_photo['Total Web Open Chk'],
            name='Web Open',
            marker_color='#EC4899',
            opacity=0.8
        ))
        
        fig.update_layout(
            title='이미지 업로드 건수 추이',
            xaxis_title='Date',
            yaxis_title='건수',
            height=500,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(family="Arial", size=12),
            hovermode='x unified',
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            barmode='group'
        )
        
        fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(0,0,0,0.1)')
        fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(0,0,0,0.1)')
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("기간 내 데이터가 없습니다.")


# 푸터 영역
st.markdown("---")
st.markdown(
    """
    <div style='text-align: right; color: #888; font-size: 0.9em; padding: 10px 0;'>
        © 2025 SemiMarket DB Team Workload Dashboard. All rights reserved. | Powered by Streamlit
    </div>
    """,
    unsafe_allow_html=True
)

