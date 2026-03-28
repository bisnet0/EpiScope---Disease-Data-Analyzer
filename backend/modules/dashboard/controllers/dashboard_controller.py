import json
import traceback
from datetime import datetime, timedelta
from flask import request, jsonify
from flask_jwt_extended import get_jwt_identity
from sqlalchemy import func, text

# 👇 Imports mantidos apontando para a raiz (serão ajustados quando fatiarmos os models)
from backend.models.user_model import db
from backend.models.diagnosis_model import ArbovirusDiagnosis, GlaucomaDiagnosis
from backend.models.ml_log_model import ModelTrainingLog


def get_dashboard_stats():
    try:
        current_user_id = get_jwt_identity()

        period = request.args.get("period", "all")
        model_filter = request.args.get("model", "all")

        start_date = None
        if period == "24h":
            start_date = datetime.utcnow() - timedelta(hours=24)
        elif period == "7d":
            start_date = datetime.utcnow() - timedelta(days=7)
        elif period == "30d":
            start_date = datetime.utcnow() - timedelta(days=30)

        query_arbo = ArbovirusDiagnosis.query.filter_by(user_id=current_user_id)
        query_glaucoma = GlaucomaDiagnosis.query.filter_by(user_id=current_user_id)

        query_logs = ModelTrainingLog.query.filter_by(user_id=current_user_id)

        if start_date:
            query_arbo = query_arbo.filter(ArbovirusDiagnosis.created_at >= start_date)
            query_glaucoma = query_glaucoma.filter(
                GlaucomaDiagnosis.created_at >= start_date
            )
            query_logs = query_logs.filter(ModelTrainingLog.created_at >= start_date)

        if model_filter == "glaucoma":
            query_arbo = query_arbo.filter(text("1=0"))
        elif model_filter in ["xgboost", "random_forest", "decision_tree"]:
            query_glaucoma = query_glaucoma.filter(text("1=0"))

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

        all_logs = query_logs.all()

        ga_stats = {
            "mutation": [],
            "population": [],
            "crossover": [],
            "generations": [],
        }

        for log in all_logs:
            if log.parameters:
                try:
                    p = (
                        log.parameters
                        if isinstance(log.parameters, dict)
                        else json.loads(log.parameters)
                    )

                    if "ga_config" in p:
                        cfg = p["ga_config"]
                        acc = round(log.accuracy * 100, 2)

                        if cfg.get("mutation_rate"):
                            ga_stats["mutation"].append(
                                {"x": cfg["mutation_rate"], "y": acc}
                            )
                        if cfg.get("population_size"):
                            ga_stats["population"].append(
                                {"x": cfg["population_size"], "y": acc}
                            )
                        if cfg.get("crossover_rate"):
                            ga_stats["crossover"].append(
                                {"x": cfg["crossover_rate"], "y": acc}
                            )
                        if cfg.get("generations"):
                            ga_stats["generations"].append(
                                {"x": cfg["generations"], "y": acc}
                            )
                except Exception as e:
                    print(f"Log skip: {e}")
                    continue

        for k in ga_stats:
            ga_stats[k].sort(key=lambda item: item["x"])

        model_stats = (
            query_logs.with_entities(
                ModelTrainingLog.model_name, func.avg(ModelTrainingLog.accuracy)
            )
            .group_by(ModelTrainingLog.model_name)
            .all()
        )

        model_performance = []
        for m in model_stats:
            raw_name = m[0] if m[0] else "Unknown"
            raw_acc = m[1] if m[1] is not None else 0.0

            model_performance.append(
                {
                    "name": raw_name.replace("Arbovirus_", "")
                    .replace("Glaucoma_", "")
                    .replace("_", " "),
                    "accuracy": round(raw_acc * 100, 2),
                }
            )

        timeline = []

        for log in all_logs[-50:]:
            if log.accuracy is None:
                continue

            log_name = log.model_name if log.model_name else "Unknown"

            timeline.append(
                {
                    "id": log.id,
                    "date": (log.created_at - timedelta(hours=3)).strftime(
                        "%d/%m %H:%M"
                    ),
                    "accuracy": round(log.accuracy * 100, 2),
                    "model": log_name.replace("Arbovirus_", "").replace(
                        "Glaucoma_", ""
                    ),
                }
            )

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
                    "ga_analysis": ga_stats,
                },
                "filters_applied": {"period": period, "model": model_filter},
            }
        ), 200

    except Exception as e:
        print(f"ERRO CRÍTICO DASHBOARD: {e}", flush=True)
        traceback.print_exc()
        return jsonify({"error": "Erro interno", "details": str(e)}), 500