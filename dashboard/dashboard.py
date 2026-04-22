import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
sns.set(style='dark')

# Helper function yang dibutuhkan untuk menyiapkan berbagai dataframe

def create_monthly_df(df):
    monthly_df = df.resample(rule='M', on='dteday').agg({
        "instant": "nunique",
        "cnt": "sum"
    })
    monthly_df = monthly_df.reset_index()
    monthly_df.rename(columns={
        "instant": "ride_count",
        "cnt": "total_rentals"
    }, inplace=True)
    return monthly_df
 
def create_season_df(df):
    season_df = df.groupby("season_label")["cnt"].mean().reset_index()
    season_df.rename(columns={"cnt": "avg_rentals"}, inplace=True)
    season_df["season_label"] = pd.Categorical(
        season_df["season_label"],
        ["Spring", "Summer", "Fall", "Winter"]
    )
    season_df = season_df.sort_values("season_label")
    return season_df
 
def create_weather_df(df):
    weather_df = df.groupby("weather_label")["cnt"].mean().reset_index()
    weather_df.rename(columns={"cnt": "avg_rentals"}, inplace=True)
    return weather_df
 
def create_hourly_df(df):
    hourly_df = df.groupby("hr")["cnt"].mean().reset_index()
    hourly_df.rename(columns={"cnt": "avg_rentals"}, inplace=True)
    return hourly_df
 
def create_usertype_df(df):
    usertype_df = df.groupby("workingday")[["casual", "registered"]].mean().reset_index()
    usertype_df["workingday"] = usertype_df["workingday"].map({
        0: "Libur/Akhir Pekan",
        1: "Hari Kerja"
    })
    return usertype_df
 
def create_weekday_df(df):
    weekday_df = df.groupby("weekday_label")[["casual", "registered"]].mean().reset_index()
    weekday_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    weekday_df["weekday_label"] = pd.Categorical(
        weekday_df["weekday_label"], categories=weekday_order, ordered=True
    )
    weekday_df = weekday_df.sort_values("weekday_label")
    return weekday_df
 
def create_time_segment_df(df):
    def segment(hr):
        if hr < 6:
            return "Dini Hari (00-05)"
        elif hr < 12:
            return "Pagi (06-11)"
        elif hr < 18:
            return "Siang (12-17)"
        else:
            return "Malam (18-23)"
    df = df.copy()
    df["time_segment"] = df["hr"].apply(segment)
    segment_df = df.groupby("time_segment")["cnt"].mean().reset_index()
    segment_df.rename(columns={"cnt": "avg_rentals"}, inplace=True)
    return segment_df

# Load cleaned data

day_df = pd.read_csv("day.csv")
hour_df = pd.read_csv("hour.csv")

day_df["dteday"] = pd.to_datetime(day_df["dteday"])
hour_df["dteday"] = pd.to_datetime(hour_df["dteday"])
 
season_map  = {1: "Spring", 2: "Summer", 3: "Fall", 4: "Winter"}
weather_map = {1: "Clear",  2: "Mist",   3: "Light Rain/Snow", 4: "Heavy Rain/Snow"}
weekday_map = {0: "Sunday", 1: "Monday", 2: "Tuesday", 3: "Wednesday",
               4: "Thursday", 5: "Friday", 6: "Saturday"}
 
for df in [day_df, hour_df]:
    df["season_label"]  = df["season"].map(season_map)
    df["weather_label"] = df["weathersit"].map(weather_map)
    df["weekday_label"] = df["weekday"].map(weekday_map)
 
day_df.sort_values("dteday", inplace=True)
day_df.reset_index(drop=True, inplace=True)

with st.sidebar:
    st.markdown(
        "<h2 style='text-align: center; font-size: 20px;'>Bike Sharing Dashboard</h1>",
        unsafe_allow_html=True
    )

# Filter data

    min_date = day_df["dteday"].min()
    max_date = day_df["dteday"].max()

# Mengambil start_date &end_date dari date_input
    start_date, end_date = st.date_input(
        label="Rentang Waktu",
        min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

main_day_df  = day_df[(day_df["dteday"] >= pd.Timestamp(start_date)) &
                      (day_df["dteday"] <= pd.Timestamp(end_date))]
main_hour_df = hour_df[(hour_df["dteday"] >= pd.Timestamp(start_date)) &
                       (hour_df["dteday"] <= pd.Timestamp(end_date))]
# st.dataframe(main_df)

# # Menyiapkan berbagai dataframe

monthly_df      = create_monthly_df(main_day_df)
season_df       = create_season_df(main_day_df)
weather_df      = create_weather_df(main_day_df)
hourly_df       = create_hourly_df(main_hour_df)
usertype_df     = create_usertype_df(main_day_df)
weekday_df      = create_weekday_df(main_day_df)
time_segment_df = create_time_segment_df(main_hour_df)

st.header("Bike Sharing Dashboard 🚲")

# plot statistik utama
st.subheader("Statistik Utama")
 
col1, col2, col3 = st.columns(3)
 
with col1:
    total_rentals = main_day_df["cnt"].sum()
    st.metric("Total Peminjaman", value=f"{total_rentals:,}")
 
with col2:
    total_casual = main_day_df["casual"].sum()
    st.metric("Total Pengguna Kasual", value=f"{total_casual:,}")
 
with col3:
    total_registered = main_day_df["registered"].sum()
    st.metric("Total Pengguna Terdaftar", value=f"{total_registered:,}")

# plot tren peminjaman bulanan
st.subheader("Tren Peminjaman Bulanan")
 
fig, ax = plt.subplots(figsize=(16, 6))
ax.plot(
    monthly_df["dteday"],
    monthly_df["total_rentals"],
    marker='o',
    linewidth=2,
    color="#90CAF9"
)
ax.set_xlabel("Bulan", fontsize=14)
ax.set_ylabel("Total Peminjaman", fontsize=14)
ax.tick_params(axis='x', labelsize=10)
ax.tick_params(axis='y', labelsize=12)
st.pyplot(fig)

# plot pengaruh cuaca & musim terhadap penjualan
st.subheader("Pengaruh Cuaca & Musim terhadap Peminjaman")
 
col1, col2 = st.columns(2)
 
with col1:
    fig, ax = plt.subplots(figsize=(10, 6))
    colors = ["#E8D1A7", "#E8D1A7", "#84592B", "#E8D1A7"]
    sns.barplot(
        x="season_label",
        y="avg_rentals",
        data=season_df,
        palette=colors,
        ax=ax
    )
    ax.set_title("Rata-rata Peminjaman per Musim", fontsize=16)
    ax.set_xlabel(None)
    ax.set_ylabel("Rata-rata Peminjaman", fontsize=12)
    ax.tick_params(axis='x', labelsize=12)
    for p in ax.patches:
        ax.annotate(f'{p.get_height():.0f}',
                    (p.get_x() + p.get_width() / 2., p.get_height()),
                    ha='center', va='bottom', fontsize=10)
    st.pyplot(fig)
 
with col2:
    fig, ax = plt.subplots(figsize=(10, 6))
    colors_w = ["#C8D9E6", "#2F4156", "#2F4156"]
    sns.barplot(
        x="weather_label",
        y="avg_rentals",
        data=weather_df.sort_values("avg_rentals", ascending=False),
        palette=colors_w,
        ax=ax
    )
    ax.set_title("Rata-rata Peminjaman per Kondisi Cuaca", fontsize=16)
    ax.set_xlabel(None)
    ax.set_ylabel("Rata-rata Peminjaman", fontsize=12)
    ax.tick_params(axis='x', labelsize=11)
    for p in ax.patches:
        ax.annotate(f'{p.get_height():.0f}',
                    (p.get_x() + p.get_width() / 2., p.get_height()),
                    ha='center', va='bottom', fontsize=10)
    st.pyplot(fig)

# plot waktu puncak peminjaman per jam
st.subheader("Waktu Puncak Peminjaman per Jam")
 
fig, ax = plt.subplots(figsize=(16, 6))
ax.plot(
    hourly_df["hr"],
    hourly_df["avg_rentals"],
    marker='o',
    linewidth=2,
    color="#E91E63",
    markersize=5
)
ax.fill_between(hourly_df["hr"], hourly_df["avg_rentals"], alpha=0.15, color="#E91E63")
ax.axvline(x=8,  color="gray",   linestyle="--", alpha=0.7, label="Jam 08:00")
ax.axvline(x=17, color="orange", linestyle="--", alpha=0.7, label="Jam 17:00")
ax.set_xlabel("Jam", fontsize=14)
ax.set_ylabel("Rata-rata Peminjaman", fontsize=14)
ax.set_xticks(range(0, 24))
ax.legend(fontsize=12)
ax.tick_params(axis='both', labelsize=12)
st.pyplot(fig)

# plot pola pengguna kasual vs terdaftar
st.subheader("Pola Pengguna Kasual vs Terdaftar")
 
col1, col2 = st.columns(2)
 
with col1:
    fig, ax = plt.subplots(figsize=(10, 6))
    x = range(len(usertype_df))
    width = 0.35
    ax.bar([i - width/2 for i in x], usertype_df["casual"],
           width, label="Kasual", color="#B8D8E0")
    ax.bar([i + width/2 for i in x], usertype_df["registered"],
           width, label="Terdaftar", color="#6DB5CA")
    ax.set_xticks(list(x))
    ax.set_xticklabels(usertype_df["workingday"], fontsize=12)
    ax.set_title("Hari Kerja vs Hari Libur", fontsize=16)
    ax.set_ylabel("Rata-rata Peminjaman", fontsize=12)
    ax.legend(fontsize=11)
    st.pyplot(fig)
 
with col2:
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(weekday_df["weekday_label"], weekday_df["casual"],
            marker='o', linewidth=2, color="#B8D8E0", label="Kasual")
    ax.plot(weekday_df["weekday_label"], weekday_df["registered"],
            marker='s', linewidth=2, color="#6DB5CA", label="Terdaftar")
    ax.set_title("Tren per Hari dalam Seminggu", fontsize=16)
    ax.set_xlabel(None)
    ax.set_ylabel("Rata-rata Peminjaman", fontsize=12)
    ax.tick_params(axis='x', labelsize=10)
    ax.legend(fontsize=11)
    st.pyplot(fig)

# plot segmentasi akhir
st.subheader("Analisis Lanjutan: Segmentasi Waktu")
 
fig, ax = plt.subplots(figsize=(10, 5))
segment_order = ["Dini Hari (00-05)", "Pagi (06-11)", "Siang (12-17)", "Malam (18-23)"]
colors_seg = ["#E9CEAF", "#E9CEAF", "#ED8D2A", "#E9CEAF"]
time_segment_df["time_segment"] = pd.Categorical(
    time_segment_df["time_segment"], categories=segment_order, ordered=True
)
time_segment_df = time_segment_df.sort_values("time_segment")
sns.barplot(
    x="time_segment",
    y="avg_rentals",
    data=time_segment_df,
    palette=colors_seg,
    ax=ax
)
ax.set_title("Rata-rata Peminjaman per Segmen Waktu", fontsize=16)
ax.set_xlabel(None)
ax.set_ylabel("Rata-rata Peminjaman", fontsize=12)
ax.tick_params(axis='x', labelsize=11)
for p in ax.patches:
    ax.annotate(f'{p.get_height():.0f}',
                (p.get_x() + p.get_width() / 2., p.get_height()),
                ha='center', va='bottom', fontsize=11)
st.pyplot(fig)