#!/usr/bin/env python3
"""Gera o Excel de aba única do lote. Uso: gerar_excel.py --lote PASTA --saida ARQUIVO.xlsx"""
import argparse
import json
import re
from datetime import datetime
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter

EPROC = "https://eproc1g.tjmg.jus.br/eproc/"
PJE = "https://pje.tjmg.jus.br/pje/Processo/ConsultaProcesso/listView.seam"
CAPA = ["Número CNJ", "Tribunal", "Sistema", "Grau", "Órgão julgador", "Classe", "Assuntos", "Data de distribuição", "Valor da causa", "Situação", "Partes", "Advogados", "Segredo de justiça"]
ANDS = [c for i in range(1, 21) for c in (f"Data andamento {i}", f"Andamento {i}")]
CTRL = ["Quantidade de andamentos", "Status capa", "Status andamentos", "Status cópia integral", "Motivo da falha", "Perfil de acesso", "URL de origem", "Data e hora da consulta inicial", "Data e hora da conferência final", "Nome do PDF", "Páginas do PDF"]
COL = CAPA + ANDS + CTRL
LISTAS = {"ev", "ass", "heads", "cells", "midia"}
MES = dict(jan=1, fev=2, mar=3, abr=4, mai=5, jun=6, jul=7, ago=8, set=9, out=10, nov=11, dez=12)
PARTE = re.compile(r"(.+?)(?: - OAB (\w+))?(?: - (?:CPF: CPF|CNPJ: [\d./-]+))? \(([^()]+)\)\s*")


def desfazer(v):
    while isinstance(v, str) and v[:1] in "[{":
        v = json.loads(v)
    return v


def carregar(pasta, padrao):
    dados = {}
    for arq in sorted(pasta.glob(padrao)) if pasta.exists() else []:
        for k, v in json.loads(arq.read_text(encoding="utf-8")).items():
            dados[k] = {c: desfazer(x) if c in LISTAS else x for c, x in v.items()}
    return dados


def dt(s):
    if not s:
        return None
    s = s.replace(",", "").strip()
    for f in ("%d/%m/%Y %H:%M:%S", "%d/%m/%Y %H:%M", "%d/%m/%Y"):
        try:
            return datetime.strptime(s, f)
        except ValueError:
            pass
    return None


def dinheiro(s):
    return float(s.replace("R$", "").replace(".", "").replace(",", ".").strip()) if s else None


def texto(s):
    s = re.sub(r"\d{3}\.\d{3}\.\d{3}-\d{2}", "[CPF omitido]", s)
    s = re.sub(r"(?<=\S)Refer\.", " Refer.", s)
    s = re.sub(r"(?<=\S)\((AUTOR|RÉU|REQUERENTE|REQUERIDO|EXEQUENTE|EXECUTADO) - ", r" (\1 - ", s)
    return re.sub(r"(?<=\S)Entregue em", " Entregue em", s)


def polo(s):
    partes, adv = [], []
    s = re.sub(r"^Polo (ativo|passivo) ", "", s or "")
    s = re.sub(r"\(([A-ZÀ-Ü/ ]+)\(A\)\)", r"(\1)", s)
    for nome, oab, papel in PARTE.findall(s):
        if "ADVOGADO" in papel:
            adv.append(f"{nome.strip()} ({oab})" if oab else nome.strip())
        else:
            partes.append(nome.strip())
    if not partes and adv:
        partes = [re.sub(r" \(\w+\)$", "", adv[0])]
    return partes, adv


def partes_eproc(v):
    partes, adv = [], []
    for rot, cel in zip(v.get("heads", []), v.get("cells", [])):
        m = re.match(r"(.+?) \( ?(?:CPF|[\d./-]+) ?\) - Pessoa", cel)
        outros = " e outros" if cel.rstrip().endswith("e outros") else ""
        partes.append(f"{rot}: {m.group(1).strip() if m else ''}{outros}")
        adv += [f"{n.strip()} ({o})" for n, o in re.findall(r"([A-ZÀ-Ü' ]+?) ([A-Z]{2}\d+[A-Z]?) Tipo de Usuário: ADVOGADO", cel)]
    return " | ".join(partes) or None, " ; ".join(dict.fromkeys(adv)) or None


def linha_eproc(cnj, v, c):
    cp = v.get("capa", "")
    g = lambda a, b: (re.search(a + r"\s*(.*?)\s*" + b, cp) or [None, None])[1]
    evs = sorted(v.get("ev", []), key=lambda e: (dt(e[1]) or datetime.min, int(e[0])), reverse=True)[:20]
    partes, adv = partes_eproc(v)
    sem_eventos = v.get("total", 0) == 0
    sigilo = v.get("sigilo")
    segredo = sem_eventos and sigilo and "Segredo" in sigilo
    obs = []
    if segredo:
        obs.append("Segredo de justiça: perfil sem acesso a eventos, partes e autos.")
    elif sem_eventos:
        obs.append("Processo sem eventos visíveis neste perfil.")
    if partes and "e outros" in partes:
        obs.append("Partes: 'e outros' não expandido.")
    if any("Status:ABERTO" in e[2] for e in evs):
        obs.append("Há prazo com Status ABERTO nos andamentos.")
    sit = g("Situação", "Órgão")
    if sit and "REMETIDO" in sit:
        obs.append("Autos remetidos ao tribunal; 2º grau não consultado.")
    ands = [x for e in evs for x in (dt(e[1]), texto(e[2]))]
    st = {
        "capa": "parcial" if sem_eventos or (partes and "e outros" in partes) else "sucesso",
        "andamentos": "segredo_de_justica" if segredo else "sem_acesso" if sem_eventos else "sucesso",
        "copia": "segredo_de_justica" if segredo else "sem_acesso",
    }
    capa = [cnj, "TJMG", "eproc", "1º grau", g("Órgão Julgador:", "Juiz"), g("Classe da ação:", "Competência"), " ; ".join(v.get("ass", [])) or None,
            dt(g("Data de autuação:", "Situação")), dinheiro(v.get("valor")), sit, partes, adv, sigilo]
    return capa, ands, None if sem_eventos else v.get("total"), st, obs, EPROC, v.get("hora"), v.get("perfil")


def linha_pje(cnj, v, c):
    pa, aa = polo(v.get("ativo"))
    pp, ap = polo(v.get("passivo"))
    m = re.match(r"(\d{2}) (\w{3}) (\d{4})", v.get("autuacao") or "")
    dist = datetime(int(m[3]), MES[m[2]], int(m[1])) if m else None
    evs = v.get("ev", [])
    obs = []
    if evs and "REMETIDOS OS AUTOS (EM GRAU DE RECURSO)" in evs[0][1]:
        obs.append("Autos remetidos à instância superior; 2º grau não consultado.")
    ul = v.get("ultimaLista")
    if ul and evs and ul.upper().rstrip(".") not in " ".join(e[1] for e in evs).upper():
        obs.append(f"Divergência: a lista do PJe mostra '{ul}', movimento não localizado nos 20 andamentos.")
    ands = [x for e in evs for x in (dt(e[0]), texto(e[1]))]
    st = {"capa": "sucesso", "andamentos": "sucesso", "copia": "sem_acesso"}
    capa = [cnj, "TJMG", "PJe", "1º grau", v.get("orgao"), v.get("classe"), v.get("assunto"), dist, dinheiro(v.get("valor")), None,
            f"POLO ATIVO: {' ; '.join(pa)} | POLO PASSIVO: {' ; '.join(pp)}", " ; ".join(dict.fromkeys(aa + ap)) or None,
            "Sim" if v.get("segredo") == "SIM" else "Não"]
    return capa, ands, v.get("total"), st, obs, PJE, v.get("hora"), None


def montar(lote):
    lista = json.loads((lote / "lista.json").read_text(encoding="utf-8"))
    cam = lote / "controle.json"
    controle = json.loads(cam.read_text(encoding="utf-8")) if cam.exists() else {}
    E, P = carregar(lote / "coletas", "coleta_eproc*.json"), carregar(lote / "coletas", "coleta_pje*.json")
    linhas = []
    for cnj in lista["validos"]:
        c = controle.get(cnj, {})
        if cnj in E:
            capa, ands, qtd, st, obs, url, hora, perfil = linha_eproc(cnj, E[cnj], c)
        elif cnj in P:
            capa, ands, qtd, st, obs, url, hora, perfil = linha_pje(cnj, P[cnj], c)
        else:
            capa, ands, qtd, url, hora, perfil = [cnj, "TJMG"] + [None] * 11, [], None, None, None, None
            st = {"capa": "nao_encontrado", "andamentos": "nao_encontrado", "copia": "nao_encontrado"}
            obs = []
        motivo = " ".join(x for x in [c.get("motivo")] + obs if x) or None
        ands += [None] * (40 - len(ands))
        linhas.append(capa + ands + [qtd, c.get("status_capa", st["capa"]), c.get("status_andamentos", st["andamentos"]), c.get("status_copia", st["copia"]), motivo,
                                     c.get("perfil", perfil), url, dt(hora), dt(c.get("conferencia_final")), c.get("pdf"), c.get("paginas")])
    for cnj in lista.get("invalidos", []):
        linhas.append([cnj, None] + [None] * 11 + [None] * 40 + [None, "numero_invalido", "numero_invalido", "numero_invalido", "Dígito verificador inválido.", None, None, None, None, None, None])
    return linhas


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lote", required=True)
    ap.add_argument("--saida", required=True)
    a = ap.parse_args()
    linhas = montar(Path(a.lote).expanduser())
    wb = Workbook()
    ws = wb.active
    ws.title = "Processos"
    ws.append(COL)
    for l in linhas:
        ws.append(l)
    base, cab = Font(name="Arial", size=10), Font(name="Arial", size=10, bold=True, color="FFFFFF")
    for row in ws.iter_rows():
        for c in row:
            c.font = base
            c.alignment = Alignment(vertical="top")
            if isinstance(c.value, datetime):
                c.number_format = "dd/mm/yyyy" if (c.value.hour, c.value.minute, c.value.second) == (0, 0, 0) else "dd/mm/yyyy hh:mm"
    for c in ws[1]:
        c.font, c.fill = cab, PatternFill("solid", fgColor="1F3864")
        c.alignment = Alignment(vertical="center", horizontal="center", wrap_text=True)
    for i in range(2, ws.max_row + 1):
        ws.cell(i, COL.index("Valor da causa") + 1).number_format = '"R$" #,##0.00'
    larg = {"Número CNJ": 27, "Órgão julgador": 45, "Classe": 34, "Assuntos": 50, "Partes": 50, "Advogados": 50, "Motivo da falha": 70, "Perfil de acesso": 34, "URL de origem": 40, "Segredo de justiça": 24, "Situação": 22}
    for i, nome in enumerate(COL, 1):
        ws.column_dimensions[get_column_letter(i)].width = larg.get(nome) or (18 if nome.startswith(("Data", "Status", "Valor")) else 45 if nome.startswith("Andamento ") else 12)
    ws.row_dimensions[1].height = 32
    ws.freeze_panes = "B2"
    ws.auto_filter.ref = ws.dimensions
    saida = Path(a.saida).expanduser()
    saida.parent.mkdir(parents=True, exist_ok=True)
    wb.save(saida)
    print(saida, len(linhas), "linhas", len(COL), "colunas")


if __name__ == "__main__":
    main()
