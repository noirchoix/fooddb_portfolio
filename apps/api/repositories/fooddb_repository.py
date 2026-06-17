from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

import duckdb
import numpy as np
import pandas as pd


NUMERIC_VECTOR_COLUMNS = [
    'p_n', 'n_compounds', 'total_idf_weight', 'mean_compound_idf',
    'p_mw_mean', 'p_mw_std', 'p_mw_min', 'p_mw_max', 'q_mw_wmean', 'q_mw_wstd',
    'p_logp_mean', 'p_logp_std', 'p_logp_min', 'p_logp_max', 'q_logp_wmean', 'q_logp_wstd',
    'p_tpsa_mean', 'p_tpsa_std', 'p_tpsa_min', 'p_tpsa_max', 'q_tpsa_wmean', 'q_tpsa_wstd',
    'p_hbd_mean', 'p_hbd_std', 'p_hbd_min', 'p_hbd_max', 'q_hbd_wmean', 'q_hbd_wstd',
    'p_hba_mean', 'p_hba_std', 'p_hba_min', 'p_hba_max', 'q_hba_wmean', 'q_hba_wstd',
    'p_num_rings_mean', 'p_num_rings_std', 'p_num_rings_min', 'p_num_rings_max', 'q_num_rings_wmean', 'q_num_rings_wstd',
    'p_num_aromatic_rings_mean', 'p_num_aromatic_rings_std', 'p_num_aromatic_rings_min', 'p_num_aromatic_rings_max',
    'q_num_aromatic_rings_wmean', 'q_num_aromatic_rings_wstd',
    'p_fraction_csp3_mean', 'p_fraction_csp3_std', 'p_fraction_csp3_min', 'p_fraction_csp3_max',
    'q_fraction_csp3_wmean', 'q_fraction_csp3_wstd', 'q_n', 'q_wsum',
]


def clean_value(value: Any) -> Any:
    if value is pd.NA:
        return None
    if isinstance(value, float) and (math.isnan(value) or math.isinf(value)):
        return None
    if isinstance(value, np.generic):
        return clean_value(value.item())
    return value


def records_from_df(df: pd.DataFrame) -> list[dict[str, Any]]:
    records = []
    for record in df.to_dict(orient='records'):
        records.append({k: clean_value(v) for k, v in record.items()})
    return records


class FoodDBRepository:
    def __init__(self, duckdb_path: Path, curated_dir: Path, max_limit: int = 500) -> None:
        self.duckdb_path = duckdb_path
        self.curated_dir = curated_dir
        self.max_limit = max_limit
        self._vector_cache: dict[str, pd.DataFrame] = {}

    def _connect(self) -> duckdb.DuckDBPyConnection:
        if not self.duckdb_path.exists():
            raise FileNotFoundError(f'FoodDB DuckDB file not found: {self.duckdb_path}')
        return duckdb.connect(str(self.duckdb_path), read_only=True)

    def _clamp_limit(self, limit: int) -> int:
        return max(1, min(int(limit), self.max_limit))

    def health(self) -> dict[str, Any]:
        with self._connect() as con:
            foods = con.execute('select count(*) from curated_food_lookup').fetchone()[0]
            compounds = con.execute('select count(*) from curated_compound_lookup').fetchone()[0]
            edges = con.execute('select count(*) from curated_food_compound_content').fetchone()[0]
        vector_rows = len(self._load_vectors('zscore')) if self._vector_file('zscore').exists() else 0
        qc_path = self.curated_dir / 'phase4_qc_report.json'
        qc_ok = None
        if qc_path.exists():
            try:
                qc_ok = bool(json.loads(qc_path.read_text(encoding='utf-8')).get('ok'))
            except Exception:
                qc_ok = None
        return {
            'ok': True,
            'database_path': str(self.duckdb_path),
            'curated_dir': str(self.curated_dir),
            'foods': foods,
            'compounds': compounds,
            'curated_edges': edges,
            'vector_rows': vector_rows,
            'available_policies': [p for p in ['raw', 'zscore', 'idf'] if self._vector_file(p).exists()],
            'qc_ok': qc_ok,
        }

    def search_foods(self, q: str, limit: int = 20) -> list[dict[str, Any]]:
        limit = self._clamp_limit(limit)
        pattern = f'%{q.strip()}%'
        with self._connect() as con:
            df = con.execute(
                '''
                select food_id, public_id, name, name_scientific, food_group, food_subgroup,
                       food_type, category, ncbi_taxonomy_id
                from curated_food_lookup
                where name ilike ? or coalesce(name_scientific, '') ilike ? or coalesce(public_id, '') ilike ?
                order by
                    case when lower(name) = lower(?) then 0
                         when name ilike ? then 1
                         else 2 end,
                    name
                limit ?
                ''',
                [pattern, pattern, pattern, q.strip(), f'{q.strip()}%', limit],
            ).fetchdf()
        return records_from_df(df)

    def resolve_food(self, q: str) -> dict[str, Any] | None:
        items = self.search_foods(q, limit=1)
        return items[0] if items else None

    def get_food(self, food_id: int) -> dict[str, Any] | None:
        with self._connect() as con:
            df = con.execute(
                '''
                select cast(id as bigint) as food_id, public_id, name, name_scientific, food_group,
                       food_subgroup, food_type, category,
                       try_cast(ncbi_taxonomy_id as bigint) as ncbi_taxonomy_id,
                       description, wikipedia_id
                from food
                where try_cast(id as bigint) = ?
                limit 1
                ''',
                [int(food_id)],
            ).fetchdf()
        records = records_from_df(df)
        return records[0] if records else None

    def food_compounds(self, food_id: int, limit: int = 100, measured_only: bool = False) -> list[dict[str, Any]]:
        limit = self._clamp_limit(limit)
        measured_clause = 'and e.standard_content is not null' if measured_only else ''
        parquet = str(self.curated_dir / 'food_compound_edges.parquet')
        with self._connect() as con:
            df = con.execute(
                f'''
                select e.food_id, e.compound_id, e.presence, e.standard_content, e.inchikey,
                       e.compound_name, e.orig_content, e.orig_unit, e.orig_min, e.orig_max,
                       e.preparation_type, e.citation, e.citation_type
                from read_parquet(?) e
                where e.food_id = ? {measured_clause}
                order by e.standard_content desc nulls last, e.compound_name asc
                limit ?
                ''',
                [parquet, int(food_id), limit],
            ).fetchdf()
        return records_from_df(df)

    def search_compounds(self, q: str, limit: int = 20) -> list[dict[str, Any]]:
        limit = self._clamp_limit(limit)
        pattern = f'%{q.strip()}%'
        with self._connect() as con:
            df = con.execute(
                '''
                select compound_id, public_id, name, cas_number, inchikey, inchi, cast(smiles as varchar) as smiles,
                       moldb_mono_mass, kingdom, superklass, klass, subklass
                from curated_compound_lookup
                where name ilike ? or coalesce(public_id, '') ilike ? or coalesce(inchikey, '') ilike ?
                   or coalesce(cas_number, '') ilike ?
                order by
                    case when lower(name) = lower(?) then 0
                         when name ilike ? then 1
                         else 2 end,
                    name
                limit ?
                ''',
                [pattern, pattern, pattern, pattern, q.strip(), f'{q.strip()}%', limit],
            ).fetchdf()
        return records_from_df(df)

    def get_compound(self, compound_id: int) -> dict[str, Any] | None:
        with self._connect() as con:
            df = con.execute(
                '''
                select l.compound_id, l.public_id, l.name, l.cas_number, l.inchikey, l.inchi, cast(l.smiles as varchar) as smiles,
                       l.moldb_mono_mass, l.kingdom, l.superklass, l.klass, l.subklass,
                       c.annotation_quality as description, c.state as annotation_quality
                from curated_compound_lookup l
                left join compound c on try_cast(c.id as bigint) = l.compound_id
                where l.compound_id = ?
                limit 1
                ''',
                [int(compound_id)],
            ).fetchdf()
        records = records_from_df(df)
        return records[0] if records else None

    def compound_foods(self, compound_id: int, limit: int = 100, measured_only: bool = False) -> list[dict[str, Any]]:
        limit = self._clamp_limit(limit)
        measured_clause = 'and c.standard_content is not null' if measured_only else ''
        with self._connect() as con:
            df = con.execute(
                f'''
                select c.food_id, f.name as food_name, f.food_group, f.food_subgroup,
                       c.compound_id, c.standard_content, c.orig_content, c.orig_unit,
                       c.preparation_type, c.citation, c.citation_type
                from curated_food_compound_content c
                join curated_food_lookup f on f.food_id = c.food_id
                where c.compound_id = ? {measured_clause}
                order by c.standard_content desc nulls last, f.name asc
                limit ?
                ''',
                [int(compound_id), limit],
            ).fetchdf()
        return records_from_df(df)

    def bio_links(self, compound_id: int, limit_per_kind: int = 50) -> list[dict[str, Any]]:
        limit_per_kind = self._clamp_limit(limit_per_kind)
        links: list[dict[str, Any]] = []
        files = {
            'health_effect': self.curated_dir / 'compound_health_effect_edges.parquet',
            'flavor': self.curated_dir / 'compound_flavor_edges.parquet',
            'enzyme': self.curated_dir / 'compound_enzyme_edges.parquet',
            'pathway': self.curated_dir / 'compound_pathway_edges.parquet',
        }
        with self._connect() as con:
            if files['health_effect'].exists():
                df = con.execute(
                    '''select 'health_effect' as kind, health_effect_id as id, health_effect_name as name,
                              null as "group", null as category, null as gene_name, null as uniprot_id,
                              null as kegg_map_id, null as smpdb_id, citation, citation_type
                       from read_parquet(?) where compound_id = ? limit ?''',
                    [str(files['health_effect']), int(compound_id), limit_per_kind],
                ).fetchdf()
                links.extend(records_from_df(df))
            if files['flavor'].exists():
                df = con.execute(
                    '''select 'flavor' as kind, flavor_id as id, flavor_name as name,
                              flavor_group as "group", flavor_category as category, null as gene_name, null as uniprot_id,
                              null as kegg_map_id, null as smpdb_id, citations as citation, null as citation_type
                       from read_parquet(?) where compound_id = ? limit ?''',
                    [str(files['flavor']), int(compound_id), limit_per_kind],
                ).fetchdf()
                links.extend(records_from_df(df))
            if files['enzyme'].exists():
                df = con.execute(
                    '''select 'enzyme' as kind, enzyme_id as id, enzyme_name as name,
                              null as "group", null as category, gene_name, uniprot_id,
                              null as kegg_map_id, null as smpdb_id, null as citation, null as citation_type
                       from read_parquet(?) where compound_id = ? limit ?''',
                    [str(files['enzyme']), int(compound_id), limit_per_kind],
                ).fetchdf()
                links.extend(records_from_df(df))
            if files['pathway'].exists():
                df = con.execute(
                    '''select 'pathway' as kind, pathway_id as id, pathway_name as name,
                              null as "group", null as category, null as gene_name, null as uniprot_id,
                              kegg_map_id, smpdb_id, null as citation, null as citation_type
                       from read_parquet(?) where compound_id = ? limit ?''',
                    [str(files['pathway']), int(compound_id), limit_per_kind],
                ).fetchdf()
                links.extend(records_from_df(df))
        return links

    def _vector_file(self, policy: str) -> Path:
        if policy == 'raw':
            return self.curated_dir / 'food_descriptor_vectors.parquet'
        if policy == 'zscore':
            return self.curated_dir / 'food_descriptor_vectors_zscore.parquet'
        if policy == 'idf':
            return self.curated_dir / 'food_descriptor_vectors_idf.parquet'
        raise ValueError(f'Unsupported vector policy: {policy}')

    def _load_vectors(self, policy: str) -> pd.DataFrame:
        if policy in self._vector_cache:
            return self._vector_cache[policy]
        path = self._vector_file(policy)
        if not path.exists():
            raise FileNotFoundError(f'Food descriptor vector artifact not found: {path}')
        df = duckdb.sql(f"select * from read_parquet('{path}')").fetchdf()
        df['food_id'] = pd.to_numeric(df['food_id'], errors='coerce').astype('Int64')
        self._vector_cache[policy] = df
        return df

    def vector_for_food(self, food_id: int, policy: str = 'zscore') -> dict[str, Any] | None:
        df = self._load_vectors(policy)
        match = df[df['food_id'] == int(food_id)]
        if match.empty:
            return None
        row = records_from_df(match.head(1))[0]
        metrics = {k: v for k, v in row.items() if k not in {'food_id', 'vector_policy', 'similarity_policy'}}
        return {
            'food_id': int(food_id),
            'policy': policy,
            'vector_policy': row.get('vector_policy') or policy,
            'similarity_policy': row.get('similarity_policy'),
            'metrics': metrics,
        }

    def compare_foods(self, food_id_a: int, food_id_b: int, policy: str = 'zscore') -> tuple[float, dict[str, float]] | None:
        df = self._load_vectors(policy)
        a = df[df['food_id'] == int(food_id_a)]
        b = df[df['food_id'] == int(food_id_b)]
        if a.empty or b.empty:
            return None
        cols = self._usable_vector_columns(df)
        av = a.iloc[0][cols].astype(float).fillna(0).to_numpy()
        bv = b.iloc[0][cols].astype(float).fillna(0).to_numpy()
        sim = self._cosine(av, bv)
        metric_deltas = {}
        for col in cols[:36]:
            delta = clean_value(float(b.iloc[0][col]) - float(a.iloc[0][col])) if pd.notna(a.iloc[0][col]) and pd.notna(b.iloc[0][col]) else None
            if delta is not None:
                metric_deltas[col] = delta
        return sim, metric_deltas

    def similar_foods(self, food_id: int, policy: str = 'zscore', top_k: int = 10) -> list[dict[str, Any]]:
        top_k = self._clamp_limit(top_k)
        df = self._load_vectors(policy)
        base = df[df['food_id'] == int(food_id)]
        if base.empty:
            return []
        cols = self._usable_vector_columns(df)
        matrix = df[cols].astype(float).fillna(0).to_numpy()
        target = base.iloc[0][cols].astype(float).fillna(0).to_numpy()
        denom = np.linalg.norm(matrix, axis=1) * np.linalg.norm(target)
        sims = np.divide(matrix @ target, denom, out=np.zeros(len(df)), where=denom != 0)
        ranked = df.assign(similarity=sims)
        ranked = ranked[ranked['food_id'] != int(food_id)].sort_values('similarity', ascending=False).head(top_k)
        food_ids = [int(x) for x in ranked['food_id'].dropna().tolist()]
        foods = self.foods_by_ids(food_ids)
        food_map = {int(f['food_id']): f for f in foods}
        results = []
        for record in records_from_df(ranked):
            fid = int(record['food_id'])
            if fid in food_map:
                vector_preview = {k: record.get(k) for k in ['p_mw_mean', 'p_logp_mean', 'p_tpsa_mean', 'p_hbd_mean', 'p_hba_mean', 'q_mw_wmean', 'q_logp_wmean'] if k in record}
                results.append({'food': food_map[fid], 'similarity': float(record['similarity']), 'vector': vector_preview})
        return results

    def foods_by_ids(self, food_ids: list[int]) -> list[dict[str, Any]]:
        if not food_ids:
            return []
        placeholders = ','.join(['?'] * len(food_ids))
        with self._connect() as con:
            df = con.execute(
                f'''select food_id, public_id, name, name_scientific, food_group, food_subgroup,
                           food_type, category, ncbi_taxonomy_id
                    from curated_food_lookup where food_id in ({placeholders})''',
                food_ids,
            ).fetchdf()
        records = records_from_df(df)
        order = {fid: idx for idx, fid in enumerate(food_ids)}
        return sorted(records, key=lambda x: order.get(int(x['food_id']), 999999))

    def _usable_vector_columns(self, df: pd.DataFrame) -> list[str]:
        return [col for col in NUMERIC_VECTOR_COLUMNS if col in df.columns]

    @staticmethod
    def _cosine(a: np.ndarray, b: np.ndarray) -> float:
        denom = float(np.linalg.norm(a) * np.linalg.norm(b))
        if denom == 0:
            return 0.0
        return float(np.dot(a, b) / denom)
