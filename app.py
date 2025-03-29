import streamlit as st
import pandas as pd

st.set_page_config(page_title="Simulador de Usina Solar - Tesla Energia", layout="centered")
st.image("logo.png", width=250)
st.title("Simulador de Usina Solar")
st.subheader("Preencha os dados abaixo para obter a estimativa da potência da sua usina.")

st.markdown("---")

# Dados do cliente
with st.form("formulario"):
    nome = st.text_input("Nome completo")
    email = st.text_input("E-mail")
    whatsapp = st.text_input("WhatsApp (com DDD)")
    cidade = st.text_input("Cidade/UF da instalação")

    st.markdown("### Consumo mensal (em kWh)")
    meses = ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
             "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]
    consumos = [st.number_input(f"{mes}", min_value=0.0, step=0.1, key=mes) for mes in meses]

    st.markdown("### Carga adicional futura (opcional)")
    adicionar_carga = st.checkbox("Deseja incluir uma carga futura?")
    carga_kwh_anual = 0
    if adicionar_carga:
        tipo = st.text_input("Tipo de carga (ex: Ar-condicionado 12000 BTUs)")
        potencia = st.number_input("Potência da carga (Watts)", min_value=0.0, step=0.1)
        horas_dia = st.number_input("Horas de uso por dia", min_value=0.0, step=0.1)
        dias_mes = st.number_input("Dias de uso por mês", min_value=0.0, step=1.0)
        quantidade = st.number_input("Quantidade de equipamentos", min_value=1, step=1)
        carga_kwh_anual = (potencia * horas_dia * dias_mes * 12 * quantidade) / 1000

    enviado = st.form_submit_button("Simular e Obter Resultado")

if enviado:
    consumo_anual = sum(consumos) + carga_kwh_anual
    consumo_mensal_medio = consumo_anual / 12
    consumo_diario_medio = consumo_anual / 365

    # Irradiação estimada (valor médio Brasil, ex: 4.8 kWh/m².dia)
    # Futuramente: puxar da planilha por cidade
    irrad = 4.8

    pr_75 = consumo_diario_medio / (0.75 * irrad)
    pr_85 = consumo_diario_medio / (0.85 * irrad)

    st.markdown("---")
    st.success(f"Simulação para {nome}")

    st.markdown(f"**Consumo Médio Mensal:** {consumo_mensal_medio:.2f} kWh")
    st.markdown(f"**Consumo Diário Médio:** {consumo_diario_medio:.2f} kWh")
    st.markdown(f"**Potência estimada da usina:**")
    st.markdown(f"- PR 75%: **{pr_75:.2f} kWp**")
    st.markdown(f"- PR 85%: **{pr_85:.2f} kWp**")

    st.info("Em breve, nossa equipe entrará em contato com sua proposta personalizada!")
