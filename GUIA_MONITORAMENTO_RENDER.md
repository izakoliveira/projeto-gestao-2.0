# 📊 Guia de Monitoramento - Render Deploy

## 🔍 Como Monitorar seu Deploy no Render

### 1. 📱 Acesso ao Dashboard
1. Vá para [dashboard.render.com](https://dashboard.render.com)
2. Faça login na sua conta
3. Encontre seu serviço "projeto-gestao-2-0"

### 2. 🕵️ Verificar Status do Deploy

#### Status do Serviço:
- ✅ **Live** - Funcionando
- 🔄 **Building** - Construindo
- ❌ **Build failed** - Falhou no build
- ⚠️ **Deploy failed** - Falhou no deploy

#### Logs em Tempo Real:
1. Clique no seu serviço
2. Vá na aba **"Logs"**
3. Logs aparecem em tempo real

### 3. 🔍 O que Procurar nos Logs

#### ✅ Sinais de Sucesso:
```
✅ Blueprints registrados com sucesso!
✅ Config carregado com sucesso
Conectado com sucesso ao Supabase!
🚀 Iniciando aplicação de produção...
```

#### ❌ Sinais de Problema:
```
ModuleNotFoundError: No module named 'xxx'
ImportError: cannot import name 'xxx'
Connection refused
Database connection failed
```

### 4. 🌐 URLs para Testar

Após o deploy, teste estas URLs:

```
https://seu-app.onrender.com/health
https://seu-app.onrender.com/status  
https://seu-app.onrender.com/
https://seu-app.onrender.com/login
```

### 5. 🛠️ Como Usar o Monitor Local

Execute este comando para monitorar:

```bash
python monitor_render.py
```

Digite a URL do seu app quando solicitado.

### 6. 📊 Interpretando Resultados

#### Health Check Esperado:
```json
{
  "status": "healthy",
  "version": "2.0.0",
  "database": "healthy",
  "blueprints": ["auth", "projetos", "tarefas", "admin", "pastas", "main", "producao", "relatorio"],
  "platform": "render"
}
```

#### Status Esperado:
```json
{
  "status": "operational",
  "version": "2.0.0",
  "environment": "production",
  "blueprints": [...8 blueprints...],
  "config": {...}
}
```

### 7. 🚨 Problemas Comuns e Soluções

#### Problema: Build Failed
**Logs mostram:** `No module named 'xxx'`
**Solução:** Dependência faltando no requirements_producao.txt

#### Problema: App Crashed  
**Logs mostram:** `ImportError` ou `Configuration error`
**Solução:** Verificar variáveis de ambiente no Render

#### Problema: Health Check Failed
**Logs mostram:** App inicia mas /health não responde
**Solução:** Verificar se a rota /health existe

#### Problema: Database Error
**Logs mostram:** `Database connection failed`
**Solução:** Verificar SUPABASE_URL e SUPABASE_KEY

### 8. 📞 Debug em Tempo Real

Use este comando para debug contínuo:

```bash
python monitor_render.py
# Escolha opção 2 para monitoramento contínuo
```

### 9. 🔧 Variáveis de Ambiente no Render

Verifique se estão configuradas:

1. **SECRET_KEY** ✅ (gerada automaticamente)
2. **SUPABASE_URL** ✅ (configurada no render.yaml)
3. **SUPABASE_KEY** ✅ (configurada no render.yaml)
4. **FLASK_ENV=production** ✅
5. **PORT** (automática do Render)

### 10. 📈 Métricas do Render

No dashboard, monitore:
- **CPU Usage**
- **Memory Usage** 
- **Request Count**
- **Response Time**

---

## 🎯 Checklist de Monitoramento

- [ ] Deploy iniciou sem erros
- [ ] Build completou com sucesso  
- [ ] App iniciou (logs mostram "✅ Blueprints registrados")
- [ ] Health check responde 200
- [ ] Status responde 200
- [ ] Página principal redireciona (302)
- [ ] Supabase conectado
- [ ] 8 blueprints carregados

## 📞 Próximos Passos

1. **Execute:** `python monitor_render.py`
2. **Insira:** URL do seu app no Render
3. **Monitore:** Logs em tempo real
4. **Compare:** Resultados com o diagnóstico local

**🔍 Vamos acompanhar juntos!**