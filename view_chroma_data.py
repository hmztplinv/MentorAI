# view_chroma_data.py
import os
import sys
import json
from tabulate import tabulate

def view_chroma_data():
    """ChromaDB içeriğini görüntüle"""
    try:
        import chromadb
        
        # ChromaDB dizininin yolunu belirle
        chroma_dir = "./chromadb"  # settings'teki değeri kullanın
        
        if not os.path.exists(chroma_dir):
            print(f"ChromaDB dizini bulunamadı: {chroma_dir}")
            return
        
        # ChromaDB istemcisini oluştur
        client = chromadb.PersistentClient(path=chroma_dir)
        
        # Mevcut koleksiyonları al
        collections = client.list_collections()
        
        if not collections:
            print("ChromaDB'de koleksiyon bulunamadı!")
            return
        
        print(f"ChromaDB'de {len(collections)} koleksiyon bulundu:")
        for i, collection in enumerate(collections, 1):
            print(f"{i}. {collection.name}")
        
        # Kullanıcıdan görüntülemek istediği koleksiyonu seç
        collection_choice = input("\nGörüntülemek istediğiniz koleksiyonun numarasını girin: ")
        
        try:
            collection_index = int(collection_choice) - 1
            if 0 <= collection_index < len(collections):
                selected_collection = collections[collection_index]
            else:
                print("Geçersiz koleksiyon numarası!")
                return
        except ValueError:
            print("Geçersiz giriş!")
            return
        
        # Koleksiyon içeriğini al
        collection = client.get_collection(selected_collection.name)
        
        # Tüm veriyi al (maksimum 100 öğe)
        items = collection.get(limit=100)
        
        if not items or not items["ids"]:
            print("Koleksiyon boş!")
            return
        
        # Metadata, ID ve içerik tablosu oluştur
        table_data = []
        for i in range(len(items["ids"])):
            item_id = items["ids"][i]
            metadata = items["metadatas"][i] if "metadatas" in items and i < len(items["metadatas"]) else {}
            document = items["documents"][i] if "documents" in items and i < len(items["documents"]) else ""
            
            # Uzun belgeyi kısalt
            if len(document) > 100:
                document = document[:97] + "..."
            
            # Satır ekle
            table_data.append([
                item_id, 
                json.dumps(metadata), 
                document
            ])
        
        # Tablo formatında görüntüle
        headers = ["ID", "Metadata", "İçerik (İlk 100 karakter)"]
        print(tabulate(table_data, headers=headers, tablefmt="grid"))
        print(f"Not: Toplam {len(items['ids'])} öğe görüntüleniyor (maksimum 100)")
        
    except Exception as e:
        print(f"ChromaDB verilerini görüntülerken hata oluştu: {str(e)}")

if __name__ == "__main__":
    view_chroma_data()