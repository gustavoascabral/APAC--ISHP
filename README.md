# Painel APAC

Painel de acompanhamento das APACs produzidas no âmbito do projeto. Você solta a planilha exportada do sistema sobre a página e o painel se recalcula inteiro — etapas do fluxo, competências, OCI, autorizadores, CID, perfil dos pacientes e a lista de pontos que travam o faturamento.

Solte também a planilha da **regulação (SISREG)** e o painel liga uma coisa à outra pelo CNS: quem foi agendado, quem foi atendido, quem faltou, e onde a chave do ciclo ficou aberta.

A tabela do fim da página traz a planilha **completa**: todas as 26 colunas, com nome do paciente, CNS, CPF, nome da mãe e endereço exatamente como estão na base, sem nada resumido nem omitido.

A leitura acontece dentro do navegador. **Nenhum dado de paciente é enviado para servidor nenhum**, mesmo com a página hospedada no GitHub Pages.

---

## Arquivos

| Arquivo | Para que serve |
| --- | --- |
| `index.html` | O painel inteiro: interface, leitura das planilhas e gráficos. Um arquivo só, sem build. |
| `gerar_dados_publicos.py` | Converte as planilhas em `dados/dados-publicos.json`, já sem dados pessoais. Opcional. |
| `dados/dados-publicos.json` | Dados sem identificação que a página carrega sozinha ao abrir. Apague se quiser que o painel sempre comece vazio. |

---

## As duas planilhas

### 1. Relatório de APAC — obrigatória

O `relatorio-apac-....xlsx` exportado do sistema, sem nenhuma edição. É a base do painel: etapa, competência, procedimento, CID, validade e o CNS do paciente.

### 2. Regulação / SISREG — opcional

A exportação de atendimentos do SISREG. É o que responde "essa APAC corresponde a um atendimento que aconteceu de verdade?".

Colunas reconhecidas (sem se importar com acento, maiúscula ou ordem):

`Unidade Solicitante`, `Unidade Exec.`, `Cód. Proced.`, `Descrição (Procedimento)`, `Risco`, `Cód. Solicitação`, `CNS`, `Data da Solic.`, `Tempo de Espera`, `Data do Atend.`, `CID`, `Status`.

A coluna `Telefone` é ignorada de propósito: o painel não usa contato de paciente, então ele nem entra na memória do navegador.

**A ordem de carga não importa.** O painel reconhece cada planilha pelas colunas, então você pode soltar as duas de uma vez na área tracejada, usar os botões **Anexar APAC** e **Anexar regulação** no topo, ou até trocar os campos — ele acerta sozinho e avisa. Se a regulação chegar primeiro, ela fica guardada esperando a APAC.

---

## A chave do ciclo

Esta é a leitura que o cruzamento produz, e ela está escrita na própria tela:

**Chave fechada** — o paciente foi atendido no SISREG **e** a APAC está na etapa Autorizada. Ciclo completo: o atendimento aconteceu e a produção está pronta para faturar.

**Chave aberta** — falta um dos lados. Cada linha da tabela traz a leitura do porquê, na coluna *Leitura da chave*:

| Situação | O que significa |
| --- | --- |
| Atendido, APAC ainda não autorizada | O atendimento aconteceu e a APAC parou no meio do fluxo. É o caso mais caro: produção feita que ainda não vira faturamento. |
| Atendido, mas a APAC foi reprovada ou arquivada | O atendimento aconteceu e a APAC morreu. Vale conferir o motivo da reprovação. |
| Paciente faltou ao atendimento | A regulação registrou falta. Confira se a APAC deve ser cancelada ou se houve remarcação fora do período. |
| Agendamento pendente de confirmação | O SISREG não confirmou o atendimento. |
| Agendamento ainda por acontecer | Data à frente de hoje. |
| APAC sem nenhum registro na regulação | O CNS não aparece na planilha da regulação. Costuma ser atendimento de outro período ou paciente que entrou por outra porta. |

O caminho inverso — **atendimento sem nenhuma APAC** — não cabe na tabela de APACs, então tem cartão próprio no fim do bloco da regulação, com botão para exportar a lista em CSV. É produção realizada que não foi registrada.

Quando um paciente tem mais de um agendamento, o painel usa o mais adiantado no ciclo (atendido na frente de agendado, agendado na frente de pendente) e mostra a contagem na coluna *Agendamentos*.

---

## O que o painel calcula

**Indicadores do topo** — contagens absolutas de cada etapa do fluxo. O painel não calcula nem exibe percentual de aprovação em lugar nenhum: o anel da íris mostra a repartição das etapas e traz no centro o total de APACs do recorte. Com a regulação carregada entram mais três: chave fechada, atendido sem autorização e APACs sem agendamento.

- **Validade vencida** — APACs cuja data de validade já passou e que não foram autorizadas nem arquivadas. É a produção em risco de não ser faturada.
- **Registros incompletos** — sem procedimento, sem CID ou sem competência. Não chegam ao faturamento enquanto estiverem assim.

**Ciclo da regulação até o faturamento** — o trilho de quatro passos: agendamentos → atendidos → com APAC → chave fechada, com a perda em cada passo.

**Pontos de atenção** — cada linha tem um botão *Filtrar* que aplica o recorte no painel e na tabela, para você trabalhar a lista.

**Duplicidade** — mesmo paciente (mesmo CNS, ou CPF quando falta o CNS) com mais de uma APAC. Parte é reemissão legítima, parte é retrabalho.

---

## Filtros

Competência, **OCI / procedimento**, autorizador, UF, município, CID, busca livre e recortes prontos (validade vencida, registros incompletos, pacientes com mais de uma APAC). O seletor de OCI lista cada procedimento com o código SIGTAP e a quantidade de APACs, e vale para o painel inteiro — indicadores, gráficos e tabela. As etapas ficam como botões logo abaixo: clique para somar ou tirar cada uma do recorte.

Com a regulação carregada aparece o filtro **Regulação**: chave fechada, chave aberta, atendido com APAC não autorizada, com agendamento, sem agendamento, paciente faltou, agendamento pendente ou futuro.

A tabela mostra tudo aberto por padrão. A caixa **Mascarar dados pessoais** existe só para quando você precisar projetar o painel em reunião: com ela marcada, nome vira "MARIA S. S.", CPF e CNS ficam com os dígitos finais e o resto oculto — vale também para a lista de atendidos sem APAC. Desmarcada, o CSV exportado também sai completo.

---

## Publicar no GitHub Pages

1. Crie um repositório novo (ex.: `painel-apac`).
2. Suba `index.html` na raiz do repositório. Se for usar o modo publicado, suba também a pasta `dados/`.
3. No repositório, vá em **Settings → Pages**.
4. Em *Source*, escolha **Deploy from a branch**; em *Branch*, escolha `main` e a pasta `/ (root)`. Salve.
5. Em um ou dois minutos o painel fica no ar em `https://SEU-USUARIO.github.io/painel-apac/`.

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

A página abre vazia pedindo as planilhas. Anexe a de APAC e, se tiver, a da regulação. Para atualizar, use os botões que ficam sempre no topo e escolha o arquivo novo; nada de reprocessar ou publicar.

Os botões são `<label>` ligados aos campos de arquivo, então abrem o seletor mesmo em celular e mesmo se algum script da página falhar.

É o modo mais seguro: os arquivos com nome, CPF e CNS nunca saem do computador de quem abriu a página.

### Modo publicado

Se você quer que o painel já abra com os números carregados, sem ninguém precisar ter as planilhas em mãos:

1. Abra o painel e carregue as planilhas.
2. Clique em **Gerar dados para publicar**. Baixa um `dados-publicos.json` sem nome, CPF, CNS, endereço, data de nascimento, telefone e número da APAC. Se a regulação estiver carregada, ela vai junto, também sem CNS.
3. Coloque o arquivo em `dados/dados-publicos.json` no repositório e faça o commit.

Ao abrir a página, ela procura esse arquivo e carrega sozinha — inclusive o cruzamento com a regulação, porque o paciente continua identificado pelo mesmo código sem volta dos dois lados. Quem abrir ainda pode soltar as planilhas por cima para ver a versão completa e atualizada.

Mesmo resultado pela linha de comando, útil para automatizar:

```bash
pip install pandas openpyxl
python gerar_dados_publicos.py relatorio-apac-2026-08-13.xlsx --regulacao ISHP_Atendimentos_SISREG.xlsx
git add dados/dados-publicos.json && git commit -m "Atualiza dados" && git push
```

O `--regulacao` é opcional; sem ele o arquivo sai só com as APACs, como antes.

> **Antes de publicar:** confira a política da sua instituição. Mesmo sem identificação de paciente, os números de produção do projeto, os nomes dos autorizadores e as unidades solicitantes ficam visíveis para qualquer pessoa. Se o repositório for privado, o GitHub Pages exige plano pago para manter a página privada — na dúvida, use o modo carregar e mantenha o repositório privado.

---

## Como o cruzamento encontra o paciente

No modo carregar é direto: o CNS da APAC contra o CNS da regulação, só dígitos, com o zero da frente reposto quando a planilha comeu.

No modo publicado o CNS já foi trocado por um código sem volta, então o painel refaz a mesma conta em cima do CNS da regulação e procura o código. Ele testa as variantes que os geradores já produziram ao longo do tempo, então arquivos `dados-publicos.json` antigos continuam funcionando.

> Versões antigas do `gerar_dados_publicos.py` liam o CNS como número e gravavam um dígito a mais no código do paciente. Está corrigido, e o painel aceita as duas formas — mas se você quiser os dois lados calculados do mesmo jeito, é só gerar o arquivo de novo com o script atualizado.

---

## Colunas esperadas na planilha de APAC

`Etapa`, `Autorizador`, `Unidade executora`, `Profissional solicitante`, `Registro conselho`, `Nome paciente`, `Sexo`, `Nome mãe`, `CPF`, `CNS`, `Endereço`, `Município`, `UF`, `Nascimento`, `Idade`, `Número APAC`, `Dia cadastro`, `Competência`, `Mês cadastro`, `Ano cadastro`, `Data de validade`, `CID`, `Grupo`, `Código procedimento`, `Nome procedimento`, `Origem do recurso`.

Coluna que faltar simplesmente aparece como "—". Coluna a mais é ignorada. Se o sistema mudar o nome de alguma coluna, ajuste o mapa `CHAVES` (APAC) ou `CHAVES_REG` (regulação), no início do bloco de script do `index.html`.

Etapas novas também funcionam: entram com uma cor própria. Para fixar a cor e a posição de uma etapa na ordem do funil, acrescente-a em `CORES_ETAPA`, logo no começo do script.

---

## Ajustes comuns

| O que mudar | Onde |
| --- | --- |
| Cores das etapas | `CORES_ETAPA`, início do script |
| Quais etapas contam como encerradas | `FINALIZADAS` |
| Colunas e ordem da tabela | `COLUNAS_TABELA` |
| Colunas da lista de atendidos sem APAC | `COLUNAS_ORFAOS` |
| Quais colunas somem no arquivo publicado | marca `sensivel:true` na coluna |
| Nomes de status do SISREG | `normalizarStatus` |
| Regra da chave fechada | função `cruzarRegulacao` e `leituraChave` |
| Faixas etárias e faixas de espera | `faixaEtaria` e `faixaEspera` |
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
| "Não deu para reconhecer esta planilha" | As colunas não batem com nenhuma das duas. A de APAC precisa de `Etapa` e `Número APAC`; a da regulação precisa de `CNS`, `Status` e `Data do Atend.` na primeira aba. |
| "Não foi possível ler o arquivo" | Feche a planilha no Excel e tente de novo. |
| Página abre vazia, sem erro | Normal: é o modo carregar. Clique em **Anexar APAC**. |
| Regulação carregada, mas nenhuma APAC vinculada | Confira se as duas exportações têm CNS preenchido e se cobrem o mesmo período. |

Abrir o `index.html` com duplo clique (endereço começando com `file://`) funciona para carregar planilha, mas o navegador bloqueia a leitura do `dados/dados-publicos.json` — nesse caso o painel simplesmente começa vazio. Publicado no GitHub Pages, os dois modos funcionam.
