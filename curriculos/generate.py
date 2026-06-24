#!/usr/bin/env python3
"""Generate role-focused resume PDFs from versioned HTML content."""

from __future__ import annotations

import argparse
import html
import shutil
import subprocess
import tempfile
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parent
HTML_DIR = ROOT / "html"
PDF_DIR = ROOT / "pdf"


PROFILE = {
    "name": "Luiz Carlos Vilela dos Santos",
    "title": "Engenheiro de Software Senior",
    "focus": "Backend - Mobile - RPA",
    "phone": "82 9 9189-0441",
    "email": "luizcarlosvilela@outlook.com.br",
    "linkedin": "linkedin.com/in/luiz-carlos-vilela",
    "github": "github.com/LuizCarlosVilela",
    "location": "Maceio, Alagoas, Brasil",
    "summary": (
        "Engenheiro de Software Senior com ampla experiencia em sistemas de alta complexidade "
        "no setor de FinTech e Open Finance. Especialista em arquitetura de microsservicos, "
        "desenvolvimento mobile com Flutter e automacoes inteligentes (RPA). Historico comprovado "
        "liderando times tecnicos e construindo produtos que atendem mais de 1 milhao de clientes, "
        "processando centenas de milhoes em transacoes financeiras."
    ),
}


METRICS = [
    ("+1M", "clientes PF ativos no app Mentore"),
    ("R$335M", "em transacoes conciliadas na Vink"),
    ("30k+", "empresas PJ atendidas em Open Finance na Celero"),
]


BASE_EXPERIENCES = {
    "mentore": {
        "company": "Mentore Instituicao de Pagamentos",
        "role": "Engenheiro de Software Senior",
        "period": "Jan 2026 - Atual",
        "location": "Sao Paulo, SP",
        "bullets": [
            "Evolucao continua do app Flutter/Dart com novas features, estabilidade e otimizacao de UX.",
            "Desenvolvimento e evolucao de microsservicos e APIs para sustentar o ecossistema web e mobile.",
            "Implementacao de solucoes RPA para otimizar fluxos operacionais internos e integrar sistemas legados.",
            "Gestao do ciclo completo de release e publicacao automatizada nas lojas App Store e Google Play.",
        ],
    },
    "sciensa": {
        "company": "Sciensa -> Mentore Bank",
        "role": "Tech Lead Mobile -> Engenheiro de Software Senior",
        "period": "Jun 2025 - Fev 2026",
        "location": "Sao Paulo, SP",
        "bullets": [
            "Arquitetura e desenvolvimento de ponta a ponta do app bancario PF com Flutter, Swift e Kotlin.",
            "Implementacao de fluxos core: onboarding digital completo, area Pix e solicitacao de cartao.",
            "Definicao do Design System global e dos padroes de gerenciamento de estado para escala de +1 milhao de clientes.",
            "Estruturacao de pipelines CI/CD para o ecossistema mobile com foco em qualidade e agilidade.",
            "Promocao a Tech Lead, com responsabilidade por decisoes arquiteturais, code review e mentoria tecnica.",
        ],
    },
    "celero": {
        "company": "Celero",
        "role": "Engenheiro de Software Senior - Open Finance PJ",
        "period": "Jan 2025 - Jun 2025",
        "location": "Remoto",
        "bullets": [
            "Implementacao de integracoes Open Finance para Caixa Economica Federal e Sicredi.",
            "Desenvolvimento de fluxos Open Finance PJ sob demanda de clientes bancarios.",
            "Participacao no desenho de arquitetura orientada a eventos com Kafka e RabbitMQ.",
            "Processamento assincrono de alto volume em Google Cloud Platform para atender +30 mil empresas.",
        ],
    },
    "vink": {
        "company": "Vink",
        "role": "Engenheiro de Software Senior",
        "period": "Set 2022 - Jan 2025",
        "location": "Campinas, SP",
        "bullets": [
            "Desenvolvimento de sistemas web e mobile para conciliacao bancaria automatizada.",
            "Criacao e evolucao de microsservicos Node.js atendendo milhoes de transacoes.",
            "Aplicacao de DDD, Clean Code e SOLID em sistemas financeiros criticos.",
            "Integracoes com adquirentes como Cielo, PagSeguro, Stone e GetNet.",
            "Conciliacao de aproximadamente R$335 milhoes em transacoes com robos e motor de inteligencia desenvolvido internamente.",
        ],
    },
    "segov": {
        "company": "SEGOV / Policia Civil de Alagoas",
        "role": "Engenheiro de Software Senior",
        "period": "Out 2021 - Fev 2024",
        "location": "Maceio, AL",
        "bullets": [
            "Lideranca tecnica em sistemas internos de gestao para a Policia Civil.",
            "Criacao e otimizacao de APIs robustas com Node.js, NestJS, Prisma e Docker.",
            "Construcao de aplicacoes server-side renderizadas com Next.js e React.",
            "Estruturacao de arquitetura de microsservicos e dados para o PcDigital.",
        ],
    },
    "i9colab": {
        "company": "i9Colab",
        "role": "Consultor de Desenvolvimento / Software Developer / Full Stack Engineer",
        "period": "Out 2020 - Jul 2023",
        "location": "Maceio, AL",
        "bullets": [
            "Desenvolvimento de sistemas web, mobile, e-commerce, automacoes industriais, bots e solucoes com IA.",
            "Atuacao full stack com React, React Native, Node.js, Express, TypeORM, Knex, MySQL e MariaDB.",
            "Experiencia com infraestrutura AWS, administracao de ambientes, seguranca, Git, Scrum e Kanban.",
        ],
    },
}


EDUCATION = [
    "Instituto Federal de Alagoas - Desenvolvimento de Sistemas e Comunicacao (2018 - 2021)",
    "Harvard University - CS50 / Computer Science, e-Learning (2021 - 2022)",
    "Google - Tecnologia da Informacao, e-Learning (2020 - 2021)",
]


CERTIFICATIONS = [
    "Rio Innovation Week",
    "Arquitetura de Redes de Computadores",
    "Desenvolvimento avancado com JavaScript ES6",
    "Praticas avancadas em projetos com ReactJS",
    "Web Developer",
]


RESUMES = [
    {
        "filename": "luiz-carlos-vilela-mobile-backend",
        "title": "Mobile + Backend",
        "headline": "Flutter, Kotlin, Swift, Node.js, NestJS, Kafka, RabbitMQ, CI/CD",
        "badges": ["Flutter - Dart", "Kotlin - Swift", "Node.js - TypeScript", "Kafka - RabbitMQ", "AWS - GCP"],
        "positioning": (
            "Versao focada em vagas mobile com forte integracao backend: concepcao de app, arquitetura, "
            "Design System, estado global, pipelines CI/CD, publicacao em lojas e APIs/microsservicos financeiros."
        ),
        "skills": [
            ("Mobile", ["Flutter", "Dart", "Kotlin", "Swift", "React Native", "Expo", "Design System", "State Management"]),
            ("Backend", ["Node.js", "TypeScript", "NestJS", "Express", "REST APIs", "Microsservicos", "RPA"]),
            ("Eventos e dados", ["Kafka", "RabbitMQ", "Prisma", "Knex", "PostgreSQL", "Redis", "MySQL"]),
            ("Entrega", ["CI/CD Mobile", "App Store", "Google Play", "Docker", "AWS", "GCP", "Code Review"]),
        ],
        "experiences": ["mentore", "sciensa", "celero", "vink", "i9colab"],
        "projects": [
            {
                "name": "App bancario PF - Mentore Bank",
                "kind": "Experiencia profissional",
                "stack": "Flutter, Dart, Swift, Kotlin, CI/CD, App Store, Google Play",
                "impact": (
                    "Arquitetura e desenvolvimento de ponta a ponta do aplicativo PF, incluindo onboarding digital, "
                    "Pix, solicitacao de cartao, padroes globais de estado e Design System para escala de +1M clientes."
                ),
            },
            {
                "name": "Open Finance PJ - Celero",
                "kind": "Experiencia profissional",
                "stack": "Node.js, Kafka, RabbitMQ, GCP, Integracoes bancarias",
                "impact": (
                    "Fluxos de Open Finance PJ e integracoes bancarias para Caixa e Sicredi, com processamento assincrono "
                    "de alto volume atendendo +30 mil empresas."
                ),
            },
            {
                "name": "NextLevelWeek-2 / Proffy",
                "kind": "Projeto publico",
                "url": "https://github.com/LuizCarlosVilela/NextLevelWeek-2",
                "stack": "React Native, React, Node.js, TypeScript, Express, Knex, SQLite, Expo",
                "impact": (
                    "Plataforma com app mobile, web e API REST; reforca integracao mobile-backend, rotas, banco de dados "
                    "e consumo de APIs."
                ),
            },
            {
                "name": "orders-nestjs-kafka",
                "kind": "Projeto publico",
                "url": "https://github.com/LuizCarlosVilela/orders-nestjs-kafka",
                "stack": "NestJS, Kafka, Prisma, TypeScript, Docker",
                "impact": "Comunicacao entre servicos de pedidos e pagamentos usando mensageria e arquitetura orientada a eventos.",
            },
        ],
    },
    {
        "filename": "luiz-carlos-vilela-java-angular",
        "title": "Java + Angular",
        "headline": "Java, Spring Boot, Angular, TypeScript, Node.js, APIs, Microsservicos",
        "badges": ["Java - Spring Boot", "Angular - TypeScript", "Node.js - NestJS", "Kafka - RabbitMQ", "AWS - GCP"],
        "positioning": (
            "Versao focada em vagas full stack Java/Angular, destacando senioridade em backend, APIs, "
            "arquitetura distribuida, produtos financeiros e experiencia front-end com TypeScript."
        ),
        "skills": [
            ("Java", ["Java", "Spring Boot", "JUnit", "TDD", "POO", "JDBC", "Clean Architecture", "SOLID"]),
            ("Angular", ["Angular", "TypeScript", "Angular CLI", "Router", "CRUD", "Bootstrap", "Design Systems"]),
            ("Backend senior", ["Node.js", "NestJS", "REST APIs", "Microsservicos", "Kafka", "RabbitMQ", "RPA"]),
            ("Dados e Cloud", ["PostgreSQL", "MySQL", "Redis", "Docker", "GCP", "AWS", "Oracle Cloud"]),
        ],
        "experiences": ["celero", "mentore", "vink", "segov", "i9colab"],
        "projects": [
            {
                "name": "Open Finance PJ - Celero",
                "kind": "Experiencia profissional",
                "stack": "Backend, eventos, Kafka, RabbitMQ, GCP, integracoes bancarias",
                "impact": (
                    "Arquitetura e implementacao de fluxos de Open Finance PJ para Caixa, Sicredi e clientes bancarios, "
                    "com alto volume e impacto em +30 mil empresas."
                ),
            },
            {
                "name": "PcDigital - SEGOV / Policia Civil",
                "kind": "Experiencia profissional",
                "stack": "Node.js, NestJS, Next.js, React, Prisma, Docker, Microsservicos",
                "impact": (
                    "Sistema interno que otimizou processos de gestao de dados policiais no estado de Alagoas, "
                    "com APIs robustas e arquitetura de dados."
                ),
            },
            {
                "name": "CourseManager-Angular",
                "kind": "Projeto publico",
                "url": "https://github.com/LuizCarlosVilela/CourseManager-Angular",
                "stack": "Angular, TypeScript, Angular CLI, Bootstrap, Router, CRUD",
                "impact": "Sistema de gerenciamento de cursos em Angular, evidenciando componentes, rotas, formularios e manutencao de dados.",
            },
            {
                "name": "meetup-manager",
                "kind": "Projeto publico",
                "url": "https://github.com/LuizCarlosVilela/meetup-manager",
                "stack": "Java 11, JUnit 5, TDD",
                "impact": "Projeto focado em TDD com Java 11 e JUnit Jupiter, reforcando disciplina de testes para regras de negocio.",
            },
            {
                "name": "API-POO-Java",
                "kind": "Projeto publico",
                "url": "https://github.com/LuizCarlosVilela/API-POO-Java",
                "stack": "Java, JDBC, JUnit, API, POO",
                "impact": "API Java com persistencia relacional e testes automatizados; base solida para backend corporativo.",
            },
        ],
    },
    {
        "filename": "luiz-carlos-vilela-react-java",
        "title": "React + Java",
        "headline": "React, Next.js, TypeScript, Java, Spring Boot, APIs, FinTech",
        "badges": ["React - Next.js", "TypeScript", "Java - Spring Boot", "Node.js - NestJS", "AWS - GCP"],
        "positioning": (
            "Versao focada em vagas React + Java, enfatizando produtos web escalaveis, integracao com APIs, "
            "experiencia full stack e fundamentos backend para atuar em times de produto financeiro."
        ),
        "skills": [
            ("React", ["React", "Next.js", "TypeScript", "Hooks", "React Router", "Redux", "SSR"]),
            ("UI", ["Material UI", "Styled Components", "Responsividade", "Design Systems", "CSS Grid", "Dark Mode"]),
            ("Java e backend", ["Java", "Spring Boot", "JUnit", "TDD", "POO", "REST APIs", "Microsservicos"]),
            ("Arquitetura", ["Node.js", "NestJS", "Kafka", "RabbitMQ", "PostgreSQL", "Docker", "AWS/GCP"]),
        ],
        "experiences": ["vink", "segov", "mentore", "celero", "i9colab"],
        "projects": [
            {
                "name": "Conciliacao bancaria automatizada - Vink",
                "kind": "Experiencia profissional",
                "stack": "React, React Native, Node.js, Microsservicos, DDD, SOLID, Integracoes financeiras",
                "impact": (
                    "Sistemas web/mobile para conciliacao bancaria com adquirentes como Cielo, PagSeguro, Stone e GetNet, "
                    "processando aproximadamente R$335M em transacoes."
                ),
            },
            {
                "name": "PcDigital - SEGOV / Policia Civil",
                "kind": "Experiencia profissional",
                "stack": "Next.js, React, Node.js, NestJS, Prisma, Docker",
                "impact": (
                    "Aplicacoes server-side renderizadas e APIs para gestao interna, com arquitetura de microsservicos "
                    "e foco em eficiencia operacional."
                ),
            },
            {
                "name": "Clone-GitHub",
                "kind": "Projeto publico",
                "url": "https://github.com/LuizCarlosVilela/Clone-GitHub",
                "stack": "React, TypeScript, Styled Components, React Router, Dark Mode",
                "impact": "Interface responsiva com foco em componentes, roteamento, estilizacao e experiencia de usuario.",
            },
            {
                "name": "Covid19-TrackerWorld",
                "kind": "Projeto publico",
                "url": "https://github.com/LuizCarlosVilela/Covid19-TrackerWorld",
                "stack": "ReactJS, React Redux, Material UI, JavaScript, APIs REST",
                "impact": "Dashboard com dados externos, estado de aplicacao e apresentacao visual de informacoes em tempo real.",
            },
            {
                "name": "API-POO-Java",
                "kind": "Projeto publico",
                "url": "https://github.com/LuizCarlosVilela/API-POO-Java",
                "stack": "Java, JDBC, JUnit, API, POO",
                "impact": "API Java com persistencia relacional e testes automatizados para reforcar fundamentos backend.",
            },
        ],
    },
]


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def render_badges(items: list[str]) -> str:
    return "".join(f"<span>{esc(item)}</span>" for item in items)


def render_metric_cards() -> str:
    return "\n".join(
        f"""
        <div class="metric">
          <strong>{esc(value)}</strong>
          <span>{esc(label)}</span>
        </div>
        """
        for value, label in METRICS
    )


def render_skills(groups: list[tuple[str, list[str]]]) -> str:
    cards = []
    for title, items in groups:
        chips = "".join(f"<span>{esc(item)}</span>" for item in items)
        cards.append(
            f"""
            <section class="skill-card">
              <h3>{esc(title)}</h3>
              <div class="chips">{chips}</div>
            </section>
            """
        )
    return "\n".join(cards)


def render_experiences(keys: list[str]) -> str:
    cards = []
    for key in keys:
        item = BASE_EXPERIENCES[key]
        bullets = "\n".join(f"<li>{esc(bullet)}</li>" for bullet in item["bullets"])
        cards.append(
            f"""
            <article class="experience-card">
              <div class="experience-head">
                <div>
                  <h3>{esc(item["company"])}</h3>
                  <p>{esc(item["role"])}</p>
                </div>
                <div class="meta">
                  <strong>{esc(item["period"])}</strong>
                  <span>{esc(item["location"])}</span>
                </div>
              </div>
              <ul>{bullets}</ul>
            </article>
            """
        )
    return "\n".join(cards)


def render_projects(projects: list[dict[str, str]]) -> str:
    cards = []
    for project in projects:
        url = project.get("url")
        link = f'<a href="{esc(url)}">{esc(str(url).replace("https://", ""))}</a>' if url else ""
        cards.append(
            f"""
            <article class="project-card">
              <div class="project-head">
                <div>
                  <span class="kind">{esc(project["kind"])}</span>
                  <h3>{esc(project["name"])}</h3>
                </div>
                {link}
              </div>
              <p class="stack">{esc(project["stack"])}</p>
              <p>{esc(project["impact"])}</p>
            </article>
            """
        )
    return "\n".join(cards)


def render_compact_list(items: list[str]) -> str:
    return " &bull; ".join(esc(item) for item in items)


def render_resume(resume: dict[str, object]) -> str:
    return f"""<!doctype html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{esc(PROFILE["name"])} - {esc(resume["title"])}</title>
  <style>
    :root {{
      --bg: #151515;
      --panel: #222321;
      --panel-2: #2d2f2c;
      --text: #e8e2d8;
      --muted: #b7afa4;
      --line: #3b3d39;
      --blue: #3c8eea;
      --green: #95d5b2;
      --cream: #f2dfb5;
      --lavender: #d8cdfc;
      --print-bg: #ffffff;
      --print-text: #20242b;
    }}

    * {{
      box-sizing: border-box;
    }}

    body {{
      margin: 0;
      background: #0f0f0f;
      color: var(--text);
      font-family: Arial, Helvetica, sans-serif;
      font-size: 12px;
      line-height: 1.45;
    }}

    a {{
      color: var(--blue);
      text-decoration: none;
    }}

    .page {{
      background: var(--bg);
      margin: 0 auto;
      min-height: 297mm;
      padding: 13mm 15mm;
      width: 210mm;
    }}

    header {{
      align-items: flex-start;
      border-bottom: 1px solid var(--line);
      display: grid;
      gap: 18px;
      grid-template-columns: 1.25fr 0.85fr;
      padding-bottom: 13px;
    }}

    h1 {{
      color: #fff;
      font-size: 26px;
      line-height: 1;
      margin: 0 0 4px;
    }}

    .subtitle {{
      color: var(--muted);
      font-size: 15px;
      font-weight: 700;
      margin: 0 0 8px;
    }}

    .badges {{
      display: flex;
      flex-wrap: wrap;
      gap: 6px;
    }}

    .badges span {{
      background: var(--lavender);
      border-radius: 999px;
      color: #232323;
      font-size: 11px;
      font-weight: 800;
      padding: 3px 8px;
    }}

    .badges span:nth-child(2n) {{
      background: var(--green);
    }}

    .badges span:nth-child(3n) {{
      background: var(--cream);
    }}

    .contact {{
      color: var(--muted);
      display: grid;
      gap: 3px;
      justify-items: end;
      text-align: right;
    }}

    .summary {{
      background: var(--panel);
      border-left: 3px solid var(--blue);
      border-radius: 6px;
      color: #d8d0c4;
      font-size: 13px;
      margin: 16px 0 12px;
      padding: 13px 15px;
    }}

    .summary strong {{
      color: #fff;
    }}

    .metrics {{
      display: grid;
      gap: 8px;
      grid-template-columns: repeat(3, 1fr);
      margin-bottom: 14px;
    }}

    .metric {{
      background: var(--panel);
      border-radius: 6px;
      padding: 9px 10px;
    }}

    .metric strong {{
      color: var(--blue);
      display: block;
      font-size: 16px;
      line-height: 1;
      margin-bottom: 4px;
    }}

    .metric span {{
      color: var(--muted);
      display: block;
      font-weight: 700;
    }}

    h2 {{
      align-items: center;
      color: var(--muted);
      display: flex;
      font-size: 13px;
      gap: 8px;
      letter-spacing: 0.12em;
      margin: 15px 0 8px;
      text-transform: uppercase;
    }}

    h2::after {{
      background: var(--line);
      content: "";
      flex: 1;
      height: 1px;
    }}

    h3 {{
      color: #fff;
      font-size: 13px;
      margin: 0;
    }}

    .skills {{
      display: grid;
      gap: 8px;
      grid-template-columns: repeat(2, 1fr);
    }}

    .skill-card,
    .experience-card,
    .project-card {{
      background: var(--panel-2);
      border: 1px solid var(--line);
      border-radius: 7px;
      break-inside: avoid;
      padding: 9px 11px;
    }}

    .chips {{
      display: flex;
      flex-wrap: wrap;
      gap: 5px;
      margin-top: 6px;
    }}

    .chips span {{
      background: #202220;
      border: 1px solid #454842;
      border-radius: 999px;
      color: #d8d0c4;
      font-size: 10.5px;
      font-weight: 700;
      padding: 3px 7px;
    }}

    .experience-card {{
      margin-bottom: 8px;
    }}

    .experience-head,
    .project-head {{
      display: grid;
      gap: 10px;
      grid-template-columns: 1fr auto;
      margin-bottom: 6px;
    }}

    .experience-head p,
    .project-card p {{
      margin: 2px 0 0;
    }}

    .meta {{
      color: var(--muted);
      display: grid;
      justify-items: end;
      text-align: right;
      white-space: nowrap;
    }}

    ul {{
      margin: 0;
      padding-left: 14px;
    }}

    li {{
      margin-bottom: 2px;
    }}

    li::marker {{
      color: var(--blue);
    }}

    .project-grid {{
      display: grid;
      gap: 8px;
      grid-template-columns: 1fr 1fr;
    }}

    .kind {{
      color: var(--blue);
      display: block;
      font-size: 10px;
      font-weight: 800;
      letter-spacing: 0.08em;
      margin-bottom: 2px;
      text-transform: uppercase;
    }}

    .stack {{
      color: var(--green);
      font-size: 11px;
      font-weight: 800;
    }}

    .footer {{
      color: var(--muted);
      display: grid;
      gap: 5px;
      grid-template-columns: 1fr;
      margin-top: 10px;
    }}

    @page {{
      margin: 0;
      size: A4;
    }}

    @media print {{
      body {{
        background: var(--print-bg);
      }}

      .page {{
        box-shadow: none;
        margin: 0;
      }}
    }}

    @media screen and (max-width: 780px) {{
      .page {{
        min-height: auto;
        padding: 20px;
        width: 100%;
      }}

      header,
      .metrics,
      .skills,
      .project-grid {{
        grid-template-columns: 1fr;
      }}

      .contact,
      .meta {{
        justify-items: start;
        text-align: left;
      }}
    }}
  </style>
</head>
<body>
  <main class="page">
    <header>
      <section>
        <h1>{esc(PROFILE["name"])}</h1>
        <p class="subtitle">{esc(PROFILE["title"])} - {esc(resume["title"])} - {esc(PROFILE["focus"])}</p>
        <div class="badges">{render_badges(resume["badges"])}</div>
      </section>
      <section class="contact">
        <span>{esc(PROFILE["phone"])}</span>
        <span>{esc(PROFILE["email"])}</span>
        <a href="https://{esc(PROFILE["linkedin"])}">{esc(PROFILE["linkedin"])}</a>
        <a href="https://{esc(PROFILE["github"])}">{esc(PROFILE["github"])}</a>
        <span>{esc(PROFILE["location"])}</span>
      </section>
    </header>

    <section class="summary">
      <strong>{esc(resume["headline"])}.</strong> {esc(PROFILE["summary"])}
      <br />
      {esc(resume["positioning"])}
    </section>

    <section class="metrics">{render_metric_cards()}</section>

    <section>
      <h2>Stacks prioritarias</h2>
      <div class="skills">{render_skills(resume["skills"])}</div>
    </section>

    <section>
      <h2>Experiencia</h2>
      {render_experiences(resume["experiences"])}
    </section>

    <section>
      <h2>Projetos e entregas em destaque</h2>
      <div class="project-grid">{render_projects(resume["projects"])}</div>
    </section>

    <section class="footer">
      <span><strong>Formacao:</strong> {render_compact_list(EDUCATION)}</span>
      <span><strong>Certificacoes:</strong> {render_compact_list(CERTIFICATIONS)}</span>
    </section>
  </main>
</body>
</html>
"""


def chrome_path() -> str | None:
    for candidate in ("google-chrome", "chromium", "chromium-browser"):
        path = shutil.which(candidate)
        if path:
            return path
    return None


def write_html(resume: dict[str, object]) -> Path:
    HTML_DIR.mkdir(parents=True, exist_ok=True)
    html_path = HTML_DIR / f"{resume['filename']}.html"
    html_path.write_text(render_resume(resume), encoding="utf-8")
    return html_path


def write_pdf(html_path: Path, resume: dict[str, object], chrome: str) -> Path:
    PDF_DIR.mkdir(parents=True, exist_ok=True)
    pdf_path = PDF_DIR / f"{resume['filename']}.pdf"
    pdf_path.unlink(missing_ok=True)

    with tempfile.TemporaryDirectory(prefix="resume-chrome-") as user_data_dir:
        command = [
            chrome,
            "--headless=new",
            "--disable-gpu",
            "--disable-dev-shm-usage",
            "--no-sandbox",
            "--no-pdf-header-footer",
            f"--user-data-dir={user_data_dir}",
            f"--print-to-pdf={pdf_path}",
            html_path.resolve().as_uri(),
        ]
        process = subprocess.Popen(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        deadline = time.monotonic() + 15
        while time.monotonic() < deadline:
            return_code = process.poll()
            if pdf_path.exists() and pdf_path.stat().st_size > 0:
                if return_code is None:
                    process.terminate()
                    try:
                        process.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        process.kill()
                        process.wait(timeout=5)
                return pdf_path
            if return_code is not None:
                raise subprocess.CalledProcessError(return_code, command)
            time.sleep(0.2)

        process.kill()
        process.wait(timeout=5)
        raise subprocess.TimeoutExpired(command, 15)


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate role-focused resume PDFs.")
    parser.add_argument("--html-only", action="store_true", help="Generate only HTML files.")
    args = parser.parse_args()

    chrome = chrome_path()
    if not args.html_only and not chrome:
        raise SystemExit("Chrome/Chromium was not found. Re-run with --html-only or install Chrome.")

    generated: list[Path] = []
    for resume in RESUMES:
        html_path = write_html(resume)
        generated.append(html_path)
        if not args.html_only and chrome:
            generated.append(write_pdf(html_path, resume, chrome))

    for path in generated:
        print(path.relative_to(ROOT.parent))


if __name__ == "__main__":
    main()
