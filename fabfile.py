from fabric import Connection, Config, task


@task
def deploy(c):
    remote_user = "root"
    remote_password = "mps12345"
    remote_host = "178.128.253.242"

    config = Config(overrides={'sudo':{'password':remote_password}})
    connect_kwarg = {'password': remote_password, "allow_agent": False}
    conn = Connection(host=remote_host, user=remote_user, config=config, connect_kwargs=connect_kwarg)

    print("Connected with remote machine")

    print("Copy sources")
    conn.put("flasks/app.py")
    conn.put("flasks/config.json")
    # conn.put("dist/")

    print("Install requirements")
    conn.sudo("pip3 install Flask Flask-CORS")

    print("Shutdown previous server")
    conn.sudo("pkill -F server.pid", warn=True)

    print("Start server")
    conn.sudo("nohup python3 app.py &> log.txt & echo $! > server.pid")

    print("Success!")
    conn.close()

