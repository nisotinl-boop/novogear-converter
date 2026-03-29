import streamlit as st
import pandas as pd
import re
import io

st.title("🚀 NovoGear: Convertidor para Shopify")

iva = 1.21

archivo = st.file_uploader("Sube el Excel de tu proveedor", type=['xlsx', 'csv'])

if archivo is not None:
    try:
        if archivo.name.endswith('.xlsx'):
            df = pd.read_excel(archivo)
        else:
            df = pd.read_csv(archivo, sep=None, engine='python')
        
        # Limpieza de filas basura
        df = df.dropna(subset=['Description', 'Reseller price'], how='any')
        df.columns = df.columns.str.strip()

        def calcular_precio(coste):
            try:
                valor = str(coste).replace(',', '.')
                return round(float(valor) * 1.30 * iva, 2)
            except: return 0.0

        # Crear el formato Shopify con EAN incluido
        shopify = pd.DataFrame()
        shopify['Handle'] = df['Description'].astype(str).str.lower().apply(lambda x: re.sub(r'[^a-z0-9]+', '-', x).strip('-'))
        shopify['Title'] = df['Description']
        shopify['Body (HTML)'] = df['Description']
        shopify['Vendor'] = 'NovoGear'
        shopify['Command'] = 'NEW'
        shopify['Status'] = 'active'
        shopify['Published'] = 'true'
        shopify['Variant Price'] = df['Reseller price'].apply(calcular_precio)
        shopify['Variant SKU'] = df['Manu.nr']
        
        # AQUÍ AGREGAMOS EL EAN PARA SHOPIFY
        shopify['Variant Barcode'] = df['EAN-Code'] 
        
        shopify['Variant Inventory Qty'] = df['Stock']
        shopify['Variant Inventory Policy'] = 'deny'
        shopify['Variant Fulfillment Service'] = 'manual'

        st.success(f"✅ ¡{len(shopify)} productos procesados con EAN incluido!")
        
        output = io.StringIO()
        shopify.to_csv(output, index=False, sep=',')
        st.download_button(
            label="📥 DESCARGAR CON EAN PARA SHOPIFY",
            data=output.getvalue(),
            file_name="productos_novogear_con_ean.csv",
            mime="text/csv"
        )
        
    except Exception as e:
        st.error(f"Error: Asegúrate de que el Excel tenga las columnas 'Description', 'Reseller price' y 'EAN-Code'.")
