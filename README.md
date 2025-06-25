# 🔍 Google Maps Scraper - Busca de Estabelecimentos

**👨‍💻 Desenvolvido por Lucas Henrique Messias Gonçalves**

## 📖 Descrição
Ferramenta para buscar estabelecimentos no Google Maps e gerar arquivo Excel com dados de contato, incluindo links do WhatsApp automaticamente.

## 📁 Arquivos Disponíveis

### ✨ **GoogleMapsScraper_v2.exe** (RECOMENDADO)
- **Executável independente** - não precisa instalar Python
- **Interface interativa** - pergunta o que buscar na hora da execução
- **Gera nomes com data/hora** - exemplo: `casa_de_carnes_Cerquilho_20250625_121530.xlsx`
- **32MB** - contém tudo necessário para funcionar
- **Inclui créditos do desenvolvedor**

### 🖱️ **GoogleMapsScraper.bat** 
- **Arquivo batch** - executa clicando duas vezes
- **Instala dependências automaticamente** se necessário
- **Executa a versão interativa** do Python

### 🐍 **Scripts Python**
- `GoogleMapsScraper_Interactive.py` - versão interativa
- `GoogleMapsButcherScraper.py` - versão linha de comando

## 🚀 Como Usar

### Opção 1: Download do Executável (Mais Fácil)
1. **[Baixe o executável](https://github.com/LucasHenriqueMessias/GoogleMapsScraping/blob/main/dist/GoogleMapsScraper_v2.exe)** diretamente do GitHub
   - Clique no link acima
   - Clique no botão "Download" na página do GitHub
   - Salve o arquivo em uma pasta de sua escolha
2. **Clique duas vezes** no arquivo baixado
3. **Digite o tipo de estabelecimento** (ex: "casa de carnes", "padaria")
4. **Digite a cidade** (ex: "Cerquilho", "São Paulo")
5. **Confirme** e aguarde o processamento
6. **Arquivo Excel será criado** na mesma pasta

### Opção 2: Executar com Python
1. **Clone o repositório:**
   ```bash
   git clone https://github.com/LucasHenriqueMessias/GoogleMapsScraping.git
   cd GoogleMapsScraping
   ```

2. **Instale as dependências:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Execute o script interativo:**
   ```bash
   python GoogleMapsScraper_Interactive.py
   ```

### Opção 3: Linha de Comando
```bash
python GoogleMapsButcherScraper.py "casa de carnes" "Cerquilho" -o "resultado.xlsx"
```

## 📊 Arquivo Excel Gerado

O arquivo Excel contém as seguintes colunas:
- **Razão Social** - Nome do estabelecimento
- **Telefone** - Número de telefone (quando disponível)
- **Link WhatsApp** - Link direto para WhatsApp
- **URL Google Maps** - Link para o estabelecimento no Google Maps
- **Website** - Site oficial (quando disponível)

## 🔧 Recursos Avançados

### 🎯 Busca Inteligente
- **Múltiplos termos**: Para "casa de carnes" também busca "açougue", "carniceria", "frigorífico"
- **Remove duplicatas**: Estabelecimentos únicos baseado no ID do Google
- **Expande raio**: Se poucos resultados, aumenta automaticamente o raio de busca

### 📱 Links WhatsApp
- **Formatação automática**: Remove caracteres especiais do telefone
- **Links clicáveis**: Abrem diretamente no WhatsApp

### 📅 Nomes com Data/Hora
- **Formato**: `tipo_cidade_YYYYMMDD_HHMMSS.xlsx`
- **Exemplo**: `casa_de_carnes_Sorocaba_20250625_143022.xlsx`

## 🔑 Configuração da API

⚠️ **IMPORTANTE**: Você precisa de uma chave da Google Places API para usar este projeto.

### Como obter sua API Key:

1. Acesse o [Google Cloud Console](https://console.cloud.google.com/)
2. Crie um projeto ou selecione um existente
3. Habilite as seguintes APIs:
   - **Places API (New)**
   - **Geocoding API**
4. Vá em "Credenciais" e crie uma chave de API
5. Configure restrições de IP/domínio se necessário

### Como usar sua API Key:

- **Executável**: A API key será solicitada quando você executar o programa
- **Scripts Python**: Substitua `YOUR_API_KEY_HERE` pela sua chave no código

### Custos:
- Places API: ~$17 por 1000 buscas de texto
- Place Details: ~$17 por 1000 detalhes
- Geocoding: ~$5 por 1000 geocodificações

Para este projeto, uma busca típica usa ~1-5 requisições da Places API + 1 Geocoding + N Place Details (onde N = número de estabelecimentos encontrados).

## 🏃‍♂️ Exemplos de Busca

### Tipos de Estabelecimento
- `casa de carnes` → Encontra açougues, carniceiras, frigoríficos
- `padaria` → Encontra padarias, panificadoras, confeitarias
- `farmácia` → Encontra farmácias, drogarias
- `restaurante` → Encontra restaurantes, lanchonetes, pizzarias
- `posto de gasolina` → Encontra postos de combustível

### Cidades
- Funciona com qualquer cidade brasileira
- Exemplos: `Cerquilho`, `São Paulo`, `Sorocaba`, `Campinas`

## ⚡ Performance
- **80+ estabelecimentos** encontrados em cidades médias
- **Busca expandida** com múltiplos termos relacionados
- **Raio adaptativo** (7km → 14km se poucos resultados)

## 🛡️ Compliance
- **Respeita Termos de Serviço** do Google Maps
- **Coleta dados públicos** já disponibilizados pelas empresas
- **Conformidade LGPD** - dados empresariais públicos

## 📞 Suporte
Em caso de problemas:
1. Verifique sua conexão com internet
2. Certifique-se de que a API key está válida
3. Teste com cidades conhecidas primeiro

---
**👨‍💻 Desenvolvido por Lucas Henrique Messias Gonçalves - 2025** | Versão com múltiplas estratégias de busca e geração de Excel
