import os
import tempfile

import pytest

import main


@pytest.fixture
def client():
    db_fd, main.app.config['DATABASE'] = tempfile.mkstemp()
    main.app.config['TESTING'] = True

    with main.app.test_client() as client:
        with main.app.app_context():
            main.init_db()
        yield client

    os.close(db_fd)
    os.unlink(main.app.config['DATABASE'])

def test_empty_db(client):
    """Start with a blank database."""

    rv = client.get('/')
    assert b'No entries here so far' in rv.data

def login(client, username, password):
    return client.post('/login', data=dict(
        username=username,
        password=password
    ), follow_redirects=True)

def test_login(client):
    """Make sure login and logout works."""

    rv = login(client, "test","pass")
    print(rv.data)