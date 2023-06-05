To launch the project, run the

<code>docker-compose up</code>

command. In case of network connectivity issues (i.e. Error response from daemon: i/o timeout)
you can also run the project manually by running the 

<code>pip install requirements.txt</code>
 and 
<code>python manage.py runserver</code>

commands. In this case a separate redis-server must be run on port 6379
