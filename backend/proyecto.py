import requests
from urllib.parse import urljoin
import json
from datetime import datetime
import os

BASE_URL = "https://appsl.mardelplata.gob.ar/app_cuando_llega/"
AJAX_ENDPOINT = urljoin(BASE_URL, "webWS.php")

COLECTIVOS = {
    "563_puerto_a_b": {"linea_id": "120", "linea_nombre": "563 - A-B Puerto", "parada_id": "P3853", "destino": "Puerto (ida)"},
    "563_camet_a_b": {"linea_id": "120", "linea_nombre": "563 - A-B Camet", "parada_id": "P2053", "destino": "Camet (ida)"},
    "720_chapa": {"linea_id": "344", "linea_nombre": "720 - Por Chapa", "parada_id": "29V", "destino": "Batan"},
    "720_parque": {"linea_id": "344", "linea_nombre": "720 - Por Parque", "parada_id": "35", "destino": "Centro"},
    "542_regional": {"linea_id": "108", "linea_nombre": "542 - A Regional", "parada_id": "P2053", "destino": "Regional (ida)"},
    "542_2abril": {"linea_id": "108", "linea_nombre": "542 - B 2 Abril", "parada_id": "P3853", "destino": "2 de Abril (vuelta)"},
    "525_p_hermoso": {"linea_id": "103", "linea_nombre": "525 - P. HERMOSO", "parada_id": "P2342", "destino": "P.HERMOSO (ida)"},
    "525_centro": {"linea_id": "103", "linea_nombre": "525 - Centro", "parada_id": "P11444", "destino": "Centro (vuelta)"},
    "543_camet": {"linea_id": "109", "linea_nombre": "543 - Camet", "parada_id": "P2336", "destino": "Camet (ida)"},
    "543_regional": {"linea_id": "103", "linea_nombre": "525 - Regional", "parada_id": "P2338", "destino": "Regional (vuelta)"}
}

def hacer_consulta_ajax(linea_id, parada_id, destino):
    try:
        headers = {
            'X-Requested-With': 'XMLHttpRequest',
            'Origin': BASE_URL,
            'Referer': BASE_URL,
            'User-Agent': 'Mozilla/5.0'
        }
        data = {
            'accion': 'RecuperarProximosArribosW',
            'identificadorParada': parada_id,
            'codigoLineaParada': linea_id,
            'desParada': destino
        }
        response = requests.post(AJAX_ENDPOINT, headers=headers, data=data, timeout=10)
        if response.status_code == 200:
            return response.json()
        return {'error': f"Error HTTP {response.status_code}"}
    except requests.exceptions.RequestException as e:
        return {'error': f"Error de conexión: {str(e)}"}
    except json.JSONDecodeError:
        return {'error': "Respuesta no es JSON válido"}

def procesar_resultados(resultado):
    if 'error' in resultado:
        return None, resultado['error']
    if resultado.get('CodigoEstado') == -1:
        return [], "Sin unidades"
    if resultado.get('CodigoEstado', 0) != 0:
        error_msg = resultado.get('error', 'Error en respuesta del servidor')
        return None, f"Error del servidor: {error_msg}"

    arribos = []
    for unidad in resultado.get('arribos', []):
        arribos.append({
            'tiempo': unidad.get('Arribo', 'Sin estimación'),
            'ramal': unidad.get('DescripcionCortaBandera', 'Sin ramal'),
            'actualizado': datetime.now().strftime('%H:%M:%S')
        })
    return arribos, None

def main():
    resultados_finales = {}
    for colectivo_id, datos in COLECTIVOS.items():
        respuesta = hacer_consulta_ajax(datos['linea_id'], datos['parada_id'], datos['destino'])
        arribos, error = procesar_resultados(respuesta)
        resultados_finales[colectivo_id] = {
            'linea': datos['linea_nombre'],
            'destino': datos['destino'],
            'arribos': arribos or [],
            'error': error
        }

    # Escribir resultados en JSON en la carpeta backend
    output_path = os.path.join(os.path.dirname(__file__), "resultados_colectivos.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(resultados_finales, f, ensure_ascii=False, indent=2)

    # Imprimir JSON para Node
    print(json.dumps(resultados_finales, ensure_ascii=False))

if __name__ == "__main__":
    main()
