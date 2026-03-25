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
        # 1. Leer el archivo (Excel o CSV)
        if archivo.name.endswith('.xlsx'):
            df = pd.read_excel(archivo)
        else:
            df = pd.read_csv(archivo, sep=None, engine='python')
        
        # 2. LIMPIEZA: Quitamos espacios raros en los nombres de las columnas
        df.columns = df.columns.str.strip()
        
        # 3. BUSCAR COLUMNAS (buscamos por palabras clave para no fallar)
        col_desc = next((c for c in df.columns if c.lower() in ['description', 'descripción', 'desc', 'product name']), None)
        col_price = next((c for c in df.columns if 'price' in c.lower() or 'precio' in c.lower() or 'reseller' in c.lower()), None)
        col_sku = next((c for c in df.columns if 'manu.nr' in c.lower() or 'sku' in c.lower() or 'part number' in c.lower()), None)
        col_stock = next((c for c in df.columns if 'stock' in c.lower() or 'inventario' in c.lower() or 'qty' in c.lower()), None)

        if not col_desc:
            st.error("❌ No encontré una columna de nombre o descripción. Revisa que tu Excel tenga una columna llamada 'Description'.")
            st.stop()

        def calcular_precio(coste):
            try:
                # Limpiamos el precio de símbolos extraños
                valor = str(coste).replace('€', '').replace('$', '').replace(',', '.').strip()
                # Margen del 30% + IVA
                precio_con_margen = float(valor) * 1.30
                return round(precio_con_margen * iva, 2)
            except: 
                return 0.0

        # 4. Crear el formato EXACTO de Shopify
        shopify = pd.DataFrame()
        
        # El 'Handle' es la URL (obligatorio)
        shopify['Handle'] = df[col_desc].astype(str).str.lower().apply(lambda x: re.sub(r'[^a-z0-9]+', '-', x).strip('-'))
        
        # El 'Title' es el nombre (esto es lo que te fallaba)
        shopify['Title'] = df[col_desc]
        
        # Otras columnas necesarias
        shopify['Body (HTML)'] = df[col_desc]
        shopify['Vendor'] = 'NovoGear'
        shopify['Command'] = 'NEW'
        shopify['Status'] = 'active'
        shopify['Published'] = 'true'
        
        # Precios y Stock (usando las columnas encontradas)
        shopify['Variant Price'] = df[col_price].apply(calcular_precio) if col_price else 0.0
        shopify['Variant SKU'] = df[col_sku] if col_sku else ''
        shopify['Variant Inventory Qty'] = df[col_stock] if col_stock else 0
        shopify['Variant Inventory Policy'] = 'deny'
        shopify['Variant Fulfillment Service'] = 'manual'

        st.success("✅ ¡Archivo procesado! Shopify ya reconocerá los Títulos correctamente.")
        
        # 5. Exportar con formato compatible (comas y UTF-8)
        output = io.StringIO()
        shopify.to_csv(output, index=False, sep=',', encoding='utf-8')
        csv_data = output.getvalue()

        st.download_button(
            label="📥 Descargar para Shopify",
            data=csv_data,
            file_name="productos_novogear_final.csv",
            mime="text/csv"
        )
        
    except Exception as e:
        st.error(f"Ocurrió un error al leer el archivo: {e}")
