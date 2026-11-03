#!/usr/bin/env python3
"""Organiza e confere as cópias integrais. Uso: conferir_pdfs.py --lote PASTA [--downloads ~/Downloads]"""
import argparse
import json
import re
import shutil
import subprocess
from pathlib import Path


def pdf_info(p):
    r = subprocess.run(["pdfinfo", str(p)], capture_output=True, text=True)
    pag = re.search(r"Pages:\s+(\d+)", r.stdout)
    enc = re.search(r"Encrypted:\s+(\w+)", r.stdout)
    return (int(pag.group(1)) if pag else None, enc.group(1) if enc else None)


def texto(p, ultima=None):
    cmd = ["pdftotext"] + (["-l", str(ultima)] if ultima else []) + [str(p), "-"]
    return subprocess.run(cmd, capture_output=True, text=True).stdout


def carregar_eventos(lote):
    evs = {}
    for arq in (lote / "coletas").glob("coleta_*.json") if (lote / "coletas").exists() else []:
        for cnj, v in json.loads(arq.read_text(encoding="utf-8")).items():
            ev = v.get("ev") or []
            while isinstance(ev, str):
                ev = json.loads(ev)
            evs[cnj] = ev
    return evs


def organizar(cnj, origem, pasta):
    final = pasta / f"{cnj}_copia_integral.pdf"
    direto = origem / final.name
    if direto.exists() and not final.exists():
        pasta.mkdir(parents=True, exist_ok=True)
        shutil.move(str(direto), final)
    partes = sorted(origem.glob(f"{cnj}_parte_*.pdf"), key=lambda p: int(re.search(r"parte_(\d+)", p.name).group(1)))
    if partes:
        pasta.mkdir(parents=True, exist_ok=True)
        for p in partes:
            shutil.move(str(p), pasta / p.name)
    guardadas = sorted(pasta.glob(f"{cnj}_parte_*.pdf"), key=lambda p: int(re.search(r"parte_(\d+)", p.name).group(1))) if pasta.exists() else []
    if not final.exists() and len(guardadas) == 1:
        shutil.copy2(guardadas[0], final)
        guardadas[0].unlink()
    elif not final.exists() and len(guardadas) > 1:
        subprocess.run(["pdfunite"] + [str(p) for p in guardadas] + [str(final)], check=True)
    return final if final.exists() else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lote", required=True)
    ap.add_argument("--downloads", default="~/Downloads")
    a = ap.parse_args()
    lote, origem = Path(a.lote).expanduser(), Path(a.downloads).expanduser()
    (lote / "coletas").mkdir(parents=True, exist_ok=True)
    for arq in origem.glob("coleta_*.json"):
        shutil.move(str(arq), lote / "coletas" / arq.name)
    lista = json.loads((lote / "lista.json").read_text(encoding="utf-8"))["validos"]
    cam = lote / "controle.json"
    controle = json.loads(cam.read_text(encoding="utf-8")) if cam.exists() else {}
    evs = carregar_eventos(lote)
    ok = pendentes = problemas = 0
    for cnj in lista:
        c = controle.setdefault(cnj, {})
        final = organizar(cnj, origem, lote / cnj)
        if not final:
            pendentes += 1
            continue
        pag, enc = pdf_info(final)
        falhas = []
        if not pag:
            falhas.append("PDF não abre")
        if enc and enc != "no":
            falhas.append("PDF com senha")
        if pag and cnj not in texto(final, 2):
            falhas.append("número do processo ausente nas primeiras páginas")
        if c.get("esperado") and pag != c["esperado"]:
            falhas.append(f"{pag} páginas, sistema informou {c['esperado']}")
        ids = sorted({i for e in evs.get(cnj, []) for i in re.findall(r"\b1\d{10}\b", e[-1])})
        if ids and pag:
            corpo = texto(final)
            faltam = [i for i in ids if i not in corpo]
            if faltam:
                falhas.append(f"documentos dos andamentos ausentes: {', '.join(faltam[:5])}")
        c["pdf"], c["paginas"] = final.name, pag
        if falhas:
            c["status_copia"] = "parcial"
            c["motivo"] = "; ".join(([c["motivo"]] if c.get("motivo") else []) + falhas)
            problemas += 1
            print("VERIFICAR", cnj, falhas)
        else:
            if c.get("status_copia") != "parcial":
                c["status_copia"] = "sucesso"
            ok += 1
            print("ok", cnj, pag)
    cam.write_text(json.dumps(controle, ensure_ascii=False, indent=1), encoding="utf-8")
    print({"conferidos": ok, "verificar": problemas, "sem_arquivo": pendentes})


if __name__ == "__main__":
    main()
