import requests
import hashlib
import time
import json
import random
from datetime import datetime

APP_ID = "18314931008"
SECRET = "TYWPOY5HUDTGJ2YL6C57AFEDYCWK5DHX"
API_URL = "https://open-api.affiliate.shopee.com.br/graphql"

def buscar_produtos():
    print("🔍 Buscando Organização de Cozinha (V19 - Filtros Fortes)...\n")
    
    keywords = [
        "organizador cozinha", "pote organizador", "porta tempero", "prateleira cozinha",
        "caixa organizadora cozinha", "escorredor louça", "organizador geladeira",
        "suporte microondas", "gaveteiro cozinha", "potes hermeticos cozinha"
    ]
    
    todos = []
    for kw in keywords:
        print(f"   → {kw}")
        timestamp = str(int(time.time()))
        
        query = f"""query Fetch {{
  productOfferV2(listType: 0, sortType: 5, page: 1, limit: 40, keyword: "{kw}") {{
    nodes {{
      productName
      commissionRate
      price
      imageUrl
      offerLink
      sales
      ratingStar
    }}
  }}
}}"""
        
        payload_dict = {"query": query, "operationName": "Fetch", "variables": {}}
        payload_str = json.dumps(payload_dict, separators=(',', ':'), ensure_ascii=False)
        
        assinatura = hashlib.sha256(f"{APP_ID}{timestamp}{payload_str}{SECRET}".encode()).hexdigest()
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"SHA256 Credential={APP_ID}, Timestamp={timestamp}, Signature={assinatura}"
        }
        
        try:
            r = requests.post(API_URL, headers=headers, data=payload_str, timeout=25)
            nodes = r.json().get("data", {}).get("productOfferV2", {}).get("nodes", [])
            
            for p in nodes:
                try:
                    comissao = float(p.get("commissionRate", 0))
                    nota = float(p.get("ratingStar", 0))
                    vendas = int(p.get("sales", 0))
                    
                    if comissao >= 0.12 and nota >= 4.7 and vendas >= 100:
                        todos.append(p)
                except:
                    continue
        except:
            pass
            
        time.sleep(1.3)
    
    # Remove duplicados
    unique = {p.get('offerLink'): p for p in todos if p.get('offerLink')}
    return list(unique.values())

def gerar_legenda(produto):
    nome = produto.get("productName", "")[:90]
    preco = produto.get("price", "")
    link = produto.get("offerLink", "")
    
    templates = [
        f"🔥 Organizador de cozinha que está vendendo MUITO! As pessoas estão amando 💕\n\n{nome}\n💰 Apenas R${preco}\n\n{link}",
        f"Produto com muitas vendas na Shopee! Resolve bagunça na cozinha rapidinho ✨\n\n{nome}\nR${preco}\n\n{link}",
        f"Mais um que entrou na lista de desejos de muita gente! Super prático 🔥\n\n{nome}\n\n{link}"
    ]
    return random.choice(templates)

def main():
    print("\n" + "="*120)
    print(" 🔥 ORGANIZAÇÃO DE COZINHA - V19 (Comissão ≥12% + Nota ≥4.7 + Ordenado por Vendas)")
    print("="*120 + "\n")
    
    produtos = buscar_produtos()
    
    if not produtos:
        print("❌ Nenhum produto atendeu aos critérios (12% + 4.7 estrelas). Vamos precisar baixar um pouco.")
        return
    
    # Ordena por VENDAS (o que você pediu)
    produtos.sort(key=lambda x: int(x.get("sales", 0)), reverse=True)
    
    print(f"✅ {len(produtos)} produtos qualificados encontrados!\n")
    
    export = []
    for i, p in enumerate(produtos[:15], 1):
        comissao = float(p.get("commissionRate", 0)) * 100
        nota = float(p.get("ratingStar", 0))
        vendas = int(p.get("sales", 0))
        legenda = gerar_legenda(p)
        
        print(f"{i:2d}. 📦 {vendas:,} vendidos | 💰 {comissao:.1f}% | ⭐ {nota:.1f}")
        print(f"    R$ {p.get('price')} | {p.get('productName')[:90]}...")
        print(f"    🔗 {p.get('offerLink')}\n")
        
        export.append({
            "posicao": i,
            "vendas": vendas,
            "comissao": round(comissao, 1),
            "nota": nota,
            "nome": p.get("productName"),
            "preco": p.get("price"),
            "link": p.get("offerLink"),
            "legenda": legenda
        })
    
    with open("COZINHA_TOP_VENDAS.json", "w", encoding="utf-8") as f:
        json.dump(export, f, indent=2, ensure_ascii=False)
    
    print("✅ Arquivo salvo: COZINHA_TOP_VENDAS.json")
    print("📌 Top produtos ordenados por vendas!")

if __name__ == "__main__":
    main()