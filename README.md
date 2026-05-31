# 💰 Assistente Financeira para WhatsApp

Assistente virtual que recebe mensagens de texto via WhatsApp, interpreta gastos e receitas em linguagem natural, armazena no Firebase Firestore e responde automaticamente.

---

## 🗂️ Estrutura do Projeto

```
backend/
├── app.py                        # Entry point FastAPI
├── requirements.txt
├── render.yaml                   # Config deploy no Render
├── .env.example                  # Variáveis de ambiente (modelo)
│
├── config/
│   ├── __init__.py
│   ├── settings.py               # Carrega .env com Pydantic Settings
│   └── firebase-credentials.json # ⚠️ NÃO commitar no Git!
│
├── routes/
│   ├── __init__.py
│   ├── webhook.py                # Recebe eventos da Evolution API
│   └── health.py                 # Health check para Render
│
├── services/
│   ├── __init__.py
│   ├── processador.py            # Orquestrador principal
│   ├── financas.py               # CRUD e consultas no Firestore
│   ├── mensagens.py              # Formata respostas para WhatsApp
│   └── whatsapp.py               # Envia mensagens via Evolution API
│
├── models/
│   ├── __init__.py
│   └── transacao.py              # Modelos Pydantic (Transacao, Usuario...)
│
├── database/
│   ├── __init__.py
│   └── firebase.py               # Inicialização e helpers do Firestore
│
└── ai/
    ├── __init__.py
    └── nlp_parser.py             # Extrai dados financeiros das mensagens
```

---

## ⚙️ Configuração do Firebase

### 1. Criar projeto
1. Acesse [console.firebase.google.com](https://console.firebase.google.com)
2. Clique em **Adicionar projeto** e siga o assistente
3. No menu lateral → **Firestore Database** → **Criar banco de dados**
4. Escolha **Modo de produção** e selecione uma região próxima (ex: `southamerica-east1`)

### 2. Gerar credenciais
1. No Firebase Console → **Configurações do Projeto** (ícone de engrenagem)
2. Aba **Contas de serviço**
3. Clique em **Gerar nova chave privada**
4. Salve o arquivo JSON como `backend/config/firebase-credentials.json`
5. ⚠️ **NUNCA commite esse arquivo no Git!** Adicione ao `.gitignore`

### 3. Estrutura do Firestore

```
usuarios/                          ← Coleção
  {telefone}/                      ← Documento (ex: "5511999999999")
    telefone: "5511999999999"
    nome: "João Silva"
    
    transacoes/                    ← Subcoleção
      {id}/
        tipo: "gasto"
        valor: 25.00
        categoria: "alimentacao"
        descricao: "almoco"
        data: "2026-05-31T12:30:00"
```

---

## 📱 Configuração da Evolution API

### Opção A — Auto-hospedagem no Render (grátis)
1. Faça fork do repositório oficial: [github.com/EvolutionAPI/evolution-api](https://github.com/EvolutionAPI/evolution-api)
2. No [Render.com](https://render.com) → **New Web Service** → conecte o fork
3. Configure as variáveis de ambiente conforme a documentação oficial
4. Após o deploy, acesse o Swagger em `https://sua-evolution.onrender.com/docs`

### Opção B — Cloud da Evolution (pago)
Acesse [evolution-api.com](https://evolution-api.com) para planos gerenciados.

### Criar instância WhatsApp
```bash
# Criar instância via API
curl -X POST https://sua-evolution.com/instance/create \
  -H "apikey: SUA_CHAVE" \
  -H "Content-Type: application/json" \
  -d '{"instanceName": "assistente", "qrcode": true}'

# Ver QR Code para conectar o WhatsApp
curl https://sua-evolution.com/instance/connect/assistente \
  -H "apikey: SUA_CHAVE"
```

### Configurar Webhook
```bash
curl -X POST https://sua-evolution.com/webhook/set/assistente \
  -H "apikey: SUA_CHAVE" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://sua-api.onrender.com/webhook/",
    "webhook_by_events": false,
    "events": ["MESSAGES_UPSERT"]
  }'
```

---

## 🖥️ Execução Local

### Pré-requisitos
- Python 3.11+
- Conta Firebase com Firestore configurado
- (Opcional) Evolution API para testar envio de mensagens

### Passo a passo

```bash
# 1. Clone o repositório
git clone https://github.com/seu-usuario/assistente-financeira-whatsapp.git
cd assistente-financeira-whatsapp/backend

# 2. Crie o ambiente virtual
python -m venv venv
source venv/bin/activate        # Linux/Mac
# venv\Scripts\activate         # Windows

# 3. Instale as dependências
pip install -r requirements.txt

# 4. Configure as variáveis de ambiente
cp .env.example .env
# Edite o .env com suas credenciais

# 5. Coloque o firebase-credentials.json em config/

# 6. Inicie o servidor
uvicorn app:app --reload --port 8000
```

O servidor estará disponível em `http://localhost:8000`
Documentação Swagger em `http://localhost:8000/docs`

### Testar localmente com ngrok
```bash
# Instale ngrok: https://ngrok.com
ngrok http 8000

# Use a URL gerada (ex: https://abc123.ngrok.io) como webhook na Evolution API
```

### Simular mensagem (sem WhatsApp)
```bash
curl -X POST http://localhost:8000/webhook/ \
  -H "Content-Type: application/json" \
  -d '{
    "event": "messages.upsert",
    "data": {
      "key": {"remoteJid": "5511999999999@s.whatsapp.net", "fromMe": false},
      "pushName": "Teste",
      "message": {"conversation": "Gastei 50 reais com almoço"}
    }
  }'
```

---

## 🚀 Deploy no Render (grátis)

### Pré-requisitos
- Conta no [Render.com](https://render.com)
- Repositório no GitHub

### Passo a passo

1. **Suba o código para o GitHub**
   ```bash
   git init
   echo "config/firebase-credentials.json" >> .gitignore
   echo ".env" >> .gitignore
   git add .
   git commit -m "feat: assistente financeira inicial"
   git remote add origin https://github.com/seu-usuario/seu-repo.git
   git push -u origin main
   ```

2. **No Render:** New → Web Service → conecte seu repositório GitHub

3. **Configurações:**
   - **Root Directory:** `backend`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn app:app --host 0.0.0.0 --port $PORT`

4. **Variáveis de ambiente** (aba Environment):
   - `FIREBASE_PROJECT_ID` → ID do seu projeto Firebase
   - `EVOLUTION_API_URL` → URL da sua Evolution API
   - `EVOLUTION_API_KEY` → Chave da Evolution API
   - `EVOLUTION_INSTANCE_NAME` → Nome da instância (ex: `assistente`)

5. **Credenciais Firebase:**
   O arquivo JSON não pode ir pro Git. Use uma das opções:
   - **Opção A:** Encode em Base64 e use variável de ambiente `FIREBASE_CREDENTIALS_BASE64`
   - **Opção B:** Use o Render Disk (plano pago) para montar o arquivo
   - **Opção C:** Use Firebase Authentication com Workload Identity (avançado)

6. Clique em **Deploy** e aguarde. Sua URL será algo como:  
   `https://assistente-financeira-whatsapp.onrender.com`

7. Configure essa URL como webhook na Evolution API (veja seção acima)

---

## 💬 Exemplos de Uso

| Você escreve | Assistente responde |
|---|---|
| `Gastei 25 reais com almoço` | ✅ Gasto registrado: Alimentação R$ 25,00 |
| `Paguei 120 de internet` | ✅ Gasto registrado: Moradia R$ 120,00 |
| `Uber 18 reais` | ✅ Gasto registrado: Transporte R$ 18,00 |
| `Recebi 1500 de salário` | ✅ Receita registrada: Salário R$ 1.500,00 |
| `Quanto gastei este mês?` | 💸 Você gastou R$ 163,00 este mês |
| `Resumo financeiro` | 📊 Resumo completo com categorias |
| `ajuda` | 👋 Lista de comandos disponíveis |

---

## 🔮 Funcionalidades Futuras

- [ ] Gráficos financeiros (matplotlib / Chart.js)
- [ ] Metas de economia mensais
- [ ] Controle de dívidas e parcelamentos
- [ ] Exportação em PDF e Excel
- [ ] Dashboard Web (React/Next.js)
- [ ] Integração bancária (Open Finance)
- [ ] Alertas de gastos excessivos
- [ ] Planejamento financeiro mensal
- [ ] Controle de assinaturas
- [ ] NLP avançado com OpenAI GPT

---

## 🧱 Tecnologias

| Tecnologia | Uso |
|---|---|
| FastAPI | Framework web assíncrono |
| Firebase Firestore | Banco de dados NoSQL |
| Evolution API | Integração WhatsApp |
| Pydantic v2 | Validação e tipagem |
| httpx | Cliente HTTP assíncrono |
| Render | Deploy gratuito |
