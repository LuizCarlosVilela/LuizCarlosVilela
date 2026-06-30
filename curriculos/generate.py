#!/usr/bin/env python3
"""Generate role-focused resume PDFs from versioned HTML content."""

from __future__ import annotations

import argparse
import base64
import html
import mimetypes
import shutil
import subprocess
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parent
HTML_DIR = ROOT / "html"
PDF_DIR = ROOT / "pdf"
ASSETS_DIR = ROOT / "assets"
PHOTO_FILENAMES = (
    "profile-photo.jpg",
    "profile-photo.jpeg",
    "profile-photo.png",
    "profile-photo.webp",
)


PROFILE = {
    "name": "Luiz Carlos Vilela dos Santos",
    "title": "Engenheiro de Software Senior",
    "focus": "Backend - Mobile - RPA",
    "phone": "82 9 9189-0441",
    "whatsapp_url": "https://wa.me/5582991890441",
    "email": "luizcarlosvilela@outlook.com.br",
    "email_url": "mailto:luizcarlosvilela@outlook.com.br",
    "linkedin": "linkedin.com/in/luiz-carlos-vilela",
    "linkedin_url": "https://www.linkedin.com/in/luiz-carlos-vilela/",
    "github": "github.com/LuizCarlosVilela",
    "github_url": "https://github.com/LuizCarlosVilela",
    "location": "Maceio, Alagoas, Brasil - Home office",
    "summary": (
        "Sou Engenheiro de Software Senior e atuo ha mais de 8 anos construindo sistemas de "
        "alta complexidade para FinTech e Open Finance. Trabalho ponta a ponta: arquitetura "
        "de backend com Node.js e Java, aplicacoes mobile com Flutter e nativo, automacoes "
        "inteligentes (RPA) e infraestrutura em nuvem. Ja liderei times tecnicos e participei "
        "de produtos que atendem mais de 1 milhao de clientes PF, mais de 30 mil empresas PJ "
        "em Open Finance e ja processei cerca de R$335 milhoes em transacoes financeiras."
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
        "period": "Jan 2026 - Jun 2026",
        "location": "Home office - Sao Paulo, SP",
        "bullets": [
            "Internalizado apos o periodo de consultoria para garantir manutencao, evolucao e escalabilidade do ecossistema de software, expandindo minha atuacao para backend e automacao de processos.",
            "Evolui o app Flutter/Dart com novas features, foco em estabilidade e melhoria de UX.",
            "Desenvolvi e evolui microsservicos e APIs estaveis para sustentar o ecossistema web e mobile com seguranca.",
            "Concebi e implementei solucoes de RPA para otimizar fluxos operacionais internos e integrar sistemas legados.",
            "Gerenciei o ciclo completo de release e a publicacao automatizada dos apps na App Store e na Google Play.",
        ],
    },
    "sciensa": {
        "company": "Sciensa (alocado no Mentore Bank)",
        "role": "Tech Lead Mobile / Engenheiro de Software Senior",
        "period": "Jun 2025 - Fev 2026",
        "location": "Home office - Sao Paulo, SP",
        "bullets": [
            "Atuei na concepcao e no desenvolvimento de ponta a ponta do aplicativo bancario PF da Mentore, comecando como especialista Flutter e evoluindo para Tech Lead do time mobile.",
            "Construi o app PF utilizando Flutter no core e nativo em Swift e Kotlin para fluxos especificos.",
            "Implementei funcionalidades de Core Banking de ponta a ponta: onboarding digital completo para PF, area Pix e fluxo de solicitacao do cartao Swile.",
            "Defini o Design System global e os padroes de gerenciamento de estado da aplicacao, garantindo consistencia tecnica e escala para mais de 1 milhao de clientes.",
            "Estruturei e automatizei esteiras de CI/CD para o ecossistema mobile, garantindo qualidade, testes e agilidade.",
            "Como Tech Lead, assumi as decisoes arquiteturais, revisao de codigo e mentoria do time.",
        ],
    },
    "celero": {
        "company": "Celero",
        "role": "Engenheiro de Software Senior - Open Finance PJ",
        "period": "Jan 2025 - Jun 2025",
        "location": "Home office",
        "bullets": [
            "Atuei no backend do produto de Open Finance PJ, com integracoes bancarias em larga escala para instituicoes como Sicredi e Caixa Economica Federal.",
            "Implementei integracoes de Open Finance para Caixa Economica Federal e Sicredi.",
            "Desenvolvi fluxos de Open Finance PJ para empresas, sob demanda de clientes bancarios.",
            "Participei do desenho da arquitetura orientada a eventos, com processamento assincrono de alto volume usando Kafka e RabbitMQ.",
            "Coloquei as solucoes para rodar em Google Cloud Platform (GCP), atendendo mais de 30 mil empresas em milhoes de operacoes bancarias.",
        ],
    },
    "vink": {
        "company": "Vink",
        "role": "Engenheiro de Software Senior",
        "period": "Set 2022 - Jan 2025",
        "location": "Home office - Campinas, SP",
        "bullets": [
            "Atuei no desenvolvimento de sistemas web e mobile para conciliacao bancaria automatizada, integrando varios adquirentes, bancos e fintechs.",
            "Desenvolvi solucoes de conciliacao bancaria automatica com apoio de Inteligencia Artificial.",
            "Criei e evolui microsservicos em Node.js atendendo milhoes de transacoes.",
            "Desenvolvi aplicacoes web e mobile com React e React Native.",
            "Apliquei DDD, Clean Code e SOLID em sistemas financeiros criticos.",
            "Conduzi integracoes com adquirentes como Cielo, PagSeguro, Stone e GetNet.",
            "Processei e conciliei cerca de R$335 milhoes em transacoes financeiras usando robos e um motor de inteligencia desenvolvido por mim, com monitoramento em tempo real de vendas e repasses.",
        ],
    },
    "diallink": {
        "company": "DIALLINK Tecnologia Humanizada",
        "role": "Desenvolvedor Full Stack / Desenvolvedor ChatBot",
        "period": "Mar 2023 - Nov 2024",
        "location": "Home office - Sao Paulo, SP",
        "bullets": [
            "Desenvolvi agentes de atendimento humanizado com integracoes diretas com WhatsApp e Meta.",
            "Construi solucoes em Node.js com NestJS para orquestrar fluxos de chatbot e automacao de atendimento.",
            "Integrei frontend a APIs REST, conectando necessidades de negocio com solucoes de software escalaveis.",
        ],
    },
    "segov": {
        "company": "Secretaria de Estado de Governo de Alagoas (SEGOV)",
        "role": "Engenheiro de Software Senior",
        "period": "Out 2021 - Fev 2024",
        "location": "Maceio, AL",
        "bullets": [
            "Construi sistemas internos de gestao para a Policia Civil de Alagoas, atuando como lider tecnico e desenvolvedor.",
            "Liderei projetos de implementacao e melhoria de software.",
            "Criei e otimizei APIs e solucoes back-end robustas com Node.js e NestJS.",
            "Construi aplicacoes server-side renderizadas de alta performance com Next.js.",
            "Estruturei esquemas de microsservicos e arquitetura de dados.",
            "Entre os sistemas criados se destaca o PcDigital, que revolucionou a gestao de dados policiais e otimizou processos internos do estado.",
        ],
    },
    "i9colab": {
        "company": "i9Colab - Consultorias, Tecnologia e Inovacao",
        "role": "Consultor de Desenvolvimento / Software Developer / Full Stack Engineer",
        "period": "Out 2020 - Jul 2023",
        "location": "Maceio, AL",
        "bullets": [
            "Atuei como Consultor de Desenvolvimento com Sistemas Operacionais (Windows, Linux, Mac), infraestrutura AWS, metodologias ageis (Scrum e Kanban) e linguagens como JavaScript, TypeScript, Python e PHP.",
            "Trabalhei como Software Developer em sistemas web, aplicativos, sites, e-commerce, automacao industrial e automacoes com bots e Inteligencia Artificial.",
            "Como Full Stack Engineer, desenvolvi web e mobile com React e React Native, e backend com Node.js, Express, TypeORM e Knex, usando MySQL e MariaDB.",
        ],
    },
    "beyond": {
        "company": "Beyond Co.",
        "role": "Cloud Engineer / Full Stack Developer",
        "period": "Mar 2022 - Set 2022",
        "location": "Recife, PE",
        "bullets": [
            "Desenvolvi aplicacoes full stack com Vue 2 e Vue 3 no dia a dia no frontend.",
            "Criei APIs RESTful com Node.js, definindo endpoints, autenticacao, validacao de dados e tratamento de requisicoes.",
            "Trabalhei com bancos relacionais e NoSQL (MySQL, PostgreSQL, MongoDB) e cuidei de modelagem, queries eficientes e migrations.",
            "Atuei em cloud engineering com testes unitarios, integracao e debugging para garantir estabilidade da aplicacao.",
        ],
    },
    "prefeitura": {
        "company": "Prefeitura de Maceio",
        "role": "Desenvolvedor FullStack Pleno",
        "period": "Mai 2021 - Jun 2022",
        "location": "Maceio, AL",
        "bullets": [
            "Atuei em time de desenvolvimento Node.js com front-end em React.js e Next.js usando TypeScript, e back-end em Node.js com Prisma 3.0.",
            "Trabalhei com infraestrutura baseada em CPanel e APanel.",
        ],
    },
    "zenix": {
        "company": "Zenix Technology",
        "role": "Full Stack Developer / Mobile Developer",
        "period": "Jan 2021 - Out 2021",
        "location": "Porto Alegre, RS",
        "bullets": [
            "Atuei como Full Stack Developer em projetos com o time da Zenix Tech, criando bons vinculos profissionais e tecnicos.",
            "Como freelancer mobile, desenvolvi apps com React Native, react-native-paper, mapas e tracking com MapView, evoluindo bastante no entendimento de contextos e estados.",
            "No back-end usei Express com Knex, JWT para seguranca por tokens criptografados e PostgreSQL hospedado na Heroku.",
        ],
    },
    "ifal": {
        "company": "Instituto Federal de Educacao, Ciencia e Tecnologia de Alagoas",
        "role": "Full Stack Engineer / IoT Developer",
        "period": "Out 2018 - Out 2021",
        "location": "Maceio, AL",
        "bullets": [
            "Colaborei no time de desenvolvimento do projeto PIBITI do IFAL, atuando com metodologias ageis, back-end, front-end mobile e modelagem de banco de dados.",
            "Atuei como IoT Developer com automacoes via microcontroladores conectados a Internet das Coisas (IoT), sob orientacao do professor Edison Camilo.",
        ],
    },
}


LINKEDIN_EXPERIENCE_ORDER = [
    "mentore",
    "sciensa",
    "celero",
    "vink",
    "diallink",
    "segov",
    "i9colab",
    "beyond",
    "prefeitura",
    "zenix",
    "ifal",
]


def chronological_experiences(*keys: str) -> list[str]:
    selected = set(keys)
    return [key for key in LINKEDIN_EXPERIENCE_ORDER if key in selected]


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
        "headline": "Flutter, Kotlin, Swift, Node.js, Java, NestJS, Kafka, RabbitMQ, CI/CD",
        "badges": ["Flutter - Dart", "Kotlin - Swift", "Node.js - TypeScript", "Java - Spring Boot", "Kafka - RabbitMQ", "AWS - GCP"],
        "skills": [
            ("Mobile", ["Flutter", "Dart", "Kotlin", "Swift", "React Native", "Expo", "Design System", "State Management"]),
            ("Backend Node.js", ["Node.js", "TypeScript", "NestJS", "Express", "REST APIs", "Microsservicos", "RPA"]),
            ("Backend Java", ["Java", "Spring Boot", "JUnit", "POO", "Clean Architecture", "SOLID", "SAGA Pattern"]),
            ("Eventos e dados", ["Kafka", "RabbitMQ", "Prisma", "Knex", "PostgreSQL", "Redis", "MySQL"]),
            ("Entrega", ["CI/CD Mobile", "App Store", "Google Play", "Docker", "AWS", "GCP", "Oracle Cloud"]),
        ],
        "experiences": LINKEDIN_EXPERIENCE_ORDER,
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
        "headline": "Java, Spring Boot, Angular, TypeScript, Microsservicos, APIs",
        "badges": ["Java - Spring Boot", "Angular - TypeScript", "Microsservicos", "Kafka - RabbitMQ", "AWS - GCP"],
        "skills": [
            ("Backend Java", ["Java", "Spring Boot", "JUnit", "TDD", "POO", "JDBC", "Clean Architecture", "SOLID"]),
            ("Angular & Front-end", ["Angular", "TypeScript", "Angular CLI", "Router", "CRUD", "Bootstrap", "Design Systems"]),
            ("Arquitetura & APIs", ["REST APIs", "Microsservicos", "SAGA Pattern", "Kafka", "RabbitMQ", "Open Finance"]),
            ("Backend complementar", ["Node.js", "NestJS", "Express", "Prisma", "RPA"]),
            ("Dados e Cloud", ["PostgreSQL", "MySQL", "Redis", "Docker", "GCP", "AWS", "Oracle Cloud"]),
        ],
        "experiences": LINKEDIN_EXPERIENCE_ORDER,
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
        "headline": "React, Next.js, TypeScript, Java, Spring Boot, Node.js, NestJS",
        "badges": ["React - Next.js", "TypeScript", "Java - Spring Boot", "Node.js - NestJS", "Kafka - RabbitMQ", "AWS - GCP"],
        "skills": [
            ("React & Front-end", ["React", "Next.js", "TypeScript", "Hooks", "React Router", "Redux", "SSR"]),
            ("UI", ["Material UI", "Styled Components", "Responsividade", "Design Systems", "CSS Grid", "Dark Mode"]),
            ("Backend Java", ["Java", "Spring Boot", "JUnit", "TDD", "POO", "REST APIs", "Microsservicos"]),
            ("Backend Node.js", ["Node.js", "NestJS", "Express", "Prisma", "RPA", "REST APIs"]),
            ("Arquitetura & Cloud", ["Kafka", "RabbitMQ", "PostgreSQL", "Docker", "AWS", "GCP", "Oracle Cloud"]),
        ],
        "experiences": LINKEDIN_EXPERIENCE_ORDER,
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
    {
        "filename": "luiz-carlos-vilela-angular-node",
        "title": "Angular + Node.js",
        "focus": "Frontend Angular - Backend Node.js - AWS e Azure",
        "headline": "Angular, TypeScript, Node.js, NestJS, microsservicos, AWS, Azure e APIs REST",
        "summary": (
            "Engenheiro de Software Senior especializado em produtos web full stack com Angular no frontend "
            "e Node.js no backend. No front, entrego interfaces com TypeScript, componentizacao, Reactive Forms, "
            "RxJS, roteamento, lazy loading, interceptors e Design System. No back, desenvolvo APIs e "
            "microsservicos com NestJS e Express, aplicando SOLID, DDD e arquitetura orientada a eventos. "
            "Tenho experiencia em cloud com AWS e Azure, pipelines de CI/CD, Docker, deploy de aplicacoes "
            "e integracoes de alto volume em FinTech, Open Finance e produtos corporativos."
        ),
        "badges": [
            "Angular - TypeScript",
            "Node.js - NestJS",
            "AWS - Azure",
            "Microsservicos",
            "RxJS - REST APIs",
            "Docker - CI/CD",
        ],
        "skills": [
            ("Angular & Front-end", ["Angular", "TypeScript", "Angular CLI", "Router", "Reactive Forms", "RxJS", "Design Systems", "Bootstrap"]),
            ("Backend Node.js", ["Node.js", "NestJS", "Express", "TypeScript", "REST APIs", "Microsservicos", "Prisma", "Knex"]),
            ("AWS", ["EC2", "S3", "Lambda", "RDS", "CloudWatch", "IAM", "Deploy", "Infraestrutura"]),
            ("Azure", ["App Service", "Azure DevOps", "Blob Storage", "Azure Functions", "AKS", "Pipelines CI/CD"]),
            ("Arquitetura & dados", ["Kafka", "RabbitMQ", "PostgreSQL", "MySQL", "Redis", "Docker", "SOLID", "DDD"]),
        ],
        "experiences": chronological_experiences(
            "mentore",
            "sciensa",
            "celero",
            "vink",
            "diallink",
            "segov",
            "i9colab",
            "beyond",
            "prefeitura",
        ),
        "experience_overrides": {
            "mentore": {
                "bullets": [
                    "Internalizado apos consultoria para evoluir o ecossistema web e backend do Mentore Bank.",
                    "Evolui APIs REST e microsservicos em Node.js para produtos financeiros de alta escala.",
                    "Desenvolvi integracoes entre frontend e servicos backend com contratos tipados e padroes de qualidade.",
                    "Atuei na migracao de capacidades monoliticas para servicos Node.js desacoplados e escalaveis.",
                    "Implementei fluxos assincronos com Kafka e RabbitMQ para integracoes de alto volume.",
                ],
            },
            "sciensa": {
                "bullets": [
                    "Alocado no Mentore Bank, atuei como Tech Lead na construcao do app bancario PF de ponta a ponta.",
                    "Defini Design System, padroes de componentizacao e organizacao de camadas no front-end.",
                    "Entreguei onboarding digital, Pix e cartao Swile com integracao a APIs e servicos Node.js.",
                    "Escalei o produto para +1 milhao de clientes com CI/CD, testes e governanca de codigo.",
                    "Conduzi revisao de codigo, mentoria e decisoes arquiteturais do time de produto.",
                ],
            },
            "celero": {
                "bullets": [
                    "Desenvolvi backend Node.js para Open Finance PJ com microsservicos e arquitetura orientada a eventos.",
                    "Implementei APIs e integracoes bancarias para Caixa Economica Federal e Sicredi em alto volume.",
                    "Estruturei processamento assincrono com Kafka e RabbitMQ e deploy em ambiente cloud.",
                    "Atendi mais de 30 mil empresas PJ com servicos resilientes e observabilidade.",
                ],
            },
            "vink": {
                "bullets": [
                    "Construi microsservicos Node.js e interfaces web para conciliacao bancaria automatizada.",
                    "Modelei APIs REST e integracoes com adquirentes (Cielo, PagSeguro, Stone, GetNet).",
                    "Apliquei DDD, SOLID e Clean Architecture em dominios financeiros de alta criticidade.",
                    "Processei e conciliei cerca de R$335 milhoes em transacoes com monitoramento em tempo real.",
                ],
            },
            "diallink": {
                "bullets": [
                    "Desenvolvi agentes de atendimento humanizado com integracoes diretas com WhatsApp e Meta.",
                    "Construi solucoes em Node.js com NestJS para orquestrar fluxos de chatbot e automacao de atendimento.",
                    "Integrei frontend a APIs REST com foco em usabilidade, escalabilidade e qualidade de codigo.",
                ],
            },
            "segov": {
                "bullets": [
                    "Liderei sistemas web com APIs NestJS, microsservicos e camada de dados estruturada.",
                    "Construi backends Node.js robustos e integracoes entre servicos para a Policia Civil de Alagoas.",
                    "Estruturei arquitetura de microsservicos, Docker e padroes de entrega continua.",
                    "O PcDigital otimizou gestao de dados policiais com APIs escalaveis e interface web.",
                ],
            },
            "i9colab": {
                "bullets": [
                    "Atuei como consultor full stack com Node.js, Express, TypeORM e Knex em projetos web.",
                    "Implantei e mantive solucoes em AWS com foco em infraestrutura, seguranca e entrega agil.",
                    "Desenvolvi e-commerce, sistemas corporativos e integracoes com MySQL e MariaDB.",
                ],
            },
            "beyond": {
                "role": "Cloud Engineer / Full Stack Developer",
                "bullets": [
                    "Desenvolvi aplicacoes full stack com Vue 2 e Vue 3 no dia a dia no frontend.",
                    "Criei APIs RESTful com Node.js e camadas de dados relacionais/NoSQL (MySQL, PostgreSQL, MongoDB).",
                    "Atuei em cloud engineering com testes, deploy e estabilidade de servicos web.",
                ],
            },
            "prefeitura": {
                "bullets": [
                    "Desenvolvi solucoes web com TypeScript e backend Node.js com Prisma em sistemas publicos.",
                    "Entreguei APIs e interfaces integradas com foco em manutencao e escalabilidade.",
                ],
            },
        },
        "projects": [
            {
                "name": "CourseManager-Angular",
                "kind": "Projeto publico",
                "url": "https://github.com/LuizCarlosVilela/CourseManager-Angular",
                "stack": "Angular, TypeScript, Angular CLI, Router, Reactive Forms, Bootstrap",
                "impact": (
                    "Sistema de gerenciamento de cursos com componentes reutilizaveis, rotas, formularios "
                    "reativos e organizacao clara de camadas no frontend Angular."
                ),
            },
            {
                "name": "PcDigital - SEGOV / Policia Civil",
                "kind": "Experiencia profissional",
                "stack": "NestJS, Node.js, microsservicos, Docker, PostgreSQL, APIs REST",
                "impact": (
                    "Plataforma web com APIs NestJS e arquitetura de microsservicos, otimizando processos "
                    "de gestao de dados policiais no estado de Alagoas."
                ),
            },
            {
                "name": "Open Finance PJ - Celero",
                "kind": "Experiencia profissional",
                "stack": "Node.js, NestJS, Kafka, RabbitMQ, microsservicos, cloud, APIs REST",
                "impact": (
                    "Backend Node.js para fluxos PJ e integracoes bancarias em alto volume, atendendo "
                    "+30 mil empresas com arquitetura orientada a eventos."
                ),
            },
            {
                "name": "orders-nestjs-kafka",
                "kind": "Projeto publico",
                "url": "https://github.com/LuizCarlosVilela/orders-nestjs-kafka",
                "stack": "NestJS, Kafka, Prisma, TypeScript, Docker",
                "impact": (
                    "Microsservicos Node.js com mensageria Kafka, reforcando backend desacoplado "
                    "e integracao entre servicos."
                ),
            },
            {
                "name": "Ecossistema web - Mentore Bank",
                "kind": "Experiencia profissional",
                "stack": "Node.js, NestJS, TypeScript, APIs REST, microsservicos, integracoes financeiras",
                "impact": (
                    "Evolucao de APIs e servicos Node.js que sustentam o ecossistema web e integracoes "
                    "do produto financeiro em escala."
                ),
            },
        ],
    },
    {
        "filename": "luiz-carlos-vilela-flutter-native",
        "title": "Frontend Fullstack | Flutter",
        "focus": "Flutter Web & Mobile - React - Angular",
        "headline": (
            "Flutter, Dart, React, Angular, TypeScript, APIs REST, integracao backend, "
            "CI/CD, AWS, GCP e produtos financeiros em escala"
        ),
        "summary": (
            "Engenheiro de Software Senior e Frontend Fullstack com experiencia solida em Flutter/Dart para "
            "aplicacoes Mobile (Android e iOS) em producao, atuando em FinTech de alta escala. Na Sciensa/Mentore "
            "Bank, participei da concepcao e evolucao do app bancario PF para +1 milhao de clientes, conduzindo "
            "decisoes arquiteturais, Design System, gerenciamento de estado, integracao com APIs REST e pipelines "
            "de CI/CD. Tenho ampla vivencia em frontend web com React, Next.js e Angular, alem de integracao "
            "fullstack com Node.js/NestJS — diferencial para produtos que combinam multiplas fontes de dados, "
            "interfaces performaticas e backends distribuidos. Atuo com autonomia de ponta a ponta: entendimento "
            "da necessidade, definicao tecnica, implementacao, qualidade e entrega em producao."
        ),
        "badges": [
            "Flutter - Dart",
            "React - Angular",
            "APIs REST",
            "Fullstack Frontend",
            "CI/CD",
            "AWS - GCP",
        ],
        "skills": [
            (
                "Flutter Web & Mobile",
                [
                    "Flutter",
                    "Dart",
                    "Android",
                    "iOS",
                    "Design System",
                    "State Management",
                    "Modularizacao",
                    "Performance",
                    "Git",
                ],
            ),
            (
                "React & Angular",
                [
                    "React",
                    "Next.js",
                    "Angular",
                    "TypeScript",
                    "Hooks",
                    "React Router",
                    "Redux",
                    "RxJS",
                    "Responsive UI",
                ],
            ),
            (
                "APIs & multiplos dados",
                [
                    "REST APIs",
                    "Integracao backend",
                    "JWT",
                    "OAuth",
                    "Microsservicos",
                    "Kafka",
                    "RabbitMQ",
                    "PostgreSQL",
                    "Redis",
                ],
            ),
            (
                "Fullstack & nativo",
                [
                    "Node.js",
                    "NestJS",
                    "Express",
                    "Kotlin",
                    "Swift",
                    "Platform Channels",
                    "React Native",
                ],
            ),
            (
                "Cloud & entrega",
                [
                    "CI/CD",
                    "Docker",
                    "AWS",
                    "GCP",
                    "App Store",
                    "Google Play",
                    "Testes automatizados",
                    "Scrum",
                    "Kanban",
                ],
            ),
        ],
        "experiences": chronological_experiences(
            "mentore",
            "sciensa",
            "celero",
            "vink",
            "segov",
            "i9colab",
            "prefeitura",
        ),
        "experience_overrides": {
            "mentore": {
                "role": "Engenheiro de Software Senior - Frontend Fullstack",
                "bullets": [
                    "Internalizado apos consultoria na Sciensa para evoluir o ecossistema Flutter e integracoes frontend-backend do Mentore Bank.",
                    "Desenvolvi e sustentei modulos Flutter/Dart para Android e iOS com foco em performance, UX e seguranca.",
                    "Integrei o app com APIs REST, autenticacao e fluxos criticos de onboarding em produto para +1M clientes PF.",
                    "Mantive pipelines de CI/CD com testes automatizados e publicacao nas lojas Apple e Google.",
                    "Conduzi revisao de codigo, padroes de arquitetura e alinhamento tecnico entre mobile, backend e QA.",
                ],
            },
            "sciensa": {
                "role": "Tech Lead Mobile / Frontend Fullstack Flutter",
                "bullets": [
                    "Alocado na Sciensa no Mentore Bank, liderei tecnicamente o desenvolvimento do app bancario PF de ponta a ponta.",
                    "Arquitetei e evolui aplicacao Flutter/Dart para Android e iOS com Design System e gerenciamento de estado em escala.",
                    "Defini padroes de integracao com APIs REST, modularizacao e qualidade de codigo para time multidisciplinar.",
                    "Entreguei onboarding digital, Pix e cartao Swile com interfaces performaticas e jornadas de alta criticidade.",
                    "Estruturei CI/CD mobile (build, testes, assinatura e distribuicao) com governanca tecnica e mentoria do time.",
                    "Atuei com autonomia desde o entendimento da necessidade ate implementacao e homologacao em producao.",
                ],
            },
            "celero": {
                "bullets": [
                    "Atuei no backend Node.js de Open Finance PJ com integracoes bancarias de alto volume (Caixa e Sicredi).",
                    "Trabalhei com arquitetura orientada a eventos (Kafka/RabbitMQ) e multiplas fontes de dados financeiros.",
                    "Apoiei integracao entre servicos e consumo de APIs em ambiente cloud (GCP) para +30 mil empresas PJ.",
                ],
            },
            "vink": {
                "bullets": [
                    "Desenvolvi interfaces web React e mobile integradas a microsservicos Node.js em conciliacao bancaria.",
                    "Modelei consumo de APIs REST e tratamento de grandes volumes de dados transacionais em tempo real.",
                    "Apliquei DDD, SOLID e boas praticas de frontend/backend em produto que processou cerca de R$335M.",
                ],
            },
            "segov": {
                "bullets": [
                    "Liderei frontend web com Next.js/React e integracao com APIs NestJS em sistema de missao critica.",
                    "Defini arquitetura de interfaces, padroes de componentizacao e entrega continua com Docker e microsservicos.",
                    "O PcDigital otimizou gestao de dados policiais com UX focada em eficiencia operacional e escalabilidade.",
                ],
            },
            "i9colab": {
                "bullets": [
                    "Entreguei solucoes fullstack com React, React Native e Node.js para e-commerce e sistemas corporativos.",
                    "Integrei frontends a APIs REST e bancos relacionais (MySQL/MariaDB) com TypeScript e Express.",
                    "Implantei e mantive projetos em AWS com metodologias ageis (Scrum e Kanban).",
                ],
            },
            "prefeitura": {
                "bullets": [
                    "Desenvolvi frontend web com React, Next.js e TypeScript integrado a backend Node.js com Prisma.",
                    "Entreguei interfaces responsivas e APIs com foco em manutencao, performance e escalabilidade.",
                ],
            },
        },
        "projects": [
            {
                "name": "App bancario PF - Mentore Bank (Sciensa)",
                "kind": "Experiencia profissional",
                "stack": (
                    "Flutter, Dart, Android, iOS, APIs REST, Design System, State Management, "
                    "CI/CD, App Store, Google Play"
                ),
                "impact": (
                    "Desenvolvimento e evolucao do app PF em Flutter para +1M clientes na Sciensa/Mentore, "
                    "com integracao REST, arquitetura escalavel e entrega continua em produto financeiro critico."
                ),
            },
            {
                "name": "Conciliacao bancaria - Vink",
                "kind": "Experiencia profissional",
                "stack": "React, Node.js, TypeScript, APIs REST, microsservicos, alto volume de dados",
                "impact": (
                    "Frontend web React integrado a backend Node.js processando multiplas fontes de dados "
                    "e aproximadamente R$335M em transacoes financeiras."
                ),
            },
            {
                "name": "CourseManager-Angular",
                "kind": "Projeto publico",
                "url": "https://github.com/LuizCarlosVilela/CourseManager-Angular",
                "stack": "Angular, TypeScript, Angular CLI, Router, Reactive Forms, Bootstrap",
                "impact": (
                    "Sistema web em Angular com componentes reutilizaveis, rotas, formularios reativos "
                    "e organizacao de camadas — evidencia dominio em Angular alem de Flutter/React."
                ),
            },
            {
                "name": "Open Finance PJ - Celero",
                "kind": "Experiencia profissional",
                "stack": "Node.js, Kafka, RabbitMQ, GCP, APIs REST, integracoes bancarias",
                "impact": (
                    "Integracao com multiplas fontes de dados financeiros em alto volume, "
                    "atendendo +30 mil empresas PJ com arquitetura orientada a eventos."
                ),
            },
        ],
    },
    {
        "filename": "luiz-carlos-vilela-react-native-nodejs",
        "title": "React Native + Node.js",
        "focus": "Lideranca Tecnica - Mobile - Backend",
        "headline": (
            "React Native, Expo, Node.js, NestJS, lideranca tecnica, arquitetura mobile/backend, "
            "CI/CD, AWS, APIs REST e metodologias ageis"
        ),
        "summary": (
            "Engenheiro de Software Senior com atuacao em lideranca tecnica de projetos mobile e backend. "
            "Experiencia solida em React Native, Expo e Node.js (NestJS, Express), definindo arquitetura de "
            "aplicativos, APIs REST, microsservicos e pipelines de CI/CD. Como Tech Lead no Mentore Bank, "
            "liderei time mobile, conduzi revisao de codigo, mentoria tecnica e entrega de app para +1 milhao "
            "de clientes com publicacao na App Store e Google Play. Na Vink e i9Colab, entreguei apps React Native "
            "integrados a backends Node.js em produtos financeiros e corporativos. Atuo com metodologias ageis "
            "(Scrum e Kanban), Design Patterns, testes automatizados, documentacao tecnica e servicos AWS."
        ),
        "badges": [
            "React Native - Expo",
            "Node.js - NestJS",
            "Lideranca Tecnica",
            "CI/CD - DevOps",
            "AWS",
            "APIs REST",
        ],
        "skills": [
            (
                "Lideranca & arquitetura",
                [
                    "Tech Lead",
                    "Code Review",
                    "Mentoria tecnica",
                    "Arquitetura mobile",
                    "Arquitetura backend",
                    "Design Patterns",
                    "SOLID",
                    "Documentacao tecnica",
                ],
            ),
            (
                "React Native & Mobile",
                [
                    "React Native",
                    "Expo",
                    "TypeScript",
                    "React Navigation",
                    "Design System",
                    "State Management",
                    "App Store",
                    "Google Play",
                ],
            ),
            (
                "Backend Node.js",
                [
                    "Node.js",
                    "NestJS",
                    "Express",
                    "TypeScript",
                    "REST APIs",
                    "Microsservicos",
                    "Web Services",
                ],
            ),
            (
                "Dados & qualidade",
                [
                    "PostgreSQL",
                    "MySQL",
                    "MongoDB",
                    "Redis",
                    "Prisma",
                    "Knex",
                    "Testes automatizados",
                    "Git",
                ],
            ),
            (
                "DevOps & AWS",
                [
                    "CI/CD",
                    "Docker",
                    "EC2",
                    "S3",
                    "Lambda",
                    "RDS",
                    "CloudWatch",
                    "Scrum",
                    "Kanban",
                ],
            ),
        ],
        "experiences": chronological_experiences(
            "mentore",
            "sciensa",
            "celero",
            "vink",
            "segov",
            "i9colab",
            "zenix",
        ),
        "experience_overrides": {
            "mentore": {
                "role": "Engenheiro de Software Senior",
                "bullets": [
                    "Internalizado apos consultoria para liderar evolucao tecnica do ecossistema mobile e backend do Mentore Bank.",
                    "Defini padroes de arquitetura, qualidade de codigo e integracao entre app mobile e APIs REST.",
                    "Mantive pipelines de CI/CD para build, testes automatizados e publicacao na App Store e Google Play.",
                    "Apoiei decisoes tecnicas de escalabilidade, seguranca e disponibilidade em produto para +1M clientes PF.",
                    "Conduzi revisao de codigo e alinhamento tecnico entre times mobile e backend.",
                ],
            },
            "sciensa": {
                "role": "Tech Lead Mobile / Lider Tecnico",
                "bullets": [
                    "Liderei tecnicamente o time mobile na construcao do app bancario PF da Mentore, de especialista a Tech Lead.",
                    "Defini arquitetura mobile, Design System, gerenciamento de estado e padroes de integracao com APIs REST.",
                    "Estruturei pipelines de CI/CD para build, testes, assinatura e distribuicao nas lojas Apple e Google.",
                    "Conduzi revisao de codigo, mentoria de desenvolvedores e especificacao tecnica de funcionalidades.",
                    "Entreguei onboarding digital, Pix e cartao Swile com foco em UX, qualidade e escala para +1 milhao de clientes.",
                    "Atuei com metodologias ageis, apoiando QA e garantindo aderencia a boas praticas de engenharia de software.",
                ],
            },
            "celero": {
                "bullets": [
                    "Atuei na definicao de arquitetura backend Node.js para Open Finance PJ com microsservicos e eventos.",
                    "Implementei APIs REST e integracoes bancarias para Caixa Economica Federal e Sicredi em alto volume.",
                    "Estruturei processamento assincrono com Kafka e RabbitMQ e deploy em ambiente cloud (GCP).",
                    "Projetei solucoes com foco em escalabilidade, confiabilidade e disponibilidade para +30 mil empresas PJ.",
                ],
            },
            "vink": {
                "bullets": [
                    "Desenvolvi aplicacoes mobile com React Native e backends Node.js para conciliacao bancaria automatizada.",
                    "Modelei APIs REST e microsservicos integrados ao app mobile, com DDD, SOLID e Clean Architecture.",
                    "Entreguei produto web e mobile integrado com monitoramento em tempo real de transacoes financeiras.",
                    "Processei e conciliei cerca de R$335 milhoes em transacoes com adquirentes como Cielo, PagSeguro, Stone e GetNet.",
                ],
            },
            "segov": {
                "bullets": [
                    "Liderei tecnicamente projetos de software para a Policia Civil de Alagoas, como lider tecnico e desenvolvedor.",
                    "Defini arquitetura de microsservicos e APIs NestJS/Node.js com documentacao e padroes de qualidade.",
                    "Construi aplicacoes web com Next.js e backends robustos, apoiando estrategias de testes e entrega continua.",
                    "O PcDigital revolucionou a gestao de dados policiais com APIs escalaveis e arquitetura de dados estruturada.",
                ],
            },
            "i9colab": {
                "bullets": [
                    "Desenvolvi apps mobile com React Native e backends Node.js (Express, TypeORM, Knex) para e-commerce e sistemas corporativos.",
                    "Implantei e mantive solucoes em AWS (EC2, S3, RDS) com foco em infraestrutura, seguranca e entrega agil.",
                    "Atuei como consultor com metodologias ageis (Scrum e Kanban) em projetos web e mobile integrados.",
                    "Modelei bancos relacionais (MySQL, MariaDB) e consumi APIs REST em solucoes ponta a ponta.",
                ],
            },
            "zenix": {
                "role": "Mobile Developer / Full Stack Developer",
                "bullets": [
                    "Desenvolvi apps React Native com react-native-paper, mapas e tracking com MapView.",
                    "Implementei navegacao, gerenciamento de estado e consumo de Web Services/APIs REST no mobile.",
                    "Construi backend Express com JWT, Knex e PostgreSQL, integrando app mobile a servicos de dados.",
                ],
            },
        },
        "projects": [
            {
                "name": "Conciliacao bancaria mobile - Vink",
                "kind": "Experiencia profissional",
                "stack": "React Native, Node.js, TypeScript, Express, Microsservicos, APIs REST, DDD, SOLID",
                "impact": (
                    "App mobile React Native integrado a microsservicos Node.js para conciliacao bancaria automatizada, "
                    "processando aproximadamente R$335M em transacoes com adquirentes financeiros."
                ),
            },
            {
                "name": "NextLevelWeek-2 / Proffy",
                "kind": "Projeto publico",
                "url": "https://github.com/LuizCarlosVilela/NextLevelWeek-2",
                "stack": "React Native, Expo, Node.js, TypeScript, Express, Knex, SQLite, APIs REST",
                "impact": (
                    "Plataforma completa com app mobile (React Native/Expo), web e API REST em Node.js — "
                    "evidencia dominio da stack React Native + Node.js exigida pela vaga."
                ),
            },
            {
                "name": "PcDigital - SEGOV / Policia Civil",
                "kind": "Experiencia profissional",
                "stack": "Node.js, NestJS, Next.js, Microsservicos, Docker, PostgreSQL, APIs REST",
                "impact": (
                    "Lideranca tecnica e arquitetura de sistema com APIs NestJS, microsservicos e documentacao, "
                    "otimizando processos de gestao de dados policiais no estado de Alagoas."
                ),
            },
            {
                "name": "App Mercado Livre",
                "kind": "Projeto publico",
                "url": "https://github.com/LuizCarlosVilela/App-Mercado-Livre",
                "stack": "React Native, TypeScript, navegacao, componentizacao, UX mobile",
                "impact": (
                    "App mobile React Native com fluxos de navegacao, listagem e detalhes — "
                    "reforco pratico de desenvolvimento mobile com boas praticas de UI/UX."
                ),
            },
        ],
    },
    {
        "filename": "luiz-carlos-vilela-react-node-fullstack",
        "title": "Full Stack React + Node.js",
        "focus": "React - Node.js - TypeScript - IA aplicada",
        "headline": (
            "React, Next.js, TypeScript, Node.js, NestJS, microsservicos, APIs REST, "
            "CI/CD, AWS e engenharia assistida por IA"
        ),
        "summary": (
            "Engenheiro de Software Senior especializado em produtos web full stack com React no frontend "
            "e Node.js no backend. No front, entrego interfaces com TypeScript, componentizacao, Hooks, "
            "React Router, Redux, Design System e SSR com Next.js. No back, desenvolvo APIs e microsservicos "
            "com NestJS e Express, aplicando SOLID, DDD e arquitetura orientada a eventos. Potencializo meu "
            "trabalho com IA aplicada ao desenvolvimento: uso Skills, Instructions e os melhores MCPs do mercado "
            "para acelerar entregas com seguranca e escalabilidade no codigo, e em todo o fluxo de documentacao "
            "e design docs antes da implementacao. Tenho experiencia em FinTech, Open Finance, cloud, pipelines "
            "CI/CD e produtos que atendem +1 milhao de clientes PF."
        ),
        "badges": [
            "React - Next.js",
            "Node.js - NestJS",
            "TypeScript",
            "IA + MCPs",
            "Microsservicos",
            "AWS - CI/CD",
        ],
        "skills": [
            (
                "React & Front-end",
                [
                    "React",
                    "Next.js",
                    "TypeScript",
                    "Hooks",
                    "React Router",
                    "Redux",
                    "SSR",
                    "Design Systems",
                ],
            ),
            (
                "Backend Node.js",
                [
                    "Node.js",
                    "NestJS",
                    "Express",
                    "TypeScript",
                    "REST APIs",
                    "Microsservicos",
                    "Prisma",
                    "Knex",
                ],
            ),
            (
                "IA & engenharia",
                [
                    "Skills",
                    "Instructions",
                    "MCPs",
                    "Design Docs",
                    "Documentacao tecnica",
                    "Code Review",
                    "Arquitetura antes do codigo",
                ],
            ),
            (
                "Arquitetura & dados",
                [
                    "SOLID",
                    "DDD",
                    "Clean Architecture",
                    "Kafka",
                    "RabbitMQ",
                    "PostgreSQL",
                    "MySQL",
                    "Redis",
                ],
            ),
            (
                "Entrega & cloud",
                [
                    "CI/CD",
                    "Docker",
                    "AWS",
                    "GCP",
                    "Git",
                    "Testes automatizados",
                    "Scrum",
                    "Kanban",
                ],
            ),
        ],
        "experiences": chronological_experiences(
            "mentore",
            "sciensa",
            "celero",
            "vink",
            "diallink",
            "segov",
            "i9colab",
            "beyond",
            "prefeitura",
        ),
        "experience_overrides": {
            "mentore": {
                "bullets": [
                    "Internalizado apos consultoria para evoluir o ecossistema web e backend do Mentore Bank.",
                    "Evolui APIs REST e microsservicos em Node.js para produtos financeiros de alta escala.",
                    "Desenvolvi integracoes entre frontend e servicos backend com contratos tipados e padroes de qualidade.",
                    "Atuei na migracao de capacidades monoliticas para servicos Node.js desacoplados e escalaveis.",
                    "Implementei fluxos assincronos com Kafka e RabbitMQ para integracoes de alto volume.",
                ],
            },
            "sciensa": {
                "bullets": [
                    "Alocado no Mentore Bank, atuei como Tech Lead na construcao do produto bancario PF de ponta a ponta.",
                    "Defini Design System, padroes de componentizacao e organizacao de camadas no front-end.",
                    "Entreguei onboarding digital, Pix e cartao Swile com integracao a APIs e servicos Node.js.",
                    "Escalei o produto para +1 milhao de clientes com CI/CD, testes e governanca de codigo.",
                    "Conduzi revisao de codigo, mentoria e decisoes arquiteturais do time de produto.",
                ],
            },
            "celero": {
                "bullets": [
                    "Desenvolvi backend Node.js para Open Finance PJ com microsservicos e arquitetura orientada a eventos.",
                    "Implementei APIs e integracoes bancarias para Caixa Economica Federal e Sicredi em alto volume.",
                    "Estruturei processamento assincrono com Kafka e RabbitMQ e deploy em ambiente cloud.",
                    "Atendi mais de 30 mil empresas PJ com servicos resilientes e observabilidade.",
                ],
            },
            "vink": {
                "bullets": [
                    "Construi microsservicos Node.js e interfaces web React para conciliacao bancaria automatizada.",
                    "Modelei APIs REST e integracoes com adquirentes (Cielo, PagSeguro, Stone, GetNet).",
                    "Apliquei DDD, SOLID e Clean Architecture em dominios financeiros de alta criticidade.",
                    "Processei e conciliei cerca de R$335 milhoes em transacoes com monitoramento em tempo real.",
                ],
            },
            "diallink": {
                "bullets": [
                    "Desenvolvi produtos full stack com frontend React integrado a APIs Node.js.",
                    "Implementei fluxos de chatbot e automacao conectando interface a servicos de atendimento.",
                    "Entreguei features ponta a ponta com foco em usabilidade, integracao de dados e qualidade de codigo.",
                ],
            },
            "segov": {
                "bullets": [
                    "Liderei sistemas web com Next.js, APIs NestJS, microsservicos e camada de dados estruturada.",
                    "Construi backends Node.js robustos e integracoes entre servicos para a Policia Civil de Alagoas.",
                    "Estruturei arquitetura de microsservicos, Docker e padroes de entrega continua.",
                    "O PcDigital otimizou gestao de dados policiais com APIs escalaveis e interface web React/Next.js.",
                ],
            },
            "i9colab": {
                "bullets": [
                    "Atuei como consultor full stack com React, React Native e Node.js (Express, TypeORM, Knex).",
                    "Implantei e mantive solucoes em AWS com foco em infraestrutura, seguranca e entrega agil.",
                    "Desenvolvi e-commerce, sistemas corporativos e integracoes com MySQL e MariaDB.",
                ],
            },
            "beyond": {
                "role": "Cloud Engineer / Full Stack Developer",
                "bullets": [
                    "Desenvolvi aplicacoes full stack com Vue 2 e Vue 3 no dia a dia no frontend.",
                    "Criei APIs RESTful com Node.js e camadas de dados relacionais/NoSQL (MySQL, PostgreSQL, MongoDB).",
                    "Atuei em cloud engineering com testes, deploy e estabilidade de servicos web.",
                ],
            },
            "prefeitura": {
                "bullets": [
                    "Desenvolvi solucoes web com React, Next.js, TypeScript e backend Node.js com Prisma.",
                    "Entreguei APIs e interfaces integradas com foco em manutencao e escalabilidade.",
                ],
            },
        },
        "projects": [
            {
                "name": "Conciliacao bancaria automatizada - Vink",
                "kind": "Experiencia profissional",
                "stack": "React, Node.js, TypeScript, Microsservicos, DDD, SOLID, APIs REST",
                "impact": (
                    "Plataforma web full stack para conciliacao bancaria com adquirentes como Cielo, PagSeguro, "
                    "Stone e GetNet, processando aproximadamente R$335M em transacoes."
                ),
            },
            {
                "name": "PcDigital - SEGOV / Policia Civil",
                "kind": "Experiencia profissional",
                "stack": "Next.js, React, Node.js, NestJS, Prisma, Docker, Microsservicos",
                "impact": (
                    "Sistema web full stack com SSR, APIs NestJS e arquitetura de microsservicos, "
                    "otimizando processos de gestao de dados policiais no estado de Alagoas."
                ),
            },
            {
                "name": "Clone-GitHub",
                "kind": "Projeto publico",
                "url": "https://github.com/LuizCarlosVilela/Clone-GitHub",
                "stack": "React, TypeScript, Styled Components, React Router, Dark Mode",
                "impact": (
                    "Interface responsiva com componentes reutilizaveis, roteamento e estilizacao — "
                    "evidencia de dominio em React e experiencia de usuario."
                ),
            },
            {
                "name": "orders-nestjs-kafka",
                "kind": "Projeto publico",
                "url": "https://github.com/LuizCarlosVilela/orders-nestjs-kafka",
                "stack": "NestJS, Kafka, Prisma, TypeScript, Docker",
                "impact": (
                    "Microsservicos Node.js com mensageria Kafka, reforcando backend desacoplado "
                    "e integracao entre servicos em arquitetura event-driven."
                ),
            },
        ],
    },
    {
        "filename": "luiz-carlos-vilela-backend-node",
        "title": "Backend Senior Node.js",
        "focus": "Node.js - NestJS - Microsservicos - APIs REST",
        "headline": (
            "Node.js, NestJS, TypeScript, microsservicos, Kafka, RabbitMQ, APIs REST, "
            "PostgreSQL, Docker, AWS, GCP e FinTech em escala"
        ),
        "summary": (
            "Engenheiro de Software Senior especializado em backend com Node.js, atuando ha mais de 8 anos "
            "em arquitetura de microsservicos, APIs REST e sistemas distribuidos de alta criticidade. "
            "Desenvolvo servicos com NestJS e Express aplicando SOLID, DDD, Clean Architecture e processamento "
            "orientado a eventos com Kafka e RabbitMQ. Tenho forte experiencia em FinTech e Open Finance: "
            "evolui backends do Mentore Bank (+1M clientes PF), Open Finance PJ na Celero (+30 mil empresas), "
            "conciliacao financeira na Vink (~R$335M em transacoes) e orquestracao de atendimento na DIALLINK. "
            "Atuo com autonomia em definicao arquitetural, code review, observabilidade, CI/CD e entrega em "
            "cloud (AWS e GCP), com foco em resiliencia, seguranca e escalabilidade."
        ),
        "badges": [
            "Node.js - NestJS",
            "Microsservicos",
            "Kafka - RabbitMQ",
            "APIs REST",
            "PostgreSQL - Redis",
            "AWS - GCP",
        ],
        "skills": [
            (
                "Node.js & APIs",
                [
                    "Node.js",
                    "NestJS",
                    "Express",
                    "TypeScript",
                    "JavaScript",
                    "REST APIs",
                    "Webhooks",
                    "Prisma",
                    "Knex",
                    "TypeORM",
                ],
            ),
            (
                "Arquitetura",
                [
                    "Microsservicos",
                    "Event-driven",
                    "SOLID",
                    "DDD",
                    "Clean Architecture",
                    "SAGA Pattern",
                    "Design de APIs",
                    "Integracoes",
                ],
            ),
            (
                "Mensageria & dados",
                [
                    "Kafka",
                    "RabbitMQ",
                    "PostgreSQL",
                    "MySQL",
                    "MongoDB",
                    "Redis",
                    "SQL",
                    "Modelagem de dados",
                ],
            ),
            (
                "Cloud & DevOps",
                [
                    "Docker",
                    "CI/CD",
                    "AWS",
                    "GCP",
                    "Linux",
                    "Observabilidade",
                    "Deploy",
                    "Git",
                ],
            ),
            (
                "Qualidade & praticas",
                [
                    "Testes automatizados",
                    "Jest",
                    "Code Review",
                    "Refactoring",
                    "Documentacao tecnica",
                    "Scrum",
                    "Kanban",
                ],
            ),
        ],
        "experiences": chronological_experiences(
            "mentore",
            "sciensa",
            "celero",
            "vink",
            "diallink",
            "segov",
            "i9colab",
            "beyond",
        ),
        "experience_overrides": {
            "mentore": {
                "bullets": [
                    "Internalizado para evoluir microsservicos e APIs REST em Node.js do ecossistema Mentore Bank.",
                    "Desenvolvi e mantive servicos backend para produto financeiro de alta escala (+1M clientes PF).",
                    "Implementei fluxos assincronos e integracoes com Kafka e RabbitMQ em ambiente de alta criticidade.",
                    "Estruturei CI/CD, testes automatizados e governanca de releases para servicos em producao.",
                    "Concebi solucoes de RPA e automacao para integrar sistemas legados ao ecossistema Node.js.",
                ],
            },
            "sciensa": {
                "role": "Tech Lead / Engenheiro de Software Senior",
                "bullets": [
                    "Liderei decisoes arquiteturais de backend e integracao de APIs para o app bancario PF da Mentore.",
                    "Modelei contratos REST, padroes de integracao e camadas de servico consumidas pelo app mobile.",
                    "Escalei a plataforma para +1 milhao de clientes com pipelines de CI/CD, testes e observabilidade.",
                    "Conduzi revisao de codigo, mentoria tecnica e governanca de qualidade no time de engenharia.",
                ],
            },
            "celero": {
                "bullets": [
                    "Desenvolvi backend Node.js para Open Finance PJ com microsservicos e arquitetura orientada a eventos.",
                    "Implementei integracoes bancarias de alto volume (Caixa e Sicredi) com Kafka e RabbitMQ em GCP.",
                    "Projetei APIs resilientes com reprocessamento seguro, observabilidade e tratamento de falhas.",
                    "Atendi mais de 30 mil empresas PJ em milhoes de operacoes bancarias.",
                ],
            },
            "vink": {
                "bullets": [
                    "Construi microsservicos Node.js para conciliacao bancaria automatizada em alto volume transacional.",
                    "Modelei APIs REST e integracoes com adquirentes (Cielo, PagSeguro, Stone e GetNet).",
                    "Apliquei DDD, SOLID e Clean Architecture em dominio financeiro critico.",
                    "Processei e conciliei cerca de R$335 milhoes em transacoes com monitoramento em tempo real.",
                ],
            },
            "diallink": {
                "role": "Desenvolvedor Backend / Full Stack",
                "bullets": [
                    "Construi backend em Node.js/NestJS para agentes de atendimento humanizado em escala.",
                    "Implementei integracoes com WhatsApp, Meta, Weni, Blip e CRMs com filas em RabbitMQ.",
                    "Orquestrei fluxos de chatbot e automacao para campanhas de grande porte (Atacadao, Ambev e outras).",
                ],
            },
            "segov": {
                "bullets": [
                    "Liderei backends com APIs NestJS, microsservicos Node.js e camada de dados estruturada.",
                    "Defini arquitetura de servicos, documentacao tecnica e padroes de qualidade para a Policia Civil de Alagoas.",
                    "Estruturei Docker, entrega continua e APIs escalaveis no PcDigital.",
                ],
            },
            "i9colab": {
                "bullets": [
                    "Desenvolvi backends com Node.js, Express e TypeORM para e-commerce e sistemas corporativos.",
                    "Modelei bancos relacionais (MySQL, MariaDB) e integrei servicos com APIs REST.",
                    "Implantei e mantive solucoes em AWS com metodologias ageis (Scrum e Kanban).",
                ],
            },
            "beyond": {
                "role": "Cloud Engineer / Backend Developer",
                "bullets": [
                    "Criei APIs RESTful em Node.js com autenticacao, validacao e camadas de persistencia.",
                    "Trabalhei com MySQL, PostgreSQL e MongoDB em modelagem, queries e migrations.",
                    "Atuei em cloud engineering com testes automatizados, deploy e estabilidade de servicos.",
                ],
            },
        },
        "projects": [
            {
                "name": "Open Finance PJ - Celero",
                "kind": "Experiencia profissional",
                "stack": "Node.js, Kafka, RabbitMQ, GCP, microsservicos, APIs REST, Open Finance",
                "impact": (
                    "Backend event-driven para Open Finance PJ com integracoes Caixa e Sicredi, "
                    "atendendo +30 mil empresas em alto volume operacional."
                ),
            },
            {
                "name": "Conciliacao bancaria - Vink",
                "kind": "Experiencia profissional",
                "stack": "Node.js, TypeScript, microsservicos, APIs REST, DDD, SOLID, integracoes financeiras",
                "impact": (
                    "Microsservicos Node.js para conciliacao bancaria com adquirentes como PagSeguro, Cielo, "
                    "Stone e GetNet, processando aproximadamente R$335M em transacoes."
                ),
            },
            {
                "name": "orders-nestjs-kafka",
                "kind": "Projeto publico",
                "url": "https://github.com/LuizCarlosVilela/orders-nestjs-kafka",
                "stack": "NestJS, Kafka, Prisma, TypeScript, Docker",
                "impact": (
                    "Microsservicos Node.js com mensageria Kafka, demonstrando arquitetura event-driven "
                    "e integracao desacoplada entre servicos."
                ),
            },
            {
                "name": "Agentes de atendimento - DIALLINK",
                "kind": "Experiencia profissional",
                "stack": "NestJS, Node.js, RabbitMQ, WhatsApp API, Meta API, REST APIs",
                "impact": (
                    "Backend NestJS orquestrando atendimento humanizado com integracoes WhatsApp, Meta, "
                    "Weni e Blip em campanhas de alto volume."
                ),
            },
        ],
    },
    {
        "filename": "luiz-carlos-vilela-senior-fullstack",
        "title": "Desenvolvedor Senior Full Stack",
        "focus": "Vue - NestJS - React - Lideranca Tecnica",
        "headline": (
            "Vue.js, NestJS, Node.js, TypeScript, React, microsservicos, APIs REST, "
            "CI/CD, Docker, AWS, GCP e lideranca tecnica"
        ),
        "summary": (
            "Engenheiro de Software Senior com mais de 8 anos em solucoes web e integracoes de alta complexidade. "
            "Minha jornada comecou consolidando frontend com Vue 2 e Vue 3 na Beyond Co., evolui para construcao de "
            "agentes de atendimento humanizado na DIALLINK com Node.js/NestJS e integracoes WhatsApp e Meta, e "
            "amadureceu em sistemas financeiros de alto volume na Vink, Celero, Sciensa e Mentore (+1M clientes, "
            "R$335M conciliados, Open Finance PJ). Atuo como referencia tecnica: arquitetura, code review, mentoria, "
            "CI/CD, cloud e entrega ponta a ponta com foco em escalabilidade, seguranca e manutenibilidade."
        ),
        "badges": [
            "Vue 2 - Vue 3",
            "NestJS - Node.js",
            "Lideranca Tecnica",
            "Microsservicos",
            "CI/CD - Docker",
            "AWS - GCP",
        ],
        "skills": [
            (
                "Frontend",
                [
                    "Vue 2",
                    "Vue 3",
                    "React",
                    "Next.js",
                    "TypeScript",
                    "JavaScript",
                    "Design Systems",
                    "Responsive UI",
                ],
            ),
            (
                "Backend & APIs",
                [
                    "Node.js",
                    "NestJS",
                    "Express",
                    "REST APIs",
                    "Webhooks",
                    "Microsservicos",
                    "PHP",
                    "Laravel",
                ],
            ),
            (
                "Dados & mensageria",
                [
                    "PostgreSQL",
                    "MySQL",
                    "MongoDB",
                    "Redis",
                    "Kafka",
                    "RabbitMQ",
                    "Prisma",
                    "Knex",
                ],
            ),
            (
                "Lideranca & arquitetura",
                [
                    "Tech Lead",
                    "Code Review",
                    "Mentoria",
                    "SOLID",
                    "DDD",
                    "Design Patterns",
                    "Documentacao tecnica",
                ],
            ),
            (
                "DevOps & cloud",
                [
                    "CI/CD",
                    "Docker",
                    "Git",
                    "AWS",
                    "GCP",
                    "Testes automatizados",
                    "Scrum",
                    "Kanban",
                ],
            ),
        ],
        "experiences": chronological_experiences(
            "mentore",
            "sciensa",
            "celero",
            "vink",
            "diallink",
            "segov",
            "beyond",
            "i9colab",
        ),
        "experience_overrides": {
            "mentore": {
                "bullets": [
                    "Internalizado apos consultoria para liderar evolucao tecnica do ecossistema web e backend do Mentore Bank.",
                    "Evolui microsservicos e APIs REST em Node.js para produto financeiro de alta escala (+1M clientes PF).",
                    "Defini padroes de arquitetura, qualidade de codigo e integracao entre frontend e backend.",
                    "Mantive pipelines de CI/CD com testes automatizados e governanca de releases.",
                    "Conduzi revisao de codigo e apoio tecnico a desenvolvedores em fluxos criticos de producao.",
                ],
            },
            "sciensa": {
                "role": "Tech Lead / Engenheiro de Software Senior",
                "bullets": [
                    "Liderei tecnicamente o produto bancario PF na Sciensa/Mentore, com decisoes arquiteturais e mentoria.",
                    "Defini padroes de frontend, integracao com APIs REST e escalabilidade para +1 milhao de clientes.",
                    "Estruturei CI/CD, testes e governanca de codigo com foco em qualidade e entrega continua.",
                    "Atuei com autonomia entre PO, QA e engenharia, da especificacao ate producao.",
                ],
            },
            "celero": {
                "bullets": [
                    "Desenvolvi backend Node.js para Open Finance PJ com microsservicos e arquitetura orientada a eventos.",
                    "Implementei integracoes bancarias de alto volume (Caixa e Sicredi) com Kafka e RabbitMQ em GCP.",
                    "Projetei solucoes resilientes para +30 mil empresas PJ com observabilidade e reprocessamento seguro.",
                ],
            },
            "vink": {
                "bullets": [
                    "Construi microsservicos Node.js e interfaces web React para conciliacao bancaria automatizada.",
                    "Modelei APIs REST e integracoes com multiplos adquirentes em ambiente de alto volume transacional.",
                    "Apliquei DDD, SOLID e Clean Architecture; processei cerca de R$335 milhoes em transacoes.",
                ],
            },
            "diallink": {
                "role": "Desenvolvedor Full Stack / ChatBot",
                "bullets": [
                    "Desenvolvi agentes de atendimento humanizado com integracoes diretas com WhatsApp e Meta.",
                    "Construi backend em Node.js com NestJS para orquestrar fluxos de chatbot e automacao de atendimento.",
                    "Entreguei solucoes full stack integradas a APIs REST com foco em escalabilidade e UX.",
                ],
            },
            "segov": {
                "bullets": [
                    "Liderei tecnicamente sistemas de gestao com Next.js, NestJS, microsservicos e Docker.",
                    "Defini arquitetura, documentacao tecnica e padroes de qualidade para a Policia Civil de Alagoas.",
                    "O PcDigital otimizou processos de gestao institucional com APIs escalaveis e alta disponibilidade.",
                ],
            },
            "beyond": {
                "role": "Cloud Engineer / Full Stack Developer",
                "bullets": [
                    "Desenvolvi aplicacoes full stack com Vue 2 e Vue 3 no dia a dia no frontend.",
                    "Criei APIs REST em Node.js com MySQL, PostgreSQL e MongoDB.",
                    "Atuei em cloud engineering com testes automatizados, deploy e estabilidade de aplicacoes web.",
                ],
            },
            "i9colab": {
                "bullets": [
                    "Atuei como consultor full stack com PHP, Laravel, React, Node.js, Express e TypeORM.",
                    "Desenvolvi e-commerce, sistemas corporativos e integracoes com MySQL e MariaDB.",
                    "Implantei e mantive solucoes em AWS com metodologias ageis (Scrum e Kanban).",
                ],
            },
        },
        "projects": [
            {
                "name": "Agentes de atendimento - DIALLINK",
                "kind": "Experiencia profissional",
                "stack": "NestJS, Node.js, WhatsApp API, Meta API, REST APIs, chatbot",
                "impact": (
                    "Agentes de atendimento humanizado com integracoes WhatsApp e Meta, "
                    "orquestrados em Node.js/NestJS para automacao de atendimento em escala."
                ),
            },
            {
                "name": "Conciliacao bancaria - Vink",
                "kind": "Experiencia profissional",
                "stack": "React, Node.js, microsservicos, APIs REST, DDD, SOLID",
                "impact": (
                    "Plataforma full stack para conciliacao bancaria com alto volume de dados, "
                    "processando aproximadamente R$335M em transacoes financeiras."
                ),
            },
            {
                "name": "PcDigital - SEGOV",
                "kind": "Experiencia profissional",
                "stack": "Next.js, NestJS, Node.js, Docker, PostgreSQL, microsservicos",
                "impact": (
                    "Sistema de gestao institucional com lideranca tecnica, APIs NestJS e arquitetura "
                    "de microsservicos para otimizacao de processos criticos."
                ),
            },
            {
                "name": "Open Finance PJ - Celero",
                "kind": "Experiencia profissional",
                "stack": "Node.js, Kafka, RabbitMQ, GCP, APIs REST, integracoes bancarias",
                "impact": (
                    "Backend de alto volume para Open Finance PJ, atendendo +30 mil empresas "
                    "com arquitetura orientada a eventos e resiliencia operacional."
                ),
            },
        ],
    },
    {
        "filename": "luiz-carlos-vilela-fullstack-generalista",
        "title": "Engenheiro de Software Full Stack",
        "focus": "React - Angular - Node.js - Java - PHP - Python",
        "headline": (
            "Engenheiro de Software Full Stack: React, Angular, Node.js, Java, PHP, Python, "
            "APIs REST, microsservicos, SQL e cloud"
        ),
        "summary": (
            "Engenheiro de Software Senior Full Stack com mais de 8 anos construindo "
            "produtos digitais ponta a ponta. No frontend, domino React, Next.js e Angular com TypeScript, "
            "componentizacao, Design System e integracao com APIs. No backend, tenho expertise em Node.js "
            "(NestJS, Express), Java (Spring Boot), PHP (Laravel) e Python, aplicando SOLID, DDD e "
            "arquitetura de microsservicos em FinTech, Open Finance, atendimento inteligente e sistemas "
            "corporativos. Ja entreguei produtos para +1M clientes, Open Finance em larga escala e plataformas "
            "de alto volume transacional, com autonomia tecnica, CI/CD e atuacao em cloud (AWS e GCP)."
        ),
        "badges": [
            "React - Angular",
            "Node.js - NestJS",
            "Java - Spring Boot",
            "PHP - Python",
            "Full Stack",
            "AWS - GCP",
        ],
        "skills": [
            (
                "Frontend",
                [
                    "React",
                    "Next.js",
                    "Angular",
                    "TypeScript",
                    "JavaScript",
                    "Redux",
                    "RxJS",
                    "Design Systems",
                    "SSR",
                ],
            ),
            (
                "Backend Node.js",
                [
                    "Node.js",
                    "NestJS",
                    "Express",
                    "TypeScript",
                    "REST APIs",
                    "Microsservicos",
                    "Prisma",
                    "Knex",
                ],
            ),
            (
                "Backend Java",
                [
                    "Java",
                    "Spring Boot",
                    "JUnit",
                    "TDD",
                    "POO",
                    "JDBC",
                    "REST APIs",
                    "Microsservicos",
                ],
            ),
            (
                "PHP & Python",
                [
                    "PHP",
                    "Laravel",
                    "Python",
                    "Scripts",
                    "Automacao",
                    "Bots",
                    "Integracoes",
                ],
            ),
            (
                "Dados & cloud",
                [
                    "PostgreSQL",
                    "MySQL",
                    "MongoDB",
                    "Redis",
                    "Kafka",
                    "RabbitMQ",
                    "Docker",
                    "AWS",
                    "GCP",
                    "CI/CD",
                ],
            ),
        ],
        "experiences": LINKEDIN_EXPERIENCE_ORDER,
        "experience_overrides": {
            "mentore": {
                "bullets": [
                    "Internalizado para evoluir ecossistema full stack do Mentore Bank: web, backend Node.js e integracoes.",
                    "Evolui APIs REST e microsservicos em Node.js para produto financeiro de alta escala (+1M clientes).",
                    "Desenvolvi integracoes entre frontend e backend com contratos tipados e padroes de qualidade.",
                    "Mantive CI/CD, testes e governanca de releases em ambiente de alta criticidade.",
                ],
            },
            "sciensa": {
                "bullets": [
                    "Atuei como Tech Lead na construcao do produto bancario PF, com decisoes arquiteturais e mentoria.",
                    "Defini Design System, padroes de frontend e integracao com APIs REST e servicos Node.js.",
                    "Escalei o produto para +1 milhao de clientes com CI/CD, testes e governanca de codigo.",
                ],
            },
            "celero": {
                "bullets": [
                    "Desenvolvi backend Node.js para Open Finance PJ com microsservicos e arquitetura orientada a eventos.",
                    "Implementei integracoes bancarias de alto volume (Caixa e Sicredi) com Kafka e RabbitMQ em GCP.",
                    "Atendi mais de 30 mil empresas PJ com APIs resilientes e processamento assincrono.",
                ],
            },
            "vink": {
                "bullets": [
                    "Construi solucoes full stack com React no frontend e microsservicos Node.js no backend.",
                    "Apliquei DDD, SOLID e Clean Architecture em dominio financeiro de alta criticidade.",
                    "Processei e conciliei cerca de R$335 milhoes em transacoes com monitoramento em tempo real.",
                ],
            },
            "diallink": {
                "bullets": [
                    "Desenvolvi solucoes full stack com React e Node.js/NestJS para atendimento humanizado.",
                    "Construi integracoes com WhatsApp, Meta, Weni, Blip e CRMs com filas em RabbitMQ.",
                    "Atendi campanhas de grande porte (Atacadao, Ambev e outras) com milhares de interacoes.",
                ],
            },
            "segov": {
                "bullets": [
                    "Liderei sistemas web com Next.js/React, APIs NestJS e microsservicos em Node.js.",
                    "Estruturei arquitetura de dados, Docker e padroes de entrega continua.",
                    "O PcDigital otimizou gestao institucional com APIs escalaveis e interface web performatica.",
                ],
            },
            "i9colab": {
                "bullets": [
                    "Atuei como consultor full stack com PHP, Laravel, Python, React e Node.js (Express, TypeORM).",
                    "Desenvolvi e-commerce, sistemas corporativos, bots e automacoes com MySQL e MariaDB.",
                    "Implantei e mantive solucoes em AWS com metodologias ageis (Scrum e Kanban).",
                ],
            },
            "beyond": {
                "bullets": [
                    "Desenvolvi aplicacoes full stack com Vue 2/3 no frontend e APIs REST em Node.js.",
                    "Modelei bancos relacionais e NoSQL (MySQL, PostgreSQL, MongoDB) com migrations e queries.",
                ],
            },
            "prefeitura": {
                "bullets": [
                    "Desenvolvi solucoes web com React, Next.js, TypeScript e backend Node.js com Prisma.",
                    "Entreguei APIs e interfaces integradas com foco em manutencao e escalabilidade.",
                ],
            },
        },
        "projects": [
            {
                "name": "Conciliacao bancaria - Vink",
                "kind": "Experiencia profissional",
                "stack": "React, Node.js, TypeScript, microsservicos, APIs REST, DDD, SOLID",
                "impact": (
                    "Plataforma full stack para conciliacao bancaria automatizada, "
                    "processando aproximadamente R$335M em transacoes financeiras."
                ),
            },
            {
                "name": "CourseManager-Angular",
                "kind": "Projeto publico",
                "url": "https://github.com/LuizCarlosVilela/CourseManager-Angular",
                "stack": "Angular, TypeScript, Router, Reactive Forms, Bootstrap",
                "impact": (
                    "Sistema web em Angular com componentes reutilizaveis, rotas e formularios reativos — "
                    "evidencia dominio em frontend Angular alem de React."
                ),
            },
            {
                "name": "API-POO-Java",
                "kind": "Projeto publico",
                "url": "https://github.com/LuizCarlosVilela/API-POO-Java",
                "stack": "Java, JDBC, JUnit, API REST, POO",
                "impact": (
                    "API Java com persistencia relacional e testes automatizados, "
                    "reforçando fundamentos backend corporativo em Java."
                ),
            },
            {
                "name": "PcDigital - SEGOV",
                "kind": "Experiencia profissional",
                "stack": "Next.js, React, NestJS, Node.js, PostgreSQL, Docker, microsservicos",
                "impact": (
                    "Sistema full stack com SSR, APIs NestJS e arquitetura de microsservicos "
                    "para gestao institucional em escala estadual."
                ),
            },
        ],
    },
]


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def profile_photo_data_uri() -> str | None:
    for filename in PHOTO_FILENAMES:
        path = ASSETS_DIR / filename
        if path.exists():
            mime_type = mimetypes.guess_type(path.name)[0] or "image/jpeg"
            encoded = base64.b64encode(path.read_bytes()).decode("ascii")
            return f"data:{mime_type};base64,{encoded}"
    return None


def render_photo() -> str:
    data_uri = profile_photo_data_uri()
    if data_uri:
        return f'<img class="photo" src="{data_uri}" alt="Foto de perfil de {esc(PROFILE["name"])}" />'
    return '<div class="photo photo-fallback">LC</div>'


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


def render_sidebar_stack(groups: list[tuple[str, list[str]]]) -> str:
    items = []
    for _, stack_items in groups:
        items.extend(stack_items[:4])
    unique_items = list(dict.fromkeys(items))[:18]
    return "\n".join(f"<li>{esc(item)}</li>" for item in unique_items)


def render_experiences(keys: list[str], overrides: dict[str, dict] | None = None) -> str:
    overrides = overrides or {}
    cards = []
    for key in keys:
        base = BASE_EXPERIENCES[key]
        custom = overrides.get(key, {})
        item = {**base, **{k: v for k, v in custom.items() if k != "bullets"}}
        bullets = custom.get("bullets", base["bullets"])
        bullet_items = "\n".join(f"<li>{esc(bullet)}</li>" for bullet in bullets)
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
              <ul>{bullet_items}</ul>
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
    return "\n".join(f"<li>{esc(item)}</li>" for item in items)


def render_contact_list() -> str:
    contacts = [
        ("WhatsApp", PROFILE["phone"], PROFILE["whatsapp_url"]),
        ("E-mail", PROFILE["email"], PROFILE["email_url"]),
        ("LinkedIn", PROFILE["linkedin"], PROFILE["linkedin_url"]),
        ("GitHub", PROFILE["github"], PROFILE["github_url"]),
    ]
    items = []
    for label, display, url in contacts:
        items.append(
            f"""
        <li>
          <a class="contact-link" href="{esc(url)}">
            <span class="contact-label">{esc(label)}</span>
            <span class="contact-value">{esc(display)}</span>
          </a>
        </li>
        """
        )
    items.append(f'<li class="contact-location">{esc(PROFILE["location"])}</li>')
    return "\n".join(items)


def render_resume(resume: dict[str, object]) -> str:
    return f"""<!doctype html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{esc(PROFILE["name"])} - {esc(resume["title"])}</title>
  <style>
    :root {{
      --royal: #1f4fbf;
      --royal-dark: #173a8c;
      --royal-soft: #e8efff;
      --ink: #2d333a;
      --muted: #69727c;
      --line: #dbe3e8;
      --paper: #ffffff;
      --panel: #f6f8fa;
      --accent: #2166a7;
      --gold: #d9a441;
    }}

    * {{
      box-sizing: border-box;
    }}

    body {{
      background: #e8ecef;
      color: var(--ink);
      font-family: Arial, Helvetica, sans-serif;
      font-size: 11.3px;
      line-height: 1.42;
      margin: 0;
    }}

    a {{
      color: var(--accent);
      text-decoration: none;
    }}

    .page {{
      background: var(--paper);
      display: grid;
      grid-template-columns: 64mm 1fr;
      margin: 0 auto;
      min-height: 297mm;
      overflow: hidden;
      width: 210mm;
    }}

    .sidebar {{
      background: linear-gradient(180deg, var(--royal) 0%, var(--royal-dark) 100%);
      color: #fff;
      padding: 12mm 8mm;
    }}

    .photo-wrap {{
      display: flex;
      justify-content: center;
      margin: 0 0 13mm;
      position: relative;
    }}

    .photo-wrap::before {{
      background: repeating-linear-gradient(0deg, rgba(255,255,255,.18), rgba(255,255,255,.18) 1px, transparent 1px, transparent 4px);
      content: "";
      height: 42mm;
      left: -8mm;
      position: absolute;
      right: -8mm;
      top: 7mm;
    }}

    .photo {{
      background: #dfe7ea;
      border: 5px solid rgba(255,255,255,.42);
      border-radius: 50%;
      box-shadow: 0 10px 24px rgba(0,0,0,.18);
      display: block;
      flex-shrink: 0;
      height: 38mm;
      object-fit: cover;
      object-position: center 18%;
      position: relative;
      width: 38mm;
      z-index: 1;
    }}

    .photo-fallback {{
      align-items: center;
      color: var(--royal-dark);
      display: flex;
      font-size: 26px;
      font-weight: 900;
      justify-content: center;
      letter-spacing: .08em;
    }}

    .side-section {{
      margin-bottom: 9mm;
    }}

    .side-title {{
      align-items: center;
      color: #fff;
      display: flex;
      font-size: 11px;
      font-weight: 900;
      gap: 7px;
      letter-spacing: .08em;
      margin: 0 0 8px;
      text-transform: uppercase;
    }}

    .side-title::before {{
      background: #fff;
      content: "";
      display: inline-block;
      height: 3px;
      width: 14px;
    }}

    .side-title::after {{
      display: none;
    }}

    .side-section p,
    .side-section li {{
      color: rgba(255,255,255,.9);
      margin: 0 0 4px;
    }}

    .side-section ul {{
      list-style: none;
      margin: 0;
      padding: 0;
    }}

    .contact-list {{
      list-style: none;
      margin: 0;
      padding: 0;
    }}

    .contact-list li {{
      margin: 0 0 7px;
    }}

    .contact-link {{
      border-bottom: 1px solid rgba(255,255,255,.18);
      color: #fff;
      display: block;
      overflow-wrap: anywhere;
      padding: 4px 0 6px;
      text-decoration: none;
    }}

    .contact-label {{
      color: rgba(255,255,255,.78);
      display: block;
      font-size: 9px;
      font-weight: 900;
      letter-spacing: .1em;
      margin-bottom: 2px;
      text-transform: uppercase;
    }}

    .contact-value {{
      color: #fff;
      display: block;
      font-weight: 700;
      line-height: 1.28;
      text-decoration: underline;
      text-decoration-color: rgba(255,255,255,.62);
      text-underline-offset: 2px;
    }}

    .contact-location {{
      color: rgba(255,255,255,.9);
      font-size: 10.5px;
      line-height: 1.35;
      margin-top: 2px;
      padding-top: 2px;
    }}

    .main {{
      min-width: 0;
      padding: 13mm 12mm 12mm;
    }}

    .top {{
      border-bottom: 2px solid var(--royal);
      margin-bottom: 12px;
      padding-bottom: 12px;
    }}

    h1 {{
      color: var(--ink);
      font-size: 27px;
      letter-spacing: .02em;
      line-height: 1.06;
      margin: 0 0 6px;
      text-transform: uppercase;
    }}

    .subtitle {{
      color: var(--muted);
      font-size: 14px;
      font-weight: 800;
      margin: 0 0 9px;
    }}

    .badges {{
      display: flex;
      flex-wrap: wrap;
      gap: 6px;
    }}

    .badges span {{
      background: var(--royal-soft);
      border-radius: 999px;
      color: var(--royal-dark);
      font-size: 10.5px;
      font-weight: 900;
      padding: 4px 8px;
    }}

    .badges span:nth-child(3n) {{
      background: #fff2d6;
      color: #765419;
    }}

    .summary {{
      background: var(--panel);
      border-left: 4px solid var(--royal);
      border-radius: 7px;
      margin: 0 0 10px;
      padding: 10px 12px;
    }}

    .summary strong {{
      color: var(--royal-dark);
    }}

    .metrics {{
      display: grid;
      gap: 8px;
      grid-template-columns: repeat(3, 1fr);
      margin: 0 0 12px;
    }}

    .metric {{
      background: var(--royal-soft);
      border-radius: 7px;
      min-width: 0;
      padding: 8px 9px;
    }}

    .metric strong {{
      color: var(--accent);
      display: block;
      font-size: 16px;
      line-height: 1;
      margin-bottom: 3px;
    }}

    .metric span {{
      color: var(--ink);
      display: block;
      font-weight: 800;
    }}

    h2 {{
      align-items: center;
      color: var(--royal-dark);
      display: flex;
      font-size: 12.5px;
      gap: 8px;
      letter-spacing: .11em;
      margin: 13px 0 8px;
      text-transform: uppercase;
    }}

    h2::after {{
      background: var(--line);
      content: "";
      flex: 1;
      height: 1px;
    }}

    h3 {{
      color: var(--ink);
      font-size: 12.5px;
      margin: 0;
    }}

    .skills {{
      display: grid;
      gap: 7px;
      grid-template-columns: repeat(2, 1fr);
    }}

    .skill-card,
    .experience-card,
    .project-card {{
      background: #fff;
      border: 1px solid var(--line);
      border-radius: 8px;
      break-inside: avoid;
      box-shadow: 0 3px 10px rgba(22, 38, 48, .05);
      padding: 8px 10px;
    }}

    .chips {{
      display: flex;
      flex-wrap: wrap;
      gap: 5px;
      margin-top: 6px;
    }}

    .chips span {{
      background: var(--panel);
      border-radius: 999px;
      color: var(--muted);
      font-size: 10px;
      font-weight: 800;
      padding: 3px 7px;
    }}

    .experience-card {{
      margin-bottom: 7px;
    }}

    .experience-head,
    .project-head {{
      display: grid;
      gap: 8px;
      grid-template-columns: 1fr auto;
      margin-bottom: 5px;
    }}

    .experience-head p,
    .project-card p {{
      margin: 2px 0 0;
    }}

    .meta {{
      color: var(--muted);
      display: grid;
      font-size: 10.5px;
      justify-items: end;
      line-height: 1.25;
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
      color: var(--royal);
    }}

    .project-grid {{
      display: grid;
      gap: 7px;
      grid-template-columns: 1fr 1fr;
    }}

    .kind {{
      color: var(--royal);
      display: block;
      font-size: 9.5px;
      font-weight: 900;
      letter-spacing: .08em;
      margin-bottom: 2px;
      text-transform: uppercase;
    }}

    .project-head a {{
      color: var(--accent);
      display: inline-block;
      font-size: 9.5px;
      max-width: 42mm;
      overflow-wrap: anywhere;
      text-align: right;
      text-decoration: underline;
      text-underline-offset: 2px;
    }}

    .stack {{
      color: var(--accent);
      font-size: 10.5px;
      font-weight: 900;
    }}

    @page {{
      margin: 0;
      size: A4;
    }}

    @media print {{
      body {{
        background: #fff;
      }}

      .page {{
        box-shadow: none;
        margin: 0;
      }}
    }}

    @media screen and (max-width: 780px) {{
      .page {{
        grid-template-columns: 1fr;
        min-height: auto;
        width: 100%;
      }}

      .sidebar,
      .main {{
        padding: 22px;
      }}

      .metrics,
      .skills,
      .project-grid,
      .experience-head,
      .project-head {{
        grid-template-columns: 1fr;
      }}

      .meta,
      .project-head a {{
        justify-items: start;
        text-align: left;
      }}
    }}
  </style>
</head>
<body>
  <main class="page">
    <aside class="sidebar">
      <div class="photo-wrap">{render_photo()}</div>

      <section class="side-section">
        <h2 class="side-title">Contato</h2>
        <ul class="contact-list">
          {render_contact_list()}
        </ul>
      </section>

      <section class="side-section">
        <h2 class="side-title">Stacks-chave</h2>
        <ul>{render_sidebar_stack(resume["skills"])}</ul>
      </section>

      <section class="side-section">
        <h2 class="side-title">Formacao</h2>
        <ul>{render_compact_list(EDUCATION)}</ul>
      </section>

      <section class="side-section">
        <h2 class="side-title">Certificacoes</h2>
        <ul>{render_compact_list(CERTIFICATIONS)}</ul>
      </section>
    </aside>

    <section class="main">
      <header class="top">
        <h1>{esc(PROFILE["name"])}</h1>
        <p class="subtitle">{esc(PROFILE["title"])} | {esc(resume["title"])} | {esc(resume.get("focus", PROFILE["focus"]))}</p>
        <div class="badges">{render_badges(resume["badges"])}</div>
      </header>

      <section class="summary">
        <strong>{esc(resume["headline"])}.</strong> {esc(resume.get("summary", PROFILE["summary"]))}
      </section>

      <section class="metrics">{render_metric_cards()}</section>

      <section>
        <h2>Competencias por stack</h2>
        <div class="skills">{render_skills(resume["skills"])}</div>
      </section>

      <section>
        <h2>Experiencia profissional</h2>
        {render_experiences(resume["experiences"], resume.get("experience_overrides"))}
      </section>

      <section>
        <h2>Projetos e entregas em destaque</h2>
        <div class="project-grid">{render_projects(resume["projects"])}</div>
      </section>
    </section>
  </main>
</body>
</html>
"""


def chrome_path() -> str | None:
    candidates = (
        "google-chrome",
        "chromium",
        "chromium-browser",
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser",
    )
    for candidate in candidates:
        path = shutil.which(candidate) if "/" not in candidate else candidate
        if path and Path(path).exists():
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

    command = [
        chrome,
        "--headless=new",
        "--disable-gpu",
        "--disable-dev-shm-usage",
        "--no-sandbox",
        "--no-pdf-header-footer",
        f"--print-to-pdf={pdf_path}",
        html_path.resolve().as_uri(),
    ]
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    deadline = time.monotonic() + 90
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
            _, stderr = process.communicate()
            raise subprocess.CalledProcessError(return_code, command, stderr=stderr)
        time.sleep(0.2)

    process.kill()
    _, stderr = process.communicate()
    raise subprocess.TimeoutExpired(command, 90, output=stderr)


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
