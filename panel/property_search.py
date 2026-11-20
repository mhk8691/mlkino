"""Shared scoped-record filters for the supplementary search and dashboard map."""
import math
from rest_framework.exceptions import ValidationError


def filter_properties(rows, params):
    from .property_api import normalize
    for key in ('propertyType', 'contractType', 'province', 'city', 'district', 'neighborhood', 'status'):
        wanted = normalize(params.get(key))
        if wanted:
            rows = [r for r in rows if wanted in [normalize(v) for v in (r.data.get(key) if isinstance(r.data.get(key), list) else [r.data.get(key)])]]
    for key in ('roomCount', 'buildYear', 'floor', 'recordId'):
        raw = params.get(key)
        if raw in ('', None):
            continue
        try:
            value = float(normalize(raw).replace(',', ''))
        except (ValueError, TypeError):
            raise ValidationError({key: 'عدد معتبر وارد کنید.'})
        if not math.isfinite(value) or value < 0 or not value.is_integer():
            raise ValidationError({key: 'عدد صحیح معتبر وارد کنید.'})
        rows = [r for r in rows if normalize(r.pk if key == 'recordId' else r.data.get(key)) == str(int(value))]
    roles = set(str(params.get('creatorRoles') or '').split('|')) - {''}
    if not roles <= {'expert', 'agency', 'user'}:
        raise ValidationError({'creatorRoles': 'نوع کاربر ثبت‌کننده معتبر نیست.'})
    if roles:
        rows = [r for r in rows if r.created_by.role in roles]
    amenities = {normalize(v) for v in str(params.get('amenities') or '').split('|') if v}
    if amenities:
        rows = [r for r in rows if amenities <= {normalize(v) for v in (r.data.get('amenities') or [])}]
    for prefix in ('area', 'price'):
        bounds = {}
        for suffix in ('From', 'To'):
            raw = params.get(prefix + suffix)
            if raw in ('', None):
                continue
            try:
                amount = float(normalize(raw).replace(',', ''))
            except (ValueError, TypeError):
                raise ValidationError({prefix + suffix: 'عدد معتبر وارد کنید.'})
            if not math.isfinite(amount) or amount < 0 or amount > 10**16:
                raise ValidationError({prefix + suffix: 'عدد معتبر وارد کنید.'})
            bounds[suffix] = amount
        if 'From' in bounds and 'To' in bounds and bounds['From'] > bounds['To']:
            raise ValidationError({prefix: 'حداکثر نباید کمتر از حداقل باشد.'})
        def matches(row):
            field = 'area' if prefix == 'area' else ('mortgagePrice' if row.data.get('contractType') == 'رهن و اجاره' else 'totalPrice')
            low = row.data.get(field, row.data.get(field + 'From'))
            high = row.data.get(field, row.data.get(field + 'To'))
            if bounds and low is None and high is None:
                return False
            return ('From' not in bounds or high is None or high >= bounds['From']) and ('To' not in bounds or low is None or low <= bounds['To'])
        rows = [r for r in rows if matches(r)]
    ordering = params.get('ordering', '-created_at')
    if ordering in ('created_at', '-created_at'):
        rows.sort(key=lambda r: (r.created_at, r.pk), reverse=ordering.startswith('-'))
    return rows
