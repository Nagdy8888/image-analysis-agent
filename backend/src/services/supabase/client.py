"""Supabase PostgreSQL client: upsert, get, list tag records."""
import json
import logging

import psycopg2
from psycopg2.extras import RealDictCursor

from .settings import DATABASE_URI, SUPABASE_ENABLED

logger = logging.getLogger(__name__)


def build_search_index(tag_record: dict) -> list[str]:
    """Flatten all tag values from tag_record for search. Include parent + child for hierarchical."""
    out: set[str] = set()
    if not tag_record:
        return []

    for key in ("season", "theme", "design_elements", "occasion", "mood"):
        val = tag_record.get(key)
        if isinstance(val, list):
            for v in val:
                if isinstance(v, str):
                    out.add(v)

    for key in ("objects", "dominant_colors"):
        val = tag_record.get(key)
        if isinstance(val, list):
            for item in val:
                if isinstance(item, dict):
                    p = item.get("parent")
                    c = item.get("child")
                    if p:
                        out.add(p)
                    if c:
                        out.add(c)

    pt = tag_record.get("product_type")
    if isinstance(pt, dict):
        if pt.get("parent"):
            out.add(pt["parent"])
        if pt.get("child"):
            out.add(pt["child"])

    return sorted(out)


class SupabaseClient:
    """PostgreSQL client for image_tags table."""

    def __init__(self, database_uri: str | None = None):
        self._uri = database_uri or DATABASE_URI
        if not self._uri:
            raise ValueError("DATABASE_URI is required for SupabaseClient")

    def _conn(self):
        return psycopg2.connect(self._uri)

    def upsert_tag_record(
        self,
        image_id: str,
        tag_record: dict,
        image_url: str | None = None,
        needs_review: bool = False,
        processing_status: str = "complete",
    ) -> None:
        """Insert or update a row in image_tags."""
        search_index = build_search_index(tag_record)
        tag_record_json = json.dumps(tag_record)
        conn = self._conn()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO image_tags (image_id, tag_record, search_index, image_url, needs_review, processing_status, updated_at)
                    VALUES (%s, %s::jsonb, %s, %s, %s, %s, NOW())
                    ON CONFLICT (image_id) DO UPDATE SET
                      tag_record = EXCLUDED.tag_record,
                      search_index = EXCLUDED.search_index,
                      image_url = EXCLUDED.image_url,
                      needs_review = EXCLUDED.needs_review,
                      processing_status = EXCLUDED.processing_status,
                      updated_at = NOW()
                    """,
                    (image_id, tag_record_json, search_index, image_url, needs_review, processing_status),
                )
            conn.commit()
        except Exception as e:
            conn.rollback()
            logger.exception("upsert_tag_record failed: %s", e)
            raise
        finally:
            conn.close()

    def get_tag_record(self, image_id: str) -> dict | None:
        """Return one row as dict or None."""
        conn = self._conn()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    "SELECT image_id, tag_record, search_index, image_url, needs_review, processing_status, created_at, updated_at FROM image_tags WHERE image_id = %s",
                    (image_id,),
                )
                row = cur.fetchone()
                if row is None:
                    return None
                d = dict(row)
                return d
        finally:
            conn.close()

    def list_tag_images(self, limit: int = 20, offset: int = 0) -> list[dict]:
        """Return rows ordered by created_at DESC."""
        conn = self._conn()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    "SELECT image_id, tag_record, search_index, image_url, needs_review, processing_status, created_at, updated_at FROM image_tags ORDER BY created_at DESC LIMIT %s OFFSET %s",
                    (limit, offset),
                )
                rows = cur.fetchall()
            return [dict(row) for row in rows]
        finally:
            conn.close()


def get_client() -> SupabaseClient | None:
    """Return a SupabaseClient if DATABASE_URI is set, else None."""
    if not SUPABASE_ENABLED:
        return None
    try:
        return SupabaseClient()
    except Exception as e:
        logger.warning("Supabase client not available: %s", e)
        return None
