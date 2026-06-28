import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
import numpy as np

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Dashboard Penyewaan Sepeda",
    page_icon="🚲",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    /* Main background */
    .stApp { background-color: #0f1117; color: #e0e0e0; }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #1a1d27;
        border-right: 1px solid #2e3250;
    }

    /* Metric cards */
    .metric-card {
        background: linear-gradient(135deg, #1e2235 0%, #252a40 100%);
        border: 1px solid #2e3250;
        border-radius: 14px;
        padding: 20px 24px;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    }
    .metric-card .value {
        font-size: 2.2rem;
        font-weight: 700;
        color: #7c9dff;
        line-height: 1.1;
    }
    .metric-card .label {
        font-size: 0.78rem;
        color: #8891b0;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-top: 4px;
    }
    .metric-card .delta {
        font-size: 0.85rem;
        margin-top: 6px;
        font-weight: 600;
    }
    .delta-up   { color: #4ade80; }
    .delta-down { color: #f87171; }

    /* Section headers */
    .section-header {
        font-size: 1.15rem;
        font-weight: 700;
        color: #c9d1f5;
        padding: 10px 0 4px;
        border-bottom: 2px solid #2e3250;
        margin-bottom: 16px;
    }

    /* Chart container */
    .chart-box {
        background: #1e2235;
        border: 1px solid #2e3250;
        border-radius: 14px;
        padding: 20px;
    }

    /* Hide matplotlib toolbar */
    .stPlotlyChart, iframe { border: none !important; }
    div[data-testid="stHorizontalBlock"] > div { gap: 1rem; }
</style>
""", unsafe_allow_html=True)

# ── Colour palette for charts ─────────────────────────────────────────────────
BG      = "#1e2235"
GRID    = "#2e3250"
TEXT    = "#c9d1f5"
BLUE    = "#7c9dff"
TEAL    = "#4fd1c5"
PINK    = "#f687b3"
YELLOW  = "#f6c90e"
GREEN   = "#4ade80"
PURPLE  = "#a78bfa"
PALETTE = [BLUE, TEAL, PINK, YELLOW, GREEN, PURPLE]

def style_ax(ax, title="", xlabel="", ylabel=""):
    ax.set_facecolor(BG)
    ax.figure.patch.set_facecolor(BG)
    for spine in ax.spines.values():
        spine.set_edgecolor(GRID)
    ax.tick_params(colors=TEXT, labelsize=9)
    ax.xaxis.label.set_color(TEXT)
    ax.yaxis.label.set_color(TEXT)
    ax.set_xlabel(xlabel, fontsize=10, color=TEXT)
    ax.set_ylabel(ylabel, fontsize=10, color=TEXT)
    ax.yaxis.grid(True, color=GRID, linewidth=0.6, alpha=0.7)
    ax.set_axisbelow(True)
    if title:
        ax.set_title(title, fontsize=12, fontweight="bold", color=TEXT, pad=12)

# ── Load & prepare data ───────────────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_csv("all_data.csv")
    month_mapping = {1:"Jan",2:"Feb",3:"Mar",4:"Apr",5:"May",6:"Jun",
                     7:"Jul",8:"Aug",9:"Sep",10:"Oct",11:"Nov",12:"Dec"}
    month_order  = list(month_mapping.values())
    day_order    = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
    season_order = ["Spring","Summer","Fall","Winter"]

    df["mnth"]    = df["mnth"].map(month_mapping)
    df["mnth"]    = pd.Categorical(df["mnth"],    categories=month_order,  ordered=True)
    df["weekday"] = pd.Categorical(df["weekday"], categories=day_order,    ordered=True)
    df["season"]  = pd.Categorical(df["season"],  categories=season_order, ordered=True)
    df["dteday"]  = pd.to_datetime(df["dteday"])
    return df

df = load_data()

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🚲 Filter Data")
    st.markdown("---")

    years   = sorted(df["yr"].unique())
    seasons = list(df["season"].cat.categories)
    days    = list(df["weekday"].cat.categories)

    sel_years = st.multiselect("📅 Tahun", years, default=years)
    sel_seasons = st.multiselect("🌤️ Musim", seasons, default=seasons)

    st.markdown("---")
    st.markdown("### 🕐 Rentang Jam")
    hr_min, hr_max = st.slider("Jam", 0, 23, (0, 23))

    st.markdown("---")
    st.markdown("### 📊 Tampilan Chart")
    chart_type = st.radio("Tipe Bar", ["Batang", "Horizontal"], index=0)
    show_avg_line = st.checkbox("Tampilkan garis rata-rata", value=True)

    st.markdown("---")
    st.caption("Dibuat oleh **Saftana Fitri**")

# ── Filter ────────────────────────────────────────────────────────────────────
df_f = df[
    df["yr"].isin(sel_years) &
    df["season"].isin(sel_seasons) &
    df["hr"].between(hr_min, hr_max)
].copy()

# ── KPI Cards ─────────────────────────────────────────────────────────────────
total     = int(df_f["cnt"].sum())
daily_avg = df_f.groupby("dteday")["cnt"].sum().mean()
peak_hr   = int(df_f.groupby("hr")["cnt"].mean().idxmax())
best_day  = df_f.groupby("weekday")["cnt"].sum().idxmax()

# Year-over-year delta
if len(sel_years) == 2:
    y_vals = df_f.groupby("yr")["cnt"].sum().values
    delta_pct = (y_vals[1] - y_vals[0]) / y_vals[0] * 100
    delta_html = f'<div class="delta delta-up">▲ {delta_pct:.1f}% YoY</div>' if delta_pct >= 0 \
                 else f'<div class="delta delta-down">▼ {abs(delta_pct):.1f}% YoY</div>'
else:
    delta_html = ""

st.markdown("## 🚲 Dashboard Penyewaan Sepeda")
st.markdown(f"Menampilkan **{len(df_f):,}** baris data · Tahun **{', '.join(map(str,sel_years))}** · Musim **{', '.join(sel_seasons)}** · Jam **{hr_min}:00 – {hr_max}:00**")
st.markdown("")

c1, c2, c3, c4 = st.columns(4)
cards = [
    (c1, f"{total:,}", "Total Penyewaan", delta_html),
    (c2, f"{daily_avg:,.0f}", "Rata-rata per Hari", ""),
    (c3, f"{peak_hr:02d}:00", "Jam Tersibuk", ""),
    (c4, str(best_day), "Hari Terpopuler", ""),
]
for col, val, lbl, dlt in cards:
    col.markdown(
        f'<div class="metric-card">'
        f'<div class="value">{val}</div>'
        f'<div class="label">{lbl}</div>'
        f'{dlt}'
        f'</div>',
        unsafe_allow_html=True,
    )

st.markdown("<br>", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
#  ROW 1 — Monthly trend + Season breakdown
# ═══════════════════════════════════════════════════════════════════════════════
col_l, col_r = st.columns([3, 2])

with col_l:
    st.markdown('<div class="section-header">📈 Tren Penyewaan per Bulan</div>', unsafe_allow_html=True)
    df_monthly = df_f.groupby(["yr", "mnth"])["cnt"].sum().reset_index()

    fig, ax = plt.subplots(figsize=(7, 3.4))
    colors_yr = [BLUE, TEAL]
    for i, yr in enumerate(sorted(df_monthly["yr"].unique())):
        sub = df_monthly[df_monthly["yr"] == yr].sort_values("mnth")
        ax.plot(sub["mnth"].astype(str), sub["cnt"], marker="o", linewidth=2.2,
                color=colors_yr[i], label=str(yr), markersize=5)
        ax.fill_between(sub["mnth"].astype(str), sub["cnt"], alpha=0.10, color=colors_yr[i])
    if show_avg_line:
        avg_monthly = df_f.groupby("mnth")["cnt"].sum().reset_index().sort_values("mnth")
        ax.plot(avg_monthly["mnth"].astype(str), avg_monthly["cnt"],
                linestyle="--", linewidth=1.2, color=YELLOW, alpha=0.6, label="Gabungan")
    ax.legend(fontsize=8, facecolor=BG, edgecolor=GRID, labelcolor=TEXT)
    plt.xticks(rotation=35, ha="right")
    style_ax(ax, ylabel="Jumlah Penyewa")
    fig.tight_layout()
    st.pyplot(fig)
    plt.close(fig)

with col_r:
    st.markdown('<div class="section-header">🌤️ Penyewaan per Musim</div>', unsafe_allow_html=True)
    df_season = df_f.groupby("season")["cnt"].sum().reset_index().sort_values("season")
    season_colors = [TEAL, GREEN, YELLOW, BLUE]

    fig, ax = plt.subplots(figsize=(4, 3.4))
    bars = ax.bar(df_season["season"].astype(str), df_season["cnt"],
                  color=season_colors[:len(df_season)], edgecolor="none", width=0.55)
    for bar, val in zip(bars, df_season["cnt"]):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + df_season["cnt"].max()*0.01,
                f'{int(val):,}', ha='center', va='bottom', fontsize=7.5, color=TEXT)
    if show_avg_line:
        avg_s = df_season["cnt"].mean()
        ax.axhline(avg_s, color=PINK, linestyle="--", linewidth=1.2, alpha=0.8)
    style_ax(ax, ylabel="Jumlah Penyewa")
    fig.tight_layout()
    st.pyplot(fig)
    plt.close(fig)

# ═══════════════════════════════════════════════════════════════════════════════
#  ROW 2 — Hourly pattern + Day of week
# ═══════════════════════════════════════════════════════════════════════════════
col_l2, col_r2 = st.columns([3, 2])

with col_l2:
    st.markdown('<div class="section-header">🕐 Pola Penyewaan per Jam (Cluster)</div>', unsafe_allow_html=True)
    df_hr = df_f.groupby("hr")["cnt"].mean().reset_index()

    def cluster(v):
        if v < 100:   return "Rendah"
        if v < 250:   return "Sedang"
        return "Tinggi"

    df_hr["Kategori"] = df_hr["cnt"].apply(cluster)
    cat_colors = {"Rendah": PURPLE, "Sedang": BLUE, "Tinggi": PINK}

    fig, ax = plt.subplots(figsize=(7, 3.4))
    for _, row in df_hr.iterrows():
        ax.bar(row["hr"], row["cnt"], color=cat_colors[row["Kategori"]],
               edgecolor="none", width=0.75, alpha=0.92)
    if show_avg_line:
        ax.axhline(df_hr["cnt"].mean(), color=YELLOW, linestyle="--", linewidth=1.2, alpha=0.8, label="Rata-rata")
    patches = [mpatches.Patch(color=v, label=k) for k, v in cat_colors.items()]
    ax.legend(handles=patches, fontsize=8, facecolor=BG, edgecolor=GRID, labelcolor=TEXT)
    ax.set_xticks(range(0, 24))
    style_ax(ax, xlabel="Jam", ylabel="Rata-rata Penyewaan")
    fig.tight_layout()
    st.pyplot(fig)
    plt.close(fig)

with col_r2:
    st.markdown('<div class="section-header">📅 Penyewaan per Hari</div>', unsafe_allow_html=True)
    df_day = df_f.groupby("weekday")["cnt"].sum().reset_index().sort_values("weekday")
    day_labels = [d[:3] for d in df_day["weekday"].astype(str)]

    fig, ax = plt.subplots(figsize=(4, 3.4))
    if chart_type == "Horizontal":
        colors_d = [BLUE if d not in ["Saturday","Sunday"] else TEAL for d in df_day["weekday"].astype(str)]
        bars = ax.barh(day_labels, df_day["cnt"], color=colors_d, edgecolor="none", height=0.6)
        for bar, val in zip(bars, df_day["cnt"]):
            ax.text(val + df_day["cnt"].max()*0.01, bar.get_y() + bar.get_height()/2,
                    f'{int(val):,}', va='center', fontsize=7.5, color=TEXT)
        ax.invert_yaxis()
        style_ax(ax, xlabel="Jumlah Penyewa")
    else:
        colors_d = [BLUE if d not in ["Saturday","Sunday"] else TEAL for d in df_day["weekday"].astype(str)]
        bars = ax.bar(day_labels, df_day["cnt"], color=colors_d, edgecolor="none", width=0.6)
        for bar, val in zip(bars, df_day["cnt"]):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + df_day["cnt"].max()*0.01,
                    f'{int(val):,}', ha='center', va='bottom', fontsize=7, color=TEXT)
        style_ax(ax, ylabel="Jumlah Penyewa")
    if show_avg_line:
        avg_d = df_day["cnt"].mean()
        if chart_type == "Horizontal":
            ax.axvline(avg_d, color=YELLOW, linestyle="--", linewidth=1.2, alpha=0.8)
        else:
            ax.axhline(avg_d, color=YELLOW, linestyle="--", linewidth=1.2, alpha=0.8)
    fig.tight_layout()
    st.pyplot(fig)
    plt.close(fig)

# ═══════════════════════════════════════════════════════════════════════════════
#  ROW 3 — Heatmap jam × hari
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-header">🔥 Heatmap Penyewaan: Jam × Hari</div>', unsafe_allow_html=True)

day_order_abbr = ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]
df_heat = df_f.copy()
df_heat["weekday_abbr"] = df_heat["weekday"].astype(str).str[:3]
pivot = df_heat.pivot_table(index="weekday_abbr", columns="hr", values="cnt",
                             aggfunc="mean").reindex(day_order_abbr)

fig, ax = plt.subplots(figsize=(14, 3))
sns.heatmap(pivot, ax=ax, cmap="YlOrRd", linewidths=0.3, linecolor=BG,
            cbar_kws={"shrink": 0.8}, annot=False)
ax.set_facecolor(BG)
fig.patch.set_facecolor(BG)
ax.tick_params(colors=TEXT, labelsize=8)
ax.set_xlabel("Jam dalam Sehari", fontsize=10, color=TEXT)
ax.set_ylabel("")
ax.set_xticklabels([f"{h:02d}:00" for h in range(hr_min, hr_max+1)], rotation=45, ha="right")
cbar = ax.collections[0].colorbar
cbar.ax.tick_params(colors=TEXT, labelsize=8)
fig.tight_layout()
st.pyplot(fig)
plt.close(fig)

# ═══════════════════════════════════════════════════════════════════════════════
#  Raw Data Table (collapsible)
# ═══════════════════════════════════════════════════════════════════════════════
with st.expander("🗂️ Lihat Data Mentah"):
    sample = df_f[["dteday","hr","weekday","mnth","yr","season","cnt"]].sort_values("dteday")
    st.dataframe(
        sample.rename(columns={"dteday":"Tanggal","hr":"Jam","weekday":"Hari",
                                "mnth":"Bulan","yr":"Tahun","season":"Musim","cnt":"Penyewaan"}),
        use_container_width=True, height=300
    )
    csv = sample.to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Download CSV", csv, "filtered_data.csv", "text/csv")

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    "<div style='text-align:center;color:#8891b0;font-size:0.8rem;'>"
    "🚲 Dashboard Penyewaan Sepeda · Dibuat oleh <b>Saftana Fitri</b>"
    "</div>",
    unsafe_allow_html=True,
)
