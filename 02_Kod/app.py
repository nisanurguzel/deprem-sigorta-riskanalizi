import os
import glob
import json
import pandas as pd
import streamlit as st
import plotly.express as px

st.set_page_config(page_title="G07 Deprem Risk Segmentasyonu", layout="wide")

DUZ = str.maketrans("çğıöşüÇĞİÖŞÜ", "cgiosuCGIOSU")


def norm(s):
    return str(s).translate(DUZ).lower()


def yol_bul(dosya):
    for klasor in [".", "01_Veri", "../01_Veri", "data"]:
        p = os.path.join(klasor, dosya)
        if os.path.exists(p):
            return p
    return None


@st.cache_data
def oku(dosya):
    p = yol_bul(dosya)
    return pd.read_csv(p) if p else None


def sutun_bul(df, adaylar):
    for c in df.columns:
        if any(a in norm(c) for a in adaylar):
            return c
    return None


def sec(df, etiket, adaylar, sayisal=False):
    secenekler = [None] + [
        c for c in df.columns if (not sayisal or pd.api.types.is_numeric_dtype(df[c]))
    ]
    varsayilan = sutun_bul(df, adaylar)
    idx = secenekler.index(varsayilan) if varsayilan in secenekler else 0
    return st.sidebar.selectbox(etiket, secenekler, index=idx)


# ---------------- Veri ----------------
risk = oku("il_risk_skorlari.csv")
ozellik = oku("il_ozellikleri_nufus.csv")
deprem = oku("deprem_temiz.csv")

if risk is None:
    st.error("il_risk_skorlari.csv bulunamadı. app.py ile aynı klasöre veya 01_Veri klasörüne koyun.")
    st.stop()

df = risk.copy()
if ozellik is not None:
    il_r = sutun_bul(risk, ["il", "province", "sehir"])
    il_o = sutun_bul(ozellik, ["il", "province", "sehir"])
    if il_r and il_o:
        ek = ozellik[[c for c in ozellik.columns if c == il_o or c not in risk.columns]]
        df = risk.merge(ek, left_on=il_r, right_on=il_o, how="left", suffixes=("", "_oz"))

st.sidebar.header("Sütun eşleştirme")
st.sidebar.caption("Otomatik bulundu. Yanlışsa buradan değiştirin.")
IL = sec(df, "İl sütunu", ["il", "province", "sehir"])
SKOR = sec(df, "Risk skoru / segment (1-5)", ["risk_skoru"], True)
NUFUS = sec(df, "Nüfus", ["nufus", "pop"], True)
SAYI = sec(df, "Deprem sayısı", ["sayi", "count", "adet", "n_"], True)
MAXM = sec(df, "Maks. büyüklük", ["max", "maks"], True)

if not IL or not SKOR:
    st.error("İl ve risk skoru sütunları seçilmeli (soldaki menü).")
    st.dataframe(df.head())
    st.stop()

s = df[SKOR].astype(float)
if s.min() < 1 or s.max() > 5:
    s = 1 + 4 * (s - s.min()) / (s.max() - s.min() + 1e-9)
df["risk_1_5"] = s.round().clip(1, 5).astype(int)

# ---------------- Prim formülü ----------------
st.sidebar.header("Prim varsayımları")
MIN_K, MAX_K = 1.00, 1.60
MEVCUT = st.sidebar.number_input("Mevcut (varsayılan) prim katsayısı", 0.80, 2.00, 1.30, 0.05)


def baz_katsayi(skor):
    return MIN_K + (skor - 1) / 4 * (MAX_K - MIN_K)


def yas_ek(yas):
    if yas <= 10: return 0.00
    if yas <= 30: return 0.03
    if yas <= 50: return 0.06
    return 0.10


def kat_ek(kat):
    if kat <= 3: return 0.00
    if kat <= 7: return 0.02
    return 0.05


def prim(skor, yas, kat):
    return baz_katsayi(skor) * (1 + yas_ek(yas) + kat_ek(kat))


df["onerilen_katsayi"] = df["risk_1_5"].apply(baz_katsayi)
df["mevcut_katsayi"] = MEVCUT
df["fark"] = df["onerilen_katsayi"] - df["mevcut_katsayi"]

# ---------------- Arayüz ----------------
st.title("Deprem Verisiyle Sigorta Risk Segmentasyonu")
st.warning(
    "Bu uygulama deprem tahmini yapmaz. Geçmiş sismik aktiviteye dayalı bir risk "
    "segmentasyonu sunar; gelecekte deprem olup olmayacağını söylemez."
)

t1, t2, t3, t4 = st.tabs(["Harita", "İl risk profili", "Prim hesaplayıcı", "Mevcut vs önerilen prim"])

with t1:
    st.subheader("Deprem haritası ve il risk skorları")
    if deprem is not None:
        la = sutun_bul(deprem, ["lat"])
        lo = sutun_bul(deprem, ["lon"])
        mg = sutun_bul(deprem, ["mag"])
        if la and lo:
            min_m = st.slider("Minimum büyüklük", 2.5, 7.0, 4.0, 0.1)
            d = deprem[deprem[mg] >= min_m] if mg else deprem
            d = d.sample(min(len(d), 6000), random_state=1)
            fig = px.scatter_mapbox(
                d, lat=la, lon=lo, color=mg, size=mg if mg else None,
                color_continuous_scale="YlOrRd", zoom=4.5, height=550,
                center={"lat": 39, "lon": 35}, mapbox_style="open-street-map",
            )
            st.plotly_chart(fig, use_container_width=True)
    gj = next(iter(glob.glob("*.geojson") + glob.glob("01_Veri/*.geojson") + glob.glob("../01_Veri/*.geojson")), None)
    if gj:
        with open(gj, encoding="utf-8") as f:
            geo = json.load(f)
        anahtar = next((k for k in geo["features"][0]["properties"] if norm(k) in ("name", "ad", "il", "adi", "ilad")), None)
        if anahtar:
            fig2 = px.choropleth_mapbox(
                df, geojson=geo, locations=IL, featureidkey=f"properties.{anahtar}",
                color="risk_1_5", color_continuous_scale="YlOrRd", range_color=(1, 5),
                zoom=4.5, center={"lat": 39, "lon": 35}, mapbox_style="carto-positron", height=550,
            )
            st.plotly_chart(fig2, use_container_width=True)
    else:
        st.caption("İl bazlı renkli harita için bir .geojson dosyasını app.py'nin yanına koyun.")
        fig3 = px.bar(df.sort_values("risk_1_5", ascending=False).head(30), x=IL, y="risk_1_5",
                      color="risk_1_5", color_continuous_scale="YlOrRd", title="En yüksek riskli 30 il")
        st.plotly_chart(fig3, use_container_width=True)

with t2:
    il = st.selectbox("İl seçin", sorted(df[IL].astype(str).unique()))
    satir = df[df[IL].astype(str) == il].iloc[0]
    c1, c2, c3 = st.columns(3)
    c1.metric("Risk segmenti (1-5)", int(satir["risk_1_5"]))
    c2.metric("Önerilen baz katsayı", f"{satir['onerilen_katsayi']:.2f}")
    if NUFUS: c3.metric("Nüfus", f"{satir[NUFUS]:,.0f}")
    st.write("Tüm özellikler")
    st.dataframe(satir.drop(["fark"]).astype(str).to_frame("değer"))
        if deprem is not None and "place" in deprem.columns:
        gecmis = deprem[deprem["place"].astype(str).map(norm).str.contains(norm(il), na=False)]
        st.write("Yer bilgisinde ilin adı geçen en büyük 20 deprem (yaklaşık eşleştirme)")
        st.dataframe(gecmis.sort_values("mag", ascending=False).head(20))

with t3:
    st.subheader("Prim katsayısı hesaplayıcı")
    a, b, c = st.columns(3)
    il_p = a.selectbox("İl", sorted(df[IL].astype(str).unique()), key="p_il")
    yas = b.number_input("Bina yaşı", 0, 150, 20)
    kat = c.number_input("Kat sayısı", 1, 60, 5)
    sk = int(df[df[IL].astype(str) == il_p]["risk_1_5"].iloc[0])
    k = prim(sk, yas, kat)
    st.metric("Önerilen prim katsayısı", f"{k:.3f}", f"il segmenti {sk}")
    st.caption(
        f"Baz katsayı {baz_katsayi(sk):.2f} × (1 + yaş eki {yas_ek(yas):.2f} + kat eki {kat_ek(kat):.2f})"
    )
    st.info("Bu bir deprem tahmini değildir; geçmiş aktiviteye dayalı segmentasyondur.")

with t4:
    st.subheader("Hangi illerde mevcut prim riskin altında kalıyor?")
    alt = df[df["fark"] > 0].sort_values("fark", ascending=False)
    st.write(f"Mevcut katsayı {MEVCUT:.2f} varsayımıyla **{len(alt)} ilde** önerilen katsayı mevcuttan yüksek.")
    st.dataframe(alt[[IL, "risk_1_5", "mevcut_katsayi", "onerilen_katsayi", "fark"]])
    st.plotly_chart(px.bar(alt.head(25), x=IL, y="fark", color="risk_1_5",
                           color_continuous_scale="YlOrRd"), use_container_width=True)
