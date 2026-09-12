"""CI contract check against a migrated PostgreSQL database."""
from app import create_app

app = create_app()
first = app.test_client()
second = app.test_client()
assert first.get("/health/ready").status_code == 200
before = first.get("/projects/snake/api/state").json
assert first.post("/projects/snake/api/move/right/manual").status_code == 200
assert second.get("/projects/snake/api/state").json["total_steps"] == 0
# Transfer a signed visitor cookie to another app instance.
other = create_app().test_client()
other.set_cookie("session", first.get_cookie("session").value)
assert other.get("/projects/snake/api/state").json["total_steps"] == before["total_steps"] + 1
url = "/projects/todolist/api/todolist"
assert first.post(url, json={"text": "ci"}).status_code == 403
task = first.post(url, json={"text": "ci"}, headers={"X-Admin-Token": app.config["ADMIN_API_TOKEN"]})
assert task.status_code == 201
assert task.json in second.get(url).json
assert second.delete(f"{url}/{task.json['id']}", headers={"X-Admin-Token": app.config["ADMIN_API_TOKEN"]}).status_code == 204

# Concurrent requests with the same session must preserve every move.
from concurrent.futures import ThreadPoolExecutor
cookie = first.get_cookie("session").value

def move_once(_):
    visitor = app.test_client()
    visitor.set_cookie("session", cookie)
    return visitor.post("/projects/snake/api/move/right/manual").status_code

with ThreadPoolExecutor(max_workers=8) as pool:
    assert list(pool.map(move_once, range(8))) == [200] * 8
assert first.get("/projects/snake/api/state").json["total_steps"] == before["total_steps"] + 9
