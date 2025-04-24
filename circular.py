import pandas as pd
import streamlit as st
from pathlib import Path
from io import BytesIO


ERP_PATH = Path("Base_de_ERP_circular_030.xlsx")

def load_erp():
    try:
        return pd.read_excel(ERP_PATH, header=0)
    except Exception as e:
        st.error(f"Error al cargar el archivo de ERP:{str(e)}")
        return None

def main():
    st.image("LOGO_RED_SLOGM-02.png", use_container_width=True)
    st.title("Circular 030 en formato excel")
    
    tipo_id = load_erp()
    if tipo_id is None:
        return

    with st.expander("📥 Subir Archivos", expanded=True):
        file = st.file_uploader("Carga el archivo (CSV)", type="csv")
    
    if file:
        try:
            with st.spinner('Procesando datos...'):
                # Procesa los archivos csv
                circular = pd.read_csv(file, 
                                    decimal=",",
                                    thousands=".")
            st.expander("Preprocesamiento de datos")
            col_necesarias = ["NIT", "Responsable", "NIT_Empresa", "Factura", "Valor_Factura",
                    "Fecha_Emision", "Fecha_Radicacion", "Recaudo", "Retenciones",
                    "OtrasGlosasAceptada", "GlosaAcepConciliacion", "CarteraTotal", "Plan"]
            
            circular = circular[col_necesarias]
            circular = circular[circular["Plan"]!= "ESTATAL"]
            
            # Validación de los datos
            if circular.empty:
                st.error("No hay datos después del filtrado de planes estables")
                return
            
            #Muestra de vista previa
            with st.expander("📊 Vista previa de los datos cargados", expanded= False):
                st.dataframe(circular, use_container_width=True)
            
            # Transformación
            st.expander("Transformación de datos")
            
            circular[['Factura_Prefijo', 'Factura_Numero']] = circular['Factura'].str.split('-', expand=True)

            circular["Recaudo"] = circular["Recaudo"].str.replace(".", "").str.replace("$", "").astype(int)
            circular["Retenciones"] = circular["Retenciones"].str.replace(".", "").str.replace("$", "").astype(int)
            circular["OtrasGlosasAceptada"] = circular["OtrasGlosasAceptada"].str.replace(".", "").str.replace("$", "").astype(int)
            circular["GlosaAcepConciliacion"] = circular["GlosaAcepConciliacion"].str.replace(".", "").str.replace("$", "").astype(int)
            circular["Valor_Factura"] = circular["Valor_Factura"].str.replace(".", "").str.replace("$","").astype(int)
            circular["CarteraTotal"] = circular["CarteraTotal"].str.replace(".", "").str.replace("$", "").astype(int)
            
            #Convertir a fechas
            circular["Fecha_Emision"] = pd.to_datetime(circular["Fecha_Emision"], format="%d/%m/%Y", errors="coerce").dt.date
            circular["Fecha_Radicacion"] = pd.to_datetime(circular["Fecha_Radicacion"], format="%d/%m/%Y", errors="coerce").dt.date
            circular.dropna(subset=["Fecha_Radicacion"], inplace=True)
            
            # circular["Fecha_Emision"] = circular["Fecha_Emision"].dt.normalize()
            # circular["Fecha_Radicacion"] = circular["Fecha_Radicacion"].dt.normalize()
            
            circular["Tipo de registro"] = 2
            circular["Consecutivo de Registro"] = range(1, len(circular) + 1)
            circular["Tipo de idenftificacion ERP"] = ""
            circular["Numero de identificacion ERP"] = circular["NIT"]
            circular["Razon Social de la ERP"] = circular["Responsable"]
            circular["Tipo Identificación IPS"] = "NI"
            circular["Número de identificación IPS"] = circular["NIT_Empresa"]
            circular["Tipo de Cobro"] = "F"
            circular["Prefijo de la Factura o N° Recobro de la ERP"] = circular["Factura_Prefijo"]
            circular["Número de la Factura o N° Recobro de la ERP"] = circular["Factura_Numero"]
            circular["Indicador de Actualización de la Factura o Recobro"] = ""
            circular["VL Factura o Recobro"] = circular["Valor_Factura"]
            circular["Fecha Emisión de la Factura o Recobro"] = circular["Fecha_Emision"]
            circular["Fecha Presentación de la factura o Recobro"] = circular["Fecha_Radicacion"]
            circular["Fecha Devolución de la Factura o Recobro"] = ""
            circular["Valor Total Pagos Aplicados a esta Factura o Recobro"] = circular["Recaudo"] + circular["Retenciones"]
            circular["Valor Glosa Aceptada"] = circular["OtrasGlosasAceptada"] + circular["GlosaAcepConciliacion"]
            circular["Glosa fue Respondida"] = ""
            circular["Saldo Factura o Recobro"] = circular["CarteraTotal"]
            circular["Facturas se Encuentran en Cobro Juridico"] = "No"
            circular["Etapa en que se Encuentra el Proceso"] = 0

            circular = circular.merge(tipo_id, 
                                    how="left", 
                                    left_on="Razon Social de la ERP", 
                                    right_on="RAZON SOCIAL DE LA ERP")
            
            circular["Tipo de idenftificacion ERP"] = circular["TIPO IDENTIFICACION ERP"] 
            
            col_finales = ["Tipo de registro", "Consecutivo de Registro", "Tipo de idenftificacion ERP",
                    "Numero de identificacion ERP","Razon Social de la ERP", 
                    "Tipo Identificación IPS", "Número de identificación IPS",
                    "Tipo de Cobro", "Prefijo de la Factura o N° Recobro de la ERP",
                    "Número de la Factura o N° Recobro de la ERP", "Indicador de Actualización de la Factura o Recobro",
                    "VL Factura o Recobro", "Fecha Emisión de la Factura o Recobro", "Fecha Presentación de la factura o Recobro",
                    "Fecha Devolución de la Factura o Recobro", "Valor Total Pagos Aplicados a esta Factura o Recobro",
                    "Valor Glosa Aceptada", "Glosa fue Respondida", "Saldo Factura o Recobro",
                    "Facturas se Encuentran en Cobro Juridico", "Etapa en que se Encuentra el Proceso"]
            
            circular = circular[col_finales]
            
            # Mostrar resultados
            st.success("Procesamiento completado exitosamente!")
            st.metric("Registros procesados", len(circular))
            
            with st.expander("Ver datos finales ✅", expanded=False):
                st.dataframe(circular, use_container_width=True)
                
            # Descargar archivo
            st.expander("Exportación de resultados")
            with BytesIO() as output:
                with pd.ExcelWriter(output, engine="openpyxl") as writer:
                    circular.to_excel(writer, index=False, sheet_name="Circular 030")
                
                excel_data = output.getvalue()
            
            st.download_button(
                label="📤 Descargar archivo procesado",
                data=excel_data,
                file_name="Circular_030.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                help="Descarga el archivo procesado en formato Excel"
            )
        except Exception as e:
            st.error(f"Error al procesar el archivo: {str(e)}")
            st.exception(e)

if __name__ == "__main__":
    main()