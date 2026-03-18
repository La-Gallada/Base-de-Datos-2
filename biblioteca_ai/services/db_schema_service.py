"""
Servicio para obtener y cachear la estructura de la base de datos.
Proporciona información sobre tablas, columnas, relaciones y tipos de datos.
"""

import json
from typing import Dict, List, Optional, Any
from db import get_connection


class DBSchemaService:
    """
    Gestiona información sobre la estructura de la base de datos.
    Cachea los resultados para mejorar performance.
    """
    
    _cache: Optional[Dict[str, Any]] = None
    
    @staticmethod
    def get_schema() -> Dict[str, Any]:
        """
        Obtiene toda la información de la estructura de la BD.
        Cachea el resultado (requiere reinicio para actualizar).
        
        Returns:
            Dict con estructura: {
                'tables': {...},
                'relationships': [...],
                'stored_procedures': [...]
            }
        """
        if DBSchemaService._cache is not None:
            return DBSchemaService._cache
        
        schema = {
            'tables': DBSchemaService._get_tables_info(),
            'relationships': DBSchemaService._get_relationships(),
            'stored_procedures': DBSchemaService._get_stored_procedures(),
            'datetime': DBSchemaService._get_current_datetime(),
        }
        
        DBSchemaService._cache = schema
        return schema
    
    @staticmethod
    def _get_current_datetime() -> str:
        """Obtiene la fecha/hora actual del servidor."""
        with get_connection() as cn:
            cur = cn.cursor()
            cur.execute("SELECT CAST(GETDATE() AS DATE)")
            return str(cur.fetchone()[0])
    
    @staticmethod
    def _get_tables_info() -> Dict[str, Dict[str, Any]]:
        """
        Obtiene información de todas las tablas y sus columnas.
        
        Returns:
            {
                'NombreTabla': {
                    'columns': [
                        {'name': str, 'type': str, 'nullable': bool},
                        ...
                    ]
                },
                ...
            }
        """
        with get_connection() as cn:
            cur = cn.cursor()
            
            # Obtener todas las tablas y columnas
            query = """
            SELECT 
                TABLE_NAME,
                COLUMN_NAME,
                DATA_TYPE,
                IS_NULLABLE
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_SCHEMA = 'dbo'
            ORDER BY TABLE_NAME, ORDINAL_POSITION
            """
            
            cur.execute(query)
            rows = cur.fetchall()
            
            tables = {}
            for table_name, col_name, data_type, is_nullable in rows:
                if table_name not in tables:
                    tables[table_name] = {'columns': []}
                
                tables[table_name]['columns'].append({
                    'name': col_name,
                    'type': data_type,
                    'nullable': is_nullable == 'YES'
                })
            
            return tables
    
    @staticmethod
    def _get_relationships() -> List[Dict[str, str]]:
        """
        Obtiene las relaciones de clave foránea entre tablas.
        
        Returns:
            [
                {
                    'from_table': str,
                    'from_column': str,
                    'to_table': str,
                    'to_column': str
                },
                ...
            ]
        """
        with get_connection() as cn:
            cur = cn.cursor()
            
            query = """
            SELECT 
                FK.TABLE_NAME as from_table,
                CU.COLUMN_NAME as from_column,
                PK.TABLE_NAME as to_table,
                PT.COLUMN_NAME as to_column
            FROM INFORMATION_SCHEMA.REFERENTIAL_CONSTRAINTS RC
            INNER JOIN INFORMATION_SCHEMA.KEY_COLUMN_USAGE CU ON RC.CONSTRAINT_NAME = CU.CONSTRAINT_NAME
            INNER JOIN INFORMATION_SCHEMA.KEY_COLUMN_USAGE PT ON RC.UNIQUE_CONSTRAINT_NAME = PT.CONSTRAINT_NAME
            INNER JOIN INFORMATION_SCHEMA.TABLE_CONSTRAINTS FK ON CU.CONSTRAINT_NAME = FK.CONSTRAINT_NAME
            INNER JOIN INFORMATION_SCHEMA.TABLE_CONSTRAINTS PK ON PT.CONSTRAINT_NAME = PK.CONSTRAINT_NAME
            WHERE FK.TABLE_SCHEMA = 'dbo'
            """
            
            cur.execute(query)
            rows = cur.fetchall()
            
            relationships = []
            for from_table, from_col, to_table, to_col in rows:
                relationships.append({
                    'from_table': from_table,
                    'from_column': from_col,
                    'to_table': to_table,
                    'to_column': to_col
                })
            
            return relationships
    
    @staticmethod
    def _get_stored_procedures() -> List[str]:
        """
        Obtiene la lista de procedimientos almacenados disponibles.
        
        Returns:
            ['SP_Nombre1', 'SP_Nombre2', ...]
        """
        with get_connection() as cn:
            cur = cn.cursor()
            
            query = """
            SELECT ROUTINE_NAME
            FROM INFORMATION_SCHEMA.ROUTINES
            WHERE ROUTINE_SCHEMA = 'dbo'
            AND ROUTINE_TYPE = 'PROCEDURE'
            ORDER BY ROUTINE_NAME
            """
            
            cur.execute(query)
            rows = cur.fetchall()
            
            return [row[0] for row in rows]
    
    @staticmethod
    def get_schema_summary() -> str:
        """
        Retorna un resumen legible de la estructura para incluir en prompts.
        """
        schema = DBSchemaService.get_schema()
        
        summary = """
ESTRUCTURA DE BASE DE DATOS - BIBIOTECA:
==========================================

TABLAS:
"""
        
        for table_name, table_info in schema['tables'].items():
            summary += f"\n  • {table_name}:\n"
            for col in table_info['columns']:
                nullable = "✓ nullable" if col['nullable'] else "NOT NULL"
                summary += f"      - {col['name']}: {col['type']} ({nullable})\n"
        
        if schema['relationships']:
            summary += "\nRELACIONES (Foreign Keys):\n"
            for rel in schema['relationships']:
                summary += f"  • {rel['from_table']}.{rel['from_column']} → {rel['to_table']}.{rel['to_column']}\n"
        
        if schema['stored_procedures']:
            summary += "\nPROCEDIMIENTOS DISPONIBLES:\n"
            for sp in schema['stored_procedures']:
                summary += f"  • {sp}\n"
        
        summary += f"\nFECHA ACTUAL DEL SERVIDOR: {schema['datetime']}\n"
        
        return summary
    
    @staticmethod
    def get_schema_json() -> str:
        """Retorna la estructura en formato JSON puro."""
        return json.dumps(DBSchemaService.get_schema(), indent=2, default=str)
    
    @staticmethod
    def validate_column_exists(table_name: str, column_name: str) -> bool:
        """
        Valida si una columna existe en una tabla.
        
        Args:
            table_name: Nombre de la tabla
            column_name: Nombre de la columna
            
        Returns:
            True si existe, False en caso contrario
        """
        schema = DBSchemaService.get_schema()
        
        if table_name not in schema['tables']:
            return False
        
        columns = schema['tables'][table_name]['columns']
        column_names = [col['name'] for col in columns]
        
        return column_name in column_names
    
    @staticmethod
    def get_table_columns(table_name: str) -> List[str]:
        """Retorna lista de columnas de una tabla."""
        schema = DBSchemaService.get_schema()
        
        if table_name not in schema['tables']:
            return []
        
        return [col['name'] for col in schema['tables'][table_name]['columns']]
    
    @staticmethod
    def clear_cache():
        """Limpia el cache para forzar recarga de la estructura."""
        DBSchemaService._cache = None
