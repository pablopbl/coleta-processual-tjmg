#!/usr/bin/env python3
"""Normaliza e valida números CNJ. Uso: validar_cnj.py <arquivo ou números> --saida lista.json [--coluna NOME]"""
import argparse
import csv
import json
import re
from pathlib import Path

PADRAO = re.compile(r"\b(\d{7})-?(\d{2})\.?(\d{4})\.?(\d)\.?(\d{2})\.?(\d{4})\b")


def formatar(p):
    return f"{p[0]}-{p[1]}.{p[2]}.{p[3]}.{p[4]}.{p[5]}"


def digito_ok(p):
    return 98 - int(p[0] + p[2] + p[3] + p[4] + p[5] + "00") % 97 == int(p[1])


def ler(entradas, coluna):
    textos = []
    for ent in entradas:
        arq = Path(ent).expanduser()
        if not arq.exists():
            textos.append(ent)
        elif arq.suffix.lower() in (".xlsx", ".xlsm"):
            from openpyxl import load_workbook
            ws = load_workbook(arq, read_only=True, data_only=True).active
            linhas = list(ws.iter_rows(values_only=True))
            idx = None
            if coluna:
                cab = [str(c or "").strip().lower() for c in linhas[0]]
                idx = cab.index(coluna.strip().lower())
            for lin in linhas[1 if coluna else 0:]:
                vals = [lin[idx]] if idx is not None else lin
                textos.extend(str(v) for v in vals if v is not None)
        elif arq.suffix.lower() == ".csv" and coluna:
            with open(arq, newline="", encoding="utf-8-sig") as f:
                textos.extend(str(l.get(coluna, "")) for l in csv.DictReader(f))
        else:
            textos.append(arq.read_text(encoding="utf-8", errors="ignore"))
    return textos


def validar(textos):
    validos, duplicados, invalidos, fora = [], [], [], []
    vistos = set()
    for texto in textos:
        for m in PADRAO.finditer(texto):
            p = m.groups()
            n = formatar(p)
            if n in vistos:
                duplicados.append(n)
                continue
            vistos.add(n)
            if not digito_ok(p):
                invalidos.append(n)
            elif p[3] != "8" or p[4] != "13":
                fora.append(n)
            else:
                validos.append(n)
    return {"validos": validos, "duplicados": sorted(set(duplicados)), "invalidos": invalidos, "fora_tjmg": fora}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("entradas", nargs="+")
    ap.add_argument("--saida", required=True)
    ap.add_argument("--coluna")
    a = ap.parse_args()
    r = validar(ler(a.entradas, a.coluna))
    s = Path(a.saida).expanduser()
    s.parent.mkdir(parents=True, exist_ok=True)
    s.write_text(json.dumps(r, ensure_ascii=False, indent=1), encoding="utf-8")
    print({k: len(v) for k, v in r.items()})
    for k in ("duplicados", "invalidos", "fora_tjmg"):
        if r[k]:
            print(k, r[k])


if __name__ == "__main__":
    main()
