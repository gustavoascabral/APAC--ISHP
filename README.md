# Painel APAC

Painel de acompanhamento das APACs produzidas no âmbito do projeto. Você solta a planilha exportada do sistema sobre a página e o painel se recalcula inteiro — etapas do fluxo, competências, OCI, autorizadores, CID, perfil dos pacientes e a lista de pontos que travam o faturamento.

A tabela do fim da página traz a planilha **completa**: todas as 26 colunas, com nome do paciente, CNS, CPF, nome da mãe e endereço exatamente como estão na base, sem nada resumido nem omitido.

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

A página abre vazia pedindo a planilha. Clique em **Anexar planilha** e escolha o `relatorio-apac-....xlsx` no computador — ou arraste o arquivo para dentro da área tracejada, se preferir. Para atualizar, use o botão **Anexar planilha** que fica sempre no topo e escolha o arquivo novo; nada de reprocessar ou publicar.

O botão é um `<label>` ligado ao campo de arquivo, então ele abre o seletor mesmo em celular e mesmo se algum script da página falhar.

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

**Indicadores do topo** — contagens absolutas de cada etapa do fluxo. O painel não calcula nem exibe percentual de aprovação em lugar nenhum: o anel da íris mostra a repartição das etapas e traz no centro o total de APACs do recorte.

- **Validade vencida** — APACs cuja data de validade já passou e que não foram autorizadas nem arquivadas. É a produção em risco de não ser faturada.
- **Registros incompletos** — sem procedimento, sem CID ou sem competência. Não chegam ao faturamento enquanto estiverem assim.

**Pontos de atenção** — cada linha tem um botão *Filtrar* que aplica o recorte no painel e na tabela, para você trabalhar a lista.

**Duplicidade** — mesmo paciente (mesmo CNS, ou CPF quando falta o CNS) com mais de uma APAC. Parte é reemissão legítima, parte é retrabalho.

---

## Filtros

Competência, **OCI / procedimento**, autorizador, UF, município, CID, busca livre e recortes prontos (validade vencida, registros incompletos, pacientes com mais de uma APAC). O seletor de OCI lista cada procedimento com o código SIGTAP e a quantidade de APACs, e vale para o painel inteiro — indicadores, gráficos e tabela. As etapas ficam como botões logo abaixo: clique para somar ou tirar cada uma do recorte.

A tabela mostra tudo aberto por padrão. A caixa **Mascarar dados pessoais** existe só para quando você precisar projetar o painel em reunião: com ela marcada, nome vira "MARIA S. S.", CPF e CNS ficam com os dígitos finais e o resto oculto. Desmarcada, o CSV exportado também sai completo.

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
| Quais etapas contam como encerradas | `FINALIZADAS` |
| Colunas e ordem da tabela | `COLUNAS_TABELA` |
| Quais colunas somem no arquivo publicado | marca `sensivel:true` em `COLUNAS_TABELA` |
| Faixas etárias | função `faixaEtaria` |
| Registros por página | `estado.porPagina` |
| Paleta e tipografia | bloco `:root` do CSS |

O painel usa duas dependências, ambas via CDN: a biblioteca SheetJS para ler o `.xlsx` e as fontes do Google. Se a rede da sua instituição bloqueia CDN, baixe `xlsx.full.min.js` para junto do `index.html` e troque o endereço na tag `<script>` do topo; sem as fontes o painel continua funcionando com a fonte do sistema.


---

## Se aparecer erro

O painel mostra uma faixa vermelha no topo explicando o que houve. Os casos mais comuns:

| Mensagem | O que fazer |
| --- | --- |
| "A biblioteca que lê arquivos .xlsx não carregou" | A rede está bloqueando CDN. Baixe `xlsx.full.min.js` do site do SheetJS, deixe na mesma pasta do `index.html` e recarregue — o painel usa a cópia local sozinho. |
| "Formato não reconhecido" | Use o arquivo exportado direto do sistema (.xlsx). PDF, foto da tela ou arquivo renomeado não servem. |
| "Esta planilha não parece ser o relatório de APAC" | A exportação veio com outro layout. Confira se as colunas `Etapa` e `Número APAC` existem na primeira aba. |
| "Não foi possível ler o arquivo" | Feche a planilha no Excel e tente de novo. |
| Página abre vazia, sem erro | Normal: é o modo carregar. Clique em **Anexar planilha**. |

Abrir o `index.html` com duplo clique (endereço começando com `file://`) funciona para carregar planilha, mas o navegador bloqueia a leitura do `dados/dados-publicos.json` — nesse caso o painel simplesmente começa vazio. Publicado no GitHub Pages, os dois modos funcionam.
