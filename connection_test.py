from sqlalchemy import create_engine, text

def test_database_connection():
    try:
        # Use text() para consultas SQL
        engine = create_engine("postgresql://postgres:891ea6f1fe7d3b49fd23@easypanel.singularmodel.com.br:54327/singular?sslmode=disable")
        with engine.connect() as connection:
            print("✅ Conexão bem-sucedida!")
            
            # Informações adicionais de diagnóstico
            print("\n🔍 Detalhes da conexão:")
            
            # Correção: Usar text() para consultas
            version_result = connection.execute(text("SELECT version()"))
            version = version_result.scalar()
            print(f"Versão do PostgreSQL: {version}")
            
            # Verificar esquemas disponíveis
            schemas_result = connection.execute(text("""
                SELECT schema_name 
                FROM information_schema.schemata
            """))
            print("\nEsquemas disponíveis:")
            for schema in schemas_result:
                print(f" - {schema[0]}")
            
            # Verificar tabelas existentes
            tables_result = connection.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
            """))
            print("\nTabelas no esquema público:")
            for table in tables_result:
                print(f" - {table[0]}")
            
            return True
    except Exception as e:
        print(f"❌ Erro de conexão: {e}")
        import traceback
        traceback.print_exc()
        return False

# Se o script for executado diretamente
if __name__ == "__main__":
    test_database_connection()
