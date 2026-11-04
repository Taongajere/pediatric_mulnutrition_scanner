
import csv
import sqlite3


def _export_visits(db_path, filename, child_id=None):
    """Export screening visits for one child or all children."""

    query = """
        SELECT
            c.child_id,
            c.date_of_birth,
            c.sex,
            c.registration_date,
            sv.visit_id,
            sv.visit_date,
            sv.visit_type,
            sv.age_in_months_at_visit,
            m.weight_kg,
            m.height_length_cm,
            m.muac_mm,
            m.oedema_status,
            m.measurement_position,
            na.waz,
            na.haz,
            na.whz,
            na.muac_classification,
            na.overall_flag
        FROM children AS c
        INNER JOIN screening_visits AS sv
            ON sv.child_id = c.child_id
        LEFT JOIN measurements AS m
            ON m.visit_id = sv.visit_id
        LEFT JOIN nutritional_assessment AS na
            ON na.visit_id = sv.visit_id
    """

    params = ()

    if child_id:
        query += " WHERE c.child_id = ?"
        params = (child_id.strip().upper(),)

    query += """
        ORDER BY c.child_id ASC,
                 sv.visit_date ASC,
                 sv.visit_id ASC
    """

    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.execute(query, params)
            columns = [col[0] for col in cursor.description]
            rows = cursor.fetchall()

        if not rows:
            return 0

        with open(filename, "w", newline="", encoding="utf-8-sig") as file:
            writer = csv.writer(file)
            writer.writerow(columns)
            writer.writerows(rows)

        return len(rows)

    except (sqlite3.Error, OSError) as exc:
        print(f"Export failed: {exc}")
        return None


def export_child_visits_to_csv(db_path, child_id, filename):
    """Export all screening visits for one child."""
    return _export_visits(db_path, filename, child_id)


def export_all_visits_to_csv(db_path, filename):
    """Export all children's screening visits."""
    return _export_visits(db_path, filename)
