
# Gerenciador PDF

Bem-vindo ao **Gerenciador PDF**, o aplicativo que vai transformar a forma como você organiza e manipula arquivos PDF!

Se você já cansou de:

- Renomear arquivos manualmente
- Dividir arquivos PDF grandes
- Mesclar vários PDFs em um único
- Comprimir arquivos PDF para economizar espaço
então você está no lugar certo!

---

## 📚 O Que Esse App Faz?

O **Gerenciador PDF** é um gerenciador completo e fácil de usar para tarefas em lote com arquivos PDF, oferecendo:

- **Renomeação de arquivos em massa** usando uma lista TXT.
- **Divisão de PDFs** em partes menores automaticamente.
- **Mesclagem de múltiplos PDFs** em um único documento.
- **Compressão de arquivos PDF** usando o Ghostscript para redução de tamanho.
- **Atualização automática**: verifica, baixa e instala novas versões do app!
- **Interface Gráfica Amigável** feita com PyQt6.
- **Nenhuma instalação complicada**: tudo pronto para rodar no Windows.

---

## 🚀 Principais Funcionalidades

- 📂 **Renomeação em Massa:**  
  Selecione vários arquivos e renomeie-os com base em um arquivo `.txt` que você define.

- ✂️ **Dividir PDFs:**  
  Corte arquivos PDF em partes menores, configurando quantas páginas por novo arquivo.

- 🔗 **Mesclar PDFs:**  
  Combine vários documentos PDF em apenas um, mantendo a ordem.

- 📦 **Compressão de PDFs:**  
  Reduza o tamanho dos PDFs usando **Ghostscript**, com presets de qualidade:

  | Preset       | Descrição |
  |:-------------|:----------|
  | screen       | Menor tamanho, qualidade baixa |
  | ebook        | Equilíbrio entre qualidade e tamanho |
  | printer      | Alta qualidade para impressão |
  | prepress     | Qualidade máxima (pré-impressão) |
  | default      | Configurações padrão |

- 🔄 **Atualizador Automático:**  
  Ao abrir, o app pode verificar e instalar automaticamente novas versões, garantindo que você tenha sempre as últimas melhorias!

---

## 🖥 Plataforma Windows

Se você estiver no **Windows**, pode executar o aplicativo diretamente via instalador — **não é necessário instalar Python**.  Basta executar o GerenciadorPDF-Setup.exe, baise ele através do link: [GerenciadorPDF-Setup.exe](https://github.com/rodineyw/gerenciador_pdf/releases/latest/download/GerenciadorPDF-Setup.exe)
Para desenvolvedores, também é possível rodar diretamente o código fonte.

---

## 🛠 Como Usar (Desenvolvedores)

1. **Clone o Repositório:**

   ```bash
   git clone https://github.com/rodineyw/gerenciador_pdf.git
   ```

2. **Instale o Python 3.10 ou superior** (se ainda não tiver).

3. **Instale as dependências necessárias:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Rode o Aplicativo:**

   ```bash
   python app/main.py
   ```

5. **Aproveite a Interface Gráfica:**
   - Selecione arquivos PDF.
   - Escolha ações como renomear, dividir, mesclar ou comprimir.
   - Use o botão "Verificar Atualizações" para sempre estar na última versão!

---

## 🤝 Contribuições

Contribuições são muito bem-vindas!  
Se quiser colaborar:

1. **Fork este repositório.**
2. **Crie uma branch de funcionalidade:**

   ```bash
   git checkout -b feature/nova-funcionalidade
   ```

3. **Commit suas mudanças:**

   ```bash
   git commit -m 'Adicionando nova funcionalidade'
   ```

4. **Push para o seu repositório:**

   ```bash
   git push origin feature/nova-funcionalidade
   ```

5. **Abra um Pull Request.**

---

## 📜 Licença

Este projeto está sob a licença MIT — use como quiser, respeitando os termos.  
Veja o arquivo LICENSE para mais detalhes.

---

## ✨ Autor

Desenvolvido com ❤️ por [Ródiney Wanderson](https://github.com/rodineyw).  
Siga-me no [LinkedIn](https://www.linkedin.com/in/rodineyw/) para mais projetos incríveis!

---
