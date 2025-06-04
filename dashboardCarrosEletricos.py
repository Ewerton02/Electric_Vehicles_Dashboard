import streamlit as st
import pandas as pd
import plotly.express as px

st.title("Dashboard - Mercado de Veículos Elétricos")

arquivo = st.file_uploader("Faça o upload do arquivo CSV", type="csv")

if arquivo:
    try:
        df = pd.read_csv(arquivo)

        df = df.dropna(subset=["region", "parameter", "powertrain", "year", "value", "unit"])

        st.success("Dados carregados com sucesso!")
        st.dataframe(df.head())

        regioes = df["region"].dropna().unique()
        parametros = df["parameter"].dropna().unique()
        motores = df["powertrain"].dropna().unique()

        regiao_selecionada = st.selectbox("Escolha a região", sorted(regioes))
        parametro_selecionado = st.selectbox("Escolha o parâmetro", sorted(parametros))
        motor_selecionado = st.selectbox("Escolha o tipo de motor", sorted(motores))

        anos = sorted(df["year"].dropna().unique())
        ano_min, ano_max = int(min(anos)), int(max(anos))
        intervalo_anos = st.slider(
            "Selecione o intervalo de anos",
            min_value=ano_min,
            max_value=ano_max,
            value=(ano_min, ano_max)
        )

        df_filtrado = df[
            (df["region"] == regiao_selecionada) &
            (df["parameter"] == parametro_selecionado) &
            (df["powertrain"] == motor_selecionado) &
            (df["year"] >= intervalo_anos[0]) &
            (df["year"] <= intervalo_anos[1])
        ]

        if not df_filtrado.empty:
            valor_total = df_filtrado["value"].sum()
            media_anual = df_filtrado.groupby("year")["value"].sum().mean()

            if df_filtrado["value"].notna().any():
                ano_pico = df_filtrado.loc[df_filtrado["value"].idxmax()]["year"]
                valor_pico = df_filtrado["value"].max()
            else:
                ano_pico = "N/A"
                valor_pico = 0

            unidade = df_filtrado["unit"].dropna().iloc[0] if not df_filtrado["unit"].dropna().empty else ""

            col1, col2, col3 = st.columns(3)
            col1.metric("Total no Período", f"{valor_total:,.0f} {unidade}")
            col2.metric("Média Anual", f"{media_anual:,.2f} {unidade}")
            col3.metric("Pico no Ano", f"{ano_pico}", f"{valor_pico:,.0f}")

            fig = px.line(
                df_filtrado,
                x="year",
                y="value",
                title=f"{parametro_selecionado} em {regiao_selecionada} ({motor_selecionado})",
                markers=True
            )
            fig.update_layout(xaxis_title="Ano", yaxis_title=unidade)
            st.plotly_chart(fig)
        else:
            st.warning("Nenhum dado encontrado para os filtros selecionados.")

    except Exception as e:
        st.error(f"Ocorreu um erro ao processar o arquivo: {e}")
