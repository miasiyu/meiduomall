from celery_tasks.main import app

@app.task(bind=True,name="helloworld")
def hello_world(self):
    import time
    for i in range(0,10):
        time.sleep(1)
        print("i = %s"%i)