import html
from decimal import Decimal, InvalidOperation


def render_form(token: str, action: str, amount: str | None = None) -> str:
    action_label = "Aprovar" if action == "APPROVED" else "Recusar"
    action_color = "#2e7d32" if action == "APPROVED" else "#c62828"
    action_symbol = "[OK]" if action == "APPROVED" else "[X]"

    return f"""
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
    <meta charset="UTF-8"/>
    <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
    <title>Pitflow - Confirmar decisão</title>
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
        .amount {{ background:#f8f8fb; border-radius:6px; margin-bottom:24px;
                   padding:16px; text-align:center; }}
        .amount span {{ display:block; color:#999; font-size:12px;
                        text-transform:uppercase; letter-spacing:1px; }}
        .amount strong {{ display:block; color:#1a1a2e; font-size:24px;
                          margin-top:6px; }}
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
            <p>Gestão de Ordens de Serviço</p>
            </div>
            <div class="body">
                <h2>{action_symbol} {action_label} Orçamento</h2>
                <p>Confirme sua decisão abaixo.</p>
                {_amount_field(amount)}
                <form method="POST" action="/customer/budget/confirm">
                    <input type="hidden" name="token" value="{html.escape(token)}"/>
                    {_reason_field(action)}
                    <button type="submit">{action_symbol} {action_label} Orçamento</button>
                </form>
            </div>
            <div class="footer">
            <p>Este link expira em <strong>3 horas</strong>.</p>
            </div>
        </div>
    </body>
    </html>
    """


def _amount_field(amount: str | None) -> str:
    if amount is None:
        return ""

    try:
        normalized = Decimal(str(amount)).quantize(Decimal("0.01"))
    except (InvalidOperation, ValueError):
        return ""

    integer, decimal = f"{normalized:.2f}".split(".")
    groups = []
    while integer:
        groups.append(integer[-3:])
        integer = integer[:-3]
    formatted = ".".join(reversed(groups)) + "," + decimal

    return f"""
                <div class="amount">
                    <span>Valor total do orçamento</span>
                    <strong>R$ {formatted}</strong>
                </div>
    """


def _reason_field(action: str) -> str:
    if action != "REJECTED":
        return ""

    return """
                    <label for="reason">Motivo da recusa</label>
                    <input type="text" id="reason" name="reason"
                        maxlength="500" required/>
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
            <h2>{symbol} Orçamento {html.escape(label)} com sucesso!</h2>
            <p>Sua decisão foi registrada. Você pode fechar esta página.</p>
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
