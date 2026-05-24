# apps/api/app/routers/hospitals.py
"""Hospital search and details endpoints.

This router attempts to use the real database-backed repositories and the
`ranking` service. If the database does not have matching data the endpoints
fall back to the demo catalog so the product remains usable in development.
"""

from typing import Optional, List
from hashlib import sha256

from fastapi import APIRouter, Query, Depends
from sqlalchemy.ext.asyncio import AsyncSession
import aioredis
import json

from app.db import get_session
from app.dependencies.auth import get_optional_user
from app.repositories.normalizer import NormalizerRepository
from app.repositories.procedure import ProcedureRepository
from app.repositories.hospital import HospitalRepository
from app.repositories.audit import AuditRepository
from app.services import demo_catalog
from app.services import ranking as ranking_service
from app.config import settings

router = APIRouter()


def _hash_params(params: dict) -> str:
    s = json.dumps(params, sort_keys=True, separators=(",", ":"))
    return sha256(s.encode("utf-8")).hexdigest()


@router.get("/search")
async def search_hospitals(
    procedure_code: str = Query(...),
    country: Optional[str] = None,
    lat: Optional[float] = Query(None, alias="latitude"),
    lng: Optional[float] = Query(None, alias="longitude"),
    radius_km: int = Query(100),
    session: AsyncSession = Depends(get_session),
    current_user=Depends(get_optional_user),
):
    """Search hospitals by procedure code (CPT/ICD/UHI) and optional location.

    Returns top candidates ranked by success-adjusted value. Results are cached
    for 5 minutes in Redis.
    """
    params = {
        "procedure_code": procedure_code,
        "country": country,
        "lat": lat,
        "lng": lng,
        "radius_km": radius_km,
    }

    cache_key = f"search:{_hash_params(params)}"

    # Try Redis cache
    redis = None
    try:
        if settings.redis_url:
            redis = aioredis.from_url(settings.redis_url)
            cached = await redis.get(cache_key)
            if cached:
                data = json.loads(cached)
                # Log audit asynchronously but don't block returning cached data
                try:
                    audit_repo = AuditRepository(session)
                    await audit_repo.log_action(
                        user_id=(getattr(current_user, "id", None) if current_user else None),
                        action="HOSPITAL_SEARCH",
                        resource_type="HospitalSearch",
                        resource_id=cache_key,
                    )
                except Exception:
                    pass
                return {"procedure_code": procedure_code, "count": len(data), "hospitals": data}
    except Exception:
        # Redis is best-effort
        redis = None

    # Resolve normalizer (try CPT then ICD-10)
    normalizer_repo = NormalizerRepository(session)
    normalizer = await normalizer_repo.find_by_cpt_code(procedure_code)
    if not normalizer:
        normalizer = await normalizer_repo.find_by_icd10_code(procedure_code)

    candidates: List[dict] = []

    if normalizer:
        proc_repo = ProcedureRepository(session)
        hosp_repo = HospitalRepository(session)

        # Query procedure prices for this normalizer
        from sqlalchemy import select
        from app.models import ProcedurePrice, GlobalHospital

        q = select(ProcedurePrice, GlobalHospital).join(GlobalHospital).where(
            ProcedurePrice.normalizer_id == normalizer.id,
            GlobalHospital.is_active == True,
            GlobalHospital.is_deleted == False,
        )

        if country:
            q = q.where(GlobalHospital.country_code == country.upper())

        result = await session.execute(q)
        rows = result.all()

        # Build candidate dicts
        for proc, hosp in rows:
            total = proc.base_price or 0.0
            total += proc.facility_fee or 0.0
            total += proc.anesthesia_fee or 0.0
            total += proc.surgeon_fee or 0.0

            candidate = {
                "hospital_id": hosp.id,
                "hospital_name": hosp.name,
                "country_code": hosp.country_code,
                "city": hosp.city,
                "state_province": hosp.state_province,
                "jci_accredited": hosp.jci_accredited,
                "nabh_accredited": hosp.nabh_accredited,
                "latitude": hosp.latitude,
                "longitude": hosp.longitude,
                "price": total,
                "currency_code": proc.currency_code or "USD",
                "success_rate": proc.success_rate,
                "complication_rate": proc.complication_rate,
                "estimated_total_usd": getattr(proc, "estimated_total_usd", None) or None,
                "clinical_category": normalizer.clinical_category,
                "complexity_score": normalizer.complexity_score,
            }

            # Optionally compute geographic distance if lat/lng provided
            if lat is not None and lng is not None and hosp.latitude is not None and hosp.longitude is not None:
                # Haversine distance in km
                from math import radians, sin, cos, asin, sqrt

                lon1, lat1, lon2, lat2 = map(radians, [lng, lat, hosp.longitude, hosp.latitude])
                dlon = lon2 - lon1
                dlat = lat2 - lat1
                a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
                c = 2 * asin(sqrt(a))
                km = 6371 * c
                candidate["distance_km"] = round(km, 2)
                if km > radius_km:
                    continue

            candidates.append(candidate)

    # If no candidates from DB, fall back to demo catalog
    if not candidates:
        demo_countries = [country] if country else None
        demo_results = demo_catalog.search_hospitals(procedure_code, countries=demo_countries)
        # attach search context if provided
        for d in demo_results:
            if lat is not None and lng is not None:
                d["search_context"] = {"latitude": lat, "longitude": lng, "radius_km": radius_km}

        # Compute ranking for demo results using our ranking service
        ranked_demo = ranking_service.compute_success_adjusted_scores(demo_results)
        # Cache and audit
        if redis:
            try:
                await redis.set(cache_key, json.dumps(ranked_demo), ex=300)
            except Exception:
                pass

        try:
            audit_repo = AuditRepository(session)
            await audit_repo.log_action(
                user_id=(getattr(current_user, "id", None) if current_user else None),
                action="HOSPITAL_SEARCH",
                resource_type="HospitalSearch",
                resource_id=cache_key,
            )
        except Exception:
            pass

        return {"procedure_code": procedure_code, "count": len(ranked_demo), "hospitals": ranked_demo}

    # Compute ranking for DB candidates
    ranked = ranking_service.compute_success_adjusted_scores(candidates)
    top = ranked[:20]

    # Cache result
    if redis:
        try:
            await redis.set(cache_key, json.dumps(top), ex=300)
        except Exception:
            pass

    # Audit log
    try:
        audit_repo = AuditRepository(session)
        await audit_repo.log_action(
            user_id=(getattr(current_user, "id", None) if current_user else None),
            action="HOSPITAL_SEARCH",
            resource_type="HospitalSearch",
            resource_id=cache_key,
        )
    except Exception:
        pass

    return {"procedure_code": procedure_code, "count": len(top), "hospitals": top}


@router.get("/{hospital_id}")
async def get_hospital(hospital_id: str, session: AsyncSession = Depends(get_session)):
    """Get hospital details including accreditation and procedures."""
    hosp_repo = HospitalRepository(session)
    proc_repo = ProcedureRepository(session)

    hospital = await hosp_repo.get_by_id(hospital_id)
    if not hospital:
        # Fallback to demo data
        demo = demo_catalog.get_hospital(hospital_id)
        if not demo:
            return {"hospital_id": hospital_id, "found": False, "departments": []}
        return {"found": True, "hospital": demo, "departments": demo_catalog.get_departments(hospital_id)}

    procedures = await proc_repo.list_by_hospital(hospital.id)
    procs = []
    for p in procedures:
        procs.append(
            {
                "procedure_id": p.id,
                "normalizer_id": p.normalizer_id,
                "base_price": p.base_price,
                "facility_fee": p.facility_fee,
                "anesthesia_fee": p.anesthesia_fee,
                "surgeon_fee": p.surgeon_fee,
                "currency_code": p.currency_code,
                "success_rate": p.success_rate,
                "complication_rate": p.complication_rate,
            }
        )

    return {"found": True, "hospital": {
        "id": hospital.id,
        "name": hospital.name,
        "country_code": hospital.country_code,
        "city": hospital.city,
        "state_province": hospital.state_province,
        "latitude": hospital.latitude,
        "longitude": hospital.longitude,
        "jci_accredited": hospital.jci_accredited,
        "nabh_accredited": hospital.nabh_accredited,
    }, "procedures": procs}


@router.get("/{hospital_id}/departments")
async def get_departments(hospital_id: str, session: AsyncSession = Depends(get_session)):
    hosp_repo = HospitalRepository(session)
    hospital = await hosp_repo.get_by_id(hospital_id)
    if not hospital:
        return {"hospital_id": hospital_id, "departments": []}

    # use ORM relationship loaded lazily
    depts = []
    for d in getattr(hospital, "departments", []) or []:
        depts.append({"id": d.id, "name": d.name, "specialization_code": d.specialization_code, "phone": d.phone})

    return {"hospital_id": hospital_id, "departments": depts}
