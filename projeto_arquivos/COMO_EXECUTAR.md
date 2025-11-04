# 🖥️ OPÇÕES DE EXECUÇÃO DO SISTEMA

## 🎯 Após a instalação, você terá 4 formas de iniciar o sistema:

### 1️⃣ **executar_sistema.bat** (Janela Normal)
```
✅ Mostra logs e status
✅ Abre navegador automaticamente
❌ Janela precisa ficar aberta
```

**Como usar:**
- Duplo-clique no arquivo
- Janela do terminal abre mostrando logs
- Navegador abre automaticamente
- **Para parar**: Feche a janela ou Ctrl+C

**Ideal para:**
- Primeira vez usando o sistema
- Quando quer ver os logs
- Desenvolvimento/teste

---

### 2️⃣ **executar_minimizado.bat** (Janela Minimizada)
```
✅ Roda em segundo plano (minimizado)
✅ Abre navegador automaticamente
✅ Janela some da vista
⚠️ Ainda pode ver na barra de tarefas
```

**Como usar:**
- Duplo-clique no arquivo
- Janela inicia minimizada
- Navegador abre automaticamente
- **Para parar**: Procure janela minimizada ou use `parar_sistema.bat`

**Ideal para:**
- Uso diário
- Quando não quer ver o terminal
- Sistema rodando "discretamente"

---

### 3️⃣ **iniciar_oculto.vbs** (Totalmente Oculto) ⭐ **RECOMENDADO**
```
✅ Sem janela alguma
✅ Roda em segundo plano total
✅ Abre navegador automaticamente
✅ Experiência mais limpa
```

**Como usar:**
- Duplo-clique no arquivo .vbs
- Nenhuma janela aparece
- Navegador abre em 3 segundos
- **Para parar**: Execute `parar_sistema.bat`

**Ideal para:**
- Uso profissional
- Quando quer experiência mais limpa
- Sistema rodando "invisível"

---

### 4️⃣ **parar_sistema.bat** (Para o Sistema)
```
✅ Para todos os processos Python
✅ Fecha o servidor Flask
✅ Fácil de usar
```

**Como usar:**
- Duplo-clique no arquivo
- Confirma que o sistema foi parado
- Pronto!

**Quando usar:**
- Após usar `iniciar_oculto.vbs`
- Quando não encontra a janela minimizada
- Para garantir que tudo foi fechado

---

## 📊 COMPARAÇÃO

| Método | Janela Visível | Navegador Abre | Facilidade para Parar | Recomendado para |
|--------|---------------|----------------|----------------------|------------------|
| **executar_sistema.bat** | ✅ Sim (normal) | ✅ Sim | ⭐⭐⭐ Muito fácil | Primeira vez |
| **executar_minimizado.bat** | ⚠️ Minimizada | ✅ Sim | ⭐⭐ Fácil | Uso ocasional |
| **iniciar_oculto.vbs** | ❌ Não | ✅ Sim | ⭐ Precisa do .bat | Uso diário |

---

## 🎯 RECOMENDAÇÃO DE USO

### Para usuários iniciantes:
```
1. Use: executar_sistema.bat
   - Você vê o que está acontecendo
   - Fácil de parar (só fechar)
   
2. Quando se acostumar:
   - Mude para: iniciar_oculto.vbs
   - Use: parar_sistema.bat para encerrar
```

### Para usuários avançados:
```
1. Use sempre: iniciar_oculto.vbs
   - Experiência mais limpa
   - Sistema roda como "serviço"
   
2. Para parar: parar_sistema.bat
   - Ou Gerenciador de Tarefas
```

---

## 💡 DICAS

### Criar atalho com ícone personalizado:
1. Clique direito em `iniciar_oculto.vbs`
2. Criar atalho
3. Clique direito no atalho > Propriedades
4. Alterar ícone
5. Mova o atalho para área de trabalho

### Iniciar automaticamente com Windows:
1. Pressione `Win + R`
2. Digite: `shell:startup`
3. Copie o atalho de `iniciar_oculto.vbs` para lá
4. Sistema inicia automaticamente ao ligar o PC!

### Verificar se está rodando:
```
1. Abra: http://localhost:5000
   - Se carregar = está rodando
   - Se não carregar = não está rodando

2. Ou abra Gerenciador de Tarefas
   - Procure por "python.exe"
```

---

## ⚙️ CONFIGURAÇÕES AVANÇADAS

### Alterar a porta (padrão: 5000):
1. Edite o arquivo `app_producao.py`
2. Procure por: `port=5000`
3. Altere para a porta desejada
4. Salve e reinicie o sistema

### Executar em rede local:
O sistema já aceita conexões de outros computadores!
- Descubra seu IP: `ipconfig`
- Outros computadores acessam: `http://SEU-IP:5000`

---

## ❓ PERGUNTAS FREQUENTES

**P: Posso fechar o navegador e o sistema continua rodando?**
R: ✅ SIM! O navegador é só o "visualizador". O sistema continua rodando em segundo plano.

**P: Como sei se o sistema está rodando?**
R: Abra `http://localhost:5000` no navegador. Se carregar, está rodando!

**P: Posso usar múltiplas abas do navegador?**
R: ✅ SIM! Quantas quiser, todas funcionarão.

**P: O que acontece se reiniciar o computador?**
R: O sistema para. Você precisa executá-lo novamente (ou configurar inicialização automática).

**P: Consome muitos recursos?**
R: ❌ NÃO! Python + Flask são leves. ~50-100MB de RAM.

**P: Posso usar enquanto faço outras coisas?**
R: ✅ SIM! O sistema roda em segundo plano e não interfere em nada.

---

## 🎉 RESUMO RÁPIDO

Para o **melhor uso diário**:

1. **Iniciar**: Duplo-clique em `iniciar_oculto.vbs`
2. **Usar**: Navegador abre automaticamente em http://localhost:5000
3. **Parar**: Duplo-clique em `parar_sistema.bat`

**É simples assim! 🚀**

---

**Atualizado em:** 4 de novembro de 2025  
**Versão:** 2.0  
**Autor:** Sistema de Gestão de Projetos
