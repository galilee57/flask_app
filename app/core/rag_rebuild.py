"""Coordinate full index rebuilds in local Flask development."""

from contextlib import contextmanager
import fcntl
from threading import Event, Thread

from flask import current_app

from .rag import RagError, build_index, index_path


def state_path():
    return index_path().with_suffix(".rebuild-status")


def write_state(value):
    path = state_path()
    temp = path.with_suffix(".rebuild-tmp")
    temp.write_text(value, encoding="utf-8")
    temp.replace(path)


@contextmanager
def rebuild_lock():
    path = index_path().with_suffix(".rebuild-lock")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        yield


def rebuild_state():
    path = state_path()
    if not path.exists():
        return "ready" if index_path().exists() else "missing"
    try:
        state = path.read_text(encoding="utf-8")
        if state == "running":
            with rebuild_lock():
                state = "interrupted"
        return state
    except BlockingIOError:
        return "running"
    except OSError:
        return "failed"


def start_rag_rebuild():
    app = current_app._get_current_object()
    # Wait only until the worker has reserved the rebuild, so the redirect sees its state.
    reserved = Event()

    def worker():
        try:
            with app.app_context(), rebuild_lock():
                write_state("running")
                reserved.set()
                try:
                    build_index()
                except RagError as exc:
                    write_state(str(exc) if str(exc) == "embeddings" else "failed")
                except Exception:
                    app.logger.exception("Portfolio RAG rebuild failed")
                    write_state("failed")
                else:
                    write_state("complete")
        except BlockingIOError:
            pass
        except OSError:
            app.logger.exception("Could not record portfolio RAG rebuild state")
        finally:
            reserved.set()

    Thread(target=worker, name="portfolio-rag-rebuild", daemon=True).start()
    reserved.wait()
