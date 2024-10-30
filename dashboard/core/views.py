from django.shortcuts import render 
import pandas as pd
from .models import Desperdicio

def dashboard_view(request):
    file_path = 'C:/Cursodjango/desperdicios_con_tipo.xlsx'
    
    try:
        # Cargar el archivo Excel
        df = pd.read_excel(file_path)

        # Procesar los datos
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        df.dropna(subset=['date'], inplace=True)

        # Agrupar los datos por tipo de desperdicio y hotel, y calcular la suma de los pesos
        desperdicio_agrupado = df.groupby(['type', 'hotel'])['weight'].sum().reset_index()

        # Agregar la columna 'month' para el registro mensual
        df['month'] = df['date'].dt.strftime('%Y-%m')

        # Agrupar registros por mes y hotel para obtener la cantidad de registros por hotel en cada mes
        registros_por_mes_y_hotel_df = df.groupby(['month', 'hotel']).size().unstack(fill_value=0)
        
        # Convertir cada columna (hotel) a una lista de datos en lugar de usar `get` en la plantilla
        registros_por_mes_y_hotel = [
            {'name': hotel, 'data': registros_por_mes_y_hotel_df[hotel].tolist()}
            for hotel in registros_por_mes_y_hotel_df.columns
        ]
        nombres_meses = registros_por_mes_y_hotel_df.index.tolist()

        # Identificar el hotel líder por cada tipo de desperdicio
        hoteles_lideres_por_tipo = desperdicio_agrupado.loc[desperdicio_agrupado.groupby('type')['weight'].idxmax()]

        # Crear un diccionario con los hoteles líderes por cada tipo
        hoteles_lideres_por_tipo = desperdicio_agrupado.loc[desperdicio_agrupado.groupby('type')['weight'].idxmax()]
        hoteles_lideres_por_tipo_dict = hoteles_lideres_por_tipo.set_index('type')['hotel'].to_dict()

        # Datos de desperdicio por hotel
        desperdicio_por_hotel = df.groupby('hotel')['weight'].sum().reset_index()
        desperdicio_por_hotel_dict = desperdicio_por_hotel['weight'].tolist()
        nombres_hoteles = desperdicio_por_hotel['hotel'].tolist()

        # Datos de desperdicio por tipo
        desperdicio_por_tipo_df = df.groupby('type')['weight'].sum().reset_index()
        desperdicio_por_tipo_dict = desperdicio_por_tipo_df['weight'].tolist()
        nombres_tipos = desperdicio_por_tipo_df['type'].tolist()

        # Calcular el desperdicio promedio por tipo
        promedio_desperdicio_por_tipo = desperdicio_por_tipo_df['weight'].mean()

        # Datos de evolución diaria
        evolucion_diaria = df.groupby('date')['weight'].sum().reset_index()
        evolucion_diaria_dict = evolucion_diaria['weight'].tolist()
        fechas_evolucion = evolucion_diaria['date'].dt.strftime('%Y-%m-%d').tolist()

        # Registros mensuales por hotel
        df['month'] = df['date'].dt.strftime('%Y-%m')
        registros_por_mes = df.groupby('month')['hotel'].count().reset_index()
        registros_por_mes_dict = registros_por_mes['hotel'].tolist()
        nombres_meses = registros_por_mes['month'].tolist()

        # Calcular media y varianza del peso total por hotel
        media_varianza_df = df.groupby('hotel')['weight'].agg(['mean', 'var']).reset_index()
        media_varianza_dict = media_varianza_df[['mean', 'var']].to_dict(orient='list')
        nombres_media_varianza = media_varianza_df['hotel'].tolist()

        # Obtener datos del modelo Desperdicio (si es necesario)
        desperdicios = Desperdicio.objects.all()
        desperdicio_por_tipo_model = {}
        
        for desperdicio in desperdicios:
            tipo = desperdicio.tipo  
            desperdicio_por_tipo_model[tipo] = desperdicio_por_tipo_model.get(tipo, 0) + desperdicio.peso  

        # Combinar datos del modelo con datos del DataFrame (si es necesario)
        nombres_tipos_combined = set(nombres_tipos) | set(desperdicio_por_tipo_model.keys())
        valores_tipos_combined = [
            (desperdicio_por_tipo_dict[nombres_tipos.index(nombre)] if nombre in nombres_tipos else 0) +
            desperdicio_por_tipo_model.get(nombre, 0)
            for nombre in nombres_tipos_combined
        ]

        # Preparar datos para el gráfico de hoteles y tipos de desperdicio relevante
        desperdicio_por_hotel_y_tipo = desperdicio_agrupado.pivot(index='hotel', columns='type', values='weight').fillna(0)

        # Seleccionar solo los 10 tipos de desperdicio más relevantes
        top_10_tipos = desperdicio_por_tipo_df.nlargest(5, 'weight')
        datos_grafico_hotel_tipo = desperdicio_por_hotel_y_tipo[top_10_tipos['type']].values.tolist()
        nombres_tipos_para_grafico = top_10_tipos['type'].tolist()

        # Preparar el contexto
        context = {
            'desperdicio_por_hotel_dict': desperdicio_por_hotel_dict,
            'nombres_hoteles': nombres_hoteles,
            'desperdicio_por_tipo_dict': desperdicio_por_tipo_dict,
            'nombres_tipos': nombres_tipos,
            'promedio_desperdicio_por_tipo': promedio_desperdicio_por_tipo,
            'evolucion_diaria_dict': evolucion_diaria_dict,
            'fechas_evolucion': fechas_evolucion,
            'registros_por_mes_dict': registros_por_mes_dict,
            'nombres_meses': nombres_meses,
            'media_varianza_dict': media_varianza_dict,
            'nombres_media_varianza': nombres_media_varianza,
            'hoteles_lideres_por_tipo': hoteles_lideres_por_tipo_dict,
            'valores_tipos_combined': valores_tipos_combined,
            'datos_grafico_hotel_tipo': datos_grafico_hotel_tipo,
            'nombres_tipos_para_grafico': nombres_tipos_para_grafico,
            'registros_por_mes_y_hotel': registros_por_mes_y_hotel,
            'nombres_meses': nombres_meses,
            'nombres_hoteles': nombres_hoteles,
        }

        return render(request, 'core/dashboard.html', context)

    except Exception as e:
        print("Error al procesar el archivo:", e)
        return render(request, 'core/dashboard.html', {'error': 'Error al cargar los datos.'})
