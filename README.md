#Restaurant Report Service

##What Does This Service Do?
>The Restaurant Report Service Is Provided A Constant Stream Of Data Validating If A Restaurant Is Servicable Or Not.
> 
>We Also Have Timezone Information For Each Restaurant Store And The Operational Hours For Those Particular Stores In Their Timezone.
> 
>This Service Computes Abnormal Downtimes And Effective Uptimes As Recorded By The Status Streamer And Consolidates This Data Accross All Restaurant Stores

##Dependencies Setup
The Following Dependencies Are Required By Default For This Project To Run Smoothly
> MySQL `https://medium.com/macoclock/installing-mysql-5-7-using-homebrew-974cc2d42509`
>> You Can Set Your Database Env Variables In restaurant_reports/settings:DATABASES
> 
> Redis `https://redis.io/docs/getting-started/installation/install-redis-on-mac-os/`
>> You Can Set Your Redis Cache Variables In restaurant_reports/settings:CACHES

##Project Setup
>Since This Project is written in Python-Django, you will need to have python > 3.6 version to set this project up
> 
>>Clone The GitHub Repo In Your Local Machine
> 
>>Go To The Root Directory Of The Repository
>
>> Download The Required CSV Files Into The Root Directory i.e Outside The Scope Of restaurant_reports
> 
>>Run The Following Commands On The Terminal
>>> `python3 -m virtualenv venv`
>>
>>> `source /venv/bin/activate`
>>
>>> `pip3 install -r requirements.txt`
>>
>>> `python3 manage.py migrate`
>>
>>> `python3 manage.py import_csv_data`
>>
If your project setup ran successfully, you can go ahead and open two terminals.

In One We Need The REST Server Setup For That You Need To Run
> `python3 manage.py runserver`
>> Server Will Be Available On Port 8000
> 
In The Second Terminal, We Need To Setup Celery Consumer Which Will Pick Up Tasks For Rendering Reports Asynchronously using Redis Cache as a Queue
> `celery -A restaurant_reports.settings worker -Q celery -l info`
> 
Now You Can Start Testing The API Functionalities Properly



