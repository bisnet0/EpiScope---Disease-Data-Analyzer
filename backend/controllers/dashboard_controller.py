from flask import request, jsonify
from flask_jwt_extended import jwt_required
from sqlalchemy import func
from datetime import datetime, timedelta, timezone
from backend.models.user_model import db
from backend.models.diagnosis_model import ArbovirusDiagnosis, GlaucomaDiagnosis
from backend.models.ml_log_model import ModelTrainingLog


def get_dashboard_stats():
    try:
        period = request.args.get("period", "all")
        model_filter = request.args.get("model", "all")

        start_date = None
        if period == "24h":
            start_date = datetime.utcnow() - timedelta(hours=24)
        elif period == "7d":
            start_date = datetime.utcnow() - timedelta(days=7)
        elif period == "30d":
            start_date = datetime.utcnow() - timedelta(days=30)

        query_arbo = ArbovirusDiagnosis.query
        query_glaucoma = GlaucomaDiagnosis.query
        query_logs = ModelTrainingLog.query

        if start_date:
            query_arbo = query_arbo.filter(ArbovirusDiagnosis.created_at >= start_date)
            query_glaucoma = query_glaucoma.filter(
                GlaucomaDiagnosis.created_at >= start_date
            )
            query_logs = query_logs.filter(ModelTrainingLog.created_at >= start_date)

        if model_filter != "all":
            query_logs = query_logs.filter(
                ModelTrainingLog.model_name.ilike(f"%{model_filter}%")
            )

        total_arbovirus = query_arbo.count()
        total_glaucoma = query_glaucoma.count()
        total_diagnoses = total_arbovirus + total_glaucoma

        best_accuracy_query = query_logs.with_entities(
            func.max(ModelTrainingLog.accuracy)
        ).scalar()
        best_accuracy = float(best_accuracy_query) if best_accuracy_query else 0.0

        total_trainings = query_logs.count()

        model_stats = (
            query_logs.with_entities(
                ModelTrainingLog.model_name, func.avg(ModelTrainingLog.accuracy)
            )
            .group_by(ModelTrainingLog.model_name)
            .all()
        )

        model_performance = []
        for m in model_stats:
            clean_name = (
                m[0]
                .replace("Arbovirus_", "")
                .replace("Glaucoma_", "")
                .replace("_", " ")
            )
            model_performance.append(
                {"name": clean_name, "accuracy": round(m[1] * 100, 2)}
            )

        timeline_query = (
            query_logs.order_by(ModelTrainingLog.created_at.asc()).limit(100).all()
        )
        timeline = [
            {
                "id": log.id,
                "date": log.created_at.replace(tzinfo=timezone.utc).isoformat(),
                "accuracy": round(log.accuracy * 100, 2),
                "model": log.model_name.replace("Arbovirus_", "").replace(
                    "Glaucoma_", ""
                ),
            }
            for log in timeline_query
        ]

        return jsonify(
            {
                "kpis": {
                    "total_diagnoses": total_diagnoses,
                    "best_ai_accuracy": round(best_accuracy * 100, 2),
                    "total_trainings": total_trainings,
                    "arbovirus_count": total_arbovirus,
                    "glaucoma_count": total_glaucoma,
                },
                "charts": {
                    "model_performance": model_performance,
                    "learning_curve": timeline,
                },
                "filters_applied": {"period": period, "model": model_filter},
            }
        ), 200

    except Exception as e:
        print(f"Erro no dashboard: {e}")
        return jsonify({"error": "Erro ao carregar estatísticas"}), 500
