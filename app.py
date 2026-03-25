import streamlit as st
import pandas as pd
import re

st.title("🚀 NovoGear: Convertidor para Shopify")

# IVA Países Bajos (21%)
iva = 1.21

archivo = st.file_uploader("Sube el Excel de tu proveedor", type=['xlsx', 'csv'])

if archivo is not None:
    try:
        # Leer el archivo
        if archivo.name.endswith('.xlsx'):
            df = pd.read_excel(archivo)
        else:
            df = pd.read_csv(archivo)
        
        def calcular_precio(coste):
            try:
                # Margen del 30% + IVA
                precio_con_margen = float(str(coste).replace(',', '.')) * 1.30
                return round(precio_con_margen * iva, 2)
            except: 
                return 0.0

        # Crear el archivo para Shopify
        shopify = pd.DataFrame()
        
        # Estas son las columnas EXACTAS que Shopify necesita
        shopify['Handle'] = df['Description'].astype(str).str.lower().apply(lambda x: re.sub(r'[^a-z0-9]+', '-', x).strip('-'))
        shopify['Title'] = df['Description']
        shopify['Body (HTML)'] = df['Description']
        shopify['Vendor'] = 'NovoGear'
        shopify['Variant Price'] = df['Reseller price'].apply(calcular_precio)
        shopify['Variant SKU'] = df['Manu.nr']
        shopify['Variant Inventory Qty'] = df['Stock']
        shopify['Variant Inventory Policy'] = 'deny'
        shopify['Variant Fulfillment Service'] = 'manual'
        shopify['Status'] = 'active'
        
        st.success("✅ ¡Archivo procesado con éxito!")
        
        # Generar CSV
        csv = shopify.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Descargar para Shopify", data=csv, file_name="productos_novogear.csv")
        
    except Exception as e:
        st.error("Error: Asegúrate de que el Excel tenga las columnas 'Description', 'Reseller price', 'Manu.nr' y 'Stock'.")
