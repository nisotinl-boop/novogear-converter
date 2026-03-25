import streamlit as st
import pandas as pd
import re
import io

st.title("🚀 NovoGear: Convertidor para Shopify")

# IVA Países Bajos (21%)
iva = 1.21

archivo = st.file_uploader("Sube el Excel de tu proveedor", type=['xlsx', 'csv'])

if archivo is not None:
    try:
        # 1. Leer archivo
        if archivo.name.endswith('.xlsx'):
            df = pd.read_excel(archivo)
        else:
            df = pd.read_csv(archivo, sep=None, engine='python')
        
        # Limpiar espacios en los nombres de las columnas
        df.columns = df.columns.str.strip()

        def calcular_precio(coste):
            try:
                valor = str(coste).replace(',', '.')
                precio_con_margen = float(valor) * 1.30
                return round(precio_con_margen * iva, 2)
            except: 
                return 0.0

        # 2. Crear el archivo EXACTO para Shopify
        shopify = pd.DataFrame()
        
        # Shopify necesita estas columnas con estos nombres exactos
        shopify['Handle'] = df['Description'].astype(str).str.lower().apply(lambda x: re.sub(r'[^a-z0-9]+', '-', x).strip('-'))
        shopify['Title'] = df['Description']
        shopify['Body (HTML)'] = df['Description']
        shopify['Vendor'] = 'NovoGear'
        shopify['Published'] = 'true'
        shopify['Variant Price'] = df['Reseller price'].apply(calcular_precio)
        shopify['Variant SKU'] = df['Manu.nr']
        shopify['Variant Inventory Qty'] = df['Stock']
        shopify['Variant Inventory Policy'] = 'deny'
        shopify['Variant Fulfillment Service'] = 'manual'
        shopify['Status'] = 'active'

        st.success("✅ ¡Archivo convertido con éxito!")
        
        # 3. TRUCO FINAL: Forzar formato CSV estándar (con comas)
        towrite = io.BytesIO()
        shopify.to_csv(towrite, index=False, encoding='utf-8', sep=',') # Forzamos la coma
        towrite.seek(0)
        
        st.download_button(
            label="📥 Descargar para Shopify",
            data=towrite,
            file_name="productos_novogear.csv",
            mime="text/csv"
        )
        
    except Exception as e:
        st.error(f"Error: Asegúrate de que las columnas se llamen 'Description', 'Reseller price', 'Manu.nr' y 'Stock'.")
