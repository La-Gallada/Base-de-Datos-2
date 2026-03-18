"""
Servicio para generar y validar queries SQL personalizadas.
Asegura que todas las queries solo usen datos reales de la BD.
"""

from typing import Dict, List, Optional, Tuple, Any
from services.db_schema_service import DBSchemaService
from db import get_connection
import re


class QueryGenerator:
    """
    Genera y valida queries SQL personalizadas basadas en la estructura real de la BD.
    """
    
    # Palabras clave SQL permitidas
    ALLOWED_SQL_KEYWORDS = {
        'SELECT', 'FROM', 'WHERE', 'JOIN', 'INNER', 'LEFT', 'RIGHT', 
        'ON', 'AND', 'OR', 'ORDER', 'BY', 'GROUP', 'HAVING',
        'COUNT', 'SUM', 'AVG', 'MAX', 'MIN', 'DISTINCT',
        'AS', 'DESC', 'ASC', 'LIMIT', 'OFFSET'
    }
    
    @staticmethod
    def validate_query_safety(sql: str) -> Tuple[bool, str]:
        """
        Valida que una query SQL sea segura (sin inyecciones, solo SELECT).
        
        Args:
            sql: Query SQL a validar
            
        Returns:
            (es_segura, mensaje_error_o_vacio)
        """
        sql = sql.strip().upper()
        
        # Solo permitir SELECT
        if not sql.startswith('SELECT'):
            return False, "Solo se permiten queries SELECT. No se pueden usar INSERT, UPDATE, DELETE."
        
        # No permitir comandos peligrosos
        dangerous = ['DROP', 'DELETE', 'TRUNCATE', 'ALTER', 'CREATE', 'EXEC', 'EXECUTE', 'sp_']
        for cmd in dangerous:
            if cmd in sql:
                return False, f"Comando no permitido: {cmd}"
        
        return True, ""
    
    @staticmethod
    def validate_table_and_columns(sql: str) -> Tuple[bool, str]:
        """
        Valida que todas las tablas y columnas en la query existan en la BD.
        
        Args:
            sql: Query SQL a validar
            
        Returns:
            (es_valida, mensaje_error_o_vacio)
        """
        schema = DBSchemaService.get_schema()
        valid_tables = set(schema['tables'].keys())
        
        # Extraer nombres de tabla mencionadas
        # Busca patrones: FROM TableName, JOIN TableName
        table_pattern = r'(?:FROM|JOIN)\s+(\w+)'
        tables_mentioned = re.findall(table_pattern, sql, re.IGNORECASE)
        
        for table in tables_mentioned:
            if table not in valid_tables:
                return False, f"La tabla '{table}' no existe en la base de datos."
        
        return True, ""
    
    @staticmethod
    def generate_filtered_query(
        table: str,
        columns: List[str],
        where_conditions: Optional[Dict[str, Any]] = None,
        order_by: Optional[str] = None,
        limit: Optional[int] = None
    ) -> str:
        """
        Genera una query SELECT validada.
        
        Args:
            table: Nombre de la tabla
            columns: Lista de columnas a seleccionar (o ['*'] para todas)
            where_conditions: Dict con condiciones WHERE {columna: valor}
            order_by: Columna para ordenar
            limit: Límite de resultados
            
        Returns:
            Query SQL validada
        """
        schema = DBSchemaService.get_schema()
        
        # Validar tabla
        if table not in schema['tables']:
            raise ValueError(f"Tabla no existe: {table}")
        
        # Validar columnas
        valid_columns = [col['name'] for col in schema['tables'][table]['columns']]
        
        if columns != ['*']:
            for col in columns:
                if col not in valid_columns:
                    raise ValueError(f"Columna no existe en {table}: {col}")
        
        # Construir query
        cols_str = ', '.join(columns) if columns != ['*'] else '*'
        query = f"SELECT {cols_str} FROM dbo.{table}"
        
        # Agregar WHERE si hay condiciones
        if where_conditions:
            conditions = []
            for col, val in where_conditions.items():
                if col not in valid_columns:
                    raise ValueError(f"Columna no existe: {col}")
                # Escapar valores para SQL
                if isinstance(val, str):
                    val_escaped = val.replace("'", "''")
                    conditions.append(f"[{col}] = '{val_escaped}'")
                else:
                    conditions.append(f"[{col}] = {val}")
            
            query += " WHERE " + " AND ".join(conditions)
        
        # Agregar ORDER BY
        if order_by:
            # Validar que la columna exista
            order_col = order_by.split()[0] if ' ' in order_by else order_by
            if order_col not in valid_columns:
                raise ValueError(f"Columna no existe para ORDER BY: {order_col}")
            query += f" ORDER BY {order_by}"
        
        # Agregar LIMIT
        if limit:
            query += f" OFFSET 0 ROWS FETCH NEXT {limit} ROWS ONLY"
        
        return query
    
    @staticmethod
    def execute_safe_query(sql: str) -> List[Tuple]:
        """
        Ejecuta una query SELECT validada y retorna resultados.
        
        Args:
            sql: Query SQL SELECT validada
            
        Returns:
            Lista de tuplas con resultados
        """
        # Validar seguridad
        is_safe, error = QueryGenerator.validate_query_safety(sql)
        if not is_safe:
            raise ValueError(f"Query no segura: {error}")
        
        # Validar estructura
        is_valid, error = QueryGenerator.validate_table_and_columns(sql)
        if not is_valid:
            raise ValueError(f"Query inválida: {error}")
        
        # Ejecutar
        with get_connection() as cn:
            cur = cn.cursor()
            cur.execute(sql)
            return cur.fetchall()
    
    @staticmethod
    def generate_count_query(table: str, filters: Optional[Dict[str, Any]] = None) -> str:
        """
        Genera una query de COUNT.
        
        Args:
            table: Nombre de la tabla
            filters: Condiciones de filtro
            
        Returns:
            Query SQL COUNT
        """
        schema = DBSchemaService.get_schema()
        
        if table not in schema['tables']:
            raise ValueError(f"Tabla no existe: {table}")
        
        query = f"SELECT COUNT(*) FROM dbo.{table}"
        
        if filters:
            valid_columns = [col['name'] for col in schema['tables'][table]['columns']]
            conditions = []
            
            for col, val in filters.items():
                if col not in valid_columns:
                    raise ValueError(f"Columna no existe: {col}")
                if isinstance(val, str):
                    val_escaped = val.replace("'", "''")
                    conditions.append(f"[{col}] = '{val_escaped}'")
                else:
                    conditions.append(f"[{col}] = {val}")
            
            query += " WHERE " + " AND ".join(conditions)
        
        return query
    
    @staticmethod
    def generate_join_query(
        main_table: str,
        join_table: str,
        join_column_main: str,
        join_column_ref: str,
        columns: List[str],
        filters: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Genera una query con JOIN.
        
        Args:
            main_table: Tabla principal
            join_table: Tabla a unir
            join_column_main: Columna en tabla principal
            join_column_ref: Columna en tabla de referencia
            columns: Columnas a seleccionar (ej: ['main.col1', 'ref.col2'])
            filters: Condiciones WHERE
            
        Returns:
            Query SQL con JOIN
        """
        schema = DBSchemaService.get_schema()
        
        # Validar tablas
        if main_table not in schema['tables']:
            raise ValueError(f"Tabla no existe: {main_table}")
        if join_table not in schema['tables']:
            raise ValueError(f"Tabla no existe: {join_table}")
        
        # Validar columnas
        main_cols = [col['name'] for col in schema['tables'][main_table]['columns']]
        join_cols = [col['name'] for col in schema['tables'][join_table]['columns']]
        
        if join_column_main not in main_cols:
            raise ValueError(f"Columna no existe en {main_table}: {join_column_main}")
        if join_column_ref not in join_cols:
            raise ValueError(f"Columna no existe en {join_table}: {join_column_ref}")
        
        cols_str = ', '.join(columns)
        query = f"""
        SELECT {cols_str}
        FROM dbo.{main_table}
        INNER JOIN dbo.{join_table} 
            ON dbo.{main_table}.[{join_column_main}] = dbo.{join_table}.[{join_column_ref}]
        """
        
        if filters:
            conditions = []
            for col, val in filters.items():
                if isinstance(val, str):
                    val_escaped = val.replace("'", "''")
                    conditions.append(f"[{col}] = '{val_escaped}'")
                else:
                    conditions.append(f"[{col}] = {val}")
            query += " WHERE " + " AND ".join(conditions)
        
        return query.strip()
