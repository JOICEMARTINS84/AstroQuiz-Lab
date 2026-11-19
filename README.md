# AstroQuiz Lab

Projeto educacional independente de Matemática & Contexto, por Joice Souza Martins Santos. Preparação para a Olimpíada Brasileira de Astronomia e Astronáutica.

- 80 questões autorais de preparação para a OBA nos quatro níveis escolares (8 ilustradas) e 17 questões científicas adaptadas em português (97 no total).
- Rodadas de dez questões (sete de astronomia e três de astronáutica).
- Modo treino com feedback imediato e modo simulado com gabarito no final.
- Questões e alternativas embaralhadas; pontuação e revisão comentada.
- Sem cadastro ou armazenamento de dados pessoais.

## Executar no Windows

Abra o PowerShell na pasta do projeto e execute:

```powershell
py -m pip install -r requirements.txt
py -m streamlit run app.py
```

## Publicar

No Streamlit Community Cloud, clique em Create app e selecione o repositório JOICEMARTINS84/AstroQuiz-Lab, a branch main e o arquivo app.py.

## Referências

- [Regulamento e conteúdos da OBA 2025](https://docs.oba.org.br/regulamento-da-28-olimpiada-brasileira-de-astronomia-e-astronautica-28-oba-2025)
- [Provas e gabaritos oficiais](https://site.oba.org.br/provas-e-gabaritos)

As questões são autorais, alinhadas ao conteúdo programático de 2025; não são cópias de provas oficiais. Este projeto não possui vínculo com a organização da OBA.

## Astro Arcade e banco científico

- Space Shooter e Cinturão de Asteroides: minijogos Canvas com som e controles por teclado e toque.
- Nível 5: 17 questões científicas traduzidas/adaptadas, armazenadas localmente em JSON e consultadas com SQLite; não dependem de uma API durante a partida.
- Fonte: P. Fleith, *Astro-MCQ: A Multiple-Choice Question Benchmark Dataset for Evaluating LLMs in Space Mission Engineering and Astronautics* (2025), [dataset](https://huggingface.co/datasets/patrickfleith/astro-mcq), [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Traduções, adaptações, explicações e eventuais correções foram acrescentadas pelo projeto. Importação parcial.

## Campanha OBA e menu de console

Menu em Canvas com cenário animado e nave low-poly em perspectiva, inspirado em jogos da era PlayStation 2. Campanha principal com 10 perguntas por missão: sete de astronomia e três de astronáutica. Pontuação de 100 pontos por acerto, sequência de acertos e cronômetro. Questões escolares autorais, não transcrições oficiais. [Programa oficial da OBA](https://site.oba.org.br/o-que-e-a-oba).
