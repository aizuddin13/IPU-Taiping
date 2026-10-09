#!/usr/bin/env python3
"""Kemas kini fail data untuk halaman Kualiti Udara Taiping.

Mengambil bacaan IPU sejam dari portal APIMS (Jabatan Alam Sekitar) dan
ramalan cuaca MET Malaysia melalui portal data terbuka kerajaan, kemudian
menulis semula fail JSON dalam data/.

Hanya pustaka standard Python digunakan. Dijalankan setiap jam oleh
.github/workflows/kemaskini.yml pada pelari GitHub.
"""

import json
import os
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timedelta, timezone

MYT = timezone(timedelta(hours=8))
AKAR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(AKAR, "data")

NEGERI_PERAK = 8
STESEN_TAIPING = "CA10A"
JAM_DISIMPAN = 168          # tetingkap bergolek tujuh hari
AMBANG_BASI_JAM = 3         # bacaan lebih lama daripada ini dikira basi

APIMS = "https://eqms.doe.gov.my/api3/publicportalapims/apitablehourly"
CUACA = ("https://api.data.gov.my/weather/forecast"
         "?contains=Taiping@location__location_name&limit=10")

HARI_MELAYU = ["Isnin", "Selasa", "Rabu", "Khamis", "Jumaat", "Sabtu", "Ahad"]

SIMBOL_PENCEMAR = {
    "**": "PM2.5",
    "*": "PM10",
    "a": "SO2",
    "b": "NO2",
    "c": "O3",
    "d": "CO",
    "&": "2 pencemar atau lebih",
}


def kategori(ipu):
    if ipu <= 50:
        return "Baik"
    if ipu <= 100:
        return "Sederhana"
    if ipu <= 200:
        return "Tidak Sihat"
    if ipu <= 300:
        return "Sangat Tidak Sihat"
    return "Berbahaya"


def ayat_biasa(teks):
    teks = (teks or "").strip()
    return teks[:1].upper() + teks[1:].lower() if teks else teks


def ambil_json(url, cubaan=3):
    """Ambil JSON dengan beberapa cubaan. Mengembalikan None jika gagal."""
    for i in range(cubaan):
        try:
            req = urllib.request.Request(
                url, headers={"User-Agent": "ipu-taiping/1.0 (+github actions)",
                              "Accept": "application/json"})
            with urllib.request.urlopen(req, timeout=45) as res:
                return json.loads(res.read().decode("utf-8"))
        except (urllib.error.URLError, urllib.error.HTTPError,
                json.JSONDecodeError, TimeoutError, OSError) as e:
            print(f"  cubaan {i + 1}/{cubaan} gagal: {e}", file=sys.stderr)
            if i + 1 < cubaan:
                time.sleep(5 * (i + 1))
    return None


def muat(nama, lalai):
    laluan = os.path.join(DATA, nama)
    try:
        with open(laluan, encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return lalai


def simpan(nama, isi):
    laluan = os.path.join(DATA, nama)
    os.makedirs(DATA, exist_ok=True)
    with open(laluan, "w", encoding="utf-8") as f:
        json.dump(isi, f, ensure_ascii=False, indent=1)
        f.write("\n")


def ambil_apims(sekarang):
    """Tingkap 25 jam bagi semua stesen Perak, sehingga jam hadapan."""
    sehingga = (sekarang.replace(minute=0, second=0, microsecond=0)
                + timedelta(hours=1)).strftime("%Y-%m-%dT%H:00:00")
    url = (f"{APIMS}?stateid={NEGERI_PERAK}&datetime={sehingga}"
           f"&stn=all&_r={int(time.time())}")
    print(f"APIMS: {url}")
    jawapan = ambil_json(url)
    if not jawapan:
        return None
    baris = jawapan.get("api_table_hourly") if isinstance(jawapan, dict) else jawapan
    if not baris:
        return None
    bersih = []
    for r in baris:
        try:
            ipu = int(r["API"])
        except (KeyError, TypeError, ValueError):
            continue  # bacaan tiada atau rosak — langkau
        masa = str(r.get("DATETIME", ""))[:19]
        if len(masa) != 19:
            continue
        bersih.append({
            "id": r.get("STATION_ID"),
            "lokasi": str(r.get("STATION_LOCATION", "")).split(",")[0].strip(),
            "masa": masa,
            "ipu": ipu,
            "pencemar": SIMBOL_PENCEMAR.get(str(r.get("PARAM_SYMBOL", "")).strip(), "PM2.5"),
        })
    return bersih or None


def tulis_ipu(baris, sekarang):
    taiping = sorted([b for b in baris if b["id"] == STESEN_TAIPING],
                     key=lambda b: b["masa"])
    if not taiping:
        print("Tiada baris Taiping dalam jawapan APIMS.", file=sys.stderr)
        return None

    terbaharu = taiping[-1]
    umur = sekarang - datetime.strptime(terbaharu["masa"], "%Y-%m-%dT%H:%M:%S").replace(tzinfo=MYT)
    if umur > timedelta(hours=AMBANG_BASI_JAM):
        print(f"DATA BASI: bacaan terbaharu {terbaharu['masa']} "
              f"({umur.total_seconds() / 3600:.1f} jam lalu).", file=sys.stderr)
        return None

    sedia = muat("ipu.json", {"bacaan": []})
    simpanan = {b["masa"]: b for b in sedia.get("bacaan", [])}
    baharu = 0
    for b in taiping:
        if b["masa"] not in simpanan:
            simpanan[b["masa"]] = {
                "masa": b["masa"], "ipu": b["ipu"],
                "kategori": kategori(b["ipu"]), "pencemar": b["pencemar"],
            }
            baharu += 1

    bacaan = [simpanan[m] for m in sorted(simpanan)][-JAM_DISIMPAN:]
    simpan("ipu.json", {
        "stesen": "Taiping",
        "id_stesen": STESEN_TAIPING,
        "negeri": "Perak",
        "dikemaskini": terbaharu["masa"] + "+08:00",
        "sumber": "APIMS, Jabatan Alam Sekitar",
        "bacaan": bacaan,
    })
    print(f"ipu.json: {baharu} bacaan baharu, {len(bacaan)} jam disimpan, "
          f"terkini {terbaharu['masa']} = {terbaharu['ipu']}")
    return terbaharu


def tulis_perak(baris):
    terkini = {}
    for b in baris:
        ada = terkini.get(b["id"])
        if ada is None or b["masa"] > ada["masa"]:
            terkini[b["id"]] = b
    if not terkini:
        return
    stesen = sorted(terkini.values(), key=lambda b: -b["ipu"])
    simpan("perak.json", {
        "dikemaskini": max(b["masa"] for b in stesen) + "+08:00",
        "sumber": "APIMS, Jabatan Alam Sekitar",
        "stesen": [{
            "nama": b["lokasi"], "id": b["id"], "ipu": b["ipu"],
            "kategori": kategori(b["ipu"]), "pencemar": b["pencemar"],
        } for b in stesen],
    })
    print(f"perak.json: {len(stesen)} stesen")


def tulis_cuaca(sekarang):
    print(f"Cuaca: {CUACA}")
    rekod = ambil_json(CUACA)
    if not rekod:
        print("  gagal — fail cuaca dibiarkan seperti sedia ada.", file=sys.stderr)
        return
    hari_ini = sekarang.strftime("%Y-%m-%d")
    ramalan = []
    for r in rekod:
        tarikh = str(r.get("date", ""))[:10]
        if len(tarikh) != 10 or tarikh < hari_ini:
            continue
        try:
            d = datetime.strptime(tarikh, "%Y-%m-%d")
        except ValueError:
            continue
        ramalan.append({
            "tarikh": tarikh,
            "hari": HARI_MELAYU[d.weekday()],
            "ringkasan": ayat_biasa(r.get("summary_forecast") or r.get("summary")),
            "ringkasan_bila": ayat_biasa(r.get("summary_when")),
            "pagi": ayat_biasa(r.get("morning_forecast")),
            "petang": ayat_biasa(r.get("afternoon_forecast")),
            "malam": ayat_biasa(r.get("night_forecast")),
            "suhu_min": int(r.get("min_temp", 0)),
            "suhu_maks": int(r.get("max_temp", 0)),
        })
    if not ramalan:
        print("  tiada rekod Taiping — fail cuaca dibiarkan.", file=sys.stderr)
        return
    ramalan.sort(key=lambda x: x["tarikh"])
    simpan("cuaca.json", {
        "dikemaskini": sekarang.strftime("%Y-%m-%dT%H:%M:%S+08:00"),
        "sumber": "MET Malaysia melalui data.gov.my",
        "ramalan": ramalan,
    })
    print(f"cuaca.json: {len(ramalan)} hari")


def main():
    sekarang = datetime.now(MYT)
    print(f"Masa Malaysia: {sekarang:%Y-%m-%d %H:%M:%S}")

    baris = ambil_apims(sekarang)
    if baris is None:
        print("APIMS tidak dapat dibaca. Tiada fail ditulis.", file=sys.stderr)
        return 1

    terbaharu = tulis_ipu(baris, sekarang)
    if terbaharu is None:
        return 1
    tulis_perak(baris)
    tulis_cuaca(sekarang)

    if terbaharu["ipu"] > 200:
        print(f"::warning::AMARAN: IPU Taiping {terbaharu['ipu']} — sangat tidak sihat")
    elif terbaharu["ipu"] > 150:
        print(f"::warning::AMARAN: IPU Taiping {terbaharu['ipu']} — melepasi ambang 150")
    return 0


if __name__ == "__main__":
    sys.exit(main())
