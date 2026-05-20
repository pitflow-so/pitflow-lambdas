import html


def render_form(service_order_id: str, action: str) -> str:
    action_label = "Aprovar" if action == "APPROVED" else "Recusar"
    action_color = "#2e7d32" if action == "APPROVED" else "#c62828"
    action_symbol = "[OK]" if action == "APPROVED" else "[X]"

    return f"""
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
    <meta charset="UTF-8"/>
    <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
    <title>Pitflow - Confirmar Decisao</title>
    <style>
        body {{ margin:0; padding:0; background:#f4f4f4; font-family:Arial,sans-serif; }}
        .container {{ max-width:480px; margin:60px auto; background:#fff;
                    border-radius:8px; overflow:hidden;
                    box-shadow:0 2px 8px rgba(0,0,0,0.08); }}
        .header {{ background:#1a1a2e; padding:28px; text-align:center; }}
        .header h1 {{ margin:0; color:#fff; font-size:22px; letter-spacing:1px; }}
        .header p {{ margin:6px 0 0; color:#a0a0c0; font-size:13px; }}
        .body {{ padding:36px 40px; }}
        .body h2 {{ margin:0 0 8px; color:#1a1a2e; font-size:18px; }}
        .body p {{ color:#666; font-size:14px; margin:0 0 24px; }}
        label {{ display:block; font-size:13px; color:#444; margin-bottom:6px; }}
        input[type=text] {{ width:100%; box-sizing:border-box; padding:12px;
                            border:1px solid #ddd; border-radius:6px; font-size:15px; }}
        button {{ width:100%; margin-top:20px; padding:16px;
                background:{action_color}; color:#fff; border:none;
                border-radius:6px; font-size:16px; font-weight:bold;
                cursor:pointer; }}
        .footer {{ background:#f8f8fb; padding:20px 40px; text-align:center;
                border-top:1px solid #eee; }}
        .footer p {{ margin:0; color:#999; font-size:12px; }}
    </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
            <h1>PITFLOW</h1>
            <p>Gestao de Ordens de Servico</p>
            </div>
            <div class="body">
                <h2>{action_symbol} {action_label} Orcamento</h2>
                <p>Para confirmar sua decisao, informe seu CPF abaixo.</p>
                <form method="POST">
                    <input type="hidden" name="serviceOrderId" value="{html.escape(service_order_id)}"/>
                    <input type="hidden" name="action" value="{html.escape(action)}"/>
                    <label for="cpf">CPF</label>
                    <input type="text" id="cpf" name="cpf"
                        placeholder="000.000.000-00" maxlength="14" required/>
                    <button type="submit">{action_symbol} {action_label} Orcamento</button>
                </form>
            </div>
            <div class="footer">
            <p>Este link expira em <strong>3 horas</strong>.</p>
            </div>
        </div>
    </body>
    </html>
    """


def render_success(label: str) -> str:
    symbol = "[OK]" if label == "aprovado" else "[X]"
    return f"""
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head><meta charset="UTF-8"/><title>Pitflow - Confirmado</title>
        <style>
            body{{margin:0;padding:0;background:#f4f4f4;font-family:Arial,sans-serif;}}
            .box{{max-width:480px;margin:80px auto;background:#fff;border-radius:8px;
                    padding:48px 40px;text-align:center;box-shadow:0 2px 8px rgba(0,0,0,0.08);}}
            h2{{color:#1a1a2e;}} p{{color:#666;font-size:14px;}}
        </style>
    </head>
    <body>
        <div class="box">
            <h2>{symbol} Orcamento {html.escape(label)} com sucesso!</h2>
            <p>Sua decisao foi registrada. Voce pode fechar esta pagina.</p>
        </div>
    </body>
    </html>
    """


def render_error(message: str) -> str:
    safe_message = html.escape(message)
    return f"""
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head><meta charset="UTF-8"/><title>Pitflow - Erro</title>
        <style>
            body{{margin:0;padding:0;background:#f4f4f4;font-family:Arial,sans-serif;}}
            .box{{max-width:480px;margin:80px auto;background:#fff;border-radius:8px;
                    padding:48px 40px;text-align:center;box-shadow:0 2px 8px rgba(0,0,0,0.08);}}
            h2{{color:#c62828;}} p{{color:#666;font-size:14px;}}
        </style>
    </head>
    <body>
    <div class="box">
        <h2>Algo deu errado</h2>
        <p>{safe_message}</p>
    </div>
    </body></html>
    """
