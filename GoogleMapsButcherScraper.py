"""
Ferramenta: google_maps_butcher_scraper.py
-------------------------------------------------
Coleta razão social (nome cadastrado) e telefone (formato internacional ou local)
de todas as empresas que aparecem no Google Maps em uma cidade específica
e gera um arquivo Excel (.xlsx) com link de WhatsApp.

Requisitos:
- Python 3.8+
- Bibliotecas: requests, pandas, openpyxl
  (`pip install requests pandas openpyxl`)
- Chave da Google Places API (New) com acesso a:
  * Places API (New)
  * Geocoding API

Uso:
python GoogleMapsButcherScraper.py "casa de carnes" "Cerquilho"
python GoogleMapsButcherScraper.py "padaria" "São Paulo"

Observação de compliance:
Use apenas para fins comerciais legítimos, respeitando Termos de Serviço
do Google Maps e a LGPD (coletando dados já tornados públicos pelas empresas).
"""

import os
import time
import csv
import argparse
import requests
import pandas as pd
from typing import Dict, List, Optional

API_KEY = "AIzaSyDsvywMtfkUUfZGep5UWqiOXK89L7SCYAA"


def get_city_coordinates(city_name: str) -> Optional[tuple]:
    """Obtém as coordenadas de uma cidade usando geocoding."""
    try:
        url = "https://maps.googleapis.com/maps/api/geocode/json"
        params = {
            "address": f"{city_name}, Brasil",
            "key": API_KEY
        }
        
        response = requests.get(url, params=params)
        data = response.json()
        
        if data["status"] == "OK" and data["results"]:
            location = data["results"][0]["geometry"]["location"]
            return (location["lat"], location["lng"])
        else:
            print(f"❌ Cidade '{city_name}' não encontrada.")
            return None
    except Exception as e:
        print(f"❌ Erro ao buscar coordenadas: {e}")
        return None


def search_places(query: str, city_coords: tuple, radius: int = 7000) -> List[Dict]:
    """Pesquisa por estabelecimentos em uma cidade específica usando múltiplas estratégias."""
    all_results: List[Dict] = []
    seen_place_ids = set()

    # Lista de termos relacionados para expandir a busca
    search_terms = [query]
    
    # Se buscar por "casa de carnes", adiciona termos relacionados
    if "casa de carnes" in query.lower():
        search_terms.extend(["açougue", "carniceria", "casa de carne", "frigorífico"])
    elif "padaria" in query.lower():
        search_terms.extend(["panificadora", "confeitaria", "casa do pão"])
    elif "farmácia" in query.lower():
        search_terms.extend(["drogaria", "pharmacy"])
    
    print(f"🔍 Buscando em {city_coords} com {len(search_terms)} termos: {search_terms}")

    for term in search_terms:
        print(f"   🔎 Buscando: '{term}'")
        results = search_places_single_term(term, city_coords, radius)
        
        # Remove duplicatas baseado no place_id
        for place in results:
            if place["place_id"] not in seen_place_ids:
                all_results.append(place)
                seen_place_ids.add(place["place_id"])
    
    print(f"✅ Total encontrado: {len(all_results)} estabelecimentos únicos")
    return all_results


def search_places_single_term(query: str, city_coords: tuple, radius: int = 7000) -> List[Dict]:
    """Pesquisa por um termo específico usando a nova Places API."""
    results: List[Dict] = []
    next_page_token: str = ""

    while True:
        url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
        params = {
            "query": f"{query} near {city_coords[0]},{city_coords[1]}",
            "location": f"{city_coords[0]},{city_coords[1]}",
            "radius": radius,
            "language": "pt-BR",
            "key": API_KEY
        }
        
        if next_page_token:
            params["pagetoken"] = next_page_token
        
        response = requests.get(url, params=params)
        data = response.json()
        
        if data["status"] == "OK":
            page_results = data.get("results", [])
            results.extend(page_results)
            next_page_token = data.get("next_page_token", "")
            
            print(f"      📄 Página: +{len(page_results)} resultados")
            
            if not next_page_token:
                break
                
            print("      ⏳ Aguardando próxima página...")
            time.sleep(2)
        else:
            print(f"      ❌ Erro na busca: {data.get('status', 'UNKNOWN_ERROR')}")
            break
    
    print(f"      ✅ '{query}': {len(results)} resultados")
    return results


def place_details(place_id: str) -> Dict:
    """Obtém detalhes (nome, telefone, site…) de um Place usando a nova Places API."""
    url = "https://maps.googleapis.com/maps/api/place/details/json"
    params = {
        "place_id": place_id,
        "fields": "name,formatted_phone_number,international_phone_number,website,url",
        "language": "pt-BR",
        "key": API_KEY
    }
    
    try:
        response = requests.get(url, params=params)
        data = response.json()
        
        if data["status"] == "OK":
            return data.get("result", {})
        else:
            print(f"❌ Erro ao obter detalhes: {data.get('status', 'UNKNOWN_ERROR')}")
            return {}
    except Exception as e:
        print(f"❌ Erro na requisição de detalhes: {e}")
        return {}


def whatsapp_link(phone: str) -> str:
    """Converte telefone em link https://wa.me/<numero> se possível."""
    digits = "".join(filter(str.isdigit, phone))
    if digits.startswith("0"):
        digits = digits[1:]
    return f"https://wa.me/{digits}" if digits else ""


def scrape(query: str, city: str, radius: int = 7000, output_file: str = None) -> int:
    """Função principal que executa a busca e gera o arquivo Excel."""
    
    # Define nome do arquivo baseado na consulta e cidade
    if output_file is None:
        safe_query = "".join(c if c.isalnum() else "_" for c in query)
        safe_city = "".join(c if c.isalnum() else "_" for c in city)
        output_file = f"{safe_query}_{safe_city}.xlsx"
    
    print(f"🌍 Obtendo coordenadas de {city}...")
    city_coords = get_city_coordinates(city)
    if not city_coords:
        return 0
    
    raw_places = search_places(query, city_coords, radius)
    
    # Se encontrou poucos resultados, tenta com raio maior
    if len(raw_places) < 5:
        print(f"⚠️  Poucos resultados encontrados ({len(raw_places)}). Expandindo raio de busca...")
        larger_radius = radius * 2
        print(f"🔍 Tentando novamente com raio de {larger_radius}m...")
        raw_places = search_places(query, city_coords, larger_radius)
    
    if not raw_places:
        print("❌ Nenhum estabelecimento encontrado.")
        return 0
    
    rows: List[Dict] = []
    
    print("📋 Coletando detalhes dos estabelecimentos...")
    for i, place in enumerate(raw_places, 1):
        print(f"   {i}/{len(raw_places)}: {place.get('name', 'N/A')}")
        details = place_details(place["place_id"])
        phone = details.get("international_phone_number") or details.get("formatted_phone_number") or ""
        rows.append(
            {
                "Razão Social": details.get("name", ""),
                "Telefone": phone,
                "Link WhatsApp": whatsapp_link(phone),
                "URL Google Maps": details.get("url", ""),
                "Website": details.get("website", ""),
            }
        )

    if rows:
        # Criar DataFrame e salvar como Excel
        df = pd.DataFrame(rows)
        
        # Configurar o Excel com formatação
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Estabelecimentos', index=False)
            
            # Obter a planilha para formatação
            worksheet = writer.sheets['Estabelecimentos']
            
            # Ajustar largura das colunas
            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = min(max_length + 2, 50)
                worksheet.column_dimensions[column_letter].width = adjusted_width
        
        print(f"📊 Arquivo Excel criado com formatação automática")
    
    return len(rows)


def main():
    """Função principal com argumentos de linha de comando."""
    parser = argparse.ArgumentParser(
        description="Busca estabelecimentos no Google Maps e gera arquivo Excel com dados de contato",
        epilog="Exemplo: python GoogleMapsButcherScraper.py 'casa de carnes' 'Cerquilho'"
    )
    
    parser.add_argument(
        "query", 
        help="Tipo de estabelecimento a buscar (ex: 'casa de carnes', 'padaria', 'farmácia')"
    )
    
    parser.add_argument(
        "city",
        help="Nome da cidade onde buscar (ex: 'Cerquilho', 'São Paulo')"
    )
    
    parser.add_argument(
        "-o", "--output",
        help="Nome do arquivo Excel de saída (opcional, ex: 'resultado.xlsx')"
    )
    
    parser.add_argument(
        "-r", "--radius",
        type=int,
        default=7000,
        help="Raio de busca em metros (padrão: 7000)"
    )
    
    args = parser.parse_args()
    
    print(f"🚀 Iniciando busca por '{args.query}' em {args.city}")
    print(f"📄 Arquivo de saída: {args.output or 'gerado automaticamente (.xlsx)'}")
    print("-" * 50)
    
    total = scrape(args.query, args.city, args.radius, args.output)
    
    if total > 0:
        output_file = args.output or f"{''.join(c if c.isalnum() else '_' for c in args.query)}_{''.join(c if c.isalnum() else '_' for c in args.city)}.xlsx"
        print(f"✅ Salvo com sucesso: {total} registros em '{output_file}'.")
        print(f"📊 Arquivo Excel criado com formatação e links clicáveis!")
    else:
        print("❌ Nenhum registro foi salvo.")


if __name__ == "__main__":
    main()
