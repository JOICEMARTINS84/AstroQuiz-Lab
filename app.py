import random
import json
import base64
from html import escape
from pathlib import Path
from streamlit.components.v1 import declare_component

import streamlit as st
from questions import DATA
from scientific_bank import scientific_questions

DATA = {level: list(pool) for level, pool in DATA.items()}
DATA[5] = scientific_questions()
ILLUSTRATED = json.loads((Path(__file__).parent / "data" / "illustrated_questions.json").read_text(encoding="utf-8"))
FIGURES = {}
for item in ILLUSTRATED:
    question = (item["topic"], item["prompt"], item["correct"], item["wrong"], item["explanation"])
    DATA[item["level"]].append(question)
    FIGURES[item["prompt"]] = (item["figure"], item["alt"])
OBA_EXTRA = json.loads((Path(__file__).parent / "data" / "oba_training_2026.json").read_text(encoding="utf-8"))
for item in OBA_EXTRA:
    DATA[item["level"]].append((item["topic"], item["prompt"], item["correct"], item["wrong"], item["explanation"]))
OBA_REFERENCED = json.loads((Path(__file__).parent / "data" / "oba_2025_referenced.json").read_text(encoding="utf-8"))
OBA_SOURCES = {}
for item in OBA_REFERENCED:
    DATA[item["level"]].append((item["topic"], item["prompt"], item["correct"], item["wrong"], item["explanation"]))
    OBA_SOURCES[item["prompt"]] = item
    if item.get("figure"):
        FIGURES[item["prompt"]] = (item["figure"], item["alt"])
OBA_PDF = json.loads((Path(__file__).parent / "data" / "oba_pdf_2024_2026.json").read_text(encoding="utf-8"))
for item in OBA_PDF:
    # The source identifier prevents collisions between identical short prompts.
    unique_prompt = f'{item["prompt"]} [OBA {item["year"]}/{item["level"]}/{item["question"]}]'
    DATA[item["level"]].append((item["topic"], unique_prompt, item["correct"], item["wrong"], item["explanation"]))
    OBA_SOURCES[unique_prompt] = item
    if item.get("figure"):
        FIGURES[unique_prompt] = (item["figure"], item["alt"])
TOTAL_QUESTIONS = sum(len(pool) for pool in DATA.values())
OBA_COUNT = sum(len(DATA[n]) for n in range(1, 5))

st.set_page_config(page_title="AstroQuiz Lab", page_icon="✦", layout="wide")

background_file = Path(__file__).parent / "astroquiz.webp"
background_uri = "data:image/webp;base64," + base64.b64encode(background_file.read_bytes()).decode("ascii") if background_file.is_file() else ""

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
@keyframes starshine{50%{opacity:.15;box-shadow:0 0 2px #d9d1ff}}
@keyframes planetfloat{0%,100%{translate:0 0}50%{translate:0 -10px}}
.star{animation:starshine 3s ease-in-out infinite}.star:nth-of-type(3n){animation-delay:.8s}.star:nth-of-type(4n){animation-delay:1.6s}
.planet-art{animation:planetfloat 5s ease-in-out infinite}
@media(prefers-reduced-motion:reduce){.star,.planet-art{animation:none}}

:root{--ink:#edf6ff;--muted:#aabdd8;--line:#355483;--paper:#050a1b;--violet:#6bdcff}
.stApp{background-color:#050a1b;background-image:radial-gradient(circle at 18% 20%,#49208a77,transparent 33%),radial-gradient(circle at 84% 75%,#134f9888,transparent 41%),radial-gradient(circle,#a9d8ff77 1px,transparent 1.3px);background-size:auto,auto,37px 37px;color:#edf6ff}
[data-testid="stHeader"]{background:transparent}
.brand{color:#eaf7ff}.brand-mark{background:#092443;border:1px solid #5edbff;box-shadow:0 0 16px #3ed3ff66;color:#c7f7ff}.brand-tag{color:#a8d9f4}
.hero{background:radial-gradient(ellipse at 75% 40%,#3c238e88,transparent 60%),linear-gradient(130deg,#050b20,#0c2144);border:1px solid #347cc3;box-shadow:0 0 35px #1768c73b}
.hero-kicker{color:#7ce6ff}.hero-tags span{background:#0b235f8f;border-color:#458fd3;color:#d4f7ff}
[data-testid="stVerticalBlockBorderWrapper"]{background:#09152de8!important;border-color:#2d4d78!important}
.section-kicker{color:#6ce2ff}.section-title,.question-title{color:#f2f7ff}.section-desc,.small-note{color:#b0c3de}
.stButton button{background:linear-gradient(135deg,#10254b,#192145);border:1px solid #355b96;color:#e6f7ff;box-shadow:0 0 12px #1767b51c}
.stButton button:hover{background:#1e3b68;color:white;border-color:#5edaff;box-shadow:0 0 15px #4cadef48}
.stButton button[kind="primary"]{background:linear-gradient(115deg,#244fdb,#6750d9);color:white;border-color:#78b8ff;box-shadow:0 0 24px #3669de52}
.stButton button[kind="primary"]:hover{background:linear-gradient(115deg,#3269f3,#8266ed);border-color:#a8ecff}
.st-key-levels .stButton button{background:#0b1934e8;color:#e5f6ff;border-color:#37598a}.st-key-levels .stButton button[kind="primary"]{background:linear-gradient(135deg,#163d78,#362c72);color:#c6f7ff;border:2px solid #5bdaff;box-shadow:0 0 19px #40c8ff35}.st-key-levels .stButton button:hover{background:#183c6d;color:white;border-color:#72e6ff}
.feature-num{background:#14385e;color:#8de8ff;border:1px solid #326b9f}.feature strong{color:#e8f4ff}.feature p{color:#b3c5df}.mini-stat{background:#0e2240;border-color:#315784}.mini-stat span{color:#b5cbe6}.mini-stat strong{color:#eaf6ff}.footer-note{color:#a9c8e6}
.result-panel{background:#0b1939ed;border:1px solid #4895c9;box-shadow:0 0 25px #3970d333}.score-core{background:#0b1939}.question-tag{background:#133759;color:#9be9ff}
.st-key-levels,.st-key-choices{border-radius:16px}.stCaption p{color:#a9c9e9}
.game-banner{border:1px solid #4697dd;border-radius:22px;overflow:hidden;box-shadow:0 0 35px #2486e34d;position:relative;background:#040a20}
.game-banner img{display:block;width:100%;height:auto}
.game-menu{display:flex;align-items:center;justify-content:space-between;gap:16px;margin:14px 0 12px;padding:17px 20px;background:#08152de8;border:1px solid #355d91;border-radius:14px}
.game-menu strong{color:#c6f4ff;font-size:1.1rem}.game-menu span{font-size:.82rem;color:#b2c8e7}
@media(max-width:680px){.game-banner{border-radius:14px}.game-menu{display:block}.game-menu span{display:block;margin-top:5px}}


/* Estética de videogame de arcade, inspirada em Pygame. */
:root{--ink:#e8f6ff;--muted:#b2bbd5;--line:#2c4f93;--violet:#65e2ff}
.stApp{background-color:#030616;background-image:radial-gradient(ellipse at 80% 15%,#43207888,transparent 40%),radial-gradient(ellipse at 10% 60%,#0e428c66,transparent 38%),radial-gradient(circle,#a3c4ff88 1px,transparent 1.5px),radial-gradient(circle,#cbe9ffbb .7px,transparent 1px);background-size:auto,auto,71px 71px,43px 43px;background-position:0 0,0 0,13px 7px,3px 29px}
.brand-name,.brand-tag,.section-kicker,.hero-kicker,.mini-stat strong,.game-menu strong,.hero-tags span{font-family:Consolas,'Courier New',monospace;letter-spacing:.065em}
.brand-name{font-weight:900;text-transform:uppercase;color:#94f3ff;text-shadow:0 0 12px #48caff80}.brand-mark{border-radius:4px}
.hero,.game-banner{border-radius:5px;border:2px solid #4c8cdb;box-shadow:0 0 26px #4b84fa55,inset 0 0 40px #131f4f}
.hero h1{font-family:Consolas,'Courier New',monospace;letter-spacing:-.07em;font-weight:950;color:#c5f5ff;text-shadow:3px 3px 0 #7248d5,0 0 28px #39e9ff85}
.hero:after{content:"";position:absolute;inset:0;pointer-events:none;background:repeating-linear-gradient(0deg,transparent 0 3px,#02061525 3px 4px)}
.section-title{font-weight:850;letter-spacing:-.03em}.section-kicker{color:#74eaff}
[data-testid="stVerticalBlockBorderWrapper"],.mini-stat,.game-menu{border-radius:6px!important}
.stButton button{border-radius:5px!important;min-height:51px;font-weight:800}
.stButton button[kind="primary"]{background:linear-gradient(110deg,#0a73bd,#6944d8);border:2px solid #85e9ff;box-shadow:0 4px 0 #143c80,0 0 18px #59bcff50;text-shadow:0 1px 2px #1a115a}
.stButton button:active:not(:disabled){transform:translateY(3px);box-shadow:none}
.st-key-levels .stButton button{border-radius:4px!important;box-shadow:inset 0 0 16px #14234d}
.st-key-levels .stButton button[kind="primary"]{border:2px solid #73f2ff;box-shadow:inset 0 0 25px #3876d866,0 0 14px #52dfff55}
.hero-tags span{border-radius:3px;background:#08182f;color:#a7f5ff}

</style>
""", unsafe_allow_html=True)

if background_uri:
    st.markdown(f"""<style>
    .stApp {{background-image:linear-gradient(180deg,rgba(3,8,25,.38),rgba(3,8,25,.86) 65%),url('{background_uri}');background-size:cover;background-position:center top;background-attachment:fixed;}}
    </style>""", unsafe_allow_html=True)

LEVELS = {1: "1º ao 3º ano", 2: "4º e 5º ano", 3: "6º ao 9º ano", 4: "Ensino Médio", 5: "Desafio científico"}
game = declare_component('astroquiz_game', path=str(Path(__file__).parent / 'game_frontend'))
menu = declare_component('astroquiz_menu', path=str(Path(__file__).parent / 'menu_frontend'))
arcade = declare_component('astro_arcade', path=str(Path(__file__).parent / 'arcade_frontend'))
s = st.session_state
if "stage" not in s:
    s.stage = "home"
if "menu_round" not in s:
    s.menu_round = 0
if "selected_level" not in s:
    s.selected_level = 3

def html(markup):
    st.markdown(markup, unsafe_allow_html=True)

def section(kicker, title, desc=""):
    html(f'<div class="section-kicker">{kicker}</div><div class="section-title">{title}</div><div class="section-desc">{desc}</div>')

def stat(label, value):
    html(f'<div class="mini-stat"><span>{escape(str(label))}</span><strong>{escape(str(value))}</strong></div>')

def start(level, mode, duration, sound=True):
    pool = DATA[level]
    if level == 5:
        selected = random.sample(pool, min(10, len(pool)))
    else:
        selected = []
        for topic, count in [("Astronomia", 7), ("Astronáutica", 3)]:
            topic_pool = [q for q in pool if q[0] == topic]
            referenced = [q for q in topic_pool if q[1] in OBA_SOURCES]
            chosen = random.sample(referenced, min(len(referenced), max(0, count - 1)))
            illustrated = [q for q in topic_pool if q[1] in FIGURES and q not in chosen]
            if illustrated and len(chosen) < count and not any(q[1] in FIGURES for q in chosen):
                chosen.append(random.choice(illustrated))
            selected.extend(chosen + random.sample([q for q in topic_pool if q not in chosen], count - len(chosen)))
    random.shuffle(selected)
    s.questions = []
    for topic, prompt, correct, wrong, explanation in selected:
        opts = [correct, *wrong]
        random.shuffle(opts)
        entry = dict(topic=topic, prompt=prompt, correct=correct, opts=opts, explanation=explanation)
        if prompt in FIGURES:
            drawing, alt = FIGURES[prompt]
            entry["figure"] = "data:image/svg+xml;base64," + base64.b64encode(drawing.encode("utf-8")).decode("ascii")
            entry["figure_alt"] = alt
        if prompt in OBA_SOURCES:
            ref = OBA_SOURCES[prompt]
            from_pdf = prompt.endswith(f'[OBA {ref["year"]}/{ref["level"]}/{ref["question"]}]')
            entry["source"] = f'OBA {ref["year"]} · nível {ref["level"]} · questão {ref["question"]}' + (" (material fornecido)" if from_pdf else " (exercício relacionado)")
            entry["from_pdf"] = from_pdf
            if from_pdf:
                entry["prompt"] = ref["prompt"]
                if ref.get("statements"):
                    entry["statements"] = list(ref["statements"])
            entry["reference"] = ref["reference"]
            entry["official_letter"] = ref["official_letter"]
        s.questions.append(entry)
    s.level = level
    s.mode = mode
    s.duration = duration
    s.sound = sound
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
    s.menu_round = s.get("menu_round", 0) + 1

def open_arcade():
    s.stage = "arcade"
    s.arcade_round = s.get("arcade_round", 0) + 1

html('<div class="brand"><div class="brand-name"><span class="brand-mark">✦</span> AstroQuiz Lab</div><span class="brand-tag">Matemática &amp; Contexto</span></div>')

if s.stage == "home":
    command = menu(oba_count=OBA_COUNT, science_count=len(DATA[5]), round=s.menu_round, key=f"console_menu_{s.menu_round}", default=None)
    if isinstance(command, dict) and command.get("round") == s.menu_round:
        action = command.get("action")
        if action == "arcade":
            open_arcade()
            st.rerun()
        elif action == "quiz":
            level = command.get("level")
            mode = command.get("mode")
            duration = command.get("duration")
            if level in LEVELS and mode in ("Treino comentado", "Simulado") and duration in (0, 30, 45, 60, 90, 120):
                start(level, mode, duration, bool(command.get("sound", True)))
                st.rerun()

elif s.stage == "arcade":
    section("Astro Arcade", "Minijogos espaciais", "Escolha uma missão arcade. A pontuação dos jogos é independente do quiz.")
    a1, a2 = st.columns(2)
    with a1:
        st.button("Voltar ao AstroQuiz", on_click=home, use_container_width=True)
    with a2:
        selected_game = st.selectbox("Escolha o minijogo", ["Space Shooter", "Cinturão de Asteroides"], label_visibility="collapsed", key="arcade_mode")
    arcade_round = s.get("arcade_round", 0)
    arcade_result = arcade(mode="shooter" if selected_game == "Space Shooter" else "dodge", round=arcade_round, key=f"astro_arcade_client_{arcade_round}", default=None)
    if isinstance(arcade_result, dict) and arcade_result.get("round") == arcade_round and arcade_result.get("action") == "exit":
        home()
        st.rerun()
    st.caption("Space Shooter: adaptação para navegador inspirada no código Pygame fornecido pela autora do projeto. Cinturão de Asteroides: desafio de sobrevivência e coleta de amostras.")

elif s.stage == "quiz":
    left, right = st.columns([2.4, 1], gap="large")
    with left:
        result = game(questions=s.questions, round=s.round, level=s.level, mode=s.mode, duration=s.duration, background=background_uri, sound=s.get("sound", True), key=f"game_{s.round}", default=None)
        if isinstance(result, dict) and result.get("round") == s.round:
            if result.get("action") == "exit":
                home()
                st.rerun()
            elif result.get("action") == "complete":
                recorded = result.get("answers")
                if isinstance(recorded, list) and len(recorded) == len(s.questions):
                    checked = []
                    for q, a in zip(s.questions, recorded):
                        choice = a.get("option") if isinstance(a, dict) else None
                        if choice not in q["opts"]:
                            choice = None
                        elapsed = a.get("elapsed", 0) if isinstance(a, dict) else 0
                        if not isinstance(elapsed, (int, float)) or elapsed < 0:
                            elapsed = 0
                        if s.duration:
                            elapsed = min(s.duration, elapsed)
                        checked.append(dict(q=q, chosen=choice or "Não respondida", ok=choice == q["correct"], elapsed=elapsed, expired=choice is None))
                    s.answers = checked
                    s.stage = "results"
                    st.rerun()
    with right:
        with st.container(border=True):
            section("Painel da missão", f"Nível {s.level}")
            st.caption(LEVELS[s.level] + " · " + s.mode)
            stat("Perguntas", len(s.questions))
            stat("Tempo por questão", f"{s.duration} s" if s.duration else "Livre")
            st.caption("Ative ou desative os efeitos sonoros no próprio jogo. Seu resultado será exibido ao concluir a missão.")

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
                if q.get("statements"):
                    for j, statement in enumerate(q["statements"], 1):
                        st.write(f"{j}. {statement}")
                if q.get("figure"):
                    html(f'<img style="width:100%;max-width:560px" src="{q["figure"]}" alt="{escape(q["figure_alt"])}">')
                st.write(f'**Sua resposta:** {r["chosen"]}')
                st.write(f'**Resposta correta:** {q["correct"]}')
                st.write(q["explanation"])
                if q.get("source"):
                    label = "Gabarito informado no PDF" if q.get("from_pdf") else "Gabarito da prova original"
                    st.markdown(f'**Referência:** [{q["source"]}]({q["reference"]}). {label}: {q["official_letter"]}. As alternativas no jogo são embaralhadas.')
                st.caption(f'Tempo utilizado: {r.get("elapsed", 0)} s')
    with right:
        with st.container(border=True):
            section("Desempenho", "Por área")
            for topic in ["Astronomia", "Astronáutica"]:
                subset = [r for r in s.answers if r["q"]["topic"] == topic]
                stat(topic, f'{sum(r["ok"] for r in subset)}/{len(subset)}' if subset else "—")
            stat("Tempo de resposta total", f'{sum(r.get("elapsed", 0) for r in s.answers)} s')
            stat("Tempo esgotado", sum(r.get("expired", False) for r in s.answers))
            st.button("Nova missão  →", type="primary", on_click=home, use_container_width=True)
            st.button("Jogar Astro Arcade", on_click=open_arcade, use_container_width=True)

st.divider()
with st.expander("Sobre o projeto e referências"):
    st.markdown("Níveis 1–4: questões autorais de preparação para a OBA, alinhadas aos conteúdos das edições 2025 e 2026, sem vínculo oficial. Inclui exercícios relacionados a provas de 2025 e questões importadas do material fornecido de 2024, 2025 e 2026. As respostas importadas seguem o gabarito do PDF, sem conferência externa independente. As sequências de verdadeiro ou falso têm alternativas geradas pelo jogo; algumas figuras foram reconstruídas. Nível 5: 17 questões traduzidas e adaptadas do Astro-MCQ, com explicações e atribuição. [Patrick Fleith, Astro-MCQ (2025)](https://huggingface.co/datasets/patrickfleith/astro-mcq) · [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).")
    st.markdown("[Programa da OBA 2026](https://site.oba.org.br/o-que-e-a-oba) · [Conteúdos oficiais da OBA 2025](https://docs.oba.org.br/regulamento-da-28-olimpiada-brasileira-de-astronomia-e-astronautica-28-oba-2025) · [Provas e gabaritos oficiais](https://site.oba.org.br/provas-e-gabaritos)")
html('<div class="footer-note">AstroQuiz Lab · Matemática &amp; Contexto · Joice Souza Martins Santos</div>')
