#!/usr/bin/env python3
"""
Script de Migração: Migrar cache de notificações do arquivo JSON para o banco de dados
"""

import os
import json
from datetime import datetime
from supabase_client import add_to_notification_cache, get_notification_cache

def migrate_cache_to_database():
    """Migra dados do arquivo JSON para o banco de dados"""

    # Caminho do arquivo antigo
    cache_file = os.path.join(os.path.dirname(__file__), 'data', 'notification_cache.json')

    if not os.path.exists(cache_file):
        print("❌ Arquivo de cache não encontrado. Nada para migrar.")
        return False

    try:
        # Carregar dados do arquivo
        with open(cache_file, 'r', encoding='utf-8') as f:
            cache_data = json.load(f)

        print(f"📁 Encontrados {len(cache_data)} registros no arquivo JSON")

        # Verificar cache atual no banco
        db_cache = get_notification_cache()
        print(f"🗄️ Encontrados {len(db_cache)} registros no banco")

        # Migrar dados
        migrated = 0
        skipped = 0

        for task_id, timestamp_str in cache_data.items():
            # Verificar se já existe no banco
            if task_id in db_cache:
                print(f"⏭️ Tarefa {task_id} já existe no banco, pulando...")
                skipped += 1
                continue

            # Adicionar ao banco
            try:
                success = add_to_notification_cache(task_id)
                if success:
                    print(f"✅ Migrada tarefa {task_id}")
                    migrated += 1
                else:
                    print(f"❌ Falha ao migrar tarefa {task_id}")
            except Exception as e:
                print(f"❌ Erro ao migrar tarefa {task_id}: {e}")

        print("
📊 Resumo da Migração:"        print(f"   ✅ Migrados: {migrated}")
        print(f"   ⏭️ Pulados: {skipped}")
        print(f"   📁 Total no arquivo: {len(cache_data)}")
        print(f"   🗄️ Total no banco após migração: {len(get_notification_cache())}")

        if migrated > 0:
            print("
💡 Migração concluída! Você pode remover o arquivo data/notification_cache.json"            return True
        else:
            print("
ℹ️ Nenhum dado foi migrado"            return True

    except Exception as e:
        print(f"❌ Erro durante migração: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Iniciando migração do cache de notificações...")
    print("=" * 50)

    success = migrate_cache_to_database()

    if success:
        print("\n🎉 Migração finalizada!")
    else:
        print("\n❌ Migração falhou!")