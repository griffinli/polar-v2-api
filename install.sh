sudo apt update
sudo apt install -y python3-pip gunicorn python3-flask
sudo pip install -r requirements.txt
sudo gunicorn -w 4 -b 0.0.0.0:80 app:app