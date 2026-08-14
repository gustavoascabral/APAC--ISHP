#!/usr/bin/env python3
"""
Converte o relatório de APAC (.xlsx) — e, se você quiser, a planilha da
regulação do SISREG — em dados/dados-publicos.json.

O arquivo gerado NÃO contém nome, nome da mãe, CPF, CNS, endereço,
data de nascimento, telefone nem número da APAC. Serve para publicar o
painel com os números já carregados, sem expor dado pessoal de paciente.

Uso:
    python gerar_dados_publicos.py relatorio-apac.xlsx
    python gerar_dados_publicos.py relatorio-apac.xlsx --regulacao sisreg.xlsx
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

# Planilha da regulação (SISREG). O telefone não entra: o painel não usa.
COLUNAS_REG = {
    "unidadesolicitante": "unidadeSolicitante",
    "unidadesolicitacao": "unidadeSolicitante",
    "unidadeexec": "unidadeExec",
    "unidadeexecutante": "unidadeExec",
    "unidadeexecutora": "unidadeExec",
    "codproced": "codProc",
    "codproc": "codProc",
    "codigoprocedimento": "codProc",
    "descricaoprocedimento": "procedimento",
    "nomeprocedimento": "procedimento",
    "procedimento": "procedimento",
    "risco": "risco",
    "classificacaoderisco": "risco",
    "datadasolic": "dataSolic",
    "datadasolicitacao": "dataSolic",
    "datasolicitacao": "dataSolic",
    "tempodeespera": "espera",
    "datadoatend": "dataAtend",
    "datadoatendimento": "dataAtend",
    "dataatendimento": "dataAtend",
    "cid": "cid",
    "status": "status",
    "situacao": "status",
    # só para gerar o código do paciente, nunca gravado
    "cns": "_cns",
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
    for formato in ("%d/%m/%Y", "%Y-%m-%d", "%d/%m/%Y %H:%M:%S", "%Y-%m-%d %H:%M:%S"):
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


def digitos_documento(v, tamanho):
    """CPF e CNS chegam do Excel como número: str() de um float grava '.0' no fim
    e vira um dígito a mais. Aqui o valor é normalizado antes de virar código."""
    if v is None or (isinstance(v, float) and pd.isna(v)):
        return None
    if isinstance(v, float) and v.is_integer():
        v = int(v)
    s = str(v).strip()
    if s.endswith(".0"):
        s = s[:-2]
    digitos = "".join(c for c in s if c.isdigit())
    if not digitos:
        return None
    return digitos.zfill(tamanho) if len(digitos) < tamanho else digitos


def codigo(digitos):
    """Código sem volta do paciente. O painel faz a mesma conta para reencontrar
    o mesmo CNS na planilha da regulação."""
    if not digitos:
        return None
    return "p" + hashlib.sha256(digitos.encode()).hexdigest()[:10]


def codigo_paciente(linha):
    return codigo(
        digitos_documento(linha.get("_cns"), 15)
        or digitos_documento(linha.get("_cpf"), 11)
    )


def ler(planilha, mapa):
    df = pd.read_excel(planilha)
    return df.rename(columns={c: mapa.get(chave(c), c) for c in df.columns})


def linhas_apac(planilha):
    df = ler(planilha, COLUNAS)
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
    return registros


def linhas_regulacao(planilha):
    df = ler(planilha, COLUNAS_REG)
    registros = []
    for _, bruta in df.iterrows():
        linha = bruta.to_dict()
        espera = linha.get("espera")
        try:
            espera = None if espera is None or pd.isna(espera) else round(float(espera))
        except (TypeError, ValueError):
            espera = None

        registros.append(
            {
                "chavePaciente": codigo(digitos_documento(linha.get("_cns"), 15)),
                "unidadeSolicitante": texto(linha.get("unidadeSolicitante")),
                "unidadeExec": texto(linha.get("unidadeExec")),
                "codProc": texto(linha.get("codProc")),
                "procedimento": texto(linha.get("procedimento")),
                "risco": texto(linha.get("risco")),
                "dataSolic": para_iso(linha.get("dataSolic")),
                "dataAtend": para_iso(linha.get("dataAtend")),
                "espera": espera,
                "cid": texto(linha.get("cid")),
                "status": texto(linha.get("status")),
            }
        )
    return registros


def main():
    ap = argparse.ArgumentParser(description="Gera o JSON público do painel APAC.")
    ap.add_argument("planilha", help="relatório de APAC (.xlsx) exportado do sistema")
    ap.add_argument("--regulacao", help="planilha de atendimentos do SISREG (.xlsx)")
    ap.add_argument("--saida", default="dados/dados-publicos.json")
    args = ap.parse_args()

    registros = linhas_apac(args.planilha)

    pacote = {
        "geradoEm": datetime.now().strftime("%d/%m/%Y"),
        "origem": Path(args.planilha).name,
        "totalRegistros": len(registros),
        "observacao": (
            "Arquivo sem dados pessoais: nome, CPF, CNS, endereço, data de nascimento, "
            "telefone e número da APAC foram removidos. O paciente é identificado apenas "
            "por um código sem volta, usado só para contar duplicidade e para ligar a APAC "
            "ao agendamento do mesmo paciente na regulação."
        ),
        "linhas": registros,
    }

    if args.regulacao:
        agendamentos = linhas_regulacao(args.regulacao)
        pacote["regulacao"] = {
            "origem": Path(args.regulacao).name,
            "total": len(agendamentos),
            "linhas": agendamentos,
        }

    saida = Path(args.saida)
    saida.parent.mkdir(parents=True, exist_ok=True)
    saida.write_text(json.dumps(pacote, ensure_ascii=False), encoding="utf-8")

    recado = f"{len(registros)} APACs gravadas em {saida}"
    if args.regulacao:
        vinculados = len(
            {l["chavePaciente"] for l in pacote["regulacao"]["linhas"] if l["chavePaciente"]}
            & {l["chavePaciente"] for l in registros if l["chavePaciente"]}
        )
        recado += (
            f"\n{pacote['regulacao']['total']} agendamentos da regulação"
            f" · {vinculados} pacientes aparecem nas duas planilhas"
        )
    print(recado)


if __name__ == "__main__":
    main()
