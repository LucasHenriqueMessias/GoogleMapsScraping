"""
Google Maps Scraper - Versão Interativa
=======================================
Script interativo para buscar estabelecimentos no Google Maps
e gerar arquivo Excel com dados de contato.
"""

import os
import time
import requests
import pandas as pd
from datetime import datetime
from typing import Dict, List, Optional

API_KEY = "AIzaSyDsvywMtfkUUfZGep5UWqiOXK89L7SCYAA"


def clear_screen():
    """Limpa a tela do terminal."""
    os.system('cls' if os.name == 'nt' else 'clear')


def print_header():
    """Exibe o cabeçalho do programa."""
    clear_screen()
    print("=" * 60)
    print("🔍 GOOGLE MAPS SCRAPER - BUSCA DE ESTABELECIMENTOS")
    print("=" * 60)
    print("📊 Gera arquivo Excel com dados de contato")
    print("📱 Inclui links do WhatsApp automaticamente")
    print("-" * 60)
    print("👨‍💻 Feito por Lucas Henrique Messias Gonçalves")
    print("-" * 60)


def get_user_input():
    """Coleta informações do usuário de forma interativa."""
    print_header()
    
    print("📝 CONFIGURE SUA BUSCA:")
    print()
    
    # Tipo de estabelecimento
    print("💡 Exemplos de busca:")
    print("   • casa de carnes")
    print("   • padaria")
    print("   • farmácia")
    print("   • restaurante")
    print("   • posto de gasolina")
    print()
    
    query = input("🔍 Digite o tipo de estabelecimento que deseja buscar: ").strip()
    if not query:
        print("❌ Tipo de estabelecimento é obrigatório!")
        input("Pressione Enter para tentar novamente...")
        return get_user_input()
    
    print()
    
    # Cidade
    print("🌍 Exemplos de cidade:")
    print("   • Cerquilho")
    print("   • São Paulo") 
    print("   • Campinas")
    print("   • Sorocaba")
    print()
    
    city = input("📍 Digite a cidade onde deseja buscar: ").strip()
    if not city:
        print("❌ Cidade é obrigatória!")
        input("Pressione Enter para tentar novamente...")
        return get_user_input()
    
    print()
    
    # Raio (opcional)
    print("📏 Raio de busca (opcional):")
    print("   • Pressione Enter para usar padrão (7km)")
    print("   • Digite um número em metros (ex: 15000 para 15km)")
    print()
    
    radius_input = input("📐 Raio de busca em metros [7000]: ").strip()
    try:
        radius = int(radius_input) if radius_input else 7000
        if radius < 1000:
            radius = 7000
            print("⚠️  Raio muito pequeno, usando 7000m")
    except ValueError:
        radius = 7000
        print("⚠️  Valor inválido, usando 7000m")
    
    return query, city, radius


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
            return None
    except Exception:
        return None


def search_places(query: str, city_coords: tuple, radius: int = 7000) -> List[Dict]:
    """Pesquisa por estabelecimentos usando múltiplas estratégias."""
    all_results: List[Dict] = []
    seen_place_ids = set()

    # Lista de termos relacionados para expandir a busca
    search_terms = [query]
    
    # Adiciona termos relacionados baseado na busca
    if "casa de carnes" in query.lower() or "açougue" in query.lower():
        search_terms.extend(["açougue", "carniceria", "casa de carne", "frigorífico"])
    elif "padaria" in query.lower():
        search_terms.extend(["panificadora", "confeitaria", "casa do pão"])
    elif "farmácia" in query.lower():
        search_terms.extend(["drogaria", "pharmacy"])
    elif "restaurante" in query.lower():
        search_terms.extend(["lanchonete", "pizzaria", "comida"])
    elif "posto" in query.lower():
        search_terms.extend(["posto de combustível", "gasolina", "auto posto"])

    print(f"🔍 Buscando com {len(search_terms)} termos relacionados...")
    
    for i, term in enumerate(search_terms, 1):
        print(f"   {i}/{len(search_terms)} 🔎 Buscando: '{term}'")
        results = search_places_single_term(term, city_coords, radius)
        
        # Remove duplicatas baseado no place_id
        new_results = 0
        for place in results:
            if place["place_id"] not in seen_place_ids:
                all_results.append(place)
                seen_place_ids.add(place["place_id"])
                new_results += 1
        
        print(f"      ✅ +{new_results} novos estabelecimentos")
    
    return all_results


def search_places_single_term(query: str, city_coords: tuple, radius: int = 7000) -> List[Dict]:
    """Pesquisa por um termo específico usando a Places API."""
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
            
            if not next_page_token:
                break
                
            time.sleep(2)  # Aguarda antes da próxima página
        else:
            break
    
    return results


def place_details(place_id: str) -> Dict:
    """Obtém detalhes de um estabelecimento."""
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
            return {}
    except Exception:
        return {}


def whatsapp_link(phone: str) -> str:
    """Converte telefone em link do WhatsApp."""
    digits = "".join(filter(str.isdigit, phone))
    if digits.startswith("0"):
        digits = digits[1:]
    return f"https://wa.me/{digits}" if digits else ""


def generate_filename(query: str, city: str) -> str:
    """Gera nome do arquivo com data e hora."""
    now = datetime.now()
    date_str = now.strftime("%Y%m%d_%H%M%S")
    
    safe_query = "".join(c if c.isalnum() else "_" for c in query)
    safe_city = "".join(c if c.isalnum() else "_" for c in city)
    
    return f"{safe_query}_{safe_city}_{date_str}.xlsx"


def scrape_and_save(query: str, city: str, radius: int = 7000) -> str:
    """Executa a busca e salva o arquivo Excel."""
    
    print()
    print("🌍 Obtendo coordenadas da cidade...")
    city_coords = get_city_coordinates(city)
    if not city_coords:
        return None
    
    print(f"✅ Coordenadas encontradas: {city_coords}")
    print()
    
    # Buscar estabelecimentos
    raw_places = search_places(query, city_coords, radius)
    
    # Se poucos resultados, expande o raio
    if len(raw_places) < 5:
        print()
        print(f"⚠️  Poucos resultados ({len(raw_places)}). Expandindo busca...")
        larger_radius = radius * 2
        print(f"🔍 Tentando com raio de {larger_radius/1000:.1f}km...")
        raw_places = search_places(query, city_coords, larger_radius)
    
    if not raw_places:
        return None
    
    print()
    print(f"✅ Total encontrado: {len(raw_places)} estabelecimentos únicos")
    print()
    
    # Coletar detalhes
    print("📋 Coletando informações detalhadas...")
    rows: List[Dict] = []
    
    for i, place in enumerate(raw_places, 1):
        name = place.get('name', 'N/A')
        print(f"   {i:3d}/{len(raw_places)} 📍 {name}")
        
        details = place_details(place["place_id"])
        phone = details.get("international_phone_number") or details.get("formatted_phone_number") or ""
        
        rows.append({
            "Razão Social": details.get("name", ""),
            "Telefone": phone,
            "Link WhatsApp": whatsapp_link(phone),
            "URL Google Maps": details.get("url", ""),
            "Website": details.get("website", ""),
        })
    
    # Gerar arquivo Excel
    print()
    print("📊 Gerando arquivo Excel...")
    
    filename = generate_filename(query, city)
    df = pd.DataFrame(rows)
    
    with pd.ExcelWriter(filename, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Estabelecimentos', index=False)
        
        # Formatação
        worksheet = writer.sheets['Estabelecimentos']
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
    
    return filename


def main():
    """Função principal interativa."""
    try:
        while True:
            # Coletar dados do usuário
            query, city, radius = get_user_input()
            
            # Mostrar resumo
            print()
            print("📋 RESUMO DA BUSCA:")
            print(f"   🔍 Estabelecimento: {query}")
            print(f"   📍 Cidade: {city}")
            print(f"   📏 Raio: {radius/1000:.1f}km")
            print()
            
            confirm = input("✅ Confirma a busca? (S/n): ").strip().lower()
            if confirm and confirm not in ['s', 'sim', 'y', 'yes']:
                continue
            
            print()
            print("🚀 INICIANDO BUSCA...")
            print("=" * 60)
            
            # Executar busca
            filename = scrape_and_save(query, city, radius)
            
            # Resultado
            print()
            print("=" * 60)
            if filename:
                print("✅ BUSCA CONCLUÍDA COM SUCESSO!")
                print(f"📁 Arquivo gerado: {filename}")
                print(f"📊 Localização: {os.path.abspath(filename)}")
            else:
                print("❌ Nenhum estabelecimento encontrado!")
            
            print()
            repeat = input("🔄 Fazer nova busca? (S/n): ").strip().lower()
            if repeat and repeat not in ['s', 'sim', 'y', 'yes']:
                break
        
        print()
        print("👋 Obrigado por usar o Google Maps Scraper!")
        print("👨‍💻 Desenvolvido por Lucas Henrique Messias Gonçalves")
        
    except KeyboardInterrupt:
        print("\n\n👋 Programa encerrado pelo usuário.")
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
        input("Pressione Enter para sair...")


if __name__ == "__main__":
    main()
