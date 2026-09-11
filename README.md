# Central Nhora

Central independente de atendimento, vendas, suporte e operações da Nhora.

## Filas

- **Leads de campanhas:** anúncios, landing pages e campanhas externas.
- **Campanhas internas:** banners, avisos e ações dentro da plataforma.
- **Suporte:** dúvidas, problemas e solicitações dos clientes ativos.
- **Transacional:** ativação de conta e recuperação de acesso; recomenda-se mantê-la isolada do atendimento humano.

Cada caixa é configurada por ID no `.env`. Uma instância real da Evolution corresponde a um número conectado; as filas podem ser separadas no Chatwoot mesmo quando a operação utiliza menos números.

## Contexto obrigatório

Ao criar conversas por automação, grave em `custom_attributes` do Chatwoot sempre que existirem:

`origem`, `campanha`, `utm_source`, `utm_medium`, `utm_campaign`, `pagina`, `empresa`, `business_id`, `usuario`, `assunto` e `evento_sistema`.

A Central exibe esses atributos no topo da conversa. Assim, o atendente sabe por que o contato chegou antes de responder.

## Instalação

1. Copie `.env.example` para `.env` e preencha os valores reais.
2. Confirme os quatro IDs de caixa no Chatwoot.
3. Confirme que a rede externa `nohra_default` existe ou altere seu nome no Compose.
4. Execute `docker compose up -d --build`.
5. Publique o frontend e `/api` atrás de HTTPS no proxy reverso.

O login usa a conta de administrador da plataforma Nhora. Somente usuários com `is_platform_admin=true` entram na Central.

## Testes mínimos

- login de administrador e bloqueio de usuário comum;
- carregamento das quatro filas;
- envio e recebimento de texto, áudio e anexo;
- atribuição, etiquetas, arquivamento e reabertura;
- origem/campanha/empresa visíveis no contexto;
- mensagem iniciada por cada caixa usando o número correspondente;
- queda do Chatwoot ou n8n retornando erro legível.
