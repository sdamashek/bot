from fabric.api import run, put, cd, prefix


def deploy():
    run("killall -USR2 python || echo No python process found")
    run("rm -rf watchtower-bot || echo No watchtower dir found")
    run("git clone --depth 1 https://github.com/watchtower/bot watchtower-bot")
    put(local_path="config.production.ini", remote_path="~/watchtower-bot/config.ini")
    with cd("~/watchtower-bot/"):
        run("virtualenv env")
        with prefix("source env/bin/activate"):
            run("pip install -r requirements.txt")
            run("python preinstall.py")
            run("python run.py")
