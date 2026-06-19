import streamlit as st
import pandas as pd
import database
import plotly.express as px

# Configuração da página
st.set_page_config(page_title="Gestor de Inventário Inteligente", layout="wide")

st.title("📦 Sistema de Gestão de Inventário e Vendas")
st.markdown("""
**Análise de Dados**.
O sistema permite gerenciar produtos, registrar vendas e visualizar métricas de desempenho.
""")

# Sidebar para navegação
menu = ["Dashboard", "Produtos", "Vendas", "Configurações"]
choice = st.sidebar.selectbox("Menu", menu)

if choice == "Dashboard":
    st.subheader("📊 Visão Geral do Negócio")
    
    # Carregar dados
    products_data = database.get_products()
    df_products = pd.DataFrame(products_data, columns=["ID", "Produto", "Categoria", "Preço", "Estoque"])
    
    sales_data = database.get_sales_report()
    df_sales = pd.DataFrame(sales_data, columns=["ID", "Produto", "Qtd", "Total", "Data"])
    
    # Métricas Principais
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total de Produtos", len(df_products))
    with col2:
        total_vendas = df_sales["Total"].sum() if not df_sales.empty else 0
        st.metric("Faturamento Total", f"R$ {total_vendas:,.2f}")
    with col3:
        st.metric("Vendas Realizadas", len(df_sales))

    # Gráficos
    st.markdown("---")
    c1, c2 = st.columns(2)
    
    with c1:
        st.write("### Estoque por Categoria")
        if not df_products.empty:
            fig_stock = px.pie(df_products, values='Estoque', names='Categoria', hole=.3)
            st.plotly_chart(fig_stock, use_container_width=True)
        else:
            st.info("Nenhum produto cadastrado.")
        
    with c2:
        st.write("### Vendas por Produto")
        if not df_sales.empty:
            df_sales_agg = df_sales.groupby("Produto")["Total"].sum().reset_index()
            fig_sales = px.bar(df_sales_agg, x='Produto', y='Total', color='Total')
            st.plotly_chart(fig_sales, use_container_width=True)
        else:
            st.info("Nenhuma venda registrada ainda.")

elif choice == "Produtos":
    st.subheader("📋 Gerenciamento de Estoque")
    
    # Formulário para adicionar produto
    with st.expander("➕ Adicionar Novo Produto"):
        with st.form("form_add_prod"):
            name = st.text_input("Nome do Produto")
            categories = database.get_categories()
            cat_options = {cat[1]: cat[0] for cat in categories}
            category_name = st.selectbox("Categoria", list(cat_options.keys()) if cat_options else ["Nenhuma"])
            price = st.number_input("Preço Unitário (R$)", min_value=0.0, step=0.01)
            stock = st.number_input("Quantidade em Estoque", min_value=0, step=1)
            
            submit = st.form_submit_button("Salvar Produto")
            if submit:
                if category_name != "Nenhuma":
                    database.add_product(name, cat_options[category_name], price, stock)
                    st.success(f"Produto '{name}' adicionado!")
                    st.rerun()
                else:
                    st.error("Crie uma categoria primeiro!")

    # Listagem de produtos
    products_data = database.get_products()
    df_products = pd.DataFrame(products_data, columns=["ID", "Produto", "Categoria", "Preço", "Estoque"])
    st.dataframe(df_products, use_container_width=True)

elif choice == "Vendas":
    st.subheader("🛒 Registro de Vendas")
    
    # Formulário de venda
    products = database.get_products()
    if products:
        with st.form("form_sale"):
            prod_options = {p[1]: p[0] for p in products}
            product_name = st.selectbox("Selecione o Produto", list(prod_options.keys()))
            quantity = st.number_input("Quantidade", min_value=1, step=1)
            
            submit_sale = st.form_submit_button("Registrar Venda")
            if submit_sale:
                success = database.record_sale(prod_options[product_name], quantity)
                if success:
                    st.success("Venda registrada com sucesso!")
                    st.rerun()
                else:
                    st.error("Estoque insuficiente para esta venda!")
    else:
        st.warning("Cadastre produtos antes de realizar vendas.")

    # Histórico de vendas
    st.write("### Histórico Recente")
    sales_data = database.get_sales_report()
    df_sales = pd.DataFrame(sales_data, columns=["ID", "Produto", "Qtd", "Total", "Data"])
    st.table(df_sales.head(10))

elif choice == "Configurações":
    st.subheader("⚙️ Configurações do Sistema")
    st.write("Gerencie categorias e configurações globais.")
    
    new_cat = st.text_input("Nova Categoria")
    if st.button("Adicionar Categoria"):
        if new_cat:
            database.add_category(new_cat)
            st.success(f"Categoria '{new_cat}' criada!")
            st.rerun()
        else:
            st.warning("Digite um nome para a categoria.")
    
    st.write("### Categorias Existentes")
    categories = database.get_categories()
    for cat in categories:
        st.text(f"- {cat[1]}")
