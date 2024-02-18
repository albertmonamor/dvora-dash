from Api.protocol import m_app
from flask import render_template
from time import sleep


# ==================== FILTER =========================
@m_app.template_filter('decimal')
def decimal_integer(value):
    return f"{value:,}"

#  ******************* ROUTES *************************

#@m_app.errorhandler(500)
@m_app.errorhandler(404)
def _404(n_error=None):
    sleep(2)
    return render_template("./error_tmp/404.html")

