
import streamlit as st
import pandas as pd
from geopy.geocoders import Nominatim
import requests

st.set_page_config(page_title="Simulador de Usina Solar - Tesla Energia", layout="centered")
st.image("logo.png", width=250)
st.title("Simulador de Usina Solar")
st.subheader("Preencha os dados abaixo para obter a estimativa da potência da sua usina.")

st.markdown("---")

# Carregar base de equipamentos
@st.cache_data
def carregar_equipamentos():
    dados = {
        "Equipamento": [
            "ASPIRADOR DE PÓ COMERCIAL", "ASPIRADOR DE PÓ RESIDENCIAL", "BALANÇA ELÉTRICA",
            "BALCÃO FRIGORÍFICO GRANDE", "CÂMARA FRIGORÍFICA", "AR-CONDICIONADO 12000 BTU's",
            "CHUVEIRO ELÉTRICO", "GELADEIRA COMUM 280 L", "TELEVISOR 28 A 30 POL",
            "MÁQUINA DE LAVAR ROUPAS"
        ],
        "Potência_kW": [1.0, 0.75, 0.02, 1.0, 22.08, 1.7, 4.0, 0.1, 0.15, 2.0]
    }
    return pd.DataFrame(dados)

equipamentos_df = carregar_equipamentos()

# Dados do cliente
with st.form("formulario"):
    nome = st.text_input("Nome completo")
    email = st.text_input("E-mail")
    whatsapp = st.text_input("WhatsApp (com DDD)")
    endereco = st.text_input("Endereço completo (incluindo cidade e estado)")
    cep = st.text_input("CEP")

    st.markdown("### Consumo mensal (em kWh)")
    meses = ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
             "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]
    consumos = [st.number_input(f"{mes}", min_value=0.0, step=0.1, key=mes) for mes in meses]

    st.markdown("### Carga adicional futura (opcional)")
    adicionar_carga = st.checkbox("Deseja incluir uma carga futura?")
    carga_kwh_anual = 0
    if adicionar_carga:
        equipamento = st.selectbox("Selecione o equipamento", equipamentos_df["Equipamento"])
        potencia_kW = equipamentos_df[equipamentos_df["Equipamento"] == equipamento]["Potência_kW"].values[0]
        st.markdown(f"**Potência estimada:** {potencia_kW:.2f} kW")
        horas_dia = st.number_input("Horas de uso por dia", min_value=0.0, step=0.1)
        dias_mes = st.number_input("Dias de uso por mês", min_value=0.0, step=1.0)
        quantidade = st.number_input("Quantidade de equipamentos", min_value=1, step=1)
        carga_kwh_anual = potencia_kW * horas_dia * dias_mes * 12 * quantidade

    tilt = st.number_input("Inclinação do telhado (Tilt, em graus)", min_value=0.0, max_value=90.0, step=1.0)
    azimute = st.number_input("Orientação do telhado (Azimute, em graus - 0=Norte, 180=Sul)", min_value=0.0, max_value=360.0, step=1.0)

    enviado = st.form_submit_button("Simular e Obter Resultado")

if enviado:
    consumo_anual = sum(consumos) + carga_kwh_anual
    consumo_mensal_medio = consumo_anual / 12
    consumo_diario_medio = consumo_anual / 365

    # Obter coordenadas pelo endereço
    geolocator = Nominatim(user_agent="simulador_solar")
    localizacao = geolocator.geocode(f"{endereco}, {cep}, Brasil")

    if localizacao:
        lat = localizacao.latitude
        lon = localizacao.longitude
        st.markdown(f"📍 Coordenadas detectadas: **{lat:.5f}, {lon:.5f}**")

        try:
            response = requests.get(
                f"https://globalsolaratlas.info/api/pvout?lat={lat}&lon={lon}&tilt={tilt}&azimuth={azimute}"
            )
            if response.status_code == 200:
                data = response.json()
                irrad = data.get("irradiance", 4.8)
            else:
                irrad = 4.8
                st.warning("⚠️ Não foi possível consultar a irradiação real. Usaremos valor médio padrão.")
        except:
            irrad = 4.8
            st.warning("⚠️ Não foi possível acessar a API de irradiação. Usaremos valor médio padrão.")
    else:
        lat = lon = None
        irrad = 4.8
        st.warning("⚠️ Não foi possível obter as coordenadas com base no endereço informado. Usaremos irradiação média padrão.")

    pr_75 = consumo_diario_medio / (0.75 * irrad)
    pr_85 = consumo_diario_medio / (0.85 * irrad)

    st.markdown("---")
    st.success(f"Simulação para {nome}")

    st.markdown(f"**Consumo Médio Mensal:** {consumo_mensal_medio:.2f} kWh")
    st.markdown(f"**Consumo Diário Médio:** {consumo_diario_medio:.2f} kWh")
    st.markdown(f"**Potência estimada da usina:**")
    st.markdown(f"- PR 75% (mais conservador): **{pr_75:.2f} kWp**")
    st.markdown(f"- PR 85% (otimizado): **{pr_85:.2f} kWp**")

    st.markdown(f"**Inclinação informada:** {tilt:.1f}° | **Azimute informado:** {azimute:.1f}°")

    st.info("Em breve, nossa equipe entrará em contato com sua proposta personalizada!")
