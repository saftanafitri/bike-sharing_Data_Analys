**Dashboard Penyewaan Sepeda**

https://dashboardbikesharingsafta.streamlit.app/

**Deskripsi Proyek**

Proyek ini dibuat sebagai bagian dari submission kursus Belajar Analisis Data dengan Python dari Dicoding. Analisis ini berfokus pada data penyewaan sepeda untuk mengidentifikasi tren berdasarkan waktu, musim, dan kondisi lingkungan yang memengaruhi jumlah penyewaan.  


 **Sumber Data** 

Dataset yang digunakan dalam proyek ini berisi data penyewaan sepeda yang mencakup variabel seperti waktu, musim, cuaca, dan jumlah penyewaan dalam satuan jam

sumber: https://www.kaggle.com/datasets/lakshmi25npathi/bike-sharing-dataset 

**Insight Utama**  

- Jumlah penyewaan melonjak pada hari **kamis, jumat dan sabtu**. Jumlah penyewaan juga melonjak dibulan **September 2012**. Begitu pun pada jam-jam sibuk seperti **pukul 8 dan 17-18** jumlah penyewaan sepeda melonjak. dan dengan meng-clustering data menjadi 3 cluster berdasarkan jam tingkat penyewaan sepeda teringgi ada pada cluster high yakni pada pukul **8, 12-13, dan 15-19** dengan rata-rata penyewaan **373.89 sepeda/jam**.
- Musim gugur (Fall) memiliki jumlah penyewaan sepeda tertinggi, dengan lonjakan signifikan pada tahun 2012 mencapai 641.479 penyewaan. Sebaliknya, musim semi (Summer) mencatat jumlah penyewaan terendah, menunjukkan perlunya strategi peningkatan pemakaian di musim tersebut. 

**Cara Menjalankan Dashboard**

nb: jalankan di cmd atau terminal

mkdir bike-sharing

cd bike-sharing

pipenv install

pipenv shell

pip install -r requirements.txt

cd dashboard 

streamlit run dashboard/dashboard.py

