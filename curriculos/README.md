# Curriculos direcionados

Este diretorio adiciona curriculos em PDF focados em stacks, experiencias e projetos, a partir do PDF exportado do LinkedIn e dos repositorios publicos do GitHub.

## Variantes geradas

- `pdf/luiz-carlos-vilela-mobile-backend.pdf` - foco em Flutter/Dart, Kotlin, Swift, CI/CD mobile, publicacao em lojas, Node.js, NestJS, Kafka e RabbitMQ.
- `pdf/luiz-carlos-vilela-java-angular.pdf` - foco em Java/Spring Boot, Angular/TypeScript, APIs, microsservicos e arquitetura backend.
- `pdf/luiz-carlos-vilela-react-java.pdf` - foco em React/Next.js/TypeScript, Java/Spring Boot, APIs e produtos financeiros web.

Os HTMLs correspondentes ficam em `html/` para revisao visual e ajustes finos antes de exportar.

## Foto de perfil

O layout esta preparado para usar foto circular na sidebar, no estilo de modelos visuais de LinkedIn/Canva.
Adicione a foto real em `assets/profile-photo.jpg` (ou `.jpeg`, `.png`, `.webp`) e rode novamente:

```bash
python3 curriculos/generate.py
```

Sem esse arquivo, o gerador usa um avatar temporario com as iniciais `LC`.
Observacao: imagens coladas diretamente na conversa podem nao ficar disponiveis como arquivo no workspace; nesse caso,
salve a foto em `curriculos/assets/profile-photo.jpg` antes de gerar os PDFs.

## Como gerar novamente

```bash
python3 curriculos/generate.py
```

O script usa Chrome/Chromium em modo headless para exportar os PDFs. Para gerar apenas os HTMLs:

```bash
python3 curriculos/generate.py --html-only
```

## Melhorias aplicadas ao curriculo

1. Resumo moderno no topo, usando o posicionamento: Engenheiro de Software Senior em Backend, Mobile e RPA.
2. Metricas de impacto destacadas: +1M clientes PF ativos no app Mentore, R$335M conciliados na Vink e 30k+ empresas PJ atendidas em Open Finance na Celero.
3. Experiencias profissionais estruturadas em cards, com bullets orientados a impacto e stack.
4. Separacao por vaga/stack, evitando um curriculo generico com muitas tecnologias competindo por atencao.
5. Projetos publicos do GitHub entram como prova tecnica complementar, sem competir com as entregas profissionais.
6. Tecnologias agrupadas por contexto: Mobile, Backend, eventos, dados, cloud, Angular, React, Java, UI e entrega.
7. Redesign visual com sidebar azul royal, foto/avatar circular, cabecalho limpo, cards de metricas e experiencias em destaque.
8. Contatos clicaveis no PDF: WhatsApp, e-mail, LinkedIn e GitHub.
9. Experiencias profissionais organizadas na ordem do PDF exportado do LinkedIn.

## Observacao sobre ATS

Modelos com sidebar e foto sao melhores para envio direto a recrutadores e networking. Para inscricoes em portais ATS
mais rigidos, o ideal e manter tambem uma versao em coluna unica, sem foto e sem sidebar, para reduzir risco de parsing.

## Pontos para enriquecer depois

- Validar se o telefone e o e-mail devem aparecer em todos os PDFs publicos do GitHub.
- Substituir o avatar `LC` pela foto real em `curriculos/assets/profile-photo.jpg`.
- Completar dados de Spring Boot/Angular com experiencias profissionais especificas, se existirem alem dos projetos publicos.
- Adicionar resultados numericos adicionais: performance, reducao de bugs, tempo de entrega, custo ou disponibilidade.
- Criar uma versao em ingles para vagas internacionais.
