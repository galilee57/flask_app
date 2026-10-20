from time import perf_counter

from flask import current_app, jsonify, render_template, request

from . import bp, service


@bp.get('/')
def home():
    return render_template('index_gpt_from_scratch.html')


@bp.get('/api/models')
def models():
    return jsonify(service.catalog())


@bp.post('/api/generate')
def generate():
    if request.content_length and request.content_length > 16384:
        return jsonify(error='invalid_request'), 413
    try:
        args = service.validate(request.get_json(silent=True))
        if not service.admit_generation(request.remote_addr or 'unknown'):
            return jsonify(error='rate_limit'), 429
        started = perf_counter()
        continuation = service.generate(*args)
        return jsonify(continuation=continuation, seconds=round(perf_counter() - started, 3))
    except ValueError as error:
        return jsonify(error=str(error)), 400
    except BlockingIOError:
        return jsonify(error='busy'), 429
    except ImportError:
        return jsonify(error='unavailable'), 503
    except Exception:
        current_app.logger.exception('GPT inference failed')
        return jsonify(error='unavailable'), 503
