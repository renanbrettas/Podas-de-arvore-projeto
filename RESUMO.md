# Resumo do projeto: da suposição inicial às conclusões

> Versão curta do projeto. Para os detalhes, veja o [README](README.md), os notebooks e
> [`docs/achados_e_qualidade_dos_dados.md`](docs/achados_e_qualidade_dos_dados.md).

## A suposição inicial

**Chamados de poda de árvore seriam um sinal de alerta.** Se um local acumula pedidos de poda, isso
indicaria árvores em situação de risco. Nesse caso, a prefeitura poderia usar os próprios dados do 1746
para **prever onde um pedido de poda vai virar um problema maior**: queda de árvore, queda sobre a
fiação ou falta de luz. Com isso, daria para agir antes e evitar gastos futuros.

Partimos de quatro hipóteses:

1. É possível isolar com clareza os chamados de poda no 1746.
2. É possível identificar quais podas envolvem a rede elétrica (Light).
3. Os chamados são bem localizados o suficiente para comparar locais.
4. **Depois de um chamado de poda, quedas de árvore no mesmo local ficam mais prováveis.**

## O que os dados mostraram

| Hipótese | Resultado | Em uma frase |
|---|:---:|---|
| 1. Isolar a poda no 1746 | ✅ Com ressalvas | Dá para isolar, mas a taxonomia mudou ao longo do tempo. O recorte final tem 3 subtipos e 133.715 chamados em 2021–2025. |
| 2. Identificar a Light | ❌ | A Light não aparece no 1746. No COR ela aparece (cerca de 5,4 mil acionamentos), mas a tabela para em abril de 2024 e tem falhas de registro. |
| 3. Localização confiável | ⚠️ Parcial | Bairro e logradouro estão ótimos (~98–99%). Já a coordenada cai de 95% para 59% dos chamados entre 2021 e 2025. |
| 4. Poda antecipa queda | ❌ | A partir de 30 dias, quedas depois de uma poda são até **menos** frequentes do que o acaso prevê. |

## Conclusões

1. **O pedido de poda, sozinho, não prevê queda de árvore.** No mesmo logradouro, a chance de queda
   depois de uma poda fica entre 15% e 26% abaixo do esperado pelo acaso (horizontes de 30 a 365 dias).
2. **O que parecia sinal era coincidência de registro.** Há um pequeno excesso de quedas na semana
   da poda, mas ele aparece também na semana *antes* dela, e ali é ainda maior. Isso indica que poda e
   queda costumam ser abertas juntas no mesmo episódio (um temporal, por exemplo). A poda não está
   avisando a queda com antecedência.
3. **A questão da rede elétrica não se responde com dados abertos.** O 1746 não registra a Light, e o
   COR público está desatualizado e incompleto. É preciso obter dados da própria Light ou do COR.
4. **O volume bruto por local engana.** Os logradouros campeões (Estrada dos Bandeirantes, Av. Brasil,
   R. Conde de Bonfim) são simplesmente vias longas. Comparar locais exige normalizar pela extensão ou
   usar uma unidade menor (trecho, CEP).
5. **A qualidade dos dados é um achado em si.** Mudanças de taxonomia, coordenadas faltando, IDs
   reaproveitados no COR e o fim da série em 2024 limitam qualquer modelo preditivo construído só
   com o Data.Rio.

## O que isso significa para a prefeitura

Contar chamados de poda **não basta** para priorizar onde agir. Um sistema de alerta útil precisa
cruzar os chamados com informações que de fato expliquem o risco:

- **chuva e vento**, que concentram podas e quedas nos mesmos dias;
- **dados da rede elétrica**, da Light ou do COR atualizado;
- **atendimento da poda**: se e quando foi feita, já que a poda pode justamente evitar a queda;
- uma **unidade espacial menor** que o logradouro.

## Próximos passos

- [ ] Refazer a análise poda → queda por CEP ou trecho de rua (código inicial em `src/podas/cep.py`).
- [ ] Incluir o índice pluviométrico como covariável.
- [ ] Obter ocorrências da Light ou do COR posteriores a abril de 2024.
- [ ] Passar de incidência para um modelo de risco por local.
