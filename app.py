import random
from html import escape

import streamlit as st
from questions import DATA

st.set_page_config(page_title="AstroQuiz Lab", page_icon="✦", layout="wide")

st.markdown("""
<style>
:root{--ink:#20222e;--muted:#676979;--line:#e3e3ec;--paper:#fbfaf8;--violet:#6246c9}
.stApp{background:var(--paper);color:var(--ink)}
[data-testid="stHeader"]{background:transparent;}
[data-testid="stToolbar"]{visibility:hidden;}
.block-container{max-width:1120px;padding:1.8rem 1.5rem 2.5rem}
h1,h2,h3,p,li{letter-spacing:-.025em}
.brand{display:flex;align-items:center;justify-content:space-between;gap:14px;margin-bottom:20px;color:var(--ink)}
.brand-name{display:flex;align-items:center;gap:10px;font-weight:800;font-size:1.05rem}
.brand-mark{display:inline-grid;place-items:center;background:#222331;color:white;width:34px;height:34px;border-radius:10px;font-size:22px}
.brand-tag{font-size:.7rem;font-weight:700;letter-spacing:.14em;color:var(--muted);text-transform:uppercase}
.hero{isolation:isolate;position:relative;overflow:hidden;min-height:325px;border-radius:26px;padding:42px 42px 35px;background:radial-gradient(ellipse at 80% 110%,#40334f 0%,transparent 64%),linear-gradient(125deg,#10111d,#24243e 66%,#19283a);color:#fff;display:flex;align-items:center}
.hero-copy{position:relative;z-index:2;width:65%;max-width:580px}
.hero-kicker{font-size:.72rem;font-weight:700;letter-spacing:.19em;color:#c2b9ff;text-transform:uppercase;margin-bottom:16px}
.hero h1{font-size:clamp(2.7rem,5.4vw,4.7rem);line-height:.99;color:#fff;margin:0 0 17px;font-weight:800;letter-spacing:-.065em}
.hero p{font-size:1.06rem;line-height:1.6;max-width:440px;color:#d7d7e8;margin:0 0 22px}
.hero-tags{display:flex;flex-wrap:wrap;gap:8px}
.hero-tags span{padding:7px 12px;background:#ffffff13;border:1px solid #ffffff28;border-radius:30px;font-size:.76rem;color:#e5e2f4}
.planet-art{position:absolute;right:-18px;top:50%;width:44%;max-width:450px;transform:translateY(-50%);z-index:1;pointer-events:none}
.star{background:white;border-radius:50%;width:2px;height:2px;position:absolute;opacity:.55;box-shadow:0 0 9px #d9d1ff}
.section-kicker{color:var(--violet);font-size:.72rem;font-weight:800;letter-spacing:.15em;text-transform:uppercase;margin-top:12px}
.section-title{font-size:1.55rem;font-weight:800;color:var(--ink);letter-spacing:-.055em;margin:3px 0 4px}
.section-desc{font-size:.93rem;color:var(--muted);margin:0 0 10px}
[data-testid="stVerticalBlockBorderWrapper"]{border-radius:20px!important;border-color:var(--line)!important;background:white;}
.stButton button{min-height:50px;border-radius:11px!important;font-weight:650;box-shadow:none;transition:border-color .15s,background .15s,transform .15s;}
.stButton button:hover{transform:translateY(-1px)}
.stButton button:focus-visible{outline:3px solid #b5a7ff;outline-offset:2px}
.stButton button[kind="primary"]{background:#6246c9;color:white;border-color:#6246c9}
.stButton button[kind="primary"]:hover{background:#5034b4;color:white;border-color:#5034b4}
.st-key-levels .stButton button,.st-key-choices .stButton button{height:auto;min-height:65px;white-space:normal;justify-content:flex-start;text-align:left;padding:14px 18px;background:white;border:1px solid #dcdce6;color:#222331}
.st-key-levels .stButton button[kind="primary"]{background:#f0ecff;color:#4f32a8;border:2px solid #765cdb}
.st-key-choices .stButton button:hover,.st-key-levels .stButton button:hover{border-color:#816ce2;background:#f5f2ff;color:#4f32a8}
.st-key-choices .stButton button p,.st-key-levels .stButton button p{text-align:left;line-height:1.4;font-size:1rem}
.small-note{font-size:.83rem;line-height:1.5;color:var(--muted)}
.feature{display:flex;align-items:flex-start;gap:13px;margin:16px 0 20px}
.feature-num{flex-shrink:0;display:grid;place-items:center;width:35px;height:35px;background:#f0ecff;color:#6246c9;font-size:.8rem;font-weight:800;border-radius:10px}
.feature strong{display:block;color:#262638;font-size:.94rem}
.feature p{font-size:.85rem;line-height:1.5;margin:3px 0;color:var(--muted)}
.question-header{display:flex;justify-content:space-between;align-items:center;gap:12px;margin-bottom:8px}
.question-tag{background:#f0ecff;color:#5e43be;border-radius:50px;padding:7px 13px;font-weight:700;font-size:.75rem}
.question-index{font-size:.82rem;color:var(--muted);font-weight:700}
.question-title{font-size:clamp(1.4rem,3vw,2.05rem);line-height:1.3;font-weight:750;letter-spacing:-.045em;margin:12px 0 6px;overflow-wrap:anywhere;color:var(--ink)}
.progress-track{display:flex;gap:5px;margin:8px 0 20px}
.progress-track span{flex:1;height:6px;border-radius:5px;background:#e3e1e9}
.progress-track .done{background:#6246c9}
.progress-track .current{background:#bcaeff}
.mini-stat{padding:15px 16px;border-radius:14px;background:#f7f6fb;border:1px solid #e9e6f2;margin:8px 0}
.mini-stat span{display:block;color:var(--muted);font-size:.75rem;font-weight:700}
.mini-stat strong{font-size:1.45rem;letter-spacing:-.06em;color:var(--ink)}
.answer-card{border:1px solid #e1e1e9;background:#fff;border-radius:12px;padding:15px 17px;margin:7px 0;color:#262638;line-height:1.5}
.answer-card.good{background:#edf9f2;border-color:#8acaa5;color:#185b3a}
.answer-card.bad{background:#fff2f0;border-color:#edada8;color:#8b3431}
.answer-card.chosen{background:#f0ecff;border-color:#b4a5f0;color:#5338a8}
.answer-card b{margin-right:10px;font-size:.8rem}
.result-panel{background:#1d2032;color:#fff;border-radius:23px;padding:32px;display:flex;align-items:center;gap:26px;margin-bottom:10px}
.result-panel h2{color:white;font-size:clamp(1.6rem,4vw,2.6rem);line-height:1.15;margin:6px 0}
.result-panel p{color:#d8d7e8;margin:0;line-height:1.5}
.score-ring{height:126px;width:126px;flex-shrink:0;display:grid;place-items:center;border-radius:50%}
.score-core{width:106px;height:106px;background:#1d2032;border-radius:50%;display:grid;place-content:center;text-align:center}
.score-core strong{font-size:2rem;letter-spacing:-.07em}
.score-core span{font-size:.7rem;color:#bfbdd5}
.footer-note{color:#767685;font-size:.75rem;padding:12px 0;text-align:center;letter-spacing:.02em}
@media(max-width:680px){
.block-container{padding:1.1rem .9rem 2rem}
.brand-tag{font-size:.58rem}.brand-name{font-size:.93rem}
.hero{min-height:345px;padding:28px 22px;align-items:flex-start}
.hero-copy{width:100%}.hero p{max-width:95%;font-size:.94rem}
.planet-art{width:52%;top:auto;bottom:-48px;right:-32px;transform:none;opacity:.49}
.hero h1{font-size:3rem}
.result-panel{padding:22px 15px;gap:14px}.score-ring{width:94px;height:94px}.score-core{width:78px;height:78px}.score-core strong{font-size:1.5rem}
}
</style>
""", unsafe_allow_html=True)

LEVELS = {1: "1º ao 3º ano", 2: "4º e 5º ano", 3: "6º ao 9º ano", 4: "Ensino Médio"}
s = st.session_state
if "stage" not in s:
    s.stage = "home"
if "selected_level" not in s:
    s.selected_level = 3

def html(markup):
    st.markdown(markup, unsafe_allow_html=True)

def section(kicker, title, desc=""):
    html(f'<div class="section-kicker">{kicker}</div><div class="section-title">{title}</div><div class="section-desc">{desc}</div>')

def stat(label, value):
    html(f'<div class="mini-stat"><span>{escape(str(label))}</span><strong>{escape(str(value))}</strong></div>')

def start(level, mode):
    pool = DATA[level]
    selected = random.sample([q for q in pool if q[0] == "Astronomia"], 7)
    selected += random.sample([q for q in pool if q[0] == "Astronáutica"], 3)
    random.shuffle(selected)
    s.questions = []
    for topic, prompt, correct, wrong, explanation in selected:
        opts = [correct, *wrong]
        random.shuffle(opts)
        s.questions.append(dict(topic=topic, prompt=prompt, correct=correct, opts=opts, explanation=explanation))
    s.level = level
    s.mode = mode
    s.idx = 0
    s.answers = []
    s.locked = False
    s.stage = "quiz"
    s.round = s.get("round", 0) + 1

def choose(choice):
    if not s.locked:
        q = s.questions[s.idx]
        s.answers.append(dict(q=q, chosen=choice, ok=choice == q["correct"]))
        s.locked = True

def advance():
    if s.idx + 1 == len(s.questions):
        s.stage = "results"
    else:
        s.idx += 1
        s.locked = False

def home():
    s.stage = "home"

html('<div class="brand"><div class="brand-name"><span class="brand-mark">✦</span> AstroQuiz Lab</div><span class="brand-tag">Matemática &amp; Contexto</span></div>')

if s.stage == "home":
    stars = "".join(f'<i class="star" style="left:{x}%;top:{y}%"></i>' for x,y in [(8,12),(48,10),(56,74),(69,13),(94,12),(93,82),(61,42),(48,86),(78,90),(99,47),(35,18),(84,27)])
    html('''<div class="hero">''' + stars + '''
    <div class="hero-copy"><div class="hero-kicker">Uma jornada pelo universo</div>
    <h1>Explore.<br>Questione.<br>Descubra.</h1>
    <p>Teste seus conhecimentos de astronomia e astronáutica. Aprenda a cada missão e prepare-se para a OBA.</p>
    <div class="hero-tags"><span>48 questões</span><span>4 níveis</span><span>10 por missão</span></div></div>
    <svg class="planet-art" viewBox="0 0 420 420" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
    <defs><radialGradient id="sphere" cx=".3" cy=".25" r=".8"><stop stop-color="#f3dac0"/><stop offset=".42" stop-color="#c294a0"/><stop offset=".75" stop-color="#7b648f"/><stop offset="1" stop-color="#343957"/></radialGradient><linearGradient id="ring" x1="0" x2="1" y1="1" y2="0"><stop stop-color="#a683c4"/><stop offset=".5" stop-color="#f7ddba"/><stop offset="1" stop-color="#736d9d"/></linearGradient><clipPath id="disk"><circle cx="216" cy="210" r="104"/></clipPath></defs>
    <g fill="none" stroke="#c6bbef" opacity=".18"><circle cx="216" cy="210" r="171"/><circle cx="216" cy="210" r="150" stroke-dasharray="2 8"/><path d="M55 210H377M216 49V371"/></g>
    <ellipse cx="216" cy="210" rx="179" ry="47" fill="none" stroke="url(#ring)" stroke-width="21" opacity=".48" transform="rotate(-25 216 210)"/>
    <circle cx="216" cy="210" r="104" fill="url(#sphere)"/>
    <g clip-path="url(#disk)" opacity=".31" fill="none" stroke-linecap="round"><path d="M95 156Q220 204 344 137M92 176Q220 218 343 155" stroke="#e5c7bc" stroke-width="13"/><path d="M95 221Q212 263 345 194M93 249Q232 285 342 226M100 286Q230 314 337 263" stroke="#55486f" stroke-width="11"/></g>
    <g transform="rotate(-25 216 210)" fill="none" stroke="url(#ring)"><path d="M37 210a179 47 0 0 0 358 0" stroke-width="21" opacity=".92"/><path d="M22 210a194 61 0 0 0 388 0" stroke-width="1.8" opacity=".55"/></g>
    <circle cx="344" cy="95" r="5" fill="#e7d6fd"/><circle cx="344" cy="95" r="11" fill="none" stroke="#c1bce9" opacity=".4"/>
    </svg></div>''')
    left, right = st.columns([1.65, 1], gap="large")
    with left:
        section("01 / Sua missão", "Escolha seu nível", "Selecione a etapa escolar para começar.")
        with st.container(key="levels"):
            for chunk in [(1, 2), (3, 4)]:
                cols = st.columns(2)
                for col, level in zip(cols, chunk):
                    with col:
                        st.button(f"Nível {level} · {LEVELS[level]}", key=f"level_{level}", type="primary" if s.selected_level == level else "secondary", use_container_width=True, on_click=lambda n=level: s.update(selected_level=n))
        section("02 / Modo de jogo", "Como você quer jogar?")
        mode = st.radio("Modo", ["Treino comentado", "Simulado"], horizontal=True, label_visibility="collapsed")
        html('<div class="small-note">' + ("Aprenda com a explicação logo após cada resposta." if mode == "Treino comentado" else "Responda todas as questões antes de consultar o gabarito.") + '</div>')
        st.button("Iniciar minha missão  →", type="primary", use_container_width=True, on_click=start, args=(s.selected_level, mode))
    with right:
        with st.container(border=True):
            section("Guia de bordo", "O que te espera")
            html('''<div class="feature"><div class="feature-num">01</div><div><strong>Explore o universo</strong><p>Planetas, estrelas, órbitas, eclipses e outros temas.</p></div></div>
            <div class="feature"><div class="feature-num">02</div><div><strong>Desafie seus conhecimentos</strong><p>Sete perguntas de astronomia e três de astronáutica por rodada.</p></div></div>
            <div class="feature"><div class="feature-num">03</div><div><strong>Aprenda com o resultado</strong><p>Veja sua pontuação e revise o gabarito explicado.</p></div></div>''')
            st.caption("Questões autorais de preparação para a OBA. Não é uma prova oficial.")

elif s.stage == "quiz":
    total = len(s.questions)
    q = s.questions[s.idx]
    letters = "ABCD"
    left, right = st.columns([2.4, 1], gap="large")
    with left:
        with st.container(border=True):
            html(f'<div class="question-header"><span class="question-tag">{escape(q["topic"])}</span><span class="question-index">QUESTÃO {s.idx+1:02d} / {total:02d}</span></div>')
            segments = "".join('<span class="' + ("done" if i < len(s.answers) else "current" if i == s.idx else "") + '"></span>' for i in range(total))
            html('<div class="progress-track">' + segments + '</div>')
            html(f'<div class="question-title">{escape(q["prompt"])}</div>')
            st.caption("Toque em uma alternativa para registrar sua resposta." if not s.locked else "Resposta registrada.")
            with st.container(key="choices"):
                if not s.locked:
                    for i, option in enumerate(q["opts"]):
                        st.button(f"{letters[i]}  ·  {option}", key=f"answer_{s.round}_{s.idx}_{i}", on_click=choose, args=(option,), use_container_width=True)
                else:
                    answer = s.answers[-1]
                    for i, option in enumerate(q["opts"]):
                        style = ""
                        if s.mode == "Treino comentado":
                            if option == q["correct"]: style = "good"
                            elif option == answer["chosen"]: style = "bad"
                        elif option == answer["chosen"]:
                            style = "chosen"
                        html(f'<div class="answer-card {style}"><b>{letters[i]}</b>{escape(option)}</div>')
                    if s.mode == "Treino comentado":
                        if answer["ok"]: st.success("Você acertou!")
                        else: st.error("A alternativa correta está destacada em verde.")
                        st.info(q["explanation"])
                    st.button("Ver meu resultado  →" if s.idx+1 == total else "Próxima questão  →", type="primary", on_click=advance, use_container_width=True)
    with right:
        with st.container(border=True):
            section("Painel da missão", f"Nível {s.level}")
            st.caption(LEVELS[s.level] + " · " + s.mode)
            stat("Respostas registradas", f"{len(s.answers)}/{total}")
            if s.mode == "Treino comentado":
                stat("Acertos", sum(r["ok"] for r in s.answers))
            st.button("Encerrar e voltar", on_click=home, use_container_width=True)

else:
    total = len(s.answers)
    hits = sum(r["ok"] for r in s.answers)
    percent = round(100*hits/total)
    message = "Excelente exploração!" if percent >= 80 else "Continue explorando!"
    html(f'<div class="result-panel"><div class="score-ring" style="background:conic-gradient(#a995fb {percent}%,#45465b 0)"><div class="score-core"><strong>{percent}%</strong><span>ACERTOS</span></div></div><div><div class="hero-kicker">Missão concluída</div><h2>{message}</h2><p>Você acertou {hits} de {total} perguntas. Agora revise suas respostas.</p></div></div>')
    left,right = st.columns([2.15,1], gap="large")
    with left:
        section("Relatório de bordo", "Gabarito comentado")
        for i, r in enumerate(s.answers, 1):
            q = r["q"]
            with st.expander(f'{i:02d} · {"Acertou" if r["ok"] else "Revisar"} — {q["prompt"]}'):
                st.write(f'**Sua resposta:** {r["chosen"]}')
                st.write(f'**Resposta correta:** {q["correct"]}')
                st.write(q["explanation"])
    with right:
        with st.container(border=True):
            section("Desempenho", "Por área")
            for topic in ["Astronomia", "Astronáutica"]:
                subset = [r for r in s.answers if r["q"]["topic"] == topic]
                stat(topic, f'{sum(r["ok"] for r in subset)}/{len(subset)}')
            st.button("Nova missão  →", type="primary", on_click=home, use_container_width=True)

st.divider()
with st.expander("Sobre o projeto e referências"):
    st.markdown("Questões autorais de treinamento, elaboradas a partir dos conteúdos programáticos da OBA de 2025. Não são transcrições de provas oficiais; projeto independente, sem vínculo com a organização da OBA.")
    st.markdown("[Conteúdos oficiais da OBA 2025](https://docs.oba.org.br/regulamento-da-28-olimpiada-brasileira-de-astronomia-e-astronautica-28-oba-2025) · [Provas e gabaritos oficiais](https://site.oba.org.br/provas-e-gabaritos)")
html('<div class="footer-note">AstroQuiz Lab · Matemática &amp; Contexto · Joice Souza Martins Santos</div>')
