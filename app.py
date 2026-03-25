import streamlit as st
import pandas as pd
import re

st.title("🚀 NovoGear: Convertidor para Shopify")

# IVA Países Bajos (21%)
iva = 1.21

archivo = st.file_uploader("Sube el Excel de tu proveedor", type=['xlsx', 'csv'])

if archivo is not None:
    try:
        df = pd.read_excel(archivo) if archivo.name.endswith('.xlsx') else pd.read_csv(archivo)
        
        def calcular_precio(coste):
            try:
                # Margen del 30% + IVA
                return round((float(coste) * 1.30) * iva, 2)
            except: return 0.0

        shopify = pd.DataFrame()
        shopify['Handle'] = df['Description'].str.lower().apply(lambda x: re.sub(r'[^a-z0-9]+', '-', str(x)).strip('-'))
        shopify['Title'] = df['Description']
        shopify['Variant Price'] = df['Reseller price'].apply(calcular_precio)
        shopify['Variant SKU'] = df['Manu.nr']
        shopify['Variant Inventory Qty'] = df['Stock']
        
        st.success("✅ ¡Listo para descargar!")
        csv = shopify.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Descargar para Shopify", data=csv, file_name="novogear_shop.csv")
    except Exception as e:
        st.error("Sube un archivo válido de proveedor.")
