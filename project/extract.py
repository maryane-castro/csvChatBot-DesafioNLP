import PyPDF2
import csv
import os
import re
import unicodedata
import pandas as pd
import json

def preprocess_text(texto):
    # Remover acentos preservando as letras
    texto_sem_acentos = ''.join((c for c in unicodedata.normalize('NFD', texto) if unicodedata.category(c) != 'Mn'))
    return texto_sem_acentos

def extract_text_from_pdf(pdf_file):
    texto = ""
    with open(pdf_file, 'rb') as arquivo_pdf:
        leitor = PyPDF2.PdfReader(arquivo_pdf)
        for pagina in range(len(leitor.pages)):
            texto_pagina = leitor.pages[pagina].extract_text()
            texto += preprocess_text(texto_pagina)
    # Escapar caracteres especiais
    texto = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\xff]', '', texto)
    return texto

def scrape_pdf_directory(pdf_directory, output_csv):
    with open(output_csv, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['arquivo', 'transcricao']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for filename in os.listdir(pdf_directory):
            if filename.endswith('.pdf'):
                pdf_file = os.path.join(pdf_directory, filename)
                texto = extract_text_from_pdf(pdf_file)
                writer.writerow({'arquivo': filename, 'transcricao': texto})

# Diretório contendo os arquivos PDF
pdf_directory = 'ativss/ativos'

# Nome do arquivo CSV de saída
output_csv = 'newCSV/dados_extraidos.csv'

scrape_pdf_directory(pdf_directory, output_csv)



caminho_arquivo_csv = 'newCSV/dados_extraidos.csv'
df = pd.read_csv(caminho_arquivo_csv)
dados_json = df.to_json(orient='records')
print(dados_json)


atualizacao_list = []
nome_pregao_list = []
atividade_principal_list = []
classificacao_setorial_list = []
site_list = []
codigos_negociacao_list = []
cnpj_list = []
ativo_imobilizado_list = []
ativo_total_list = []
patrimonio_liquido_list = []
lucro_prejuizo_list = []
atividades_operacionais_list = []
atividades_investimento_list = []
variacao_cambial_list = []
aumento_reducao_caixa_list = []
pessoas_fisicas_list = []
pessoas_juridicas_list = []
investidores_institucionais_list = []
acoes_ordinarias_list = []
acoes_preferenciais_list = []
total_acoes_list = []


caminho_arquivo_csv = 'newCSV/dados_extraidos.csv'
df = pd.read_csv(caminho_arquivo_csv)
dados_json = df.to_json(orient='records')

for item in json.loads(dados_json):
    texto = item['transcricao']

    padrao_data = re.search(r"Atualizado em (\d{2}/\d{2}/\d{4})", texto)
    if padrao_data:
        atualizacao = padrao_data.group(1)
    else:
        atualizacao = None

    padrao_nome_pregao = re.search(r"Nome de Pregao: (.+?)\n", texto)
    if padrao_nome_pregao:
        nome_pregao = padrao_nome_pregao.group(1)
    else:
        nome_pregao = None

    padrao_atividade_principal = re.search(r"Atividade Principal:(.+?)\n", texto)
    if padrao_atividade_principal:
        atividade_principal = padrao_atividade_principal.group(1).strip()
    else:
        atividade_principal = None

    padrao_classificacao_setorial = re.search(r"Setorial:(.+?)\n", texto)
    if padrao_classificacao_setorial:
        classificacao_setorial = padrao_classificacao_setorial.group(1).strip()
        padrao_linha_adicional = re.search(r"Setorial:(.+?)\n(.+?)\n", texto, re.DOTALL)
        if padrao_linha_adicional:
            classificacao_setorial += "\n" + padrao_linha_adicional.group(2).strip()
    else:
        classificacao_setorial = None

    # Encontrar o site usando expressão regular, lidando com barras invertidas
    padrao_site = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', texto)
    if padrao_site:
        site = padrao_site[0].replace('\\', '')  # Selecionar a primeira URL encontrada
    else:
        site = None

    padrao_codigos_negociacao = re.findall(r"Negociacao:(.+?)(?=CNPJ)", texto, re.DOTALL)
    if padrao_codigos_negociacao:
        codigos_negociacao = [codigo.strip() for codigo in padrao_codigos_negociacao[0].split('\n') if codigo.strip()]
    else:
        codigos_negociacao = None
    padrao_cnpj = re.search(r"CNPJ: (\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2})", texto)
    if padrao_cnpj:
        cnpj = padrao_cnpj.group(1)
    else:
        cnpj = None
    padrao_ativos_imobilizado = re.search(r"Ativo Imobilizado, Investimentos e Intang.*?([\d.,]+)\s+([\d.,]+)", texto)
    ativo_imobilizado = padrao_ativos_imobilizado.group(1).replace('.', '').replace(',', '.') if padrao_ativos_imobilizado else None
    padrao_ativos_total = re.search(r"Ativo To.*?([\d.,]+)\s+([\d.,]+)", texto)
    ativo_total = None  # Initialize ativo_total outside the if block with a default value
    padrao_ativos_total = re.search(r"Ativo To.*?([\d.,]+)\s+([\d.,]+)", texto)
    ativo_total_match = padrao_ativos_total.group(1) if padrao_ativos_total else None
    if ativo_total_match:
        if "bilh" in ativo_total_match.lower():
            ativo_total = float(ativo_total_match.replace("bilh", "").replace(".", "").replace(",", ".")) * 10**9
        else:
            ativo_total = ativo_total_match.replace('.', '').replace(',', '.')

    padrao_patrimonio_liquido = re.search(r"Patrimonio Liquido.*?([\d.,]+)\s+([\d.,]+)", texto)
    patrimonio_liquido = padrao_patrimonio_liquido.group(1).replace('.', '').replace(',', '.') if padrao_patrimonio_liquido else None
    padrao_lucro_prejuizo = re.search(r"Lucro \(Prejuizo\) do Periodo\s*[\(\)]*\s*([\d.,]+)", texto)
    lucro_prejuizo = padrao_lucro_prejuizo.group(1).replace('.', '').replace(',', '.') if padrao_lucro_prejuizo else None
    padrao_patrimonio_liquido = re.search(r"Patrimonio Liquido.*?([\d.,]+)", texto)
    patrimonio_liquido = padrao_patrimonio_liquido.group(1).replace('.', '').replace(',', '.') if padrao_patrimonio_liquido else None
    padrao_operacionais = re.search(r"Atividades Operacionais\s*\(*([\d.,\-\s]+)\)*", texto)
    atividades_operacionais = re.search(r"[\d.,]+", padrao_operacionais.group(1).replace(',', '.')) if padrao_operacionais else None
    atividades_operacionais = float(atividades_operacionais.group().replace('.', '').replace(',', '.')) if atividades_operacionais else None

    padrao_investimento = re.search(r"Atividades de Investimento\s*\(*([\d.,\-\s]+)\)*", texto)
    atividades_investimento = padrao_investimento.group(1).replace('(', '').replace(')', '').replace('.', '').replace(',', '.') if padrao_investimento else None
    padrao_variacao_cambial = re.search(r"Variacao Cambial sobre Caixa e Equivalentes\s*\(*([\d.,\-\s]+)\)*", texto)
    variacao_cambial = re.findall(r"-?\d+\.\d+", padrao_variacao_cambial.group(1).replace(',', '.')) if padrao_variacao_cambial else None
    variacao_cambial = float(variacao_cambial[0]) if variacao_cambial else None
    padrao_aumento_reducao = re.search(r"Aumento \(Reducao\) de Caixa e Equivalentes\s*\(*([\d.,\-\s]+)\)*", texto)
    aumento_reducao_caixa = re.findall(r"-?\d+\.\d+", padrao_aumento_reducao.group(1).replace(',', '.')) if padrao_aumento_reducao else None
    aumento_reducao_caixa = float(aumento_reducao_caixa[0]) if aumento_reducao_caixa else None
    padrao_pessoas_fisicas = re.search(r"Pessoas Fisicas\s*([\d.,\-\s]+)", texto)
    pessoas_fisicas = padrao_pessoas_fisicas.group(1).strip().replace("-","") if padrao_pessoas_fisicas else None
    padrao_pessoas_juridicas = re.search(r"Pessoas Juridicas\s*([\d.,\-\s]+)", texto)
    pessoas_juridicas = padrao_pessoas_juridicas.group(1).strip().replace("-","") if padrao_pessoas_juridicas else None
    padrao_investidores_institucionais = re.search(r"Investidores Institucionais\s*([\d.,\-\s]+)", texto)
    investidores_institucionais = padrao_investidores_institucionais.group(1).replace('-', '').strip() if padrao_investidores_institucionais else None
    padrao_acoes_ordinarias = re.search(r"Quantidade de Acoes Ordinarias\s*([\d.,\-\s]+)", texto)
    acoes_ordinarias = re.search(r"[\d.,]+", padrao_acoes_ordinarias.group(1)).group() if padrao_acoes_ordinarias else None
    padrao_acoes_preferenciais = re.search(r"Quantidade de Acoes Preferenciais\s*([\d.,\-\s]+)", texto)
    acoes_preferenciais = padrao_acoes_preferenciais.group(1).replace('-', '').strip() if padrao_acoes_preferenciais else None
    padrao_total_acoes = re.search(r"Total de Acoes\s*([\d.,]+)", texto)
    total_acoes = padrao_total_acoes.group(1) if padrao_total_acoes else None
    padrao_acoes = re.findall(r"(Ordinárias|Preferenciais|Total)\s*([\d.,]+)", texto)
    informacoes_acoes = {}
    for acao, quantidade in padrao_acoes:
        informacoes_acoes[acao] = quantidade

    # Imprimir as informações

    atualizacao_list.append(atualizacao)
    nome_pregao_list.append(nome_pregao)
    atividade_principal_list.append(atividade_principal)
    classificacao_setorial_list.append(classificacao_setorial)
    site_list.append(site)
    codigos_negociacao_list.append(codigos_negociacao)
    cnpj_list.append(cnpj)
    ativo_imobilizado_list.append(ativo_imobilizado)
    ativo_total_list.append(ativo_total)
    patrimonio_liquido_list.append(patrimonio_liquido)
    lucro_prejuizo_list.append(lucro_prejuizo)
    atividades_operacionais_list.append(atividades_operacionais)
    atividades_investimento_list.append(atividades_investimento)
    variacao_cambial_list.append(variacao_cambial)
    aumento_reducao_caixa_list.append(aumento_reducao_caixa)
    pessoas_fisicas_list.append(pessoas_fisicas)
    pessoas_juridicas_list.append(pessoas_juridicas)
    investidores_institucionais_list.append(investidores_institucionais)
    acoes_ordinarias_list.append(acoes_ordinarias)
    acoes_preferenciais_list.append(acoes_preferenciais)
    total_acoes_list.append(total_acoes)

data = {
  'Atualizacao': atualizacao_list,
  'Nome_Pregao': nome_pregao_list,
  'Atividade_Principal': atividade_principal_list,
  'Classificacao_Setorial': classificacao_setorial_list,
  'Site': site_list,
  'Codigos_Negociacao': codigos_negociacao_list,
  'CNPJ': cnpj_list,
  'Ativo_Imobilizado': ativo_imobilizado_list,
  'Ativo_Total': ativo_total_list,
  'Patrimonio_Liquido': patrimonio_liquido_list,
  'Lucro_Prejuizo': lucro_prejuizo_list,
  'Atividades_Operacionais': atividades_operacionais_list,
  'Atividades_Investimento': atividades_investimento_list,
  'Variacao_Cambial': variacao_cambial_list,
  'Aumento_Reducao_Caixa': aumento_reducao_caixa_list,
  'Pessoas_Fisicas': pessoas_fisicas_list,
  'Pessoas_Juridicas': pessoas_juridicas_list,
  'Investidores_Institucionais': investidores_institucionais_list,
  'Acoes_Ordinarias': acoes_ordinarias_list,
  'Acoes_Preferenciais': acoes_preferenciais_list,
  'Total_Acoes': total_acoes_list
}

df_final = pd.DataFrame(data)

caminho_arquivo_final = 'newCSV/dados_extraidos_final.csv'
df_final.to_csv(caminho_arquivo_final, index=False)