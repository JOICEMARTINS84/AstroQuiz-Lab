import random
import streamlit as st
from questions import DATA

st.set_page_config(page_title='AstroQuiz Lab', page_icon='✦', layout='centered')
st.markdown('''<style>
.stApp {background: radial-gradient(ellipse at top right,#20274a 0%,#10182c 37%,#080d18 85%);}
.block-container{padding-top:2rem;max-width:800px;}
[data-testid="stMetric"]{background:#151f35;border:1px solid #34445e;border-radius:16px;padding:12px;}
.stButton button{min-height:3rem;border-radius:12px;}
.hero{padding:24px 0 10px;color:#b4c8ef;letter-spacing:.18em;font-size:12px;}
</style>''', unsafe_allow_html=True)
st.markdown('<div class="hero">MATEMÁTICA &amp; CONTEXTO · OBSERVATÓRIO DE APRENDIZAGEM</div>',unsafe_allow_html=True)
st.title('AstroQuiz Lab')
st.caption('Astronomia e astronáutica · Preparação independente para a OBA')
LEVELS={1:'Nível 1 — 1º ao 3º ano',2:'Nível 2 — 4º e 5º ano',3:'Nível 3 — 6º ao 9º ano',4:'Nível 4 — Ensino Médio'}
s=st.session_state

def start(level, mode):
    pool=DATA[level]
    selected=random.sample([q for q in pool if q[0]=='Astronomia'],7)+random.sample([q for q in pool if q[0]=='Astronáutica'],3)
    random.shuffle(selected)
    s.questions=[]
    for topic, prompt, correct, wrong, explanation in selected:
        opts=[correct,*wrong]; random.shuffle(opts)
        s.questions.append(dict(topic=topic,prompt=prompt,correct=correct,opts=opts,explanation=explanation))
    s.level=level; s.mode=mode; s.idx=0; s.answers=[]; s.locked=False; s.stage='quiz'; s.round=s.get('round',0)+1

if 'stage' not in s: s.stage='home'
if s.stage=='home':
    st.write('Escolha seu nível e teste seus conhecimentos em uma missão de 10 perguntas.')
    a,b=st.columns(2); a.metric('Questões no banco',sum(map(len,DATA.values()))); b.metric('Níveis',len(DATA))
    level=st.selectbox('Escolaridade',list(LEVELS),format_func=LEVELS.get)
    mode=st.radio('Modo de jogo',['Treino comentado','Simulado'],help='No simulado, as explicações ficam para o final.')
    if st.button('Iniciar missão',type='primary',use_container_width=True): start(level,mode); st.rerun()
elif s.stage=='quiz':
    total=len(s.questions); q=s.questions[s.idx]
    st.progress(len(s.answers)/total,text=f'Questão {s.idx+1} de {total}')
    a,b=st.columns(2); a.metric('Respondidas',f'{len(s.answers)}/{total}'); b.metric('Acertos' if s.mode=='Treino comentado' else 'Modo',sum(r['ok'] for r in s.answers) if s.mode=='Treino comentado' else 'Simulado')
    st.caption(f'{LEVELS[s.level]} · {q["topic"]}')
    st.subheader(q['prompt'])
    choice=st.radio('Selecione uma alternativa:',q['opts'],index=None,key=f'choice_{s.round}_{s.idx}',disabled=s.locked)
    if not s.locked:
        if st.button('Confirmar resposta',type='primary',disabled=choice is None,use_container_width=True):
            s.answers.append(dict(q=q,chosen=choice,ok=choice==q['correct'])); s.locked=True; st.rerun()
    else:
        if s.mode=='Treino comentado':
            if s.answers[-1]['ok']: st.success('Resposta correta!')
            else: st.error(f'Resposta correta: {q["correct"]}')
            st.info(q['explanation'])
        else: st.success('Resposta registrada.')
        if st.button('Ver resultado' if s.idx+1==total else 'Próxima questão',type='primary',use_container_width=True):
            if s.idx+1==total: s.stage='results'
            else: s.idx+=1; s.locked=False
            st.rerun()
    if st.button('Voltar ao início'): s.stage='home'; st.rerun()
else:
    total=len(s.answers); hits=sum(r['ok'] for r in s.answers)
    st.subheader('Missão concluída')
    a,b,c=st.columns(3); a.metric('Acertos',f'{hits}/{total}'); b.metric('Aproveitamento',f'{100*hits/total:.0f}%'); c.metric('Erros',total-hits)
    st.progress(hits/total)
    for topic in ['Astronomia','Astronáutica']:
        subset=[r for r in s.answers if r['q']['topic']==topic]
        st.write(f'**{topic}:** {sum(r["ok"] for r in subset)}/{len(subset)}')
    st.subheader('Gabarito comentado')
    for i,r in enumerate(s.answers,1):
        q=r['q']
        with st.expander(f'{i}. {"Correta" if r["ok"] else "Revisar"} — {q["prompt"]}'):
            st.write(f'**Sua resposta:** {r["chosen"]}');st.write(f'**Resposta correta:** {q["correct"]}');st.write(q['explanation'])
    if st.button('Nova missão',type='primary',use_container_width=True): s.stage='home'; st.rerun()
st.divider()
with st.expander('Fontes e créditos'):
    st.markdown('Questões autorais de treinamento, elaboradas a partir dos conteúdos programáticos da OBA de 2025. Não são transcrições das provas oficiais. Projeto educacional independente, sem vínculo com a organização da OBA.')
    st.markdown('[Conteúdos oficiais da OBA 2025](https://docs.oba.org.br/regulamento-da-28-olimpiada-brasileira-de-astronomia-e-astronautica-28-oba-2025) · [Provas e gabaritos oficiais](https://site.oba.org.br/provas-e-gabaritos)')
    st.caption('Matemática & Contexto · Joice Souza Martins Santos')
