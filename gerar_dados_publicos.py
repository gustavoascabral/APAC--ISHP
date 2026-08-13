#!/usr/bin/env python3
"""
Converte o relatório de APAC (.xlsx) em dados/dados-publicos.json.

O arquivo gerado NÃO contém nome, nome da mãe, CPF, CNS, endereço,
data de nascimento nem número da APAC. Serve para publicar o painel
com os números já carregados, sem expor dado pessoal de paciente.

Uso:
    python gerar_dados_publicos.py relatorio-apac.xlsx
    python gerar_dados_publicos.py relatorio-apac.xlsx --saida dados/dados-publicos.json

Requisitos: pandas e openpyxl (pip install pandas openpyxl)
"""

import argparse
import hashlib
import json
import unicodedata
from datetime import date, datetime
from pathlib import Path

import pandas as pd

COLUNAS = {
    "etapa": "etapa",
    "autorizador": "autorizador",
    "unidadeexecutora": "unidade",
    "sexo": "sexo",
    "municipio": "municipio",
    "uf": "uf",
    "idade": "idade",
    "competencia": "competencia",
    "diacadastro": "dia",
    "mescadastro": "mes",
    "anocadastro": "ano",
    "datadevalidade": "validade",
    "cid": "cid",
    "grupo": "grupo",
    "codigoprocedimento": "codProc",
    "nomeprocedimento": "procedimento",
    "origemdorecurso": "origem",
    # usados apenas para gerar o código do paciente, nunca gravados
    "cns": "_cns",
    "cpf": "_cpf",
}


def chave(texto):
    sem_acento = unicodedata.normalize("NFD", str(texto))
    sem_acento = "".join(c for c in sem_acento if unicodedata.category(c) != "Mn")
    return "".join(c for c in sem_acento.lower() if c.isalnum())


def faixa_etaria(idade):
    if idade is None or pd.isna(idade):
        return "Não informada"
    idade = int(idade)
    if idade < 18:
        return "Até 17"
    if idade < 40:
        return "18 a 39"
    if idade < 60:
        return "40 a 59"
    if idade < 70:
        return "60 a 69"
    if idade < 80:
        return "70 a 79"
    return "80 ou mais"


def texto(v):
    if v is None or (isinstance(v, float) and pd.isna(v)):
        return None
    s = str(v).strip()
    return s or None


def para_iso(v):
    if v is None or (isinstance(v, float) and pd.isna(v)):
        return None
    if isinstance(v, (datetime, date)):
        return v.strftime("%Y-%m-%d")
    for formato in ("%d/%m/%Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(str(v).strip(), formato).strftime("%Y-%m-%d")
        except ValueError:
            continue
    return None


def codigo_procedimento(v):
    """SIGTAP tem 10 dígitos; o Excel lê como número e perde o zero da frente."""
    s = texto(v)
    if not s:
        return None
    digitos = "".join(c for c in s.split(".")[0] if c.isdigit())
    return digitos.zfill(10) if digitos else None


def codigo_paciente(linha):
    bruto = texto(linha.get("_cns")) or texto(linha.get("_cpf"))
    if not bruto:
        return None
    digitos = "".join(c for c in bruto if c.isdigit())
    if not digitos:
        return None
    return "p" + hashlib.sha256(digitos.encode()).hexdigest()[:10]


def main():
    ap = argparse.ArgumentParser(description="Gera o JSON público do painel APAC.")
    ap.add_argument("planilha", help="arquivo .xlsx exportado do sistema")
    ap.add_argument("--saida", default="dados/dados-publicos.json")
    args = ap.parse_args()

    df = pd.read_excel(args.planilha)
    df = df.rename(columns={c: COLUNAS.get(chave(c), c) for c in df.columns})

    registros = []
    for _, bruta in df.iterrows():
        linha = bruta.to_dict()
        idade = linha.get("idade")
        idade = None if idade is None or pd.isna(idade) else int(idade)

        data_cadastro = None
        try:
            ano, mes, dia = int(linha["ano"]), int(linha["mes"]), int(linha["dia"])
            data_cadastro = date(ano, mes, dia).isoformat()
        except (KeyError, TypeError, ValueError):
            pass

        competencia = texto(linha.get("competencia"))
        if competencia and "/" in competencia:
            m, a = competencia.split("/")[:2]
            competencia = f"{m.zfill(2)}/{a}"

        registros.append(
            {
                "etapa": texto(linha.get("etapa")) or "Não informada",
                "autorizador": texto(linha.get("autorizador")),
                "unidade": texto(linha.get("unidade")),
                "sexo": texto(linha.get("sexo")),
                "idade": idade,
                "faixa": faixa_etaria(idade),
                "municipio": texto(linha.get("municipio")),
                "uf": texto(linha.get("uf")),
                "competencia": competencia,
                "dataCadastro": data_cadastro,
                "validade": para_iso(linha.get("validade")),
                "cid": texto(linha.get("cid")),
                "grupo": texto(linha.get("grupo")),
                "codProc": codigo_procedimento(linha.get("codProc")),
                "procedimento": texto(linha.get("procedimento")),
                "origem": texto(linha.get("origem")),
                "chavePaciente": codigo_paciente(linha),
            }
        )

    pacote = {
        "geradoEm": datetime.now().strftime("%d/%m/%Y"),
        "origem": Path(args.planilha).name,
        "totalRegistros": len(registros),
        "observacao": (
            "Arquivo sem dados pessoais: nome, CPF, CNS, endereço, data de nascimento "
            "e número da APAC foram removidos. O paciente é identificado apenas por um "
            "código sem volta, usado só para contar duplicidade."
        ),
        "linhas": registros,
    }

    saida = Path(args.saida)
    saida.parent.mkdir(parents=True, exist_ok=True)
    saida.write_text(json.dumps(pacote, ensure_ascii=False), encoding="utf-8")
    print(f"{len(registros)} registros gravados em {saida}")


if __name__ == "__main__":
    main()
