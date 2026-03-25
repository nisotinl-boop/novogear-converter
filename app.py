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
        # 1. Leer el archivo saltando filas vacías si existen
        if archivo.name.endswith('.xlsx'):
            df = pd.read_excel(archivo)
        else:
            df = pd.read_csv(archivo, sep=None, engine='python')
        
        # ELIMINAR LA FILA BASURA (La que tiene QNTY o está casi vacía)
        df = df.dropna(subset=['Description', 'Reseller price'], how='any')
        
        # Limpiar nombres de columnas
        df.columns = df.columns.str.strip()

        def calcular_precio(coste):
            try:
                valor = str(coste).replace(',', '.')
                # Margen 30% + IVA
                precio_final = float(valor) * 1.30 * iva
                return round(precio_final, 2)
            except: return 0.0

        # 2. Crear el formato Shopify
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
        shopify['Variant Inventory Qty'] = df['Stock']
        shopify['Variant Inventory Policy'] = 'deny'
        shopify['Variant Fulfillment Service'] = 'manual'

        st.success(f"✅ ¡{len(shopify)} productos procesados!")
        
        # 3. Exportar a CSV compatible
        output = io.StringIO()
        shopify.to_csv(output, index=False, sep=',')
        st.download_button(
            label="📥 DESCARGAR ARCHIVO PARA SHOPIFY",
            data=output.getvalue(),
            file_name="productos_novogear_listos.csv",
            mime="text/csv"
        )
        
    except Exception as e:
        st.error(f"Error: Asegúrate de que el Excel tenga las columnas 'Description' y 'Reseller price'.")
