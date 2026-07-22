import json
import os

from flask import Flask, render_template

from app.api.routes import api_bp, atualizar_tudo, carregar_config


def create_app():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    app = Flask(
        __name__,
        template_folder=os.path.join(base_dir, "dashboard", "templates"),
        static_folder=os.path.join(base_dir, "dashboard", "static"),
    )

    app.register_blueprint(api_bp)

    @app.route("/")
    def index():
        cfg = carregar_config()
        return render_template("index.html", intervalo_minutos=cfg.get("intervalo_atualizacao_minutos", 60))

    return app


def iniciar_agendador(app):
    """Cria e inicia o APScheduler para rodar atualizar_tudo() no intervalo
    configurado em config/settings.json."""
    from apscheduler.schedulers.background import BackgroundScheduler

    scheduler = BackgroundScheduler(daemon=True)

    def job():
        with app.app_context():
            try:
                atualizar_tudo()
            except Exception as e:
                print(f"[agendador] falha no ciclo automático: {e}")

    cfg = carregar_config()
    intervalo = cfg.get("intervalo_atualizacao_minutos", 60)
    scheduler.add_job(job, "interval", minutes=intervalo, id="atualizacao_periodica")
    scheduler.start()
    print(f"[agendador] rodando a cada {intervalo} minuto(s).")
    return scheduler
