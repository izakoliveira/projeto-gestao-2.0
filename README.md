# Projeto de Gestão de Projetos com Gantt

## Passo a Passo para rodar, editar e publicar no GitHub

### 1. Clonar ou baixar o projeto
Se já está no seu computador, pule para o próximo passo. Para clonar:
```sh
git clone https://github.com/SEU_USUARIO/SEU_REPOSITORIO.git
```

### 2. Instalar dependências
Crie e ative um ambiente virtual (opcional, mas recomendado):
```sh
python -m venv env
./env/Scripts/activate  # Windows
source env/bin/activate  # Linux/Mac
```
Instale as dependências:
```sh
pip install -r requirements.txt
```

### 3. Configurar variáveis de ambiente
Copie o arquivo `env_example.txt` para `.env` e ajuste as variáveis conforme necessário.

### 4. Rodar o projeto localmente
```sh
python app.py
```
Acesse no navegador: [http://localhost:5000](http://localhost:5000)

### 5. Editar o projeto
- Edite os arquivos Python, HTML (templates), CSS e JS conforme necessário.
- Para atualizar o gráfico de Gantt, edite o arquivo `templates/projetos_gantt_basico.html`.

### 6. Salvar e versionar alterações com Git
```sh
git add .
git commit -m "Descreva sua alteração aqui"
```

### 7. Publicar no GitHub
```sh
git push origin main
```

### 8. Dicas para Windows
- Se aparecer erro de "safe.directory", rode:
  ```sh
  git config --global --add safe.directory 'D:/projeto-gestao - Copia'
  ```
- Se aparecer erro de conexão, verifique sua internet, firewall, proxy ou tente em outra rede.
- Sempre rode apenas o comando (sem o prompt `PS ...>` na frente).

### 9. Outras dicas
- Para criar um novo repositório, faça isso pelo site do GitHub e depois conecte com `git remote add origin ...`.
- Para trocar o remoto:
  ```sh
  git remote set-url origin https://github.com/SEU_USUARIO/SEU_REPOSITORIO.git
  ```
- Para ver o endereço remoto:
  ```sh
  git remote -v
  ```

---

Se tiver dúvidas, consulte este README ou peça ajuda! :)
