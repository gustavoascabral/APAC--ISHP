# Painel APAC

Painel de acompanhamento das APACs produzidas no âmbito do projeto. Você solta a planilha exportada do sistema sobre a página e o painel se recalcula inteiro — funil por etapa, competências, autorizadores, CID, perfil dos pacientes e a lista de pontos que travam o faturamento.

A leitura acontece dentro do navegador. **Nenhum dado de paciente é enviado para servidor nenhum**, mesmo com a página hospedada no GitHub Pages.

---

## Arquivos

| Arquivo | Para que serve |
| --- | --- |
| `index.html` | O painel inteiro: interface, leitura da planilha e gráficos. Um arquivo só, sem build. |
| `gerar_dados_publicos.py` | Converte a planilha em `dados/dados-publicos.json`, já sem dados pessoais. Opcional. |
| `dados/dados-publicos.json` | Dados sem identificação que a página carrega sozinha ao abrir. Apague se quiser que o painel sempre comece vazio. |

---

## Publicar no GitHub Pages

1. Crie um repositório novo (ex.: `painel-apac`).
2. Suba `index.html` na raiz do repositório. Se for usar o modo publicado, suba também a pasta `dados/`.
3. No repositório, vá em **Settings → Pages**.
4. Em *Source*, escolha **Deploy from a branch**; em *Branch*, escolha `main` e a pasta `/ (root)`. Salve.
5. Em um ou dois minutos o painel fica no ar em `https://SEU-USUARIO.github.io/painel-apac/`.

Pela linha de comando:

```bash
git init
git add index.html gerar_dados_publicos.py README.md
git commit -m "Painel APAC"
git branch -M main
git remote add origin https://github.com/SEU-USUARIO/painel-apac.git
git push -u origin main
```

---

## Os dois modos de uso

### Modo carregar (recomendado)

A página abre vazia pedindo a planilha. Quem for usar arrasta o arquivo `relatorio-apac-....xlsx` e vê os números na hora. Para atualizar, é só soltar a planilha nova por cima — nada de reprocessar ou publicar nada.

É o modo mais seguro: o arquivo com nome, CPF e CNS nunca sai do computador de quem abriu a página.

### Modo publicado

Se você quer que o painel já abra com os números carregados, sem ninguém precisar ter a planilha em mãos:

1. Abra o painel e carregue a planilha.
2. Clique em **Gerar dados para publicar**. Baixa um `dados-publicos.json` sem nome, CPF, CNS, endereço, data de nascimento e número da APAC.
3. Coloque o arquivo em `dados/dados-publicos.json` no repositório e faça o commit.

Ao abrir a página, ela procura esse arquivo e carrega sozinha. Quem abrir ainda pode soltar uma planilha por cima para ver a versão completa e atualizada.

Mesmo resultado pela linha de comando, útil para automatizar:

```bash
pip install pandas openpyxl
python gerar_dados_publicos.py relatorio-apac-2026-08-13.xlsx
git add dados/dados-publicos.json && git commit -m "Atualiza dados" && git push
```

> **Antes de publicar:** confira a política da sua instituição. Mesmo sem identificação de paciente, os números de produção do projeto e os nomes dos autorizadores ficam visíveis para qualquer pessoa. Se o repositório for privado, o GitHub Pages exige plano pago para manter a página privada — na dúvida, use o modo carregar e mantenha o repositório privado.

---

## O que o painel calcula

**Indicadores do topo**

- **Taxa de autorização** — autorizadas dividido por tudo que já foi decidido (autorizadas + reprovadas). Ignora o que ainda está na fila, para não parecer baixa só porque tem muita coisa parada.
- **Validade vencida** — APACs cuja data de validade já passou e que não foram autorizadas nem arquivadas. É a produção em risco de não ser faturada.
- **Registros incompletos** — sem procedimento, sem CID ou sem competência. Não chegam ao faturamento enquanto estiverem assim.

**Pontos de atenção** — cada linha tem um botão *Filtrar* que aplica o recorte no painel e na tabela, para você trabalhar a lista.

**Duplicidade** — mesmo paciente (mesmo CNS, ou CPF quando falta o CNS) com mais de uma APAC. Parte é reemissão legítima, parte é retrabalho.

---

## Colunas esperadas na planilha

O painel reconhece as colunas pelo nome, sem se importar com acento, maiúscula ou a ordem:

`Etapa`, `Autorizador`, `Unidade executora`, `Profissional solicitante`, `Registro conselho`, `Nome paciente`, `Sexo`, `Nome mãe`, `CPF`, `CNS`, `Endereço`, `Município`, `UF`, `Nascimento`, `Idade`, `Número APAC`, `Dia cadastro`, `Competência`, `Mês cadastro`, `Ano cadastro`, `Data de validade`, `CID`, `Grupo`, `Código procedimento`, `Nome procedimento`, `Origem do recurso`.

Coluna que faltar simplesmente aparece como "—". Coluna a mais é ignorada. Se o sistema mudar o nome de alguma coluna, ajuste o mapa `CHAVES`, no início do bloco de script do `index.html`.

Etapas novas também funcionam: entram com uma cor própria. Para fixar a cor e a posição de uma etapa na ordem do funil, acrescente-a em `CORES_ETAPA`, logo no começo do script.

---

## Ajustes comuns

| O que mudar | Onde |
| --- | --- |
| Cores das etapas | `CORES_ETAPA`, início do script |
| Quais etapas contam como decididas | `FINALIZADAS` |
| Colunas e ordem da tabela | `COLUNAS_TABELA` |
| Faixas etárias | função `faixaEtaria` |
| Registros por página | `estado.porPagina` |
| Paleta e tipografia | bloco `:root` do CSS |

O painel usa duas dependências, ambas via CDN: a biblioteca SheetJS para ler o `.xlsx` e as fontes do Google. Se a rede da sua instituição bloqueia CDN, baixe `xlsx.full.min.js` para junto do `index.html` e troque o endereço na tag `<script>` do topo; sem as fontes o painel continua funcionando com a fonte do sistema.
