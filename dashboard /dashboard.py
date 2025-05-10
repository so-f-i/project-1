import streamlit as st
import pandas as pd
import plotly.express as px


st.set_page_config(
    page_title="Анализ чартов Яндекс.Музыки",
    layout="wide",
    initial_sidebar_state="expanded"
)
# Функция загрузки данных
@st.cache_data
def load_data():
    try:
    
        data_url = "https://raw.githubusercontent.com/so-f-i/project-1/main/data/chart_clean.csv"
        df = pd.read_csv(data_url)
        return df
    except Exception as e:
        st.error(f"Ошибка загрузки данных: {e}")
        return None

# Загружаем данные
df = load_data()

if df is None:
    st.stop()  

# Навигация
st.sidebar.title("Навигация")
page = st.sidebar.radio(
    "Выберите раздел:",
    ("Главная", "Данные", "EDA", "Тренды", "Выводы")
)

# Главная страница
if page == "Главная":
    st.title("Анализ чарта Топ-100 Яндекс.Музыки")
    st.markdown("""
    **Интерактивный дэшборд для анализа факторов, влияющих на позиции треков в чартах.**
    
    **Описание:** Мы проанализировали чарт "Топ-100" Яндекс Музыки, чтобы понять, как факторы — длительность трека, жанр, год выпуска и особенности названия — влияют на успех песни. Этот анализ поможет лучше понять современные тренды и узнать, что определяет успех песен в российских музыкальных чартах
    
    **Источник данных:** API Яндекс.Музыки (топ-100 треков)
    
    **Собранные данные включают:** названия и id треков, исполнителей, позиции в чарте, длительность, жанры и год выпуска, что позволяет анализировать закономерности популярности песен.
    """)


# Раздел "Данные"
elif page == "Данные":
    st.header("Исходные данные")

    # Фильтры
    genre_filter = st.multiselect(
        "Фильтр по жанрам",
        options=df['Genre'].unique()
    )

    year_filter = st.slider(
        "Фильтр по году выпуска",
        min_value=int(df['Year'].min()),
        max_value=int(df['Year'].max()),
        value=(int(df['Year'].min()), int(df['Year'].max()))
    )

    # Применение фильтров
    filtered_df = df.copy()
    if genre_filter:
        filtered_df = filtered_df[filtered_df['Genre'].isin(genre_filter)]
    filtered_df = filtered_df[
        (filtered_df['Year'] >= year_filter[0]) &
        (filtered_df['Year'] <= year_filter[1])
        ]

    # Статистика
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Всего треков", len(filtered_df))
    with col2:
        st.metric("Уникальных жанров", filtered_df['Genre'].nunique())
    with col3:
        st.metric("Годы выпуска", f"{year_filter[0]} - {year_filter[1]}")

    # Таблица данных
    st.dataframe(
        filtered_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Position": st.column_config.NumberColumn("Позиция", format="%d"),
            "Duration_sec": st.column_config.ProgressColumn(
                "Длительность",
                format="%f с",
                min_value=0,
                max_value=500
            )
        }
    )

# Раздел EDA
elif page == "EDA":
    st.header("Разведочный анализ данных")

    tab1, tab2, tab3 = st.tabs(["Распределение жанров", "Длительность треков", "Годы выпуска"])

    with tab1:
        genre_counts = df['Genre'].value_counts().reset_index()
        fig = px.pie(
            genre_counts,
            names='Genre',
            values='count',
            title='Распределение по жанрам'
        )
        st.plotly_chart(fig, use_container_width=True)

    with tab2:
        fig = px.histogram(
            df,
            x='Duration_sec',
            nbins=20,
            title='Распределение длительности треков'
        )
        st.plotly_chart(fig, use_container_width=True)

    with tab3:
        fig = px.histogram(
            df,
            x='Year',
            title='Распределение по годам выпуска'
        )
        st.plotly_chart(fig, use_container_width=True)

# Раздел "Тренды"
elif page == "Тренды":
    st.header("Анализ трендов")

    # Интерактивные фильтры
    analysis_type = st.selectbox(
        "Выберите анализ:",
        ["Влияние длительности", "Влияние жанра", "Влияние года выпуска"]
    )

    if analysis_type == "Влияние длительности":
        fig = px.scatter(
            df,
            x='Position',
            y='Duration_sec',
            trendline="lowess",
            title='Зависимость позиции от длительности трека'
        )
        st.plotly_chart(fig, use_container_width=True)

    elif analysis_type == "Влияние жанра":
        top_genres = st.slider(
            "Количество топовых жанров для анализа",
            2, 10, 5
        )
        top_genres_list = df['Genre'].value_counts().head(top_genres).index
        filtered_df = df[df['Genre'].isin(top_genres_list)]

        fig = px.box(
            filtered_df,
            x='Genre',
            y='Position',
            title='Распределение позиций по жанрам'
        )
        st.plotly_chart(fig, use_container_width=True)

    elif analysis_type == "Влияние года выпуска":
        fig = px.scatter(
            df,
            x='Year',
            y='Position',
            trendline="lowess",
            title='Зависимость позиции от года выпуска'
        )
        st.plotly_chart(fig, use_container_width=True)

elif page == "Выводы":
    st.header("Ключевые выводы и рекомендации")

    # Инсайт 1
    st.markdown("""
    > 🎵 **Оптимальная длительность**: 3–4 минуты  
    > *Это золотая середина для запоминаемости и коммерческой эффективности. Исключения — песни, где узнаваемость артиста важнее длины.*  
    """)

    # Инсайт 2
    st.markdown("""
    > 🆕 **Новизна в чарте**: 83% треков — последние 2 года  
    > *Регулярные релизы — залог успеха. Старые песни закрепляются как культовые или вирусные мемы.*  
    """)

    # Инсайт 3
    st.markdown("""
    > 🎤 **Жанры-лидеры**: Русский поп и рэп  
    > *Обладает 73% топа, но конкуренция высокая. Чтобы выделиться — нужно быть уникальным или точно попадать в тренды. Фонк пока ниша, но перспективная.*  
    """)

    # Инсайт 4
    st.markdown("""
    > ✨ **Названия**: Простые, запоминающиеся слова  
    > *"Худи", "Не нужна" — мгновенно запоминаются и вызывают ассоциации. Особенно важно для TikTok-эпохи, где секунда решает всё.*  
    """)

    # Рекомендации для артистов
    st.subheader("Рекомендации для артистов")
    st.markdown("""
    1. Регулярно выпускайте новые треки — 3-5 в год.  
    2. Оптимизируйте длину — 3–4 минуты.  
    3. Используйте запоминающиеся названия — простые и эмоциональные.  
    4. Тестируйте нишевые жанры, чтобы снизить конкуренцию.  
    """)

    # Дальнейшее развитие
    st.subheader("Дальнейшее развитие")
    st.markdown("""
    - Добавить анализ текстов песен (проблема с API текстов).  
    - Исследовать влияние времени релиза.  
    - Проанализировать связь с плейлистами.  
    - Внедрить парсинг Shazam для оценки кросс-платформенной популярности.  
    - Провести A/B-тестирование названий через Яндекс.Метрику.  
    """)
