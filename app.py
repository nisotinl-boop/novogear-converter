import streamlit as st
import pandas as pd
import re

st.title("🚀 NovoGear: Convertidor para Shopify")

iva = 1.21

archivo = st.file_uploader("Sube el Excel de tu proveedor", type=['xlsx', 'csv'])

if archivo is not None:
    try:
        if archivo.name.endswith('.xlsx'):
            df = pd.read_excel(archivo)
        else:
            df = pd.read_csv(archivo, sep=None, engine='python')
        
        def calcular_precio(coste):
            try:
                precio_con_margen = float(str(coste).replace(',', '.')) * 1.30
                return round(precio_con_margen * iva, 2)
            except: 
                return 0.0

        # Crear el formato EXACTO de Shopify
        shopify = pd.DataFrame()
        shopify['Handle'] = df['Description'].astype(str).str.lower().apply(lambda x: re.sub(r'[^a-z0-9]+', '-', x).strip('-'))
        shopify['Title'] = df['Description']
        shopify['Body (HTML)'] = df['Description'] # Ponemos la descripción también como cuerpo
        shopify['Vendor'] = 'NovoGear'
        shopify['Command'] = 'NEW' # Ayuda a Shopify a saber que es nuevo
        shopify['Variant Price'] = df['Reseller price'].apply(calcular_precio)
        shopify['Variant SKU'] = df['Manu.nr']
        shopify['Variant Inventory Qty'] = df['Stock']
        shopify['Variant Inventory Policy'] = 'deny'
        shopify['Variant Fulfillment Service'] = 'manual'
        shopify['Status'] = 'active'

        st.success("✅ ¡Archivo procesado! Shopify ya no debería dar error.")
        
        # Exportar a CSV (Shopify prefiere comas ,)
        csv = shopify.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Descargar para Shopify", data=csv, file_name="productos_novogear.csv")
        
    except Exception as e:
        st.error(f"Error: Asegúrate de que el Excel tenga las columnas 'Description', 'Reseller price', 'Manu.nr' y 'Stock'.")
