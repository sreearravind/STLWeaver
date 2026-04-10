"""Small local startup convenience entrypoint for STLWeaver.

Use this for local placeholder API development after installing
the minimal dependencies from ``requirements.txt``.
"""

import uvicorn


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
