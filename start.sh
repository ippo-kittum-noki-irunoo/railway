if [ -z $UPSTREAM_REPO ]
then
  echo "Cloning main Repository"
  git clone https://github.com/Jiyad777/Railway-try.git /Railway-try
else
  echo "Cloning Custom Repo from $UPSTREAM_REPO"
  git clone $UPSTREAM_REPO /Railway-try
fi
cd /Railway-try
pip3 install -U -r requirements.txt
echo "Starting Bot...."
python3 bot.py
