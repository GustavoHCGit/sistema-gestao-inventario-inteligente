# 📦 Sistema de Gestão de Inventário Inteligente

Este é um sistema robusto de gestão de inventário e vendas desenvolvido para pequenas e médias empresas. O projeto utiliza **Python** com a biblioteca **Streamlit** para a interface de utilizador e **SQLite** para o armazenamento persistente de dados.

## 🔗 Demo ao Vivo

Você pode testar a aplicação diretamente no seu navegador através do link abaixo:

👉 **[Clique aqui para acessar a Demo](https://sistema-gestao-inventario.streamlit.app/)**

## 🚀 Funcionalidades

- **Dashboard Interativo**: Visualize métricas em tempo real, como faturamento total, número de produtos e vendas realizadas.
- **Gestão de Estoque**: Adicione, visualize e controle a quantidade de produtos disponíveis.
- **Categorização**: Organize os seus produtos por categorias para uma melhor gestão.
- **Registro de Vendas**: Registe vendas de forma rápida, com verificação automática de stock.
- **Visualização de Dados**: Gráficos dinâmicos (Pie e Bar charts) utilizando Plotly para análise de stock por categoria e desempenho de vendas por produto.

## 📸 Demonstração Visual

**Tela 1 - Dashboard com Métricas Principais:**
![Dashboard com Métricas](dashboard_screenshot_1.webp)

**Tela 2 - Gerenciamento de Produtos:**
![Gerenciamento de Produtos](dashboard_screenshot_2.webp)

**Tela 3 - Registro de Vendas:**
![Registro de Vendas](dashboard_screenshot_3.webp)

## 🛠️ Tecnologias Utilizadas

- [Python](https://www.python.org/)
- [Streamlit](https://streamlit.io/)
- [Pandas](https://pandas.pydata.org/)
- [Plotly](https://plotly.com/)
- [SQLite](https://www.sqlite.org/)

## 📋 Pré-requisitos

Certifique-se de ter o Python instalado na sua máquina. Para instalar as dependências necessárias, execute:

```bash
pip install streamlit pandas plotly
```

## 🔧 Como Executar Localmente

1. Clone o repositório:

```bash
git clone https://github.com/GustavoHCGit/sistema-gestao-inventario-inteligente.git
cd sistema-gestao-inventario-inteligente
```

2. Instale as dependências:

```bash
pip install -r requirements.txt
```

3. Popule o banco de dados com dados de exemplo:

```bash
python seed_data.py
```

4. Execute a aplicação:

```bash
streamlit run main.py
```

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

---
Desenvolvido por [Gustavo Henrique Constante Neto](https://github.com/GustavoHCGit)
