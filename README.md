# Kualiti Udara Taiping

Halaman awam yang memaparkan bacaan Indeks Pencemar Udara (IPU) bagi stesen
pemantauan **CA10A, Taiping, Perak**, bersama ramalan cuaca MET Malaysia dan
bandingan dengan stesen-stesen lain di Perak.

Halaman: https://aizuddin13.github.io/IPU-Taiping/

## Kandungan

| Fail | Keterangan |
| --- | --- |
| `index.html` | Halaman itu sendiri. Tiada kebergantungan luar — semua carta dilukis sendiri sebagai SVG. |
| `data/ipu.json` | Bacaan IPU sejam bagi Taiping, tetingkap bergolek tujuh hari (168 bacaan). |
| `data/perak.json` | Bacaan semasa kelima-lima stesen di Perak. |
| `data/cuaca.json` | Ramalan cuaca tujuh hari bagi pekan Taiping. |

## Kemas kini

Fail data dalam `data/` ditulis semula setiap jam oleh
`.github/workflows/kemaskini.yml`, yang berjalan pada pelari GitHub dan
memanggil API APIMS serta data.gov.my terus dengan Python pustaka standard.
Alur kerja yang sama menerbitkan halaman ini ke GitHub Pages, jadi tiada
langkah manual dan tiada perkhidmatan luar yang terlibat.

Dua perlindungan terbina:

- **Semakan kesegaran.** Jika bacaan terbaharu yang diterima lebih lama
  daripada tiga jam, skrip itu berhenti tanpa menulis apa-apa dan larian itu
  gagal dengan nyata dalam tab Actions. Data beku tidak akan berlalu secara
  senyap sebagai "tiada bacaan baharu".
- **Gabungan, bukan tambahan.** Setiap larian menerima tetingkap 25 jam dan
  mengisi mana-mana jam yang tiada dalam fail. Larian yang terlepas ditampal
  sendiri oleh larian berikutnya.

Larian boleh dicetuskan secara manual dari tab Actions (Run workflow).

## Sumber

- Bacaan IPU: Sistem Pengurusan Indeks Pencemar Udara (APIMS), Jabatan Alam
  Sekitar — https://eqms.doe.gov.my/APIMS/main
- Ramalan cuaca: MET Malaysia, melalui portal data terbuka kerajaan
  (`api.data.gov.my/weather/forecast`)

Kedua-duanya data awam kerajaan Malaysia. Halaman ini bukan terbitan rasmi
mana-mana agensi. Untuk keputusan kesihatan yang penting, rujuk portal APIMS
atau nasihat Kementerian Kesihatan.
