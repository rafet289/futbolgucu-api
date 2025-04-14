from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="Futbol Güç Analiz API", version="1.0")

class TakimVerisi(BaseModel):
    piyasa_degeri: float
    galibiyet_son_5: int
    ort_gol: float
    ort_yenilen_gol: float
    ort_yas: float | None = None

class TakimKarsilastirmaVerisi(BaseModel):
    takim1: TakimVerisi
    takim2: TakimVerisi

def hesapla_takim_gucu(piyasa_degeri, galibiyet_son_5, ort_gol, ort_yenilen_gol, ort_yas=None):
    katsayi_piyasa = 0.4
    katsayi_galibiyet = 0.3
    katsayi_gol = 0.2
    katsayi_yenilen_gol = 0.1
    katsayi_yas = 0.05

    max_piyasa = 1500
    max_galibiyet = 5
    max_gol = 4
    max_yenilen = 4

    norm_piyasa = min(piyasa_degeri / max_piyasa, 1.0)
    norm_galibiyet = galibiyet_son_5 / max_galibiyet
    norm_gol = ort_gol / max_gol
    norm_yenilen = ort_yenilen_gol / max_yenilen
    norm_yas = (35 - ort_yas) / (35 - 18) if ort_yas else 0

    skor = (
        (norm_piyasa * katsayi_piyasa) +
        (norm_galibiyet * katsayi_galibiyet) +
        (norm_gol * katsayi_gol) -
        (norm_yenilen * katsayi_yenilen)
    )

    if ort_yas:
        skor += norm_yas * katsayi_yas

    return round(skor * 100, 2)

def kazanma_ihtimali(takim1_skor, takim2_skor):
    toplam = takim1_skor + takim2_skor
    if toplam == 0:
        return {"takim1": 50.0, "takim2": 50.0}
    return {
        "takim1": round((takim1_skor / toplam) * 100, 2),
        "takim2": round((takim2_skor / toplam) * 100, 2)
    }

@app.post("/hesapla-guc")
def takim_gucu(veri: TakimVerisi):
    skor = hesapla_takim_gucu(**veri.dict())
    return {
        "takim_gucu_skoru": skor,
        "aciklama": f"Bu takımın potansiyel gücü % {skor} olarak hesaplandı."
    }

@app.post("/karsilastir")
def takim_karsilastir(veri: TakimKarsilastirmaVerisi):
    skor1 = hesapla_takim_gucu(**veri.takim1.dict())
    skor2 = hesapla_takim_gucu(**veri.takim2.dict())
    ihtimal = kazanma_ihtimali(skor1, skor2)

    return {
        "takim1_skor": skor1,
        "takim2_skor": skor2,
        "kazanma_ihtimali": {
            "takim1": f"%{ihtimal['takim1']}",
            "takim2": f"%{ihtimal['takim2']}"
        },
        "yorum": f"Takım 1'in kazanma ihtimali %{ihtimal['takim1']}, Takım 2'nin %{ihtimal['takim2']}"
    }

