"""
Servicio para obtener y cachear la estructura de la base de datos.
Incluye tablas, vistas, índices, relaciones y procedimientos almacenados.
"""

import json
from typing import Dict, List, Optional, Any
from db import get_connection


class DBSchemaService:
    _cache: Optional[Dict[str, Any]] = None

    @staticmethod
    def get_schema() -> Dict[str, Any]:
        if DBSchemaService._cache is not None:
            return DBSchemaService._cache

        schema = {
            'tables':              DBSchemaService._get_tables_info(),
            'views':               DBSchemaService._get_views_info(),
            'indexes':             DBSchemaService._get_indexes_info(),
            'relationships':       DBSchemaService._get_relationships(),
            'stored_procedures':   DBSchemaService._get_stored_procedures(),
            'datetime':            DBSchemaService._get_current_datetime(),
        }

        DBSchemaService._cache = schema
        return schema

    # ─────────────────────────────────────────────
    # DATETIME
    # ─────────────────────────────────────────────

    @staticmethod
    def _get_current_datetime() -> str:
        with get_connection() as cn:
            cur = cn.cursor()
            cur.execute("SELECT CAST(GETDATE() AS DATE)")
            return str(cur.fetchone()[0])

    # ─────────────────────────────────────────────
    # TABLAS
    # ─────────────────────────────────────────────

    @staticmethod
    def _get_tables_info() -> Dict[str, Dict[str, Any]]:
        with get_connection() as cn:
            cur = cn.cursor()
            cur.execute("""
                SELECT 
                    TABLE_NAME,
                    COLUMN_NAME,
                    DATA_TYPE,
                    IS_NULLABLE
                FROM INFORMATION_SCHEMA.COLUMNS
                WHERE TABLE_SCHEMA = 'dbo'
                  AND TABLE_NAME NOT IN (
                      SELECT TABLE_NAME FROM INFORMATION_SCHEMA.VIEWS
                  )
                ORDER BY TABLE_NAME, ORDINAL_POSITION
            """)
            rows = cur.fetchall()

        tables = {}
        for table_name, col_name, data_type, is_nullable in rows:
            if table_name not in tables:
                tables[table_name] = {'columns': []}
            tables[table_name]['columns'].append({
                'name':     col_name,
                'type':     data_type,
                'nullable': is_nullable == 'YES'
            })
        return tables

    # ─────────────────────────────────────────────
    # VISTAS  ← NUEVO
    # ─────────────────────────────────────────────

    @staticmethod
    def _get_views_info() -> Dict[str, Dict[str, Any]]:
        """
        Lee todas las vistas de la BD con sus columnas.
        Esto permite que la IA sepa que puede usar vw_BooksFull,
        vw_ActiveLoans, vw_OverdueLoans y vw_AuthorLoanStats.
        """
        with get_connection() as cn:
            cur = cn.cursor()

            # Nombres de vistas
            cur.execute("""
                SELECT TABLE_NAME
                FROM INFORMATION_SCHEMA.VIEWS
                WHERE TABLE_SCHEMA = 'dbo'
                ORDER BY TABLE_NAME
            """)
            view_names = [r[0] for r in cur.fetchall()]

            # Columnas de cada vista
            cur.execute("""
                SELECT 
                    c.TABLE_NAME,
                    c.COLUMN_NAME,
                    c.DATA_TYPE
                FROM INFORMATION_SCHEMA.COLUMNS c
                INNER JOIN INFORMATION_SCHEMA.VIEWS v
                    ON c.TABLE_NAME = v.TABLE_NAME
                   AND c.TABLE_SCHEMA = v.TABLE_SCHEMA
                WHERE c.TABLE_SCHEMA = 'dbo'
                ORDER BY c.TABLE_NAME, c.ORDINAL_POSITION
            """)
            col_rows = cur.fetchall()

        views = {name: {'columns': []} for name in view_names}
        for view_name, col_name, data_type in col_rows:
            if view_name in views:
                views[view_name]['columns'].append({
                    'name': col_name,
                    'type': data_type
                })
        return views

    # ─────────────────────────────────────────────
    # ÍNDICES  ← NUEVO
    # ─────────────────────────────────────────────

    @staticmethod
    def _get_indexes_info() -> List[Dict[str, str]]:
        """
        Lee los índices de la BD.
        Le indica a la IA qué columnas están optimizadas para búsquedas.
        """
        with get_connection() as cn:
            cur = cn.cursor()
            cur.execute("""
                SELECT 
                    t.name  AS table_name,
                    i.name  AS index_name,
                    c.name  AS column_name,
                    i.type_desc
                FROM sys.indexes i
                INNER JOIN sys.index_columns ic ON i.object_id = ic.object_id
                                               AND i.index_id  = ic.index_id
                INNER JOIN sys.columns c        ON ic.object_id = c.object_id
                                               AND ic.column_id = c.column_id
                INNER JOIN sys.tables t         ON i.object_id  = t.object_id
                WHERE i.is_primary_key = 0
                  AND i.name IS NOT NULL
                  AND t.schema_id = SCHEMA_ID('dbo')
                ORDER BY t.name, i.name, ic.key_ordinal
            """)
            rows = cur.fetchall()

        indexes = []
        for table_name, index_name, column_name, type_desc in rows:
            indexes.append({
                'table':  table_name,
                'index':  index_name,
                'column': column_name,
                'type':   type_desc
            })
        return indexes

    # ─────────────────────────────────────────────
    # RELACIONES
    # ─────────────────────────────────────────────

    @staticmethod
    def _get_relationships() -> List[Dict[str, str]]:
        with get_connection() as cn:
            cur = cn.cursor()
            cur.execute("""
                SELECT 
                    FK.TABLE_NAME  AS from_table,
                    CU.COLUMN_NAME AS from_column,
                    PK.TABLE_NAME  AS to_table,
                    PT.COLUMN_NAME AS to_column
                FROM INFORMATION_SCHEMA.REFERENTIAL_CONSTRAINTS RC
                INNER JOIN INFORMATION_SCHEMA.KEY_COLUMN_USAGE CU
                    ON RC.CONSTRAINT_NAME = CU.CONSTRAINT_NAME
                INNER JOIN INFORMATION_SCHEMA.KEY_COLUMN_USAGE PT
                    ON RC.UNIQUE_CONSTRAINT_NAME = PT.CONSTRAINT_NAME
                INNER JOIN INFORMATION_SCHEMA.TABLE_CONSTRAINTS FK
                    ON CU.CONSTRAINT_NAME = FK.CONSTRAINT_NAME
                INNER JOIN INFORMATION_SCHEMA.TABLE_CONSTRAINTS PK
                    ON PT.CONSTRAINT_NAME = PK.CONSTRAINT_NAME
                WHERE FK.TABLE_SCHEMA = 'dbo'
            """)
            rows = cur.fetchall()

        return [
            {'from_table': r[0], 'from_column': r[1],
             'to_table':   r[2], 'to_column':   r[3]}
            for r in rows
        ]

    # ─────────────────────────────────────────────
    # STORED PROCEDURES
    # ─────────────────────────────────────────────

    @staticmethod
    def _get_stored_procedures() -> List[str]:
        with get_connection() as cn:
            cur = cn.cursor()
            cur.execute("""
                SELECT ROUTINE_NAME
                FROM INFORMATION_SCHEMA.ROUTINES
                WHERE ROUTINE_SCHEMA = 'dbo'
                  AND ROUTINE_TYPE = 'PROCEDURE'
                ORDER BY ROUTINE_NAME
            """)
            return [r[0] for r in cur.fetchall()]

    # ─────────────────────────────────────────────
    # SUMMARY PARA EL PROMPT DE OLLAMA
    # ─────────────────────────────────────────────

    @staticmethod
    def get_schema_summary() -> str:
        """
        Genera el texto que se inyecta en el prompt de Ollama.
        Incluye tablas, vistas e índices para que la IA
        pueda aprovechar todas las estructuras de la BD.
        """
        schema = DBSchemaService.get_schema()

        lines = [
            "ESTRUCTURA DE BASE DE DATOS - BIBLIOTECA:",
            "==========================================",
            "",
            "TABLAS:",
        ]

        for table_name, info in schema['tables'].items():
            lines.append(f"\n  • {table_name}:")
            for col in info['columns']:
                nullable = "nullable" if col['nullable'] else "NOT NULL"
                lines.append(f"      - {col['name']}: {col['type']} ({nullable})")

        # ── Vistas ──────────────────────────────────────────────────────
        if schema['views']:
            lines += ["", "VISTAS (úsalas en lugar de hacer JOINs manuales):"]
            for view_name, info in schema['views'].items():
                cols = ", ".join(c['name'] for c in info['columns'])
                lines.append(f"  • {view_name}  →  columnas: {cols}")

            lines += [
                "",
                "  Cuándo usar cada vista:",
                "  - vw_BooksFull        → para listar o buscar libros con su categoría",
                "  - vw_ActiveLoans      → para ver préstamos activos (Estado='Prestado')",
                "  - vw_OverdueLoans     → para ver préstamos vencidos directamente",
                "  - vw_AuthorLoanStats  → para estadísticas de préstamos por autor y periodo",
            ]

        # ── Índices ─────────────────────────────────────────────────────
        if schema['indexes']:
            lines += ["", "ÍNDICES DISPONIBLES (columnas optimizadas para búsqueda):"]
            # Agrupar por tabla para que sea legible
            by_table: Dict[str, List[str]] = {}
            for idx in schema['indexes']:
                key = idx['table']
                if key not in by_table:
                    by_table[key] = []
                by_table[key].append(f"{idx['index']} ({idx['column']})")
            for table, idxs in by_table.items():
                lines.append(f"  • {table}: {', '.join(idxs)}")

        # ── Relaciones ───────────────────────────────────────────────────
        if schema['relationships']:
            lines += ["", "RELACIONES (Foreign Keys):"]
            for rel in schema['relationships']:
                lines.append(
                    f"  • {rel['from_table']}.{rel['from_column']} "
                    f"→ {rel['to_table']}.{rel['to_column']}"
                )

        # ── Stored Procedures ────────────────────────────────────────────
        if schema['stored_procedures']:
            lines += ["", "PROCEDIMIENTOS DISPONIBLES:"]
            for sp in schema['stored_procedures']:
                lines.append(f"  • {sp}")

        lines += ["", f"FECHA ACTUAL DEL SERVIDOR: {schema['datetime']}"]

        return "\n".join(lines)

    # ─────────────────────────────────────────────
    # UTILIDADES
    # ─────────────────────────────────────────────

    @staticmethod
    def get_schema_json() -> str:
        return json.dumps(DBSchemaService.get_schema(), indent=2, default=str)

    @staticmethod
    def validate_column_exists(table_name: str, column_name: str) -> bool:
        schema = DBSchemaService.get_schema()
        if table_name not in schema['tables']:
            return False
        return column_name in [c['name'] for c in schema['tables'][table_name]['columns']]

    @staticmethod
    def get_table_columns(table_name: str) -> List[str]:
        schema = DBSchemaService.get_schema()
        if table_name not in schema['tables']:
            return []
        return [c['name'] for c in schema['tables'][table_name]['columns']]

    @staticmethod
    def clear_cache():
        """Limpia el cache para forzar recarga tras cambios en la BD."""
        DBSchemaService._cache = None