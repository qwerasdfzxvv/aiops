from datetime import datetime, date


def json_iso_dttm_ser(obj):
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
